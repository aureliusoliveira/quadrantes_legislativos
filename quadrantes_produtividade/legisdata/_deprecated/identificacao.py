import requests
import pandas as pd
import os

from legisdata.utils.io import salvar_csv
from legisdata.config import (
    URL_API_LISTA_DEPUTADOS,
    ITENS_POR_PAGINA,
    DIRETORIO_RAW
)


def coletar_dados_deputados(itens_por_pagina=ITENS_POR_PAGINA):
    """
    Coleta dados de identificação dos deputados federais em exercício
    e retorna um DataFrame com os principais campos.
    """
    print("🔄 Coletando dados de identificação dos deputados...")

    parametros = {
        "itens": itens_por_pagina,
        "ordem": "ASC",
        "ordenarPor": "nome"
    }

    response = requests.get(URL_API_LISTA_DEPUTADOS, params=parametros)
    response.raise_for_status()

    dados = response.json()["dados"]

    df = pd.DataFrame(dados)
    df = df.rename(columns={
        "id": "id_deputado",
        "nome": "nome",
        "siglaPartido": "partido",
        "siglaUf": "uf",
        "uri": "url_detalhes"
    })

    print(f"✅ {len(df)} deputados encontrados.")
    return df


def salvar_dados_identificacao(df, nome_arquivo="deputados_identificacao.csv"):
    """
    Salva o DataFrame com os dados de identificação em CSV.
    """
    caminho = os.path.join(DIRETORIO_RAW, nome_arquivo)
    salvar_csv(df, caminho)
    print(f"💾 Arquivo salvo em: {caminho}")
