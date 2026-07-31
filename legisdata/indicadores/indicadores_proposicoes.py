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
        except Exception as e:
            raise ValueError(f"Erro ao carregar o mapa de pesos: {e}")

        # Um tipo fora do mapa não pode virar peso zero em silêncio: seria a
        # Câmara criando uma sigla e a produtividade daquele tipo desaparecendo
        # sem nenhum sinal, com o número errado seguindo para o dashboard. Peso
        # zero continua possível — mas declarado como linha do mapa.
        desconhecidos = sorted(set(df["siglaTipo"].dropna()) - set(pesos))
        if desconhecidos:
            raise ValueError(
                "Tipos de proposição ausentes do mapa de pesos: "
                f"{', '.join(desconhecidos)}. "
                f"Declare o peso de cada um em {self.caminho_pesos} — inclusive "
                "quando o peso pretendido for zero."
            )

        df["peso"] = df["siglaTipo"].map(pesos)

        return (
            df.groupby("idDeputado")["peso"]
            .sum()
            .reset_index()
            .rename(columns={"peso": "produtividade_legislativa"})
        )