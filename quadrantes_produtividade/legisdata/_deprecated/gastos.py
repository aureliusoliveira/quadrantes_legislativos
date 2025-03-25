import os
import pandas as pd
import requests
from datetime import datetime, date
from io import StringIO
import wget
import zipfile
import tempfile
import shutil

from legisdata.config import (
    DIRETORIO_RAW,
    URL_API_DESPESAS,
    ITENS_POR_PAGINA,
    ANO_ATUAL
)

CHECKPOINT_FILE = os.path.join("checkpoints", "gastos.csv")


# =======================
# 🔁 Checkpoint Management
# =======================

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


# =======================
# 📦 Coleta via API (Ano Atual)
# =======================

def coletar_despesas_mensais(id_dep, ano, mes):
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
    mes_atual = date.today().month

    for id_dep in lista_ids:
        for mes in range(1, mes_atual + 1):
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


# =======================
# 📥 CSV Consolidado (Anos Anteriores)
# =======================

def baixar_csv_consolidado(ano: int) -> pd.DataFrame:
    """
    Faz o download do arquivo ZIP da Câmara para o ano informado,
    extrai o CSV contido, carrega como DataFrame e o retorna.
    """
    url = f"http://www.camara.leg.br/cotas/Ano-{ano}.csv.zip"
    print(f"🔽 Baixando arquivo ZIP consolidado de {ano}...")

    try:
        # Criar diretório temporário seguro
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, f"gastos_{ano}.zip")

        # Baixa o arquivo .zip
        wget.download(url, out=zip_path)

        # Extrai o conteúdo
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Localiza o .csv extraído
        arquivos_extraidos = os.listdir(temp_dir)
        arquivo_csv = next((f for f in arquivos_extraidos if f.endswith(".csv")), None)

        if not arquivo_csv:
            raise FileNotFoundError("Nenhum arquivo .csv encontrado no zip.")

        csv_path = os.path.join(temp_dir, arquivo_csv)

        # Carrega o CSV em DataFrame
        df = pd.read_csv(
            csv_path,
            sep=';',
            encoding='latin1',
            engine='python',
            quoting=3,
            on_bad_lines='skip'
        )

        print(f"\n✅ {len(df)} registros carregados para {ano}")
        return df

    except Exception as e:
        print(f"\n❌ Erro ao baixar ou processar CSV consolidado de {ano}: {e}")
        return pd.DataFrame()

    finally:
        # Limpa os arquivos temporários
        shutil.rmtree(temp_dir, ignore_errors=True)


def consolidar_gastos_historicos(ano: int):
    df = baixar_csv_consolidado(ano)
    if df.empty:
        print(f"⚠️ Nenhum dado salvo para o ano {ano}.")
        return

    # Normalização
    df = df.rename(columns={"txtNumero": "id_deputado", "numMes": "mes"})

    if "id_deputado" not in df.columns or "mes" not in df.columns:
        print("❌ Dados não contêm colunas 'id_deputado' e 'mes'.")
        return

    # Salva arquivo bruto
    os.makedirs(os.path.join(DIRETORIO_RAW, "gastos"), exist_ok=True)
    caminho = os.path.join(DIRETORIO_RAW, "gastos", f"gastos_{ano}.csv")
    df.to_csv(caminho, index=False, encoding="utf-8-sig")
    print(f"💾 Dados de {ano} salvos em: {caminho}")

    # Atualiza checkpoint
    checkpoint = carregar_checkpoint()
    novos_registros = 0

    for _, linha in df[["id_deputado", "mes"]].drop_duplicates().iterrows():
        id_dep = linha["id_deputado"]
        mes = int(linha["mes"])
        if not registro_existe(id_dep, ano, mes, checkpoint):
            atualizar_checkpoint(id_dep, ano, mes)
            novos_registros += 1

    print(f"📌 {novos_registros} entradas de checkpoint adicionadas para {ano}.")


# =======================
# 📊 Roteador Inteligente
# =======================

def consolidar_gastos(lista_ids: list, ano: int):
    if ano < ANO_ATUAL:
        consolidar_gastos_historicos(ano)
    else:
        consolidar_gastos_ano_atual(lista_ids, ano)
