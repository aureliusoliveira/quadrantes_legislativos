import os
import requests
import pandas as pd
from datetime import datetime

from legisdata.utils.io import salvar_csv
from legisdata.config import (
    DIRETORIO_RAW,
    URL_API_DESPESAS,
    URL_CSV_CONSOLIDADO,
    ITENS_POR_PAGINA,
    ANO_ATUAL
)

def baixar_csv_consolidado(ano: int) -> pd.DataFrame:
    print(f"🔽 Baixando gastos consolidados de {ano}...")

    url = URL_CSV_CONSOLIDADO.format(ano)
    try:
        df = pd.read_csv(url, sep=';', encoding='latin1')
        print(f"✅ Dados de {ano} carregados com {len(df)} registros.")
        return df
    except Exception as e:
        print(f"❌ Falha ao baixar dados de {ano}: {e}")
        return pd.DataFrame()


def coletar_despesas_api(id_deputado: int, ano: int) -> pd.DataFrame:
    print(f"🔄 Coletando despesas via API - ID {id_deputado} - {ano}")
    url = URL_API_DESPESAS.format(id=id_deputado)
    despesas = []
    pagina = 1

    while True:
        params = {
            "ano": ano,
            "itens": ITENS_POR_PAGINA,
            "pagina": pagina
        }
        resposta = requests.get(url, params=params)
        if resposta.status_code != 200:
            print(f"⚠️ Erro ao coletar página {pagina} de {id_deputado}: {resposta.status_code}")
            break

        dados = resposta.json()["dados"]
        if not dados:
            break

        despesas.extend(dados)
        pagina += 1

    return pd.DataFrame(despesas)


def coletar_despesas_ano_corrente(lista_ids: list, ano: int = None) -> pd.DataFrame:
    if ano is None:
        ano = ANO_ATUAL

    print(f"\n📅 Coletando despesas do ano corrente ({ano}) via API para todos os deputados...\n")
    todas_despesas = []

    for id_dep in lista_ids:
        df_dep = coletar_despesas_api(id_dep, ano)
        if not df_dep.empty:
            todas_despesas.append(df_dep)

    if todas_despesas:
        df_total = pd.concat(todas_despesas, ignore_index=True)
        print(f"✅ Coleta concluída: {len(df_total)} registros de {len(lista_ids)} deputados.")
        return df_total
    else:
        print("⚠️ Nenhuma despesa encontrada via API.")
        return pd.DataFrame()


def salvar_gastos(df: pd.DataFrame, ano: int):
    caminho = os.path.join(DIRETORIO_RAW, f"gastos_{ano}.csv")
    salvar_csv(df, caminho)


def consolidar_gastos(ano: int, lista_ids: list):
    if ano < ANO_ATUAL:
        df = baixar_csv_consolidado(ano)
    else:
        df = coletar_despesas_ano_corrente(lista_ids, ano)

    if not df.empty:
        salvar_gastos(df, ano)
