# legisdata/processamento/carregadores/temas.py

import os

import pandas as pd

from legisdata import config
from legisdata.utils.io import ler_csv_da_fonte

from .carregador_base import CarregadorBase

COLUNAS_DA_FONTE = ["uriProposicao", "tema", "codTema"]
COLUNAS = ["idProposicao", "tema", "codTema"]


class CarregadorTemas(CarregadorBase):
    """Temas por proposição.

    O arquivo da fonte identifica a proposição por URI, e o resto do pipeline
    trabalha com id — a conversão acontece aqui, e não na coleta, para que o
    bruto continue sendo o que a Câmara publicou.
    """

    def __init__(self):
        super().__init__("temas")

    def carregar(self, anos: list) -> pd.DataFrame:
        frames = []
        for ano in anos:
            caminho = os.path.join(config.DIRETORIO_RAW, self.nome_base, f"{ano}.csv")
            if os.path.exists(caminho):
                frames.append(ler_csv_da_fonte(caminho, sep=";", colunas=COLUNAS_DA_FONTE))

        if not frames:
            return pd.DataFrame(columns=COLUNAS)

        df = pd.concat(frames, ignore_index=True)
        df["idProposicao"] = df["uriProposicao"].astype(str).str.rsplit("/", n=1).str[-1]
        df["tema"] = df["tema"].fillna("").astype(str).str.strip()

        # URI fora do padrão não tem id recuperável; passar adiante um
        # "idProposicao" que é pedaço de URL faria a junção falhar em silêncio.
        return df.loc[df["idProposicao"].str.isdigit(), COLUNAS]
