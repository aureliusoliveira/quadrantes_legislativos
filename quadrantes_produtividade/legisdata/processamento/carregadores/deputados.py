# legisdata/processamento/carregadores/deputados.py

import os
import pandas as pd
from legisdata.config import DIRETORIO_RAW
from .carregador_base import CarregadorBase


class CarregadorDeputados(CarregadorBase):
    def __init__(self):
        super().__init__("deputados")

    def carregar(self, anos=None):
        path = os.path.join(DIRETORIO_RAW, "deputados", "deputados.csv")
        return pd.read_csv(path,
                           sep=";", 
                           encoding="utf-8-sig")
