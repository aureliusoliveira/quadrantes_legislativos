"""Produtividade legislativa ponderada.

Regra: cada proposição vale o peso do seu tipo, e o score do deputado é a soma
dos pesos das proposições que ele assina.
"""

import pandas as pd
import pytest

from legisdata.indicadores.indicadores_proposicoes import IndicadoresProposicoes


def _score(resultado, id_deputado):
    linha = resultado.loc[resultado["idDeputado"] == id_deputado, "produtividade_legislativa"]
    assert len(linha) == 1, f"deputado {id_deputado} deveria aparecer exatamente uma vez"
    return linha.iloc[0]


def test_soma_os_pesos_das_proposicoes_do_deputado(proposicoes, autores, caminho_pesos):
    resultado = IndicadoresProposicoes(proposicoes, autores, caminho_pesos).calcular()

    # Dep 10: PL(1,0) + REQ(0,4) + PEC(1,0) = 2,4
    assert _score(resultado, "10") == pytest.approx(2.4)
    # Dep 20: PL(1,0) + PEC(1,0) = 2,0
    assert _score(resultado, "20") == pytest.approx(2.0)


def test_coautoria_da_peso_integral_a_cada_autor(proposicoes, autores, caminho_pesos):
    """Decisão metodológica explícita (M4): a PEC 4 é assinada por 10 e 20, e
    cada um leva 1,0 — o peso não é rateado entre coautores.

    Este teste não afirma que essa é a regra certa; afirma que é a regra vigente.
    Se ela mudar, que mude por decisão e não por acidente de merge.
    """
    resultado = IndicadoresProposicoes(proposicoes, autores, caminho_pesos).calcular()

    peso_total_da_pec = _score(resultado, "10") + _score(resultado, "20")
    assert peso_total_da_pec == pytest.approx(4.4)


def test_deputado_sem_proposicao_nao_aparece(proposicoes, caminho_pesos):
    autores_sem_dep_30 = pd.DataFrame(
        {"idProposicao": ["1"], "idDeputado": ["10"], "nomeAutor": ["Dep A"]}
    )
    resultado = IndicadoresProposicoes(proposicoes, autores_sem_dep_30, caminho_pesos).calcular()

    assert "30" not in set(resultado["idDeputado"])


def test_produtividade_zero_e_representavel(caminho_pesos):
    """Um deputado que só assina tipos de peso zero deve pontuar zero, não sumir."""
    proposicoes = pd.DataFrame({"id": ["1"], "siglaTipo": ["OFC"]})
    autores = pd.DataFrame(
        {"idProposicao": ["1"], "idDeputado": ["10"], "nomeAutor": ["Dep A"]}
    )
    pesos_com_zero = pd.DataFrame(
        {"siglaTipo": ["OFC"], "descricaoTipo": ["Ofício"], "peso": [0.0]}
    )
    caminho = caminho_pesos.replace("mapa_pesos.csv", "pesos_zero.csv")
    pesos_com_zero.to_csv(caminho, sep=";", index=False)

    resultado = IndicadoresProposicoes(proposicoes, autores, caminho).calcular()

    assert _score(resultado, "10") == 0.0


def test_tipo_de_proposicao_desconhecido_falha_alto(proposicoes, autores, caminho_pesos):
    """C6: hoje `.fillna(0)` faz tipo novo virar peso zero em silêncio.

    Se a Câmara criar uma sigla, a produtividade daquele tipo desaparece sem
    nenhum sinal — e o número errado chega ao dashboard. O comportamento correto
    é interromper o cálculo dizendo quais siglas não estão no mapa.
    """
    proposicoes_com_tipo_novo = pd.concat(
        [proposicoes, pd.DataFrame({"id": ["5"], "siglaTipo": ["XYZ"]})],
        ignore_index=True,
    )
    autores_com_tipo_novo = pd.concat(
        [autores, pd.DataFrame({"idProposicao": ["5"], "idDeputado": ["10"], "nomeAutor": ["Dep A"]})],
        ignore_index=True,
    )

    with pytest.raises(ValueError, match="XYZ"):
        IndicadoresProposicoes(
            proposicoes_com_tipo_novo, autores_com_tipo_novo, caminho_pesos
        ).calcular()


def test_mapa_de_pesos_ausente_falha_com_mensagem_util(proposicoes, autores):
    with pytest.raises(ValueError, match="mapa de pesos"):
        IndicadoresProposicoes(proposicoes, autores, "/caminho/que/nao/existe.csv").calcular()
