
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
            "tramitacoes": self._padronizar_tramitacoes(),
            "temas": self._padronizar_temas()
            #"eventos": self._padronizar_eventos()
            
        }

    def _padronizar_deputados(self):
        df = self.dados["deputados"].copy()
        df["idDeputado"] = df["uri"].str.extract(r"(\d+)$")[0]
        df.drop_duplicates(subset=["idDeputado"], inplace=True)
        df = df[["idDeputado", "nome"]]
        return df

    def _padronizar_gastos(self):
        df = self.dados["gastos"].copy()
        df.dropna(subset=["ideCadastro", "vlrLiquido"], inplace=True)
        df["ideCadastro"] = pd.to_numeric(df["ideCadastro"], errors="coerce").astype("Int64").astype(str)
        df["vlrLiquido"] = pd.to_numeric(df["vlrLiquido"], errors="coerce")
        df = df.rename(columns={"ideCadastro": "idDeputado"})
        df = df[["idDeputado","sgUF","sgPartido","txtDescricao","txtTrecho","vlrLiquido"]]
        return df

    def _padronizar_proposicoes(self):
        df = self.dados["proposicoes"].copy()
        df.dropna(subset=["id"], inplace=True)
        df["id"] = df["id"].astype(int).astype(str)
        df = df[["id", "siglaTipo"]]
        return df

    def _padronizar_autores(self):
        df = self.dados["autores"].copy()
        df.dropna(subset=["idProposicao", "idDeputadoAutor"], inplace=True)
        df = df[["idProposicao", "idDeputadoAutor", "nomeAutor"]]
        df["idProposicao"] = df["idProposicao"].astype(str)
        df["idDeputadoAutor"] = df["idDeputadoAutor"].astype(int).astype(str)
        df = df.rename(columns={"idDeputadoAutor": "idDeputado"})
        return df

# =============================================================================
#     def _padronizar_eventos(self):
#         df = self.dados["eventos"].copy()
#         return df  # poderá ser expandido depois
# =============================================================================

    def _padronizar_tramitacoes(self):
        df = self.dados["tramitacoes"].copy()
        return df
    
    def _padronizar_temas(self):
        df = self.dados["temas"].copy()
        return df
        