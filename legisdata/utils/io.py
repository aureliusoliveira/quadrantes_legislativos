import os
import tempfile
import threading
import time
import zipfile

import pandas as pd
import requests

# Identifica o projeto para a Câmara, em vez de fingir ser um navegador.
USER_AGENT = "quadrantes-legislativos (https://github.com/aureliusoliveira/quadrantes_legislativos)"

# Serializa as escritas do processo. Os coletores rodam com ThreadPoolExecutor,
# e `to_csv(mode="a")` disparado de várias threads no mesmo arquivo intercala
# conteúdo — não é operação atômica.
_TRAVA_DE_ESCRITA = threading.Lock()


def escrever_csv_atomico(df: pd.DataFrame, caminho, anexar: bool = False, sep: str = ",") -> None:
    """Escreve um CSV sem deixar o arquivo num estado intermediário.

    Grava num temporário no mesmo diretório e troca com `os.replace`, que é
    atômico dentro do mesmo sistema de arquivos: ou o arquivo antigo continua
    inteiro, ou o novo está completo. Nunca um pela metade.

    Com `anexar=True`, lê o conteúdo atual, concatena e reescreve tudo — mais
    caro que um append, e é o preço de não corromper sob concorrência.
    """
    caminho = str(caminho)
    diretorio = os.path.dirname(os.path.abspath(caminho))
    os.makedirs(diretorio, exist_ok=True)

    with _TRAVA_DE_ESCRITA:
        if anexar and os.path.exists(caminho):
            df = pd.concat([pd.read_csv(caminho, sep=sep), df], ignore_index=True)

        descritor, temporario = tempfile.mkstemp(dir=diretorio, suffix=".tmp")
        os.close(descritor)
        try:
            df.to_csv(temporario, index=False, sep=sep, encoding="utf-8")
            os.replace(temporario, caminho)
        except BaseException:
            if os.path.exists(temporario):
                os.remove(temporario)
            raise


def baixar_arquivo(url: str, destino: str, timeout: int = 120, tentativas: int = 6) -> str:
    """Baixa um arquivo para o disco, com retomada, escrevendo num temporário.

    Dois problemas resolvidos aqui. O primeiro: o servidor da Câmara encerra a
    conexão no meio dos arquivos grandes — nenhum dos arquivos consolidados de
    proposições chegou inteiro na primeira tentativa, e o de 2025 precisou de
    cinco. O segundo: download interrompido não pode substituir o arquivo bom da
    carga anterior por um truncado, que passaria pelos carregadores como "ano
    com menos dado".
    """
    destino = str(destino)
    diretorio = os.path.dirname(os.path.abspath(destino))
    os.makedirs(diretorio, exist_ok=True)

    descritor, temporario = tempfile.mkstemp(dir=diretorio, suffix=".part")
    os.close(descritor)

    try:
        tamanho_total = None
        for tentativa in range(1, tentativas + 1):
            ja_baixado = os.path.getsize(temporario)
            cabecalhos = {"User-Agent": USER_AGENT}
            if ja_baixado:
                cabecalhos["Range"] = f"bytes={ja_baixado}-"

            try:
                resposta = requests.get(url, stream=True, timeout=timeout, headers=cabecalhos)
                _abortar_se_a_fonte_recusou(resposta, url)
                resposta.raise_for_status()

                if tamanho_total is None:
                    tamanho_total = _tamanho_esperado(resposta, ja_baixado)

                modo = "ab" if ja_baixado and resposta.status_code == 206 else "wb"
                with open(temporario, modo) as arquivo:
                    for bloco in resposta.iter_content(chunk_size=1 << 16):
                        if bloco:
                            arquivo.write(bloco)
            except requests.exceptions.RequestException as e:
                if tentativa == tentativas:
                    raise
                print(f"   ⚠️  conexão interrompida ({e}); retomando {tentativa}/{tentativas}...")
                continue

            if tamanho_total is None or os.path.getsize(temporario) >= tamanho_total:
                os.replace(temporario, destino)
                return destino

            print(
                f"   ⚠️  recebido {os.path.getsize(temporario) / 1e6:.0f} de "
                f"{tamanho_total / 1e6:.0f} MB; retomando {tentativa}/{tentativas}..."
            )

        raise OSError(
            f"Download incompleto após {tentativas} tentativas: {url} "
            f"({os.path.getsize(temporario)} de {tamanho_total} bytes)"
        )
    except BaseException:
        if os.path.exists(temporario):
            os.remove(temporario)
        raise


