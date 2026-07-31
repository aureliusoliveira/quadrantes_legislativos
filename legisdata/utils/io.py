import os
import zipfile

import pandas as pd


def ler_csv_da_fonte(caminho: str, sep: str = ";") -> pd.DataFrame:
    """Lê um CSV da fonte sem descartar linha em silêncio.

    Os carregadores usavam `on_bad_lines="skip"`, que perde linha malformada sem
    contar quantas — num projeto cuja proposta é rastrear qualquer número até o
    dado bruto, isso é perda invisível de dado. Aqui a linha malformada
    interrompe a carga e diz em qual arquivo está: o bruto fica no disco para
    inspeção, e nenhum número errado segue para o dashboard.

    Também usa o motor C (5x mais rápido no CEAP, mesmo resultado) e
    `low_memory=False`, que evita o pandas inferir tipos diferentes por bloco
    dentro de um mesmo arquivo.
    """
    try:
        return pd.read_csv(
            caminho, sep=sep, encoding="utf-8-sig", engine="c", low_memory=False
        )
    except pd.errors.ParserError as e:
        raise ValueError(f"Arquivo de fonte malformado: {caminho}. {e}") from e


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
