# legisdata/processamento/carregadores/carregador_base.py

from abc import ABC, abstractmethod
import pandas as pd


class CarregadorBase(ABC):
    def __init__(self, nome_base):
        self.nome_base = nome_base

    @abstractmethod
    def carregar(self, anos: list) -> pd.DataFrame:
        pass
