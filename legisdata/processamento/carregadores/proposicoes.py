# legisdata/processamento/carregadores/proposicoes.py

import os

import pandas as pd

from legisdata import config
from legisdata.utils.io import ler_csv_da_fonte

from .carregador_base import CarregadorBase

# Das 31 colunas do arquivo consolidado, o cálculo usa duas. `siglaTipo` é a
# chave do mapa de pesos, de onde sai a produtividade; a situação da proposição
# sai do mesmo arquivo, pelo CarregadorSituacoes.
COLUNAS_DA_FONTE = ["id", "siglaTipo"]


class CarregadorProposicoes(CarregadorBase):
    def __init__(self):
        super().__init__("proposicoes")

    def carregar(self, anos: list) -> pd.DataFrame:
        frames = []
        for ano in anos:
            caminho = os.path.join(config.DIRETORIO_RAW, self.nome_base, f"{ano}.csv")
            if os.path.exists(caminho):
                df = ler_csv_da_fonte(caminho, sep=";", colunas=COLUNAS_DA_FONTE)
                df["ano"] = ano
                frames.append(df)

        if not frames:
            return pd.DataFrame(columns=COLUNAS_DA_FONTE + ["ano"])

        return pd.concat(frames, ignore_index=True)
