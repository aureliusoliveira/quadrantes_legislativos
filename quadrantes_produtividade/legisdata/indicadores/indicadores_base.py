from abc import ABC, abstractmethod

class IndicadoresBase(ABC):
    def __init__(self, dados):
        self.dados = dados

    @abstractmethod
    def calcular(self):
        pass