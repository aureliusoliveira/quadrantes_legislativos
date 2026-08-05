"""Smoke test do dashboard.

A cópia do dashboard que vivia neste repositório estava quebrada: os filtros de
UF tinham sido comentados, mas `df_filtrado` continuava sendo usado logo abaixo.
Ninguém percebeu porque o que estava no ar era o outro repositório. Consolidados
os dois, este teste existe para que uma página que não renderiza quebre o CI.
"""

import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parent.parent
DASHBOARD = RAIZ / "dashboard"

# O app é de página única: `app.py` é ao mesmo tempo o entrypoint do Streamlit
# Cloud e a visualização. O glob continua aqui para que qualquer página futura
# entre no smoke test sem ninguém precisar lembrar de registrá-la.
PAGINAS = [DASHBOARD / "app.py"] + sorted(DASHBOARD.glob("pages/*.py"))


@pytest.fixture(autouse=True)
def _dashboard_no_path():
    """O Streamlit põe o diretório do script no sys.path em runtime; o AppTest não."""
    sys.path.insert(0, str(DASHBOARD))
    yield
    sys.path.remove(str(DASHBOARD))


@pytest.mark.parametrize("pagina", PAGINAS, ids=lambda p: p.name)
def test_pagina_renderiza_sem_excecao(pagina):
    app = AppTest.from_file(str(pagina), default_timeout=60).run()
    assert not app.exception, f"{pagina.name} levantou: {app.exception}"


def test_ranking_exibido_cobre_todos_os_deputados_do_csv():
    """Guarda a mutação in-place que existia em grafico_quadrantes_interativo().

    O ranking exibido era sobrescrito dentro da função de gráfico, que mutava o
    DataFrame do chamador. O cálculo foi trazido para a página; este teste falha
    se a tabela deixar de refletir a mesma base que o gráfico.
    """
    app = AppTest.from_file(str(DASHBOARD / "app.py"), default_timeout=60).run()
    assert not app.exception

    import pandas as pd

    from settings import INDICADORES_PATH

    esperado = len(pd.read_csv(INDICADORES_PATH, sep=";", encoding="utf-8"))
    assert len(app.dataframe) == 1
    assert len(app.dataframe[0].value) == esperado
