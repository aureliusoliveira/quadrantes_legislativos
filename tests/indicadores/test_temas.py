"""Temas de destaque: os três temas mais frequentes do deputado, em texto."""

import pandas as pd

from legisdata.indicadores.indicadores_temas import IndicadoresTemas


def _montar(temas_por_proposicao):
    ids = [str(i) for i in range(1, len(temas_por_proposicao) + 1)]
    proposicoes = pd.DataFrame({"id": ids, "siglaTipo": ["PL"] * len(ids)})
    temas = pd.DataFrame({"idProposicao": ids, "tema": temas_por_proposicao})
    autores = pd.DataFrame(
        {"idProposicao": ids, "idDeputado": ["10"] * len(ids), "nomeAutor": ["Dep A"] * len(ids)}
    )
    return IndicadoresTemas(proposicoes, temas, autores).calcular()


def _texto(resultado):
    return resultado.loc[resultado["idDeputado"] == "10", "temas_destaque"].iloc[0]


def test_um_tema_sai_sem_conectivo():
    assert _texto(_montar(["Saúde"])) == "Saúde"


def test_dois_temas_saem_ligados_por_e():
    assert _texto(_montar(["Saúde", "Educação"])) == "Saúde e Educação"


def test_tres_temas_saem_com_virgula_e_e():
    resultado = _montar(["Saúde", "Saúde", "Educação", "Educação", "Meio Ambiente"])
    assert _texto(resultado) == "Saúde, Educação e Meio Ambiente"


def test_mais_de_tres_temas_mantem_apenas_os_tres_mais_frequentes():
    resultado = _montar(
        ["Saúde", "Saúde", "Saúde", "Educação", "Educação", "Cultura", "Esporte"]
    )
    texto = _texto(resultado)

    assert texto.startswith("Saúde, Educação e ")
    assert "Esporte" not in texto or "Cultura" not in texto
