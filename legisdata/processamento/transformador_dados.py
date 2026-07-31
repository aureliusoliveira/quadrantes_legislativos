import ast

import pandas as pd

from legisdata import config

class TransformadorDados:
    def __init__(self, dados: dict, legislatura: int | None = None):
        self.dados = dados.copy()
        # A legislatura era literal `57` em dois filtros. Como parâmetro, uma
        # recarga de legislatura anterior deixa de exigir edição de código.
        self.legislatura = legislatura if legislatura is not None else config.LEGISLATURA_ALVO

    def transformar(self) -> dict:
        return {
            "deputados": self._padronizar_deputados(),
            "gastos": self._padronizar_gastos(),
            "proposicoes": self._padronizar_proposicoes(),
            "autores": self._padronizar_autores(),
            "tramitacoes": self._padronizar_tramitacoes(),
            "temas": self._padronizar_temas()
            
        }

    def _padronizar_deputados(self):
        df = self.dados["deputados"].copy()

        # Converte o campo 'ultimoStatus' de string para dicionário
        df["ultimoStatus"] = df["ultimoStatus"].apply(ast.literal_eval)

        # Extrai os campos relevantes de 'ultimoStatus'
        df_status = df["ultimoStatus"].apply(pd.Series)[[
            "id", "nomeEleitoral", "siglaUf", "siglaPartido",
            "idLegislatura", "situacao", "condicaoEleitoral"
        ]]

        df_status["id"] = df_status["id"].astype(int).astype(str)

        # Remove duplicatas e garante consistência
        df_status.drop_duplicates(subset=["id"], inplace=True)
        
        # Renomeia colunas conforme convenção do projeto
        df_status = df_status.rename(columns={
            "siglaUf": "sgUF",
            "siglaPartido": "sgPartido",
            "nomeEleitoral": "nome",
            "id": "idDeputado"            
        })

        df_status = df_status.loc[
            (df_status.situacao == "Exercício")
            & (df_status.idLegislatura == self.legislatura),
            :,
        ].copy()
        return df_status


    def _padronizar_gastos(self):
        df = self.dados["gastos"].copy()
        df.dropna(subset=["ideCadastro", "vlrLiquido"], inplace=True)
        df["ideCadastro"] = pd.to_numeric(df["ideCadastro"], errors="coerce").astype("Int64").astype(str)
        df["vlrLiquido"] = pd.to_numeric(df["vlrLiquido"], errors="coerce")
        df = df.rename(columns={"ideCadastro": "idDeputado"})
        df = df.loc[
            df.codLegislatura == self.legislatura,
            ["idDeputado", "txtDescricao", "txtTrecho", "vlrLiquido"],
        ].copy()
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

    def _padronizar_tramitacoes(self):
        df = self.dados["tramitacoes"].copy()
        return df
    
    def _padronizar_temas(self):
        df = self.dados["temas"].copy()
        return df
        