# legisdata/config.py

import os
from datetime import datetime

# Diretórios para armazenar dados
DIRETORIO_RAW = os.path.join("data", "raw")
DIRETORIO_PROCESSED = os.path.join("data", "processed")
DIRETORIO_OUTPUTS = os.path.join("data", "outputs")

# Endpoints da Câmara dos Deputados
URL_API_LISTA_DEPUTADOS = "https://dadosabertos.camara.leg.br/api/v2/deputados"
URL_API_DESPESAS = "https://dadosabertos.camara.leg.br/api/v2/deputados/{id}/despesas"
URL_CSV_CONSOLIDADO = "https://www.camara.leg.br/cotas/Ano-{}.csv"

# Outros parâmetros padrão
ITENS_POR_PAGINA = 100
ANO_ATUAL = datetime.now().year
ENCODING_PADRAO = "utf-8-sig"
