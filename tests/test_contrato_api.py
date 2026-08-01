"""Testes de contrato com as fontes da Câmara.

A fonte pode renomear campo, mudar tipo ou trocar a forma do envelope. Quando
isso acontecer, o projeto tem duas opções: descobrir por um teste que quebra, ou
descobrir por um número errado no dashboard. Estes testes são a primeira opção.

São duas fontes com contratos diferentes. O **cadastro de deputados** vem da API
REST, em JSON. As **bases anuais** — proposições, temas, autores — vêm dos
arquivos CSV consolidados, e ali o contrato é o cabeçalho: nome de coluna,
separador e o formato do que vai dentro.

As fixtures são amostras reais das duas fontes, salvas em `fixtures/api/`.
**Nenhum teste aqui toca a rede** — o que se verifica é que o formato sobre o
qual o código foi escrito continua sendo o formato que a fonte entrega. Para
atualizar as fixtures, veja `docs/testes_de_contrato.md`.
"""

import json
from pathlib import Path

import pandas as pd
import pytest

from legisdata.processamento.carregadores.proposicoes import (
    COLUNAS_DA_FONTE as COLUNAS_DE_PROPOSICOES,
)
from legisdata.processamento.carregadores.situacoes import (
    COLUNAS_DA_FONTE as COLUNAS_DE_SITUACOES,
)
from legisdata.processamento.carregadores.temas import COLUNAS_DA_FONTE as COLUNAS_DE_TEMAS

FIXTURES = Path(__file__).parent / "fixtures" / "api"


def carregar(nome):
    return json.loads((FIXTURES / nome).read_text(encoding="utf-8"))


def registros(nome):
    dados = carregar(nome)["dados"]
    return dados if isinstance(dados, list) else [dados]


def tabela(nome):
    """Lê a amostra do CSV consolidado como o carregador lê o arquivo inteiro."""
    return pd.read_csv(FIXTURES / nome, sep=";", encoding="utf-8-sig")


def test_envelope_tem_a_chave_dados():
    """Todo coletor faz `resp.json().get("dados")`. Se o envelope mudar, todos
    passam a coletar vazio silenciosamente."""
    for nome in FIXTURES.glob("*.json"):
        assert "dados" in carregar(nome.name), f"{nome.name} sem a chave 'dados'"


# --- Deputados -------------------------------------------------------------


def test_lista_de_deputados_traz_id():
    """ColetorDeputados monta a fila de coleta com `dep["id"]`."""
    for registro in registros("deputados_lista.json"):
        assert "id" in registro
        assert isinstance(registro["id"], int)


@pytest.mark.parametrize("campo", ["id", "nomeEleitoral", "siglaUf", "siglaPartido",
                                   "idLegislatura", "situacao", "condicaoEleitoral"])
def test_detalhe_do_deputado_traz_os_campos_que_a_padronizacao_extrai(campo):
    """TransformadorDados._padronizar_deputados extrai exatamente estes sete
    campos de `ultimoStatus`. Um renomeado quebra a padronização inteira."""
    ultimo_status = registros("deputado_detalhe.json")[0]["ultimoStatus"]
    assert campo in ultimo_status, f"'{campo}' saiu de ultimoStatus"


def test_ultimo_status_e_objeto_e_nao_texto():
    """A padronização usa `ast.literal_eval` porque o dict vira string ao passar
    pelo CSV. Na origem ele é objeto — se deixar de ser, o round-trip muda."""
    assert isinstance(registros("deputado_detalhe.json")[0]["ultimoStatus"], dict)


def test_situacao_e_condicao_eleitoral_sao_texto():
    ultimo_status = registros("deputado_detalhe.json")[0]["ultimoStatus"]
    assert isinstance(ultimo_status["situacao"], str)
    assert isinstance(ultimo_status["condicaoEleitoral"], str)


def test_id_legislatura_e_inteiro():
    """O filtro de legislatura compara com int; se virar string, filtra tudo."""
    assert isinstance(registros("deputado_detalhe.json")[0]["ultimoStatus"]["idLegislatura"], int)


