"""Coleta: reprocessamento, escrita concorrente, download e escopo.

Os defeitos que impediam a cadência mensal do PRD, cada um com o teste que o
reproduz. Nenhum teste aqui toca a rede — as respostas são simuladas com
`responses`.
"""

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import pandas as pd
import pytest
import requests
import responses

from legisdata.coleta.coletor_base import ColetorBase, ColetorDeArquivoAnual
from legisdata.coleta.coletor_deputados import URL_DEPUTADOS, ColetorDeputados
from legisdata.utils.io import baixar_arquivo, escrever_csv_atomico


@pytest.fixture
def checkpoint_isolado(tmp_path, monkeypatch):
    from legisdata import config

    monkeypatch.setattr(config, "DIRETORIO_CHECKPOINT", str(tmp_path / "checkpoints"))
    monkeypatch.setattr(config, "ARQUIVO_CHECKPOINT", str(tmp_path / "checkpoints" / "arquivos.csv"))
    monkeypatch.setattr(config, "DIRETORIO_RAW", str(tmp_path / "raw"))
    return tmp_path


# --- Reprocessamento (C1) --------------------------------------------------


def test_ano_aberto_e_sempre_rebaixado(checkpoint_isolado):
    """O CEAP é republicado conforme a Câmara processa as despesas.

    O checkpoint antigo marcava (tipo, ano) como baixado em definitivo, e o ano
    congelava no estado do dia da primeira coleta — foi o que produziu os
    R$ 177 milhões de subestimação no artefato publicado.
    """
    coletor = ColetorBase(tipo="gastos")
    hoje = date(2026, 7, 31)

    assert coletor.deve_baixar(2026, hoje=hoje) is True
    coletor.registrar_coleta(2026)
    assert coletor.deve_baixar(2026, hoje=hoje) is True, (
        "ano corrente precisa ser rebaixado mesmo já tendo sido coletado"
    )


def test_ano_fechado_nao_e_rebaixado(checkpoint_isolado):
    coletor = ColetorBase(tipo="gastos")
    hoje = date(2026, 7, 31)

    assert coletor.deve_baixar(2023, hoje=hoje) is True
    coletor.registrar_coleta(2023)
    assert coletor.deve_baixar(2023, hoje=hoje) is False


def test_ano_recem_fechado_ainda_e_rebaixado(checkpoint_isolado):
    """Janela de carência: o CEAP de dezembro chega semanas depois."""
    coletor = ColetorBase(tipo="gastos")
    coletor.registrar_coleta(2025)

    assert coletor.deve_baixar(2025, hoje=date(2026, 1, 20)) is True
    assert coletor.deve_baixar(2025, hoje=date(2026, 6, 20)) is False


def test_checkpoint_de_tipos_diferentes_nao_se_confunde(checkpoint_isolado):
    ColetorBase(tipo="gastos").registrar_coleta(2023)

    assert ColetorBase(tipo="proposicoes").deve_baixar(2023, hoje=date(2026, 7, 31)) is True


def test_checkpoint_nao_cresce_a_cada_recoleta(checkpoint_isolado):
    """O checkpoint antigo dava append a cada execução, então uma carga mensal
    acumulava uma linha por mês por tipo por ano, indefinidamente."""
    coletor = ColetorBase(tipo="gastos")
    for _ in range(5):
        coletor.registrar_coleta(2026)

    registros = coletor.carregar_checkpoint()
    assert len(registros) == 1, f"checkpoint acumulou {len(registros)} linhas para o mesmo (tipo, ano)"


def test_checkpoint_guarda_quando_a_coleta_aconteceu(checkpoint_isolado):
    coletor = ColetorBase(tipo="gastos")
    coletor.registrar_coleta(2026)

    registro = coletor.carregar_checkpoint().iloc[0]
    assert registro["tipo"] == "gastos"
    assert int(registro["ano"]) == 2026
    assert pd.notna(registro["baixado_em"])


# --- Escrita concorrente (C3) ----------------------------------------------


def test_escrita_concorrente_nao_corrompe_o_arquivo(tmp_path):
    """Os coletores davam `to_csv(mode='a')` de dentro de 5 threads no mesmo
    arquivo. Append de múltiplas threads não é atômico: linha intercalada é
    questão de volume, não de sorte.
    """
    caminho = tmp_path / "saida.csv"
    total = 400

    def escrever(indice):
        escrever_csv_atomico(
            pd.DataFrame([{"id": indice, "texto": "x" * 200}]),
            caminho,
            anexar=True,
        )

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(escrever, range(total)))

    lido = pd.read_csv(caminho)
    assert len(lido) == total, f"esperava {total} linhas, li {len(lido)}"
    assert sorted(lido["id"]) == list(range(total)), "linhas perdidas ou duplicadas"
    assert lido["texto"].map(len).eq(200).all(), "conteúdo de linha corrompido"


