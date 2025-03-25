from legisdata.coleta.coletor_gastos import ColetorGastosCEAP
from legisdata.coleta.coletor_proposicoes import ColetorProposicoes

coletor_gastos = ColetorGastosCEAP()
coletor_proposicoes = ColetorProposicoes()

for ano in range(2023, 2026):
    coletor_gastos.baixar(ano)
    coletor_proposicoes.baixar(ano)
