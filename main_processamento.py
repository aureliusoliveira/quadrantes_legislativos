"""Pipeline de processamento: transforma o bruto em indicadores publicáveis."""

import os

from legisdata.config import ANOS, DIRETORIO_DASHBOARD_DATA, LEGISLATURA_ALVO, MAPA_DE_PESOS
from legisdata.indicadores.indicadores_gerais import IndicadoresGerais
from legisdata.processamento.processador_carregamento import ProcessadorCarregamento
from legisdata.processamento.transformador_dados import TransformadorDados


def processar(anos=None, legislatura=None):
    anos = anos if anos is not None else ANOS
    legislatura = legislatura if legislatura is not None else LEGISLATURA_ALVO

    dados_brutos = ProcessadorCarregamento(anos).processar()
    dados_tratados = TransformadorDados(dados_brutos, legislatura=legislatura).transformar()

    indicadores = IndicadoresGerais(dados_tratados, caminho_pesos=MAPA_DE_PESOS)
    return indicadores.calcular()


if __name__ == "__main__":
    resultado = processar()

    destino = os.path.join(DIRETORIO_DASHBOARD_DATA, "resultados.csv")
    resultado.to_csv(destino, sep=";", index=False)

    print(f"✅ {len(resultado)} parlamentares em {destino}")
    print(resultado.sample(min(10, len(resultado))))
