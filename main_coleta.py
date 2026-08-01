"""Pipeline de coleta: baixa os dados brutos da Câmara para data/raw/.

Os anos vêm da legislatura alvo (config.ANOS), não de um intervalo escrito à
mão. Rodar em qualquer mês de qualquer ano da legislatura traz o ano corrente.

Toda base anual vem de um arquivo consolidado publicado pela Câmara, gravado no
bruto como a fonte publicou. A coleta antiga fazia uma requisição por proposição
para situação e temas — mais de 200 mil requisições por ano, o que não terminava
dentro do limite de 6h de um job do GitHub Actions.
"""

from legisdata.coleta.coletor_deputados import ColetorDeputados
from legisdata.coleta.coletor_eventos import ColetorEventos
from legisdata.coleta.coletor_gastos import ColetorGastosCEAP
from legisdata.coleta.coletor_proposicoes import ColetorProposicoes
from legisdata.coleta.coletor_proposicoes_autores import ColetorProposicoesAutores
from legisdata.coleta.coletor_temas import ColetorTemas
from legisdata.config import ANOS, LEGISLATURA_ALVO


def coletar(anos=None, legislatura=None):
    anos = anos if anos is not None else ANOS
    legislatura = legislatura if legislatura is not None else LEGISLATURA_ALVO
    print(f"📥 Coleta da {legislatura}ª legislatura — anos {anos}")

    ColetorDeputados(legislatura=legislatura).baixar()

    coletores_anuais = [
        ColetorGastosCEAP(),
        ColetorProposicoes(),
        ColetorProposicoesAutores(),
        ColetorTemas(),
        ColetorEventos(),
    ]
    for ano in anos:
        for coletor in coletores_anuais:
            coletor.baixar(ano)

    print("✔️ Coleta concluída.")


if __name__ == "__main__":
    coletar()
