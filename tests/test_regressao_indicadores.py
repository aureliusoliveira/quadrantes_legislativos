"""Regressão dos indicadores.

Uma base de referência pequena, com resultado calculado à mão em
`fixtures/regressao/esperado.csv`, rodada pelo pipeline de indicadores com o
mapa de pesos real do projeto.

O objetivo não é provar que os números estão certos — é impedir que mudem sem
que alguém tenha decidido mudá-los. Se este teste quebrar numa refatoração, a
pergunta certa é "qual número mudou e por quê", e a resposta precisa virar uma
atualização consciente do esperado.csv.

A conferência das contas está em docs/regressao_indicadores.md.
"""

from pathlib import Path

import pandas as pd
import pytest

from legisdata.config import MAPA_DE_PESOS
from legisdata.indicadores.indicadores_gerais import IndicadoresGerais

FIXTURES = Path(__file__).parent / "fixtures" / "regressao"

COLUNAS_COMPARADAS = [
    "produtividade_legislativa",
    "gasto_ceap_ajustado",
    "pct_sucesso",
    "pct_fracasso",
    "pct_andamento",
    "temas_destaque",
    "quadrante",
    "ranking",
]


def _ler(nome, **kwargs):
    return pd.read_csv(FIXTURES / nome, sep=";", encoding="utf-8", dtype=str, **kwargs)


@pytest.fixture(scope="module")
def resultado():
    dados = {
        "deputados": _ler("deputados.csv"),
        "proposicoes": _ler("proposicoes.csv"),
        "autores": _ler("autores.csv"),
        "gastos": _ler("gastos.csv").assign(
            vlrLiquido=lambda d: pd.to_numeric(d["vlrLiquido"])
        ),
        "tramitacoes": _ler("tramitacoes.csv"),
        "temas": _ler("temas.csv"),
    }
    calculado = IndicadoresGerais(dados, caminho_pesos=MAPA_DE_PESOS).calcular()
    return calculado.set_index("idDeputado").sort_index()


@pytest.fixture(scope="module")
def esperado():
    df = pd.read_csv(FIXTURES / "esperado.csv", sep=";", encoding="utf-8", dtype={"idDeputado": str})
    return df.set_index("idDeputado").sort_index()


def test_resultado_cobre_exatamente_os_deputados_esperados(resultado, esperado):
    assert list(resultado.index) == list(esperado.index)


@pytest.mark.parametrize("coluna", COLUNAS_COMPARADAS)
def test_coluna_publicada_nao_mudou(resultado, esperado, coluna):
    pd.testing.assert_series_equal(
        resultado[coluna],
        esperado[coluna],
        check_dtype=False,
        check_names=False,
        rtol=1e-9,
    )


def test_empate_triplo_no_ranking_permanece(resultado):
    """Três deputados somam a mesma posição composta e dividem o 2º lugar.

    Está no conjunto de regressão de propósito: é o comportamento de empate que
    a Fase 2 vai revisitar, e ele precisa quebrar o teste quando mudar.
    """
    assert sorted(resultado["ranking"]) == [1, 2, 2, 2, 3]
