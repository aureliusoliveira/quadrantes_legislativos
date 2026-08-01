# legisdata/coleta/coletor_eventos.py

from .coletor_base import ColetorDeArquivoAnual


class ColetorEventos(ColetorDeArquivoAnual):
    """Eventos da Câmara no ano.

    Ainda não alimenta indicador publicado — é insumo previsto para as métricas
    de participação do IAPD (seção 7 do PRD). Fica na coleta porque o arquivo é
    barato e a série histórica não se reconstrói depois; o carregador aparece
    junto com o indicador que o consumir.
    """

    URL = "https://dadosabertos.camara.leg.br/arquivos/eventos/csv/eventos-{ano}.csv"
    ROTULO = "Eventos"

    def __init__(self):
        super().__init__(tipo="eventos")
