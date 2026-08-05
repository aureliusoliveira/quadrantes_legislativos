from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAIZ = BASE_DIR.parent

INDICADORES_PATH = BASE_DIR / "data" / "resultados.csv"

# O diagrama vive em docs/ porque serve o README também. Um só arquivo: legenda
# do painel e ilustração do repositório não podem divergir.
DIAGRAMA_QUADRANTES = RAIZ / "docs" / "como_ler_os_quadrantes.svg"
#PESOS_PATH = BASE_DIR / "static" / "mapa_pesos_proposicoes.csv"