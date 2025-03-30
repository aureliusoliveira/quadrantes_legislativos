# legisdata/processamento/carregadores/proposicoes.py

import os
import pandas as pd
from legisdata.config import DIRETORIO_RAW
from .carregador_base import CarregadorBase


class CarregadorProposicoes(CarregadorBase):
    def __init__(self):
        super().__init__("proposicoes")

    def carregar(self, anos: list):
        frames = []
        for ano in anos:
            path = os.path.join(DIRETORIO_RAW, self.nome_base, f"{ano}.csv")
            if os.path.exists(path):
                try:
                    df = pd.read_csv(path, sep=",", encoding="utf-8-sig", on_bad_lines="skip")
                    df["ano"] = ano
                    frames.append(df)
                except Exception as e:
                    print(f"⚠️ Erro ao carregar proposições {ano}: {e}")
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
