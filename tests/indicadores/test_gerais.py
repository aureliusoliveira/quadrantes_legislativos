"""Composição final: quadrantes e ranking.

É aqui que os indicadores viram o número publicado, então é aqui que os casos de
borda importam: produtividade zero, gasto perto de zero, empate e outlier.
"""

import pandas as pd
import pytest

from legisdata.indicadores.indicadores_gerais import IndicadoresGerais


def montar_dados(produtividade_por_dep, gasto_por_dep):
    """Monta as bases de entrada a partir do resultado desejado.

    Cada ponto de produtividade vira um PL de peso 1,0, e cada deputado recebe
    uma única despesa não filtrável. Assim os testes falam de produtividade e
    gasto, não de proposições e notas fiscais.
    """
    linhas_prop, linhas_autor = [], []
    contador = 1
    for id_dep, pontos in produtividade_por_dep.items():
        for _ in range(pontos):
            linhas_prop.append({"id": str(contador), "siglaTipo": "PL"})
            linhas_autor.append(
                {"idProposicao": str(contador), "idDeputado": id_dep, "nomeAutor": f"Dep {id_dep}"}
            )
            contador += 1

    ids = list(produtividade_por_dep)
    return {
        "deputados": pd.DataFrame(
            {
                "idDeputado": ids,
                "nome": [f"Dep {i}" for i in ids],
                "sgUF": ["SP"] * len(ids),
                "sgPartido": ["P1"] * len(ids),
            }
        ),
        "proposicoes": pd.DataFrame(linhas_prop, columns=["id", "siglaTipo"]),
        "autores": pd.DataFrame(linhas_autor, columns=["idProposicao", "idDeputado", "nomeAutor"]),
        "gastos": pd.DataFrame(
            {
                "idDeputado": list(gasto_por_dep),
                "txtDescricao": ["MANUTENÇÃO DE ESCRITÓRIO"] * len(gasto_por_dep),
                "txtTrecho": [""] * len(gasto_por_dep),
                "vlrLiquido": list(gasto_por_dep.values()),
            }
        ),
        "tramitacoes": None,
        "temas": None,
    }


def calcular(produtividade, gasto, caminho_pesos):
    resultado = IndicadoresGerais(montar_dados(produtividade, gasto), caminho_pesos).calcular()
    return resultado.set_index("idDeputado")


def test_quadrante_divide_pela_mediana_das_duas_dimensoes(caminho_pesos):
    r = calcular(
        {"10": 4, "20": 3, "30": 2, "40": 1},
        {"10": 1000.0, "20": 2000.0, "30": 3000.0, "40": 4000.0},
        caminho_pesos,
    )
    # medianas: produtividade 2,5 e gasto 2500
    assert r.loc["10", "quadrante"] == "Alta produtividade e baixo custo"
    assert r.loc["20", "quadrante"] == "Alta produtividade e baixo custo"
    assert r.loc["30", "quadrante"] == "Baixa produtividade e alto custo"
    assert r.loc["40", "quadrante"] == "Baixa produtividade e alto custo"


def test_valor_exatamente_na_mediana_conta_como_alto(caminho_pesos):
    """A régua é `>=`, então quem está na mediana cai no lado alto das duas
    dimensões. Com número ímpar de deputados isso decide um caso real."""
    r = calcular(
        {"10": 3, "20": 2, "30": 1},
        {"10": 3000.0, "20": 2000.0, "30": 1000.0},
        caminho_pesos,
    )
    # medianas: produtividade 2,0 e gasto 2000 — o deputado 20 está nas duas
    assert r.loc["20", "quadrante"] == "Alta produtividade e alto custo"


def test_ranking_composto_soma_as_duas_posicoes(caminho_pesos):
    r = calcular(
        {"10": 4, "20": 3, "30": 2, "40": 1},
        {"10": 1000.0, "20": 2000.0, "30": 3000.0, "40": 4000.0},
        caminho_pesos,
    )
    assert list(r.sort_values("ranking").index) == ["10", "20", "30", "40"]
    assert r.loc["10", "ranking"] == 1
    assert r.loc["40", "ranking"] == 4


def test_correlacao_inversa_perfeita_empata_todo_mundo_em_primeiro(caminho_pesos):
    """M3: o ranking composto soma posições, e a soma não desempata.

    Quem produz mais gasta mais, na mesma ordem: as duas posições se cancelam e
    os quatro deputados terminam em primeiro lugar. Não há critério de desempate
    — o empate é efeito colateral da escolha de `method='dense'`, não decisão.
    """
    r = calcular(
        {"10": 4, "20": 3, "30": 2, "40": 1},
        {"10": 4000.0, "20": 3000.0, "30": 2000.0, "40": 1000.0},
        caminho_pesos,
    )
    assert set(r["ranking"]) == {1}


def test_outlier_de_produtividade_nao_desloca_os_quadrantes_dos_demais(caminho_pesos):
    """A mediana é robusta a outlier — é justamente por isso que ela é o corte."""
    sem_outlier = calcular(
        {"10": 4, "20": 3, "30": 2, "40": 1},
        {"10": 1000.0, "20": 2000.0, "30": 3000.0, "40": 4000.0},
        caminho_pesos,
    )
    com_outlier = calcular(
        {"10": 4, "20": 3, "30": 2, "40": 1, "50": 10_000},
        {"10": 1000.0, "20": 2000.0, "30": 3000.0, "40": 4000.0, "50": 2500.0},
        caminho_pesos,
    )
    for id_dep in ["10", "40"]:
        assert sem_outlier.loc[id_dep, "quadrante"] == com_outlier.loc[id_dep, "quadrante"]


