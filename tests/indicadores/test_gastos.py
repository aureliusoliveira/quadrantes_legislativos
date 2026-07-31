"""Gasto CEAP ajustado.

Regra declarada no dashboard: soma da cota parlamentar, excluindo despesas com
passagens aéreas envolvendo Brasília, "já que são comuns a todos os mandatos".
"""

import pandas as pd
import pytest

from legisdata.indicadores.indicadores_gastos import IndicadoresGastos


def _gasto(resultado, id_deputado):
    return resultado.loc[resultado["idDeputado"] == id_deputado, "gasto_ceap_ajustado"].iloc[0]


def test_soma_despesas_do_deputado_excluindo_passagens(gastos):
    resultado = IndicadoresGastos(gastos).calcular()

    # Dep 10: 1000 + 250, sem os 500 da passagem BSB/GRU
    assert _gasto(resultado, "10") == pytest.approx(1250.0)
    assert _gasto(resultado, "20") == pytest.approx(3000.0)


def test_exclui_por_descricao_mesmo_sem_trecho():
    """O filtro casa 'PASSAGE' na descrição — pega PASSAGEM e PASSAGENS."""
    gastos = pd.DataFrame(
        {
            "idDeputado": ["10", "10"],
            "txtDescricao": ["PASSAGENS AÉREAS", "TELEFONIA"],
            "txtTrecho": ["", ""],
            "vlrLiquido": [800.0, 200.0],
        }
    )
    resultado = IndicadoresGastos(gastos).calcular()

    assert _gasto(resultado, "10") == pytest.approx(200.0)


def test_exclui_por_trecho_mesmo_sem_passagem_na_descricao():
    gastos = pd.DataFrame(
        {
            "idDeputado": ["10", "10"],
            "txtDescricao": ["LOCAÇÃO DE VEÍCULOS", "TELEFONIA"],
            "txtTrecho": ["BSB/CGH", ""],
            "vlrLiquido": [700.0, 200.0],
        }
    )
    resultado = IndicadoresGastos(gastos).calcular()

    assert _gasto(resultado, "10") == pytest.approx(200.0)


def test_trecho_nulo_nao_derruba_a_despesa():
    """Campo vazio é o caso comum em despesas que não são de viagem."""
    gastos = pd.DataFrame(
        {
            "idDeputado": ["10"],
            "txtDescricao": ["MANUTENÇÃO DE ESCRITÓRIO"],
            "txtTrecho": [None],
            "vlrLiquido": [1500.0],
        }
    )
    resultado = IndicadoresGastos(gastos).calcular()

    assert _gasto(resultado, "10") == pytest.approx(1500.0)


def test_deputado_com_todas_as_despesas_filtradas_desaparece_do_resultado():
    """Documenta perda silenciosa de dado — comportamento vigente, não desejado.

    Quem tem 100% das despesas capturadas pelo filtro não sai com gasto zero:
    sai do resultado inteiro, porque o groupby não gera linha e o dropna em
    IndicadoresGerais remove o deputado. É a mesma família do M1 — quanto menos
    dado de gasto, melhor a posição no ranking, até o ponto de sumir.

    O teste fixa o comportamento para que a mudança seja deliberada. A detecção
    do caso fica com os testes de qualidade de dados.
    """
    gastos = pd.DataFrame(
        {
            "idDeputado": ["10"],
            "txtDescricao": ["PASSAGEM AÉREA"],
            "txtTrecho": ["BSB/GRU"],
            "vlrLiquido": [5000.0],
        }
    )
    resultado = IndicadoresGastos(gastos).calcular()

    assert resultado.empty
