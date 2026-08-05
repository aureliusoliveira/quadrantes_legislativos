import pandas as pd
from .indicadores_proposicoes import IndicadoresProposicoes
from .indicadores_gastos import IndicadoresGastos
from .indicadores_tramitacao import IndicadoresTramitacao
from .indicadores_temas import IndicadoresTemas
from .pesos import MapaDePesos

class IndicadoresGerais:
    def __init__(self, dados: dict, caminho_pesos: str):
        self.dados = dados
        self.caminho_pesos = caminho_pesos

    def calcular(self) -> pd.DataFrame:
        indicadores = []

        # As duas dimensões medem o mesmo universo. Sem isto, os 76 mil
        # requerimentos de votação nominal da legislatura — que valem zero na
        # produtividade — dominariam o denominador das taxas de eficácia e
        # descreveriam o destino do procedimento, não o da produção legislativa.
        producao = MapaDePesos(self.caminho_pesos).producao(self.dados["proposicoes"])

        indicadores.append(
            IndicadoresProposicoes(
                self.dados["proposicoes"],
                self.dados["autores"],
                self.caminho_pesos
            ).calcular()
        )

        indicadores.append(
            IndicadoresGastos(
                self.dados["gastos"]
            ).calcular()
        )

        if self.dados.get("tramitacoes") is not None:
            indicadores.append(
                IndicadoresTramitacao(
                    producao,
                    self.dados["tramitacoes"],
                    self.dados["autores"]
                ).calcular()
            )

        if self.dados.get("temas") is not None:
            indicadores.append(
                IndicadoresTemas(
                    producao,
                    self.dados["temas"],
                    self.dados["autores"]
                ).calcular()
            )

        resultado = self.dados["deputados"]
        for df in indicadores:
            resultado = resultado.merge(df, on="idDeputado", how="left")

        resultado.dropna(subset=["produtividade_legislativa", "gasto_ceap_ajustado"], inplace=True)
        resultado["pct_sucesso"] = resultado.get("pct_sucesso", 0)
        resultado["pct_fracasso"] = resultado.get("pct_fracasso", 0)
        resultado["pct_andamento"] = resultado.get("pct_andamento", 0)

        mediana_pontuacao = resultado["produtividade_legislativa"].median()
        mediana_gasto = resultado["gasto_ceap_ajustado"].median()

        def classificar_quadrante(row):
            if row["produtividade_legislativa"] >= mediana_pontuacao:
                return "Alta produtividade e " + ("alto custo" if row["gasto_ceap_ajustado"] >= mediana_gasto else "baixo custo")
            else:
                return "Baixa produtividade e " + ("alto custo" if row["gasto_ceap_ajustado"] >= mediana_gasto else "baixo custo")

        resultado["quadrante"] = resultado.apply(classificar_quadrante, axis=1)

        # Ranking composto por soma de posições (Borda). Cada eixo é ordenado
        # separadamente e o que se soma são posições, não valores — por isso o
        # método não precisa arbitrar quanto um real vale em proposição, que é
        # a conversão sem resposta. Em troca assume que os dois eixos pesam
        # igual e descarta a magnitude: a distância entre o 1º e o 2º de um
        # eixo pode ser enorme ou irrisória, e a soma trata as duas do mesmo
        # jeito. Ver docs/universo_e_pesos.md.
        resultado["ranking_leg"] = resultado["produtividade_legislativa"].rank(ascending=False, method="dense").astype(int)
        resultado["ranking_gastos"] = resultado["gasto_ceap_ajustado"].rank(ascending=True, method="dense").astype(int)
        resultado["ranking_soma"] = resultado["ranking_leg"] + resultado["ranking_gastos"]
        resultado["ranking"] = resultado["ranking_soma"].rank(ascending=True, method="dense").astype(int)
        resultado = resultado.sort_values("ranking", ascending=True).reset_index(drop=True)
        resultado["ranking"] = resultado["ranking"].astype(int)

        # As parcelas ficam no artefato de propósito. Publicar só a posição
        # final obrigaria a acreditar nela: com `ranking_leg` e
        # `ranking_gastos` na mesma linha, qualquer pessoa refaz a soma e
        # confere onde o parlamentar ganhou ou perdeu posição.

        return resultado