# --- Proposições e situações -----------------------------------------------
#
# Ambas saem do mesmo arquivo consolidado: proposições usa `id` e `siglaTipo`,
# situações usa o bloco `ultimoStatus_*`.


@pytest.mark.parametrize("coluna", COLUNAS_DE_PROPOSICOES + COLUNAS_DE_SITUACOES)
def test_arquivo_de_proposicoes_traz_as_colunas_que_o_pipeline_le(coluna):
    """Os carregadores pedem estas colunas por nome. Uma renomeada na fonte não
    devolve dado faltando: interrompe a leitura do arquivo inteiro."""
    assert coluna in tabela("proposicoes_consolidado.csv").columns


def test_sigla_tipo_e_texto_curto():
    """`siglaTipo` é a chave do mapa de pesos — é dela que sai a produtividade."""
    for sigla in tabela("proposicoes_consolidado.csv")["siglaTipo"]:
        assert isinstance(sigla, str) and 2 <= len(sigla) <= 5, f"siglaTipo inesperado: {sigla!r}"


def test_id_de_proposicao_e_inteiro():
    assert pd.api.types.is_integer_dtype(tabela("proposicoes_consolidado.csv")["id"])


def test_situacao_e_texto_livre_e_pode_faltar():
    """A classificação de eficácia é feita por palavra-chave nesse texto.

    A ausência é parte do contrato: proposição sem situação registrada existe, e
    o pipeline a descarta em vez de classificá-la como "em andamento".
    """
    situacoes = tabela("proposicoes_consolidado.csv")["ultimoStatus_descricaoSituacao"]
    assert situacoes.dropna().map(lambda s: isinstance(s, str) and s.strip()).all()


def test_data_do_ultimo_status_e_iso():
    datas = tabela("proposicoes_consolidado.csv")["ultimoStatus_dataHora"].dropna()
    assert not pd.to_datetime(datas, format="ISO8601", errors="coerce").isna().any()


# --- Temas -----------------------------------------------------------------


@pytest.mark.parametrize("coluna", COLUNAS_DE_TEMAS)
def test_arquivo_de_temas_traz_as_colunas_que_o_pipeline_le(coluna):
    assert coluna in tabela("proposicoes_temas.csv").columns


def test_tema_e_texto_nao_vazio():
    for tema in tabela("proposicoes_temas.csv")["tema"]:
        assert isinstance(tema, str) and tema.strip()


def test_uri_da_proposicao_termina_no_id():
    """O arquivo de temas identifica a proposição por URI, e o resto do pipeline
    trabalha com id. O carregador extrai o id do fim da URI — se a fonte mudar a
    forma do endereço, a junção com proposições passa a não casar nada."""
    for uri in tabela("proposicoes_temas.csv")["uriProposicao"]:
        assert uri.rsplit("/", 1)[-1].isdigit(), f"URI sem id no fim: {uri}"


# --- Autores ---------------------------------------------------------------


@pytest.mark.parametrize("coluna", ["idProposicao", "idDeputadoAutor", "nomeAutor"])
def test_arquivo_de_autores_traz_as_colunas_da_padronizacao(coluna):
    assert coluna in tabela("proposicoes_autores.csv").columns


def test_autoria_de_orgao_vem_sem_id_de_deputado():
    """Proposição do Senado ou de comissão tem `idDeputadoAutor` vazio, e é assim
    que o pipeline recorta o que interessa: só entra no cálculo o que tem
    deputado autor. Se a fonte passasse a preencher esse campo com outra coisa,
    o escopo do produto mudaria em silêncio."""
    autores = tabela("proposicoes_autores.csv")
    de_orgao = autores[~autores["tipoAutor"].str.startswith("Deputado")]

    assert not de_orgao.empty, "a amostra precisa conter ao menos uma autoria de órgão"
    assert de_orgao["idDeputadoAutor"].isna().all()
