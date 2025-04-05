import pandas as pd
from .indicadores_base import IndicadoresBase

class IndicadoresProposicoes(IndicadoresBase):
    def __init__(self, proposicoes, autores, caminho_pesos):
        super().__init__({"proposicoes": proposicoes, "autores": autores})
        self.caminho_pesos = caminho_pesos

    def calcular(self):
        df = self.dados["proposicoes"].merge(
            self.dados["autores"],
            left_on="id", right_on="idProposicao", how="left"
        )

        try:
            mapa = pd.read_csv(self.caminho_pesos, sep=";")
            pesos = dict(zip(mapa["siglaTipo"], mapa["peso"]))
            df["peso"] = df["siglaTipo"].map(pesos).fillna(0)
        except Exception as e:
            raise ValueError(f"Erro ao carregar o mapa de pesos: {e}")

        return (
            df.groupby("idDeputado")["peso"]
            .sum()
            .reset_index()
            .rename(columns={"peso": "produtividade_legislativa"})
        )