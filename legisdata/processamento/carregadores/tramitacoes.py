# legisdata/processamento/carregadores/tramitacoes.py

from .carregador_base import CarregadorBase
import pandas as pd
import os
from legisdata.config import DIRETORIO_RAW

class CarregadorTramitacoes(CarregadorBase):
    def __init__(self):
        super().__init__("tramitacoes")

    def carregar(self, anos: list = None) -> pd.DataFrame:
        caminho = os.path.join(DIRETORIO_RAW, "tramitacoes.csv")
        df = pd.read_csv(caminho)
        df["idProposicao"] = df["idProposicao"].astype(str)
        df["descricaoSituacao"] = df["descricaoSituacao"].fillna("")
        return df
