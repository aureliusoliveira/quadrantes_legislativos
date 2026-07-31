import pandas as pd
from .indicadores_base import IndicadoresBase

class IndicadoresGastos(IndicadoresBase):
    def __init__(self, gastos):
        super().__init__(gastos)

    def calcular(self):
        df = self.dados
        gastos_filtrados = df[
            ~df["txtDescricao"].str.contains("PASSAGE", case=False, na=False) &
            ~df["txtTrecho"].str.contains("BSB", case=False, na=False)
        ]

        return (
            gastos_filtrados
            .groupby("idDeputado")["vlrLiquido"]
            .sum()
            .reset_index()
            .rename(columns={"vlrLiquido": "gasto_ceap_ajustado"})
        )