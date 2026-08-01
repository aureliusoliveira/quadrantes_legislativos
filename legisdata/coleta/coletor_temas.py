# legisdata/coleta/coletor_temas.py

from .coletor_base import ColetorDeArquivoAnual


class ColetorTemas(ColetorDeArquivoAnual):
    """Temas atribuídos às proposições, do arquivo consolidado do ano.

    Substitui uma requisição por proposição — com `sleep` dentro do laço, o que
    serializava a vazão em torno de 1,4 req/s e fazia a coleta anual levar
    dezenas de horas. Um job do GitHub Actions expira em 6h, então a atualização
    mensal prevista no PRD não tinha como existir.
    """

    URL = (
        "https://dadosabertos.camara.leg.br/arquivos/proposicoesTemas/csv/"
        "proposicoesTemas-{ano}.csv"
    )
    ROTULO = "Temas"

    def __init__(self):
        super().__init__(tipo="temas")
