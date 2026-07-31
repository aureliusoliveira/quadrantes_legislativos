# legisdata/processamento/processador_base.py

from abc import ABC, abstractmethod

class ProcessadorBase(ABC):
    """
    Interface para todos os processadores de dados.
    """

    def __init__(self, nome):
        self.nome = nome

    @abstractmethod
    def processar(self):
        pass
