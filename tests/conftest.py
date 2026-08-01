"""Fixtures compartilhadas.

As bases aqui são minúsculas e escritas à mão: cada linha existe para exercitar
um caso específico, e o resultado esperado é calculável de cabeça. Dado real
entra apenas nos testes de qualidade e de contrato.
"""

import pandas as pd
import pytest

PESOS_DE_TESTE = pd.DataFrame(
    {
        "siglaTipo": ["PL", "PEC", "REQ", "ATA"],
        "descricaoTipo": [
            "Projeto de Lei",
            "Proposta de Emenda à Constituição",
            "Requerimento",
            "Ata",
        ],
        "peso": [1.0, 1.0, 0.4, 0.0],
    }
)


@pytest.fixture
def caminho_pesos(tmp_path):
    """Mapa reduzido: PL e PEC valem 1,0; REQ vale 0,4; ATA é o tipo de peso zero.

    O peso zero não é detalhe do mapa — é o que declara que um tipo não conta
    como produção legislativa, e portanto não entra em nenhuma das dimensões
    publicadas. Ver docs/universo_e_pesos.md.
    """
    caminho = tmp_path / "mapa_pesos.csv"
    PESOS_DE_TESTE.to_csv(caminho, sep=";", index=False)
    return str(caminho)


@pytest.fixture
def proposicoes():
    return pd.DataFrame(
        {
            "id": ["1", "2", "3", "4"],
            "siglaTipo": ["PL", "PL", "REQ", "PEC"],
        }
    )


@pytest.fixture
def autores():
    """Deputado 10 assina as proposições 1 e 3; deputado 20 assina a 2.

    A proposição 4 é coautorada por 10 e 20 — é o caso que expõe como o modelo
    trata coautoria.
    """
    return pd.DataFrame(
        {
            "idProposicao": ["1", "2", "3", "4", "4"],
            "idDeputado": ["10", "20", "10", "10", "20"],
            "nomeAutor": ["Dep A", "Dep B", "Dep A", "Dep A", "Dep B"],
        }
    )


@pytest.fixture
def gastos():
    return pd.DataFrame(
        {
            "idDeputado": ["10", "10", "10", "20"],
            "txtDescricao": [
                "MANUTENÇÃO DE ESCRITÓRIO",
                "PASSAGEM AÉREA",
                "COMBUSTÍVEIS E LUBRIFICANTES",
                "DIVULGAÇÃO DA ATIVIDADE PARLAMENTAR",
            ],
            "txtTrecho": ["", "BSB/GRU", "", ""],
            "vlrLiquido": [1000.0, 500.0, 250.0, 3000.0],
        }
    )


@pytest.fixture
def deputados():
    return pd.DataFrame(
        {
            "idDeputado": ["10", "20"],
            "nome": ["Dep A", "Dep B"],
            "sgUF": ["SP", "RJ"],
            "sgPartido": ["P1", "P2"],
            "idLegislatura": [57, 57],
            "situacao": ["Exercício", "Exercício"],
            "condicaoEleitoral": ["Titular", "Titular"],
        }
    )
