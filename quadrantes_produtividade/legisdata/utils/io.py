import os

def salvar_csv(df, caminho):
    """
    Salva um DataFrame em formato CSV no caminho especificado.
    Cria a pasta 'data/' se ela não existir.
    """
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    df.to_csv(caminho, index=False, encoding="utf-8-sig")
