"""Testes de qualidade de dados — validam o dado, não o código.

Rodam sobre o artefato publicado (`dashboard/data/resultados.csv`), que é
versionado e portanto está disponível no CI sem rede. São as invariantes que
precisam valer em qualquer carga: se uma delas quebrar, o número que chegou ao
dashboard não é confiável, independentemente de os testes unitários passarem.
"""

from pathlib import Path

import pandas as pd
import pytest

RESULTADOS = Path(__file__).resolve().parent.parent / "dashboard" / "data" / "resultados.csv"

CADEIRAS_NA_CAMARA = 513

QUADRANTES_VALIDOS = {
    "Alta produtividade e alto custo",
    "Alta produtividade e baixo custo",
    "Baixa produtividade e alto custo",
    "Baixa produtividade e baixo custo",
}

COLUNAS_OBRIGATORIAS = [
    "idDeputado",
    "nome",
    "sgUF",
    "sgPartido",
    "produtividade_legislativa",
    "gasto_ceap_ajustado",
    "quadrante",
    "ranking",
]


@pytest.fixture(scope="module")
def resultados():
    return pd.read_csv(RESULTADOS, sep=";", encoding="utf-8")


def test_colunas_obrigatorias_presentes(resultados):
    faltando = set(COLUNAS_OBRIGATORIAS) - set(resultados.columns)
    assert not faltando, f"colunas ausentes no resultado publicado: {sorted(faltando)}"


def test_chave_de_deputado_e_unica(resultados):
    duplicados = resultados["idDeputado"][resultados["idDeputado"].duplicated()]
    assert duplicados.empty, f"idDeputado repetido: {duplicados.tolist()}"


def test_campos_criticos_sem_nulo(resultados):
    nulos = resultados[COLUNAS_OBRIGATORIAS].isna().sum()
    assert not nulos.any(), f"nulos em campo crítico:\n{nulos[nulos > 0]}"


def test_quantidade_de_parlamentares_e_plausivel(resultados):
    """A Câmara tem 513 cadeiras. Suplentes e substituições fazem o total de
    parlamentares que passaram pela legislatura ser maior, nunca muito menor —
    um resultado com poucas centenas de linhas indica merge perdendo gente."""
    assert 450 <= len(resultados) <= 700, f"{len(resultados)} parlamentares no resultado"


def test_uf_valida(resultados):
    ufs = {
        "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS",
        "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC",
        "SE", "SP", "TO",
    }
    invalidas = set(resultados["sgUF"].dropna()) - ufs
    assert not invalidas, f"UF fora da federação: {invalidas}"


def test_todas_as_ufs_estao_representadas(resultados):
    """Toda unidade da federação elege deputado federal. UF ausente é sinal de
    filtro ou merge derrubando um bloco inteiro."""
    assert resultados["sgUF"].nunique() == 27, (
        f"apenas {resultados['sgUF'].nunique()} UFs no resultado"
    )


def test_produtividade_nao_e_negativa(resultados):
    negativos = resultados[resultados["produtividade_legislativa"] < 0]
    assert negativos.empty, f"{len(negativos)} deputados com produtividade negativa"


def test_gasto_ajustado_nao_e_negativo(resultados):
    """O CEAP publica estornos como valor negativo. Se a soma de um deputado
    fica negativa, o que chegou ao resultado é restituição sem a despesa
    correspondente — sinal de recorte de período errado."""
    negativos = resultados[resultados["gasto_ceap_ajustado"] < 0]
    assert negativos.empty, (
        f"{len(negativos)} deputados com gasto negativo: "
        f"{negativos[['nome', 'gasto_ceap_ajustado']].to_dict('records')}"
    )


def test_quadrante_pertence_ao_conjunto_conhecido(resultados):
    invalidos = set(resultados["quadrante"].dropna()) - QUADRANTES_VALIDOS
    assert not invalidos, f"quadrante inesperado: {invalidos}"


def test_quadrantes_dividem_a_base_pela_mediana(resultados):
    """Corte por mediana nas duas dimensões: cada metade tem ~50%, e nenhum
    quadrante pode ficar vazio ou concentrar quase tudo."""
    contagem = resultados["quadrante"].value_counts()
    assert len(contagem) == 4, f"nem todos os quadrantes existem: {contagem.to_dict()}"

    alta = contagem.filter(like="Alta produtividade").sum()
    assert 0.40 <= alta / len(resultados) <= 0.60, (
        f"{alta / len(resultados):.1%} da base em alta produtividade — o corte "
        "deveria ser a mediana"
    )


def test_percentuais_de_tramitacao_somam_um(resultados):
    colunas = ["pct_sucesso", "pct_fracasso", "pct_andamento"]
    if not set(colunas).issubset(resultados.columns):
        pytest.skip("resultado sem métricas de tramitação")

    soma = resultados[colunas].sum(axis=1)
    fora = resultados[(soma - 1).abs() > 1e-6]
    assert fora.empty, f"{len(fora)} deputados com percentuais que não somam 1"


def test_percentuais_de_tramitacao_estao_entre_zero_e_um(resultados):
    colunas = [c for c in ["pct_sucesso", "pct_fracasso", "pct_andamento"] if c in resultados]
    if not colunas:
        pytest.skip("resultado sem métricas de tramitação")

    fora = resultados[(resultados[colunas] < 0).any(axis=1) | (resultados[colunas] > 1).any(axis=1)]
    assert fora.empty, f"{len(fora)} deputados com percentual fora de [0, 1]"


def test_ranking_comeca_em_um_e_nao_tem_buraco(resultados):
    """O ranking usa `method='dense'`, que por definição não pula posições.
    Buraco na sequência significa que a coluna foi recalculada em outro lugar."""
    posicoes = sorted(resultados["ranking"].unique())
    assert posicoes[0] == 1, f"ranking começa em {posicoes[0]}"
    assert posicoes == list(range(1, len(posicoes) + 1)), "há posições faltando no ranking"


def test_ranking_cobre_todos_os_parlamentares(resultados):
    assert resultados["ranking"].notna().all()
    assert len(resultados) <= CADEIRAS_NA_CAMARA * 2
