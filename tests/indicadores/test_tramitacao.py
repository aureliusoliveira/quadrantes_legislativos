"""Eficácia de tramitação: percentuais de sucesso, fracasso e andamento."""

import pandas as pd
import pytest

from legisdata.indicadores.indicadores_tramitacao import IndicadoresTramitacao


@pytest.mark.parametrize(
    ("situacao", "categoria"),
    [
        ("Transformado em Norma Jurídica", "sucesso"),
        ("Aguardando Sanção Presidencial", "sucesso"),
        ("Remetido ao Senado Federal", "sucesso"),
        ("Arquivada", "fracasso"),
        ("Retirado pelo Autor", "fracasso"),
        ("Prejudicada", "fracasso"),
        ("Devolvida ao Autor", "fracasso"),
        ("Pronta para Pauta", "andamento"),
        ("Tramitando em Conjunto", "andamento"),
        (None, "andamento"),
    ],
)
def test_classificacao_de_situacao(situacao, categoria):
    classificar = IndicadoresTramitacao(None, None, None)._classificar_tramitacao
    assert classificar(situacao) == categoria


def test_remetido_ao_senado_conta_como_sucesso_embora_nao_seja_lei():
    """M6: decisão metodológica vigente, discutível e não documentada.

    Proposição remetida ao Senado não virou norma — o processo apenas saiu da
    Câmara. Contar como sucesso infla a taxa. Fixado aqui para que a revisão da
    régua de eficácia (Fase 2) seja uma escolha, não uma descoberta.
    """
    classificar = IndicadoresTramitacao(None, None, None)._classificar_tramitacao
    assert classificar("Remetido ao Senado Federal") == "sucesso"


def test_percentuais_por_deputado_somam_um():
    proposicoes = pd.DataFrame({"id": ["1", "2", "3", "4"], "siglaTipo": ["PL"] * 4})
    tramitacoes = pd.DataFrame(
        {
            "idProposicao": ["1", "2", "3", "4"],
            "descricaoSituacao": [
                "Transformado em Norma Jurídica",
                "Arquivada",
                "Pronta para Pauta",
                "Pronta para Pauta",
            ],
        }
    )
    autores = pd.DataFrame(
        {
            "idProposicao": ["1", "2", "3", "4"],
            "idDeputado": ["10", "10", "10", "10"],
            "nomeAutor": ["Dep A"] * 4,
        }
    )

    resultado = IndicadoresTramitacao(proposicoes, tramitacoes, autores).calcular()
    linha = resultado.loc[resultado["idDeputado"] == "10"].iloc[0]

    assert linha["pct_sucesso"] == pytest.approx(0.25)
    assert linha["pct_fracasso"] == pytest.approx(0.25)
    assert linha["pct_andamento"] == pytest.approx(0.50)
    assert linha[["pct_sucesso", "pct_fracasso", "pct_andamento"]].sum() == pytest.approx(1.0)


def test_proposicao_sem_tramitacao_nao_entra_no_denominador():
    proposicoes = pd.DataFrame({"id": ["1", "2"], "siglaTipo": ["PL", "PL"]})
    tramitacoes = pd.DataFrame(
        {"idProposicao": ["1"], "descricaoSituacao": ["Transformado em Norma Jurídica"]}
    )
    autores = pd.DataFrame(
        {
            "idProposicao": ["1", "2"],
            "idDeputado": ["10", "10"],
            "nomeAutor": ["Dep A", "Dep A"],
        }
    )

    resultado = IndicadoresTramitacao(proposicoes, tramitacoes, autores).calcular()
    linha = resultado.loc[resultado["idDeputado"] == "10"].iloc[0]

    assert linha["pct_sucesso"] == pytest.approx(1.0)
