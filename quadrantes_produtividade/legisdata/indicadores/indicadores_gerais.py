import pandas as pd
from .indicadores_proposicoes import IndicadoresProposicoes
from .indicadores_gastos import IndicadoresGastos
from .indicadores_tramitacao import IndicadoresTramitacao
from .indicadores_temas import IndicadoresTemas

class IndicadoresGerais:
    def __init__(self, dados: dict, caminho_pesos: str):
        self.dados = dados
        self.caminho_pesos = caminho_pesos

    def calcular(self) -> pd.DataFrame:
        indicadores = []

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
                    self.dados["proposicoes"],
                    self.dados["tramitacoes"],
                    self.dados["autores"]
                ).calcular()
            )

        if self.dados.get("temas") is not None:
            indicadores.append(
                IndicadoresTemas(
                    self.dados["proposicoes"],
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

        resultado["ranking_leg"] = resultado["produtividade_legislativa"].rank(ascending=False, method="dense").astype(int)
        resultado["ranking_gastos"] = resultado["gasto_ceap_ajustado"].rank(ascending=True, method="dense").astype(int)
        resultado["ranking_soma"] = resultado["ranking_leg"] + resultado["ranking_gastos"]
        resultado["ranking"] = resultado["ranking_soma"].rank(ascending=True, method="dense").astype(int)
        resultado = resultado.sort_values("ranking", ascending=True).reset_index(drop=True)
        resultado.drop(columns=["ranking_leg", "ranking_gastos", "ranking_soma"], inplace=True)
        resultado["ranking"] = resultado["ranking"].astype(int)
        

        return resultado