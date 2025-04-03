import pandas as pd
from legisdata.processamento.indicadores import IndicadoresParlamentares
from legisdata.config import DIRETORIO_PROCESSED


def carregar_dados():
    # Caminhos relativos (ajuste conforme sua organização local)
    pasta_static = os.path.join("legisdata", "static")

    # Carregamento dos dados processados
    deputados = pd.read_csv(os.path.join(DIRETORIO_PROCESSED, "deputados.csv"))
    proposicoes = pd.read_csv(os.path.join(DIRETORIO_PROCESSED, "proposicoes.csv"))
    autores = pd.read_csv(os.path.join(DIRETORIO_PROCESSED, "autores.csv"))
    gastos = pd.read_csv(os.path.join(DIRETORIO_PROCESSED, "gastos.csv"))
    tramitacoes = pd.read_csv(os.path.join(DIRETORIO_PROCESSED, "tramitacoes.csv"))
    temas = pd.read_csv(os.path.join(DIRETORIO_PROCESSED, "temas.csv"))

    # Executa a classe de indicadores com pesos customizados
    dados = {
        "deputados": deputados,
        "proposicoes": proposicoes,
        "autores": autores,
        "gastos": gastos,
        "tramitacoes": tramitacoes,
        "temas": temas
    }

    caminho_pesos = os.path.join(pasta_static, "mapa_pesos_proposicoes.csv")
    indicadores = IndicadoresParlamentares(dados, caminho_pesos=caminho_pesos)

    # Retorna todos os dados e os resultados finais
    dados["resultados"] = indicadores.resultados
    return dados

if __name__ == "__main__":
    dados = carregar_dados()
    print(dados["resultados"].head())