def test_escrita_atomica_nao_deixa_arquivo_parcial(tmp_path):
    """Escrita interrompida não pode substituir o arquivo bom por um truncado."""
    caminho = tmp_path / "saida.csv"
    escrever_csv_atomico(pd.DataFrame([{"id": 1}]), caminho)
    original = caminho.read_text(encoding="utf-8")

    class DataFrameQueFalha(pd.DataFrame):
        def to_csv(self, *a, **k):
            raise OSError("disco cheio")

    with pytest.raises(OSError):
        escrever_csv_atomico(DataFrameQueFalha([{"id": 2}]), caminho)

    assert caminho.read_text(encoding="utf-8") == original
    assert list(caminho.parent.iterdir()) == [caminho], "sobrou arquivo temporário"


# --- Download dos arquivos anuais ------------------------------------------

URL_QUALQUER = "https://dadosabertos.camara.leg.br/arquivos/x/csv/x-2026.csv"


class ConexaoCaiu(requests.exceptions.ChunkedEncodingError):
    """Encerramento de conexão no meio do corpo, como o servidor da Câmara produz."""


@responses.activate
def test_download_interrompido_nao_substitui_o_arquivo_da_carga_anterior(tmp_path):
    """Todo arquivo consolidado grande caiu no meio pelo menos uma vez na coleta
    real. Se o truncado substituísse o bom, o ano apareceria com menos dado sem
    nada acusar."""
    destino = tmp_path / "2026.csv"
    destino.write_text("dado bom da carga anterior\n", encoding="utf-8")

    responses.add(responses.GET, URL_QUALQUER, body=ConexaoCaiu("conexão encerrada"))

    with pytest.raises(Exception):
        baixar_arquivo(URL_QUALQUER, str(destino), tentativas=2)

    assert destino.read_text(encoding="utf-8") == "dado bom da carga anterior\n"
    assert list(tmp_path.iterdir()) == [destino], "sobrou arquivo .part no diretório"


@responses.activate
def test_download_retoma_do_ponto_em_que_parou(tmp_path):
    """A retomada por `Range` é o que faz um arquivo de 90 MB terminar: sem ela,
    cada tentativa recomeça do zero e a chance de completar é baixa.

    Os tamanhos são múltiplos do bloco de leitura de propósito. O que a conexão
    entregou dentro de um bloco que não fechou se perde — só bloco inteiro conta
    como progresso, e é por isso que a retomada ajuda em arquivo grande e não
    faz diferença em arquivo pequeno.
    """
    bloco = 1 << 16
    entregue, faltante = b"a" * (2 * bloco), b"b" * bloco
    responses.add(
        responses.GET,
        URL_QUALQUER,
        body=entregue,
        headers={"Content-Length": str(len(entregue) + len(faltante))},
    )
    responses.add(responses.GET, URL_QUALQUER, status=206, body=faltante)

    destino = baixar_arquivo(URL_QUALQUER, str(tmp_path / "2026.csv"), tentativas=3)

    assert open(destino, "rb").read() == entregue + faltante
    assert responses.calls[1].request.headers["Range"] == f"bytes={len(entregue)}-"


@responses.activate
def test_arquivo_inexistente_falha_na_primeira_resposta(tmp_path):
    """404 é ano ainda não publicado, não conexão instável. Repetir seis vezes
    com espera entre elas atrasa a carga e esconde a causa."""
    responses.add(responses.GET, URL_QUALQUER, status=404)

    with pytest.raises(OSError, match="404"):
        baixar_arquivo(URL_QUALQUER, str(tmp_path / "2026.csv"))

    assert len(responses.calls) == 1


@responses.activate
def test_download_se_identifica_para_a_fonte(tmp_path):
    """A coleta antiga se anunciava como `Mozilla/5.0`. Consumir dado aberto não
    exige fingir ser um navegador, e um User-Agent honesto é o que permite à
    Câmara distinguir o tráfego do projeto se ele incomodar."""
    responses.add(responses.GET, URL_QUALQUER, body=b"x")

    baixar_arquivo(URL_QUALQUER, str(tmp_path / "2026.csv"))

    assert "quadrantes" in responses.calls[0].request.headers["User-Agent"].lower()


# --- Coletor de arquivo anual ----------------------------------------------


class ColetorDeTeste(ColetorDeArquivoAnual):
    URL = "https://exemplo.invalido/base-{ano}.csv"
    ROTULO = "Base"

    def __init__(self):
        super().__init__(tipo="base")


