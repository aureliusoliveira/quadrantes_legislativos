
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
        gastos = self.gastos.copy()
        gastos["valor"] = pd.to_numeric(gastos["vlrLiquido"], errors="coerce")
        gastos["id_deputado"] = gastos["ideCadastro"].astype(str)

        cond_passagens = (
            gastos["txtDescricao"].str.contains("passagem aérea", case=False, na=False) &
            gastos["txtTrecho"].str.contains("BSB", case=False, na=False)
        )
        gastos["valor_passagens_bsb"] = gastos["valor"].where(cond_passagens, 0)

        gastos_agg = gastos.groupby("id_deputado").agg(
            total_gastos=("valor", "sum"),
            gastos_passagens_bsb=("valor_passagens_bsb", "sum"),
            siglaPartido=("sgPartido", "last"),
            siglaUf=("sgUF", "last"),
            nomeCivil=("txNomeParlamentar", "last")
        ).reset_index()

        gastos_agg["total_gastos"] = gastos_agg["total_gastos"] - gastos_agg["gastos_passagens_bsb"]

        df["id_deputado"] = df["id_deputado"].astype(str)
        return df.merge(gastos_agg.drop(columns=["gastos_passagens_bsb"]), on="id_deputado", how="left")

    def _calcular_produtividade(self, df: pd.DataFrame):
        df.dropna(inplace=True)
        
        df["ranking_gastos"] = df["total_gastos"].rank(method="dense", ascending=True)
        df["ranking_produtividade"] = df["indice_produtividade"].rank(method="dense", ascending=False)

        df["pontuacao_final"] = df["ranking_gastos"] + df["ranking_produtividade"]
        df["ranking_final"] = df["pontuacao_final"].rank(method="dense")
        
        return df
