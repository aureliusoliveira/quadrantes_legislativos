from legisdata.coleta.coletor_gastos import ColetorGastosCEAP
from legisdata.coleta.coletor_proposicoes import ColetorProposicoes
from legisdata.coleta.coletor_deputados import ColetorDeputados
from legisdata.coleta.coletor_proposicoes_autores import ColetorProposicoesAutores
from legisdata.coleta.coletor_tramitacoes import ColetorTramitacoes
from legisdata.processamento.carregadores import proposicoes # CarregadorProposicoes
from legisdata.coleta.coletor_temas import ColetorTemas


import pandas as pd



coletor_deputados = ColetorDeputados()
coletor_gastos = ColetorGastosCEAP()
coletor_proposicoes = ColetorProposicoes()
coletor_proposicoes_autores = ColetorProposicoesAutores()
coletor_tramitacoes = ColetorTramitacoes()
coletor_temas = ColetorTemas()

for ano in range(2023, 2026):
    coletor_gastos.baixar(ano)
    coletor_proposicoes.baixar(ano)
    coletor_proposicoes_autores.baixar(ano)
    #coletor_deputados.baixar()
anos = [2023, 2024, 2025]
df_proposicoes = proposicoes.CarregadorProposicoes().carregar(anos)
coletor = ColetorTramitacoes()
#coletor = ColetorTemas()
coletor_tramitacoes.baixar(df_proposicoes)
coletor_temas.baixar(df_proposicoes)
