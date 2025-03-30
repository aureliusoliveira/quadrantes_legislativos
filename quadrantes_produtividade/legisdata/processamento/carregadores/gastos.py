# legisdata/processamento/carregadores/gastos.py

import os
import pandas as pd
from legisdata.config import DIRETORIO_RAW
from .carregador_base import CarregadorBase


class CarregadorGastos(CarregadorBase):
    def __init__(self):
        super().__init__("gastos")

    def carregar(self, anos: list):
        frames = []
        for ano in anos:
            path = os.path.join(DIRETORIO_RAW, self.nome_base, f"{ano}.csv")
            if os.path.exists(path):
                df = pd.read_csv(path, encoding="utf-8-sig", sep=";", engine="python", on_bad_lines="skip")
                df["ano"] = ano
                frames.append(df)
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
