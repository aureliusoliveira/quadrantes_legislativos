import pandas as pd
from .indicadores_base import IndicadoresBase

class IndicadoresTemas(IndicadoresBase):
    def __init__(self, proposicoes, temas, autores):
        super().__init__({
            "proposicoes": proposicoes,
            "temas": temas,
            "autores": autores
        })

    def calcular(self):
        df = self.dados["proposicoes"].merge(
            self.dados["temas"],
            left_on="id", right_on="idProposicao", how="inner"
        ).merge(
            self.dados["autores"],
            left_on="id", right_on="idProposicao", how="left"
        )

        temas_por_dep = {}
        for dep_id, grupo in df.groupby("idDeputado"):
            temas_mais_comuns = (
                grupo["tema"]
                .value_counts()
                .nlargest(3)
                .index.tolist()
            )

            if len(temas_mais_comuns) == 1:
                texto = temas_mais_comuns[0]
            elif len(temas_mais_comuns) == 2:
                texto = f"{temas_mais_comuns[0]} e {temas_mais_comuns[1]}"
            elif len(temas_mais_comuns) == 3:
                texto = f"{temas_mais_comuns[0]}, {temas_mais_comuns[1]} e {temas_mais_comuns[2]}"
            else:
                texto = ""

            temas_por_dep[dep_id] = texto

        return (
            pd.DataFrame.from_dict(temas_por_dep, orient="index", columns=["temas_destaque"])
            .reset_index()
            .rename(columns={"index": "idDeputado"})
        )