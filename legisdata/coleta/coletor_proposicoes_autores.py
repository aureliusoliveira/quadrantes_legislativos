# legisdata/coleta/coletor_proposicoes_autores.py

from .coletor_base import ColetorDeArquivoAnual


class ColetorProposicoesAutores(ColetorDeArquivoAnual):
    """Liga proposições aos seus autores.

    É a base que define o escopo da análise: das proposições do ano, só entram
    no cálculo as assinadas por deputado.
    """

    URL = (
        "https://dadosabertos.camara.leg.br/arquivos/proposicoesAutores/csv/"
        "proposicoesAutores-{ano}.csv"
    )
    ROTULO = "Autores"

    def __init__(self):
        super().__init__(tipo="proposicoes_autores")
