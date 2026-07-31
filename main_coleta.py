"""Pipeline de coleta: baixa os dados brutos da Câmara para data/raw/.

Os anos vêm da legislatura alvo (config.ANOS), não de um intervalo escrito à
mão. Rodar em qualquer mês de qualquer ano da legislatura traz o ano corrente.
"""

from legisdata.coleta.coletor_deputados import ColetorDeputados
from legisdata.coleta.coletor_gastos import ColetorGastosCEAP
from legisdata.coleta.coletor_proposicoes import ColetorProposicoes
from legisdata.coleta.coletor_proposicoes_autores import ColetorProposicoesAutores
from legisdata.coleta.coletor_temas import ColetorTemas
from legisdata.coleta.coletor_tramitacoes import ColetorTramitacoes
from legisdata.config import ANOS, LEGISLATURA_ALVO
from legisdata.processamento.carregadores.proposicoes import CarregadorProposicoes


def coletar(anos=None):
    anos = anos if anos is not None else ANOS
    print(f"📥 Coleta da {LEGISLATURA_ALVO}ª legislatura — anos {anos}")

    ColetorDeputados().baixar()

    coletor_gastos = ColetorGastosCEAP()
    coletor_proposicoes = ColetorProposicoes()
    coletor_autores = ColetorProposicoesAutores()
    for ano in anos:
        coletor_gastos.baixar(ano)
        coletor_proposicoes.baixar(ano)
        coletor_autores.baixar(ano)

    df_proposicoes = CarregadorProposicoes().carregar(anos)
    ColetorTramitacoes().baixar(df_proposicoes)
    ColetorTemas().baixar(df_proposicoes)

    print("✔️ Coleta concluída.")


if __name__ == "__main__":
    coletar()
