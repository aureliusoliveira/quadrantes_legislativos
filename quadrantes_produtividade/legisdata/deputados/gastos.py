import os
import pandas as pd
import requests
from datetime import datetime
from legisdata.config import (
    DIRETORIO_RAW,
    URL_API_DESPESAS,
    ITENS_POR_PAGINA,
    ANO_ATUAL
)

CHECKPOINT_FILE = os.path.join("checkpoints", "gastos.csv")

def carregar_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        return pd.read_csv(CHECKPOINT_FILE)
    else:
        return pd.DataFrame(columns=["id_deputado", "ano", "mes", "coletado_em"])


def atualizar_checkpoint(id_dep, ano, mes):
    df = carregar_checkpoint()
    nova_linha = pd.DataFrame([{
        "id_deputado": id_dep,
        "ano": ano,
        "mes": mes,
        "coletado_em": datetime.now().isoformat()
    }])
    df_atualizado = pd.concat([df, nova_linha], ignore_index=True)
    os.makedirs("checkpoints", exist_ok=True)
    df_atualizado.to_csv(CHECKPOINT_FILE, index=False)


def registro_existe(id_dep, ano, mes, checkpoint_df):
    cond = (
        (checkpoint_df["id_deputado"] == id_dep) &
        (checkpoint_df["ano"] == ano) &
        (checkpoint_df["mes"] == mes)
    )
    return not checkpoint_df[cond].empty


def coletar_despesas_mensais(id_dep, ano, mes):
    """
    Coleta os gastos de um deputado em um mês específico via API.
    """
    url = URL_API_DESPESAS.format(id=id_dep)
    pagina = 1
    todas = []

    while True:
        params = {
            "ano": ano,
            "mes": mes,
            "pagina": pagina,
            "itens": ITENS_POR_PAGINA
        }
        resposta = requests.get(url, params=params)
        if resposta.status_code != 200:
            break
        dados = resposta.json()["dados"]
        if not dados:
            break
        todas.extend(dados)
        pagina += 1

    return pd.DataFrame(todas)


def salvar_gastos(df, id_dep, ano):
    caminho = os.path.join(DIRETORIO_RAW, "gastos", str(ano))
    os.makedirs(caminho, exist_ok=True)
    arquivo = os.path.join(caminho, f"{id_dep}.csv")

    if os.path.exists(arquivo):
        df_antigo = pd.read_csv(arquivo)
        df_total = pd.concat([df_antigo, df], ignore_index=True)
    else:
        df_total = df

    df_total.to_csv(arquivo, index=False, encoding="utf-8-sig")


def consolidar_gastos_ano_atual(lista_ids, ano=ANO_ATUAL):
    print(f"🚀 Coletando gastos parlamentares do ano {ano} (mês a mês)...")
    checkpoint = carregar_checkpoint()

    for id_dep in lista_ids:
        for mes in range(1, 13):
            if registro_existe(id_dep, ano, mes, checkpoint):
                print(f"⏭️  {id_dep} {ano}/{mes:02d} já coletado.")
                continue

            df = coletar_despesas_mensais(id_dep, ano, mes)
            if not df.empty:
                salvar_gastos(df, id_dep, ano)
                atualizar_checkpoint(id_dep, ano, mes)
                print(f"✅ {id_dep} {ano}/{mes:02d}: {len(df)} registros.")
            else:
                print(f"⚠️  {id_dep} {ano}/{mes:02d}: Nenhuma despesa encontrada.")
