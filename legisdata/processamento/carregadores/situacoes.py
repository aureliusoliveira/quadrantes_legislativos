# legisdata/processamento/carregadores/situacoes.py

import os

import pandas as pd

from legisdata import config
from legisdata.utils.io import ler_csv_da_fonte

from .carregador_base import CarregadorBase

COLUNAS_DA_FONTE = ["id", "ultimoStatus_descricaoSituacao", "ultimoStatus_dataHora"]


class CarregadorSituacoes(CarregadorBase):
    """Situação atual de cada proposição, derivada do bruto de proposições.

    Não há coletor próprio: o arquivo consolidado de proposições já traz o
    `ultimoStatus`, que é o mesmo dado que o ColetorTramitacoes ia buscar com
    uma requisição por proposição. Ler daqui evita baixar 85 MB por ano duas
    vezes para extrair colunas do mesmo arquivo.

    Situação ausente permanece nula, e não vira texto vazio: a proposição sem
    situação registrada é descartada pelo `dropna` do IndicadoresTramitacao, e
    convertê-la em vazio a classificaria como "andamento" — mudança silenciosa
    nos percentuais publicados.
    """

    def __init__(self):
        super().__init__("situacoes")

    def carregar(self, anos: list) -> pd.DataFrame:
        frames = []
        for ano in anos:
            caminho = os.path.join(config.DIRETORIO_RAW, "proposicoes", f"{ano}.csv")
            if os.path.exists(caminho):
                frames.append(ler_csv_da_fonte(caminho, sep=";", colunas=COLUNAS_DA_FONTE))

        colunas = ["idProposicao", "descricaoSituacao", "dataHora"]
        if not frames:
            return pd.DataFrame(columns=colunas)

        df = pd.concat(frames, ignore_index=True).rename(
            columns={
                "id": "idProposicao",
                "ultimoStatus_descricaoSituacao": "descricaoSituacao",
                "ultimoStatus_dataHora": "dataHora",
            }
        )
        df = df.dropna(subset=["idProposicao"])
        df["idProposicao"] = df["idProposicao"].astype("Int64").astype(str)
        return df[colunas]
