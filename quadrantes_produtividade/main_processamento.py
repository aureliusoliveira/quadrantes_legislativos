from legisdata.processamento.processador_carregamento import ProcessadorCarregamento
from legisdata.processamento.indicadores import IndicadoresParlamentares
from legisdata.processamento.transformador_dados import TransformadorDados

from legisdata.config import DIRETORIO_PROCESSED

import os

anos = [2023, 2024, 2025]

carregador = ProcessadorCarregamento(anos)
bases = carregador.processar()


# Transformação
transformador = TransformadorDados(bases)
dados_tratados = transformador.transformar()

deputados = dados_tratados['deputados']
proposicoes = dados_tratados['proposicoes']
gastos = dados_tratados['gastos']
autores = dados_tratados['autores']
temas = dados_tratados['temas']
tramitacoes = dados_tratados['tramitacoes']

deputados.to_csv(os.path.join(DIRETORIO_PROCESSED,"deputados.csv"), sep=",", index=False)
proposicoes.to_csv(os.path.join(DIRETORIO_PROCESSED,"proposicoes.csv"), sep=",", index=False)
gastos.to_csv(os.path.join(DIRETORIO_PROCESSED,"gastos.csv"), sep=",", index=False)
autores.to_csv(os.path.join(DIRETORIO_PROCESSED,"autores.csv"), sep=",", index=False)
temas.to_csv(os.path.join(DIRETORIO_PROCESSED,"temas.csv"), sep=",", index=False)
tramitacoes.to_csv(os.path.join(DIRETORIO_PROCESSED,"tramitacoes.csv"), sep=",", index=False)

# Indicadores
indicadores = IndicadoresParlamentares(dados_tratados)
resultados = indicadores.resultados
resultados.to_csv("dashboard\\data\\resultados.csv", sep=",", index=False)
