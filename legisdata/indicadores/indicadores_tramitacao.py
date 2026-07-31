import pandas as pd
from .indicadores_base import IndicadoresBase

class IndicadoresTramitacao(IndicadoresBase):
    def __init__(self, proposicoes, tramitacoes, autores):
        super().__init__({
            "proposicoes": proposicoes,
            "tramitacoes": tramitacoes,
            "autores": autores
        })

    def _classificar_tramitacao(self, situacao: str) -> str:
        if not isinstance(situacao, str):
            return "andamento"
        situacao = situacao.lower()
        if any(palavra in situacao for palavra in ["norma jurídica", "sanção", "promulgação", "senado"]):
            return "sucesso"
        if any(palavra in situacao for palavra in ["arquivada", "retirado", "prejudic", "devolvida", "recusado"]):
            return "fracasso"
        return "andamento"

    def calcular(self):
        df = self.dados["proposicoes"].merge(
            self.dados["tramitacoes"],
            left_on="id", right_on="idProposicao", how="left"
        ).merge(
            self.dados["autores"],
            left_on="id", right_on="idProposicao", how="left"
        )

        df = df[["idDeputado", "descricaoSituacao"]].dropna()
        df["categoriaSituacao"] = df["descricaoSituacao"].apply(self._classificar_tramitacao)

        df_pct = (
            df.groupby("idDeputado")["categoriaSituacao"]
            .value_counts(normalize=True)
            .unstack(fill_value=0)
            .reset_index()
            .rename(columns={
                "sucesso": "pct_sucesso",
                "fracasso": "pct_fracasso",
                "andamento": "pct_andamento"
            })
        )

        return df_pct