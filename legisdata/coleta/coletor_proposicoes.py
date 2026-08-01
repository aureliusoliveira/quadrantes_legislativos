# legisdata/coleta/coletor_proposicoes.py

from .coletor_base import ColetorDeArquivoAnual


class ColetorProposicoes(ColetorDeArquivoAnual):
    """Proposições apresentadas no ano, do arquivo consolidado da Câmara.

    Antes a coleta era paginada pela API — cem proposições por requisição, mais
    de mil requisições por ano, com retry serial. O arquivo consolidado traz o
    mesmo universo em um download.

    Ele também traz `ultimoStatus_descricaoSituacao`, que é o dado que o
    ColetorTramitacoes buscava proposição a proposição, uma requisição HTTP para
    cada uma das ~107 mil do ano. Por isso não há coletor de situações: elas são
    derivadas deste mesmo arquivo no carregamento (CarregadorSituacoes).
    """

    URL = "https://dadosabertos.camara.leg.br/arquivos/proposicoes/csv/proposicoes-{ano}.csv"
    ROTULO = "Proposições"

    def __init__(self):
        super().__init__(tipo="proposicoes")
