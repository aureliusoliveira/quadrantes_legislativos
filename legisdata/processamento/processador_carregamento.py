# legisdata/processamento/processador_carregamento.py

from .carregadores.autores import CarregadorAutores
from .carregadores.deputados import CarregadorDeputados
from .carregadores.gastos import CarregadorGastos
from .carregadores.proposicoes import CarregadorProposicoes
from .carregadores.situacoes import CarregadorSituacoes
from .carregadores.temas import CarregadorTemas
from .processador_base import ProcessadorBase


class ProcessadorCarregamento(ProcessadorBase):
    def __init__(self, anos: list):
        super().__init__("carregamento")
        self.anos = anos

    def processar(self):
        print(f"📥 Carregando bases dos anos {self.anos}...")

        dados = {
            "deputados": CarregadorDeputados().carregar(self.anos),
            "gastos": CarregadorGastos().carregar(self.anos),
            "proposicoes": CarregadorProposicoes().carregar(self.anos),
            "autores": CarregadorAutores().carregar(self.anos),
            # A chave segue "tramitacoes" porque é o que IndicadoresTramitacao
            # consome; a fonte passou a ser a situação atual da proposição no
            # arquivo consolidado, em vez do último registro de tramitação
            # buscado proposição a proposição.
            "tramitacoes": CarregadorSituacoes().carregar(self.anos),
            "temas": CarregadorTemas().carregar(self.anos),
        }

        for nome, df in dados.items():
            print(f"   {nome:<12} {len(df):>8} linhas")

        return dados
