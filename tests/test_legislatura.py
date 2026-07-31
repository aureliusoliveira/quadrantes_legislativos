"""Legislatura como dimensão, não como constante espalhada pelo código.

O bug de origem: `for ano in range(2023, 2026)` no main_coleta.py excluía o ano
corrente, então mesmo rodando hoje o pipeline não trazia dado novo. A correção
não é trocar o 2026 por uma variável — é derivar os anos da legislatura alvo, de
modo que o ano corrente entre por construção e a lista se estenda sozinha.
"""

from datetime import date

import pytest

from legisdata import legislatura as leg


def test_anos_da_57a_legislatura():
    assert leg.anos_da_legislatura(57) == [2023, 2024, 2025, 2026]


def test_anos_da_legislatura_anterior():
    assert leg.anos_da_legislatura(56) == [2019, 2020, 2021, 2022]


def test_legislatura_dura_quatro_anos():
    for numero in range(50, 60):
        assert len(leg.anos_da_legislatura(numero)) == 4


def test_legislatura_de_um_ano():
    assert leg.legislatura_de(2023) == 57
    assert leg.legislatura_de(2026) == 57
    assert leg.legislatura_de(2022) == 56
    assert leg.legislatura_de(2019) == 56


def test_legislatura_de_um_ano_e_inversa_de_anos_da_legislatura():
    for numero in range(50, 60):
        for ano in leg.anos_da_legislatura(numero):
            assert leg.legislatura_de(ano) == numero


def test_anos_a_coletar_incluem_o_ano_corrente():
    """A falha original: rodar em 2026 e não trazer 2026.

    Enquanto a legislatura está em curso, o último ano da lista é o ano de hoje.
    """
    anos = leg.anos_a_coletar(57, hoje=date(2026, 7, 31))

    assert anos == [2023, 2024, 2025, 2026]
    assert anos[-1] == 2026


def test_anos_a_coletar_param_no_meio_da_legislatura():
    assert leg.anos_a_coletar(57, hoje=date(2024, 3, 1)) == [2023, 2024]


def test_anos_a_coletar_no_primeiro_ano():
    assert leg.anos_a_coletar(57, hoje=date(2023, 1, 5)) == [2023]


def test_legislatura_encerrada_traz_os_quatro_anos():
    assert leg.anos_a_coletar(56, hoje=date(2026, 7, 31)) == [2019, 2020, 2021, 2022]


def test_legislatura_futura_nao_tem_ano_a_coletar():
    assert leg.anos_a_coletar(58, hoje=date(2026, 7, 31)) == []


def test_ano_corrente_e_o_unico_ano_aberto():
    """Distinção que o checkpoint precisa fazer: ano fechado não muda mais, ano
    aberto ainda recebe dado e tem que ser rebaixado a cada carga."""
    assert leg.ano_esta_aberto(2026, hoje=date(2026, 7, 31)) is True
    assert leg.ano_esta_aberto(2025, hoje=date(2026, 7, 31)) is False
    assert leg.ano_esta_aberto(2023, hoje=date(2026, 7, 31)) is False


def test_ano_recem_encerrado_continua_aberto_por_uma_janela():
    """O CEAP de dezembro só é publicado semanas depois. Tratar o ano como
    fechado em 1º de janeiro perde a última leva de despesas."""
    assert leg.ano_esta_aberto(2025, hoje=date(2026, 1, 15)) is True
    assert leg.ano_esta_aberto(2025, hoje=date(2026, 4, 15)) is False


@pytest.mark.parametrize("numero", [0, -1, 48])
def test_legislatura_implausivel_e_rejeitada(numero):
    with pytest.raises(ValueError):
        leg.anos_da_legislatura(numero)
