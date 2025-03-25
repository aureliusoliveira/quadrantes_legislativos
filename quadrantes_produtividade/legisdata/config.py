import os

# Diretórios de Dados
DIRETORIO_RAW = os.path.join("quadrantes_produtividade","data", "raw")

#Checkpoints
DIRETORIO_CHECKPOINT = os.path.join("quadrantes_produtividade", "checkpoints")
ARQUIVO_CHECKPOINT = os.path.join(f"{DIRETORIO_CHECKPOINT}","arquivos_baixados.csv")

# URL base
URL_CEAP_ZIP = "http://www.camara.leg.br/cotas/Ano-{ano}.csv.zip"
