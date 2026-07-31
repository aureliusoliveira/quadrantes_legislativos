# legisdata/processamento/carregadores/temas.py

from .carregador_base import CarregadorBase
import pandas as pd
import os
from legisdata.config import DIRETORIO_RAW

class CarregadorTemas(CarregadorBase):
    def __init__(self):
        super().__init__("temas")

    def carregar(self, anos: list = None) -> pd.DataFrame:
        caminho = os.path.join(DIRETORIO_RAW, "temas_proposicoes.csv")
        df = pd.read_csv(caminho)
        df["idProposicao"] = df["idProposicao"].astype(str)
        df["tema"] = df["tema"].fillna("").str.strip()
        return df
