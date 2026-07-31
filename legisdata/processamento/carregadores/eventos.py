# legisdata/processamento/carregadores/eventos.py

import os
import pandas as pd
from legisdata.config import DIRETORIO_RAW
from legisdata.utils.io import ler_csv_da_fonte
from .carregador_base import CarregadorBase


class CarregadorEventos(CarregadorBase):
    def __init__(self):
        super().__init__("eventos")

    def carregar(self, anos: list):
        frames = []
        for ano in anos:
            path = os.path.join(DIRETORIO_RAW, self.nome_base, f"{ano}.csv")
            if os.path.exists(path):
                df = ler_csv_da_fonte(path, sep=";")
                df["ano"] = ano
                frames.append(df)
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