def obter_json(url: str, parametros: dict | None = None, timeout: int = 30, tentativas: int = 5):
    """GET na API da Câmara, devolvendo o conteúdo de `dados`.

    Cada coletor tinha seu próprio laço de retry, com constantes diferentes — um
    esperava até 600s por requisição, o que sozinho inviabilizava a coleta
    dentro de um job de CI. Aqui a espera cresce até 30s e desiste em seguida:
    fonte fora do ar é falha de carga, não motivo para segurar o pipeline.
    """
    ultima_falha = None
    for tentativa in range(1, tentativas + 1):
        try:
            resposta = requests.get(
                url,
                params=parametros,
                timeout=timeout,
                headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            )
            resposta.raise_for_status()
            return resposta.json().get("dados")
        except (requests.exceptions.RequestException, ValueError) as e:
            ultima_falha = e
            if tentativa < tentativas:
                time.sleep(min(2**tentativa, 30))

    raise OSError(f"Falha ao consultar {url} após {tentativas} tentativas: {ultima_falha}")


def _abortar_se_a_fonte_recusou(resposta, url):
    """Erro do cliente não é falha transitória.

    A Câmara devolve 404 para arquivo de ano ainda não publicado. Insistir seis
    vezes com espera entre elas só atrasa a carga e esconde a causa real atrás
    de uma pilha de tentativas.
    """
    if 400 <= resposta.status_code < 500:
        raise OSError(f"A fonte respondeu {resposta.status_code} para {url}")


def _tamanho_esperado(resposta, ja_baixado):
    """Tamanho total do arquivo, somando o que já veio quando a resposta é parcial."""
    comprimento = resposta.headers.get("Content-Length")
    if comprimento is None:
        return None
    return int(comprimento) + (ja_baixado if resposta.status_code == 206 else 0)


def ler_csv_da_fonte(caminho: str, sep: str = ";", colunas: list[str] | None = None) -> pd.DataFrame:
    """Lê um CSV da fonte sem descartar linha em silêncio.

    Os carregadores usavam `on_bad_lines="skip"`, que perde linha malformada sem
    contar quantas — num projeto cuja proposta é rastrear qualquer número até o
    dado bruto, isso é perda invisível de dado. Aqui a linha malformada
    interrompe a carga e diz em qual arquivo está: o bruto fica no disco para
    inspeção, e nenhum número errado segue para o dashboard.

    Também usa o motor C (5x mais rápido no CEAP, mesmo resultado) e
    `low_memory=False`, que evita o pandas inferir tipos diferentes por bloco
    dentro de um mesmo arquivo.

    `colunas` restringe a leitura: o arquivo consolidado de proposições tem 31
    colunas e ~85 MB por ano, das quais o pipeline usa quatro. Coluna que sumir
    da fonte quebra a leitura aqui, e é assim que se quer descobrir.
    """
    try:
        return pd.read_csv(
            caminho,
            sep=sep,
            encoding="utf-8-sig",
            engine="c",
            low_memory=False,
            usecols=colunas,
        )
    except pd.errors.ParserError as e:
        raise ValueError(f"Arquivo de fonte malformado: {caminho}. {e}") from e
    except ValueError as e:
        raise ValueError(f"Arquivo de fonte fora do formato esperado: {caminho}. {e}") from e


def salvar_csv(df, caminho):
    """
    Salva um DataFrame em formato CSV no caminho especificado.
    Cria a pasta 'data/' se ela não existir.
    """
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    df.to_csv(caminho, index=False, encoding="utf-8-sig")


def extrair_csv_de_zip(zip_path: str, destino: str) -> str:
    """
    Extrai o primeiro arquivo .csv de um arquivo .zip e salva no diretório destino.
    Retorna o caminho final do arquivo extraído.
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(destino)

    arquivos_extraidos = os.listdir(destino)
    arquivo_csv = next((f for f in arquivos_extraidos if f.endswith(".csv")), None)

    if not arquivo_csv:
        raise FileNotFoundError("Nenhum arquivo .csv encontrado no zip.")

    caminho_csv = os.path.join(destino, arquivo_csv)
    return caminho_csv
