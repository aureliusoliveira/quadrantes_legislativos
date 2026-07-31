from legisdata.indicadores.indicadores_gerais import IndicadoresGerais
from legisdata.processamento.processador_carregamento import ProcessadorCarregamento
from legisdata.processamento.transformador_dados import TransformadorDados
from legisdata.config import MAPA_DE_PESOS, DIRETORIO_DASHBOARD_DATA
import os

#MAPA_DE_PESOS = "dados/mapa_pesos_proposicoes.csv"
ANOS = [2023, 2024, 2025]

if __name__ == "__main__":
    # Carregar e transformar dados
    dados_brutos = ProcessadorCarregamento(ANOS).processar()
    dados_tratados = TransformadorDados(dados_brutos).transformar()

    # Calcular indicadores
    indicadores = IndicadoresGerais(dados_tratados, caminho_pesos=MAPA_DE_PESOS)
    resultado = indicadores.calcular()
    resultado.to_csv(os.path.join(DIRETORIO_DASHBOARD_DATA, "resultados.csv"), sep=";", index=False)

    # Exibir resultado
    print(resultado.shape)
    print(resultado.sample(10))
