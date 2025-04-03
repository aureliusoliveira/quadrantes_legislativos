# legisdata/processamento/processador_carregamento.py

from .carregadores.deputados import CarregadorDeputados
from .carregadores.gastos import CarregadorGastos
from .carregadores.proposicoes import CarregadorProposicoes
from .carregadores.autores import CarregadorAutores
from .carregadores.eventos import CarregadorEventos
from .carregadores.tramitacoes import CarregadorTramitacoes
from .carregadores.temas import CarregadorTemas
from .processador_base import ProcessadorBase

class ProcessadorCarregamento(ProcessadorBase):
    def __init__(self, anos: list):
        super().__init__("carregamento")
        self.anos = anos

    def processar(self):
        print("📥 Iniciando carregamento modular das bases...")

        dados = {
            "deputados": CarregadorDeputados().carregar(self.anos),
            "gastos": CarregadorGastos().carregar(self.anos),
            "proposicoes": CarregadorProposicoes().carregar(self.anos),
            "autores": CarregadorAutores().carregar(self.anos),
            "eventos": CarregadorEventos().carregar(self.anos),
            "tramitacoes": CarregadorTramitacoes().carregar(),
            "temas": CarregadorTemas().carregar()
        }

        print("✅ Todas as bases foram carregadas com sucesso.")
        return dados