def test_gasto_proximo_de_zero_lidera_o_ranking(caminho_pesos):
    """M1 no formato em que ele chega ao produto.

    Gasto quase nulo com produtividade mediana basta para o primeiro lugar. O
    cálculo está correto; o problema é que dado de gasto ausente é
    indistinguível de economia real. Ver tests/test_qualidade_dados.py.
    """
    r = calcular(
        {"10": 3, "20": 3, "30": 3},
        {"10": 15.19, "20": 800_000.0, "30": 900_000.0},
        caminho_pesos,
    )
    assert r.loc["10", "ranking"] == 1
    assert r.loc["20", "ranking"] == 2
    assert r.loc["30", "ranking"] == 3


def test_deputado_sem_proposicao_alguma_e_removido_do_resultado(caminho_pesos):
    """Perda silenciosa: sem proposição, produtividade vira NaN no merge e o
    dropna elimina o deputado — ele não aparece nem com score zero.

    Comportamento vigente, fixado para que a mudança seja consciente."""
    dados = montar_dados({"10": 2, "20": 1}, {"10": 1000.0, "20": 2000.0, "30": 3000.0})
    dados["deputados"] = pd.concat(
        [
            dados["deputados"],
            pd.DataFrame([{"idDeputado": "30", "nome": "Dep 30", "sgUF": "MG", "sgPartido": "P2"}]),
        ],
        ignore_index=True,
    )

    resultado = IndicadoresGerais(dados, caminho_pesos).calcular()

    assert "30" not in set(resultado["idDeputado"])


def test_deputado_sem_gasto_registrado_e_removido_do_resultado(caminho_pesos):
    dados = montar_dados({"10": 2, "20": 1, "30": 3}, {"10": 1000.0, "20": 2000.0})

    resultado = IndicadoresGerais(dados, caminho_pesos).calcular()

    assert "30" not in set(resultado["idDeputado"])


def test_cada_deputado_aparece_uma_unica_vez(caminho_pesos):
    r = calcular(
        {"10": 4, "20": 3, "30": 2},
        {"10": 1000.0, "20": 2000.0, "30": 3000.0},
        caminho_pesos,
    )
    assert r.index.is_unique


def test_colunas_publicadas_estao_presentes(caminho_pesos):
    r = calcular({"10": 2, "20": 1}, {"10": 1000.0, "20": 2000.0}, caminho_pesos)

    for coluna in ["produtividade_legislativa", "gasto_ceap_ajustado", "quadrante", "ranking"]:
        assert coluna in r.columns


def test_parcelas_do_ranking_composto_sao_publicadas(caminho_pesos):
    """As posições por eixo saem no artefato, e não só a posição final.

    Este teste já afirmou o contrário: as parcelas eram descartadas por serem
    "intermediárias". Publicar só o resultado obriga quem lê a acreditar nele,
    o que é exatamente o que este projeto não quer pedir. Com as três colunas
    na mesma linha, a soma é conferível sem sair do CSV.
    """
    r = calcular({"10": 2, "20": 1}, {"10": 1000.0, "20": 2000.0}, caminho_pesos)

    for coluna in ["ranking_leg", "ranking_gastos", "ranking_soma"]:
        assert coluna in r.columns

    assert (r["ranking_soma"] == r["ranking_leg"] + r["ranking_gastos"]).all()


def test_tipo_de_peso_zero_nao_entra_em_nenhuma_dimensao(caminho_pesos):
    """Peso zero declara "isto não é produção legislativa" — e a declaração vale
    para as duas dimensões publicadas.

    O caso concreto veio da troca da fonte pelo arquivo consolidado, que trouxe
    76 mil requerimentos de votação nominal na legislatura. Contados só na
    eficácia, eles dominariam o denominador e as taxas passariam a descrever o
    destino do procedimento, não o da produção.
    """
    dados = montar_dados({"10": 1, "20": 1}, {"10": 1000.0, "20": 2000.0})
    atas = [{"id": f"a{i}", "siglaTipo": "ATA"} for i in range(5)]
    dados["proposicoes"] = pd.concat(
        [dados["proposicoes"], pd.DataFrame(atas)], ignore_index=True
    )
    dados["autores"] = pd.concat(
        [
            dados["autores"],
            pd.DataFrame(
                [{"idProposicao": a["id"], "idDeputado": "10", "nomeAutor": "Dep 10"} for a in atas]
            ),
        ],
        ignore_index=True,
    )
    dados["tramitacoes"] = pd.DataFrame(
        {
            "idProposicao": ["1"] + [a["id"] for a in atas],
            "descricaoSituacao": ["Arquivada"] + ["Transformado em Norma Jurídica"] * len(atas),
        }
    )

    resultado = IndicadoresGerais(dados, caminho_pesos).calcular().set_index("idDeputado")

    assert resultado.loc["10", "produtividade_legislativa"] == 1.0
    assert resultado.loc["10", "pct_fracasso"] == 1.0, (
        "as atas entraram no denominador da eficácia"
    )
    assert resultado.loc["10", "pct_sucesso"] == 0.0
