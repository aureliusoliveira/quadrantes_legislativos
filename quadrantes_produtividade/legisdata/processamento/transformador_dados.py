
import pandas as pd

class TransformadorDados:
    def __init__(self, dados: dict):
        self.dados = dados.copy()

    def transformar(self) -> dict:
        return {
            "deputados": self._padronizar_deputados(),
            "gastos": self._padronizar_gastos(),
            "proposicoes": self._padronizar_proposicoes(),
            "autores": self._padronizar_autores(),
            "eventos": self._padronizar_eventos()
        }

    def _padronizar_deputados(self):
        df = self.dados["deputados"].copy()
        df.columns = df.columns.str.strip()
        df["id_deputado"] = df["uri"].str.extract(r"(\d+)$")[0]
        df.drop_duplicates(subset=["id_deputado"], inplace=True)
        return df

    def _padronizar_gastos(self):
        df = self.dados["gastos"].copy()
        df.columns = df.columns.str.strip()
        df.dropna(subset=["ideCadastro", "vlrLiquido"], inplace=True)
        df["ideCadastro"] = pd.to_numeric(df["ideCadastro"], errors="coerce").astype("Int64").astype(str)
        df["vlrLiquido"] = pd.to_numeric(df["vlrLiquido"], errors="coerce")
        return df

    def _padronizar_proposicoes(self):
        df = self.dados["proposicoes"].copy()
        df.columns = df.columns.str.strip()
        df.dropna(subset=["id"], inplace=True)
        df["id"] = df["id"].astype(int).astype(str)
        return df

    def _padronizar_autores(self):
        df = self.dados["autores"].copy()
        df.columns = df.columns.str.strip()
        df.dropna(subset=["idProposicao", "idDeputadoAutor"], inplace=True)
        df["idProposicao"] = df["idProposicao"].astype(int).astype(str)
        df["idDeputadoAutor"] = df["idDeputadoAutor"].astype(int).astype(str)
        return df

    def _padronizar_eventos(self):
        df = self.dados["eventos"].copy()
        df.columns = df.columns.str.strip()
        return df  # poderá ser expandido depois
