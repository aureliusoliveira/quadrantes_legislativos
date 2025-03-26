from legisdata.coleta.coletor_gastos import ColetorGastosCEAP
from legisdata.coleta.coletor_proposicoes import ColetorProposicoes
from legisdata.coleta.coletor_deputados import ColetorDeputados
from legisdata.coleta.coletor_eventos import ColetorEventos
from quadrantes_produtividade.legisdata._deprecated.coletor_comissoes import ColetorComissoes


#coletor_gastos = ColetorGastosCEAP()
#coletor_proposicoes = ColetorProposicoes()
#coletor_deputados = ColetorDeputados()
#coletor_eventos = ColetorEventos()
coletor_comissoes = ColetorComissoes()

for ano in range(2023, 2026):
    # coletor_gastos.baixar(ano)
    # coletor_proposicoes.baixar(ano)
    # coletor_deputados.baixar()
    # coletor_eventos.baixar(ano)
    # coletor_comissoes.baixar(ano)
