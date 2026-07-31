"""Reconciliação entre o número publicado e o dado bruto.

O PRD define como métrica de sucesso "zero divergência entre número exibido e
dado bruto rastreável". Nenhuma invariante interna do resultado consegue medir
isso: um artefato calculado sobre uma cópia velha da fonte é perfeitamente
consistente consigo mesmo. Só a comparação com a fonte revela.

Depende de `data/raw/gastos/` estar populado, então é pulado no CI e roda na
máquina de quem executa o pipeline. É o teste que fecha o ciclo da carga mensal.
"""

import os
from pathlib import Path

import pandas as pd
import pytest

from legisdata.config import DIRETORIO_RAW
from legisdata.indicadores.indicadores_gastos import IndicadoresGastos
from legisdata.processamento.carregadores.gastos import CarregadorGastos
from legisdata.processamento.transformador_dados import TransformadorDados

RESULTADOS = Path(__file__).resolve().parent.parent / "dashboard" / "data" / "resultados.csv"
ANOS_DA_LEGISLATURA_57 = [2023, 2024, 2025, 2026]

TOLERANCIA_REAIS = 1.0


def _anos_disponiveis():
    diretorio = Path(DIRETORIO_RAW) / "gastos"
    if not diretorio.is_dir():
        return []
    return sorted(
        int(p.stem) for p in diretorio.glob("*.csv") if p.stem.isdigit()
    )


ANOS = _anos_disponiveis()

pytestmark = pytest.mark.skipif(
    not ANOS,
    reason=f"sem CEAP bruto em {os.path.normpath(os.path.join(DIRETORIO_RAW, 'gastos'))} — rode main_coleta.py",
)


@pytest.fixture(scope="module")
def gastos_brutos():
    return CarregadorGastos().carregar(ANOS)


@pytest.fixture(scope="module")
def gasto_por_deputado(gastos_brutos):
    """Recalcula pela mesma regra de produção — o que se testa é o dado, não a conta."""
    padronizado = TransformadorDados({"gastos": gastos_brutos})._padronizar_gastos()
    return IndicadoresGastos(padronizado).calcular().set_index("idDeputado")["gasto_ceap_ajustado"]


@pytest.fixture(scope="module")
def publicado():
    df = pd.read_csv(RESULTADOS, sep=";", encoding="utf-8", dtype={"idDeputado": str})
    return df.set_index("idDeputado")


def test_todo_ano_da_legislatura_ja_coletado_tem_volume_comparavel(gastos_brutos):
    """Um ano da legislatura com volume muito abaixo dos outros é coleta
    interrompida ou arquivo obsoleto — não é a Câmara tendo parado de gastar.

    É a assinatura do problema do checkpoint (C1): o ano baixado uma vez fica
    congelado, e o dado que a fonte publicou depois nunca chega."""
    por_ano = gastos_brutos.groupby("ano").size()
    anos_fechados = [a for a in por_ano.index if a in ANOS_DA_LEGISLATURA_57[:-1]]
    if len(anos_fechados) < 2:
        pytest.skip("menos de dois anos fechados coletados")

    volumes = por_ano.loc[anos_fechados]
    assert volumes.min() >= 0.5 * volumes.max(), (
        f"volume de despesas muito desigual entre anos fechados: {volumes.to_dict()}"
    )


def test_nenhum_deputado_com_gasto_negativo_na_fonte(gasto_por_deputado):
    """O CEAP registra estorno como valor negativo. Total negativo significa que
    o recorte capturou a restituição sem a despesa que a originou."""
    negativos = gasto_por_deputado[gasto_por_deputado < 0]
    assert negativos.empty, f"{len(negativos)} deputados com gasto negativo: {negativos.to_dict()}"


@pytest.mark.xfail(
    strict=True,
    reason=(
        "O resultados.csv publicado foi calculado sobre uma cópia obsoleta do CEAP: "
        "510 de 510 deputados aparecem com gasto MENOR que o da fonte atual, num total "
        "de R$ 177 milhões (30,6%) a menos. Causa é o checkpoint que impede rebaixar "
        "ano já coletado (C1). Este xfail cai quando o Incremento 5 regenerar o artefato — "
        "e quando cair, remova o marcador."
    ),
)
def test_gasto_publicado_bate_com_a_fonte(publicado, gasto_por_deputado):
    comum = publicado.index.intersection(gasto_por_deputado.index)
    assert len(comum) > 0, "nenhum deputado em comum entre publicado e fonte"

    divergentes = []
    for id_dep in comum:
        esperado = float(gasto_por_deputado.loc[id_dep])
        exibido = float(publicado.loc[id_dep, "gasto_ceap_ajustado"])
        if abs(esperado - exibido) > TOLERANCIA_REAIS:
            divergentes.append((id_dep, publicado.loc[id_dep, "nome"], exibido, esperado))

    assert not divergentes, (
        f"{len(divergentes)} de {len(comum)} deputados divergem da fonte. "
        f"Exemplos: {divergentes[:5]}"
    )