@responses.activate
def test_bruto_e_gravado_como_a_fonte_publicou(checkpoint_isolado):
    """A camada bruta guarda o arquivo da fonte, byte a byte.

    Selecionar coluna ou converter tipo na coleta amarra o bruto à necessidade
    do indicador de hoje: mudar a derivação passaria a exigir baixar tudo de
    novo, e a fonte não guarda versão anterior.
    """
    publicado = '"id";"situacao"\n"1";"Arquivada"\n'.encode()
    responses.add(responses.GET, "https://exemplo.invalido/base-2026.csv", body=publicado)

    ColetorDeTeste().baixar(2026)

    gravado = os.path.join(str(checkpoint_isolado), "raw", "base", "2026.csv")
    assert open(gravado, "rb").read() == publicado


@responses.activate
def test_ano_fechado_ja_coletado_nao_gera_requisicao(checkpoint_isolado):
    responses.add(responses.GET, "https://exemplo.invalido/base-2023.csv", body=b"x")
    coletor = ColetorDeTeste()
    coletor.baixar(2023)

    coletor.baixar(2023)

    assert len(responses.calls) == 1, "ano fechado foi rebaixado sem necessidade"


# --- Cadastro de deputados -------------------------------------------------


def detalhe_de(id_deputado, situacao="Exercício", partido="P1"):
    return {
        "dados": {
            "id": id_deputado,
            "nomeCivil": f"Fulano {id_deputado}",
            "ultimoStatus": {
                "id": id_deputado,
                "nomeEleitoral": f"Dep {id_deputado}",
                "siglaUf": "SP",
                "siglaPartido": partido,
                "idLegislatura": 57,
                "situacao": situacao,
                "condicaoEleitoral": "Titular",
            },
        }
    }


def registrar_cadastro(ids, situacao="Exercício", partido="P1"):
    """Uma página com os ids, uma vazia para encerrar, e o detalhe de cada um."""
    responses.add(responses.GET, URL_DEPUTADOS, json={"dados": [{"id": i} for i in ids]})
    responses.add(responses.GET, URL_DEPUTADOS, json={"dados": []})
    for id_deputado in ids:
        responses.add(
            responses.GET,
            f"{URL_DEPUTADOS}/{id_deputado}",
            json=detalhe_de(id_deputado, situacao=situacao, partido=partido),
        )


@responses.activate
def test_cadastro_e_rebaixado_inteiro_a_cada_carga(checkpoint_isolado):
    """O coletor antigo pulava id já presente no arquivo.

    Como a padronização só mantém quem está em `situacao == "Exercício"`, um
    deputado que deixou o mandato continuava entrando no ranking — o filtro
    rodava sobre o cadastro do dia da primeira coleta.
    """
    coletor = ColetorDeputados(max_workers=2)

    registrar_cadastro([1, 2], situacao="Exercício")
    coletor.baixar()

    responses.reset()
    registrar_cadastro([1, 2], situacao="Fim de Exercício")
    coletor.baixar()

    cadastro = pd.read_csv(coletor.caminho_saida)
    assert len(cadastro) == 2, "o arquivo foi acrescido em vez de substituído"
    assert all("Fim de Exercício" in status for status in cadastro["ultimoStatus"])


@responses.activate
def test_deputado_que_saiu_da_legislatura_some_do_cadastro(checkpoint_isolado):
    coletor = ColetorDeputados(max_workers=2)

    registrar_cadastro([1, 2])
    coletor.baixar()

    responses.reset()
    registrar_cadastro([1])
    coletor.baixar()

    assert pd.read_csv(coletor.caminho_saida)["id"].tolist() == [1]


@responses.activate
def test_cadastro_pede_a_legislatura_alvo(checkpoint_isolado):
    """Sem o filtro, a listagem devolve a legislatura corrente — e uma recarga
    da 56ª cruzaria proposições de 2019-2022 com os deputados de hoje."""
    registrar_cadastro([1])

    ColetorDeputados(max_workers=1, legislatura=56).baixar()

    assert responses.calls[0].request.params["idLegislatura"] == "56"


@responses.activate
def test_falha_num_detalhe_interrompe_a_coleta(checkpoint_isolado):
    """Cadastro pela metade é deputado sumindo do ranking sem nada acusar."""
    responses.add(responses.GET, URL_DEPUTADOS, json={"dados": [{"id": 1}, {"id": 2}]})
    responses.add(responses.GET, URL_DEPUTADOS, json={"dados": []})
    responses.add(responses.GET, f"{URL_DEPUTADOS}/1", json=detalhe_de(1))
    responses.add(responses.GET, f"{URL_DEPUTADOS}/2", status=500)

    coletor = ColetorDeputados(max_workers=1, tentativas=1)
    with pytest.raises(OSError):
        coletor.baixar()

    assert not os.path.exists(coletor.caminho_saida)
