import pandas as pd

class IndicadoresParlamentares:
    def __init__(self, dados: dict, caminho_pesos: str = None):
        self.deputados = dados["deputados"]
        self.gastos = dados["gastos"]
        self.proposicoes = dados["proposicoes"]
        self.autores = dados["autores"]
        self.caminho_pesos = caminho_pesos

    def calcular_indicadores(self):
        df = self._base_deputados()
        df = self._adicionar_proposicoes(df)
        df = self._adicionar_gastos(df)
        df = self._calcular_produtividade(df)
        return df

    def _base_deputados(self):
        return self.deputados[["id_deputado"]].drop_duplicates().copy()

    def _carregar_pesos(self):
        if self.caminho_pesos:
            pesos_df = pd.read_csv(self.caminho_pesos, sep=";")
            return dict(zip(pesos_df["siglaTipo"], pesos_df["peso"]))
        else:
            return {}

    def _adicionar_proposicoes(self, df: pd.DataFrame):
        autores = self.autores.copy()
        proposicoes = self.proposicoes[["id", "siglaTipo"]].copy()
        autores = autores.merge(proposicoes, left_on="idProposicao", right_on="id", how="left")

        pesos = self._carregar_pesos()
        autores["peso"] = autores["siglaTipo"].map(pesos).fillna(0)

        resumo = autores.groupby("idDeputadoAutor").agg(
            total_proposicoes=("idProposicao", "count"),
            indice_produtividade=("peso", "sum")
        ).reset_index().rename(columns={"idDeputadoAutor": "id_deputado"})

        df["id_deputado"] = df["id_deputado"].astype(str)
        resumo["id_deputado"] = resumo["id_deputado"].astype(str)

        return df.merge(resumo, on="id_deputado", how="left")

    def _adicionar_gastos(self, df: pd.DataFrame):
        self.gastos["valor"] = pd.to_numeric(self.gastos["vlrLiquido"], errors="coerce")

        gastos_agg = self.gastos.groupby("ideCadastro").agg(
            total_gastos=("valor", "sum"),
            siglaPartido=("sgPartido", "last"),
            siglaUf=("sgUF", "last"),
            nomeCivil=("txNomeParlamentar", "last")
        ).reset_index().rename(columns={"ideCadastro": "id_deputado"})

        df["id_deputado"] = df["id_deputado"].astype(str)
        gastos_agg["id_deputado"] = gastos_agg["id_deputado"].astype(str)

        return df.merge(gastos_agg, on="id_deputado", how="left")

    def _calcular_produtividade(self, df: pd.DataFrame):
        df["total_proposicoes"] = df["total_proposicoes"].fillna(-1).astype(int)
        df.dropna(subset=["total_proposicoes"], inplace=True)
        #df["indice_produtividade"] = df["indice_produtividade"].fillna(-1).astype(float)
        df["total_gastos"] = df["total_gastos"].fillna(-1)

        df["eficiencia"] = df["indice_produtividade"] / df["total_gastos"]
        df["eficiencia"] = df["eficiencia"].replace([float("inf"), -float("inf")], None)

        return df
