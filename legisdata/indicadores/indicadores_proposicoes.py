from .indicadores_base import IndicadoresBase
from .pesos import MapaDePesos


class IndicadoresProposicoes(IndicadoresBase):
    def __init__(self, proposicoes, autores, caminho_pesos):
        super().__init__({"proposicoes": proposicoes, "autores": autores})
        self.caminho_pesos = caminho_pesos

    def calcular(self):
        proposicoes = MapaDePesos(self.caminho_pesos).aplicar(self.dados["proposicoes"])

        df = proposicoes.merge(
            self.dados["autores"], left_on="id", right_on="idProposicao", how="left"
        )

        return (
            df.groupby("idDeputado")["peso"]
            .sum()
            .reset_index()
            .rename(columns={"peso": "produtividade_legislativa"})
        )
