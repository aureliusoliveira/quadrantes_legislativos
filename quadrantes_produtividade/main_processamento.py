from legisdata.processamento.processador_carregamento import ProcessadorCarregamento
from legisdata.processamento.indicadores import IndicadoresParlamentares
from legisdata.processamento.transformador_dados import TransformadorDados


anos = [2023, 2024, 2025]

carregador = ProcessadorCarregamento(anos)
bases = carregador.processar()

deputados = bases['deputados']
proposicoes = bases['proposicoes']
gastos = bases['gastos']
eventos = bases['eventos']
autores = bases['autores']

# Transformação
transformador = TransformadorDados(bases)
dados_tratados = transformador.transformar()

# Indicadores
calc = IndicadoresParlamentares(dados_tratados, caminho_pesos="mapa_pesos_proposicoes.csv")
df_resultado = calc.calcular_indicadores()
df_resultado.dropna(inplace=True)
