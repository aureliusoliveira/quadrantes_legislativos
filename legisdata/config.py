import os
from datetime import date

# Diretório raiz do projeto (relativo ao settings.py)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Diretórios de dados
DIRETORIO_RAW = os.path.join(ROOT_DIR, "..", "data", "raw")
DIRETORIO_PROCESSED = os.path.join(ROOT_DIR, "..", "data", "processed")
DIRETORIO_CHECKPOINT = os.path.join(ROOT_DIR, "..", "checkpoints")
DIRETORIO_DASHBOARD_DATA = os.path.join(ROOT_DIR, "..", "dashboard", "data")

# Arquivo central de checkpoints de arquivos baixados
ARQUIVO_CHECKPOINT = os.path.join(DIRETORIO_CHECKPOINT, "arquivos_baixados.csv")

# Ano atual (pode ser usado em loops)
ANO_ATUAL = date.today().year

# Quantidade de itens por página nas requisições (se necessário)
ITENS_POR_PAGINA = 100

# Mapa de pesos para proposições
MAPA_DE_PESOS = os.path.join(ROOT_DIR, "static", "mapa_pesos_proposicoes.csv")
