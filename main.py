from legisdata.deputados.identificacao import coletar_dados_deputados
from legisdata.deputados.gastos import consolidar_gastos

df_ids = coletar_dados_deputados()
lista_ids = df_ids["id_deputado"].tolist()

# Consolidar gastos de anos anteriores via CSV
for ano in range(2019, 2024):
    consolidar_gastos(ano, lista_ids)

# Coletar o ano atual via API
consolidar_gastos(2025, lista_ids)
