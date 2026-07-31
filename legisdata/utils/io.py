import os
import zipfile

def salvar_csv(df, caminho):
    """
    Salva um DataFrame em formato CSV no caminho especificado.
    Cria a pasta 'data/' se ela não existir.
    """
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    df.to_csv(caminho, index=False, encoding="utf-8-sig")


def extrair_csv_de_zip(zip_path: str, destino: str) -> str:
    """
    Extrai o primeiro arquivo .csv de um arquivo .zip e salva no diretório destino.
    Retorna o caminho final do arquivo extraído.
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(destino)

    arquivos_extraidos = os.listdir(destino)
    arquivo_csv = next((f for f in arquivos_extraidos if f.endswith(".csv")), None)

    if not arquivo_csv:
        raise FileNotFoundError("Nenhum arquivo .csv encontrado no zip.")

    caminho_csv = os.path.join(destino, arquivo_csv)
    return caminho_csv
