"""Legislatura como dimensão do modelo.

A legislatura é a unidade natural de comparação do projeto — o PRD quer poder
perguntar se um deputado melhorou ou piorou em relação à anterior. Antes disso,
ela estava espalhada como constante literal em quatro lugares: o intervalo de
anos da coleta, a lista de anos do processamento, e os filtros `idLegislatura`
e `codLegislatura` da padronização.
"""

from datetime import date

# Âncora: a 57ª legislatura vai de 2023 a 2026. Todas as outras são derivadas
# daqui, quatro anos por legislatura.
LEGISLATURA_ANCORA = 57
ANO_INICIAL_DA_ANCORA = 2023
DURACAO_EM_ANOS = 4

# A Câmara publica dados abertos a partir da 48ª; abaixo disso o número é engano.
PRIMEIRA_LEGISLATURA_SUPORTADA = 49

# O CEAP de dezembro chega semanas depois do fim do ano. Fechar o ano em 1º de
# janeiro descartaria a última leva de despesas, então ele segue aberto por uma
# janela de carência.
MESES_DE_CARENCIA_APOS_O_ANO = 3


def anos_da_legislatura(numero: int) -> list[int]:
    """Os quatro anos civis cobertos pela legislatura."""
    if numero < PRIMEIRA_LEGISLATURA_SUPORTADA:
        raise ValueError(
            f"Legislatura {numero} fora do suportado — a partir da "
            f"{PRIMEIRA_LEGISLATURA_SUPORTADA}ª."
        )
    inicio = ANO_INICIAL_DA_ANCORA + (numero - LEGISLATURA_ANCORA) * DURACAO_EM_ANOS
    return list(range(inicio, inicio + DURACAO_EM_ANOS))


def legislatura_de(ano: int) -> int:
    """A legislatura à qual o ano civil pertence."""
    return LEGISLATURA_ANCORA + (ano - ANO_INICIAL_DA_ANCORA) // DURACAO_EM_ANOS


def anos_a_coletar(numero: int, hoje: date | None = None) -> list[int]:
    """Os anos da legislatura que já começaram.

    É a correção do `range(2023, 2026)` fixo: o ano corrente entra por
    construção, e a lista se estende sozinha na virada do ano — sem ninguém
    lembrar de editar código em janeiro.
    """
    hoje = hoje or date.today()
    return [ano for ano in anos_da_legislatura(numero) if ano <= hoje.year]


def ano_esta_aberto(ano: int, hoje: date | None = None) -> bool:
    """Se o ano ainda pode receber dado novo da fonte.

    Distinção que o checkpoint precisa fazer e não fazia: ano fechado foi
    coletado em definitivo, ano aberto tem que ser rebaixado a cada carga. Sem
    isso, o CEAP — que é republicado conforme as despesas são processadas —
    congela no estado do dia da primeira coleta.
    """
    hoje = hoje or date.today()
    if ano > hoje.year:
        return False
    if ano == hoje.year:
        return True
    meses_desde_o_fim = (hoje.year - ano - 1) * 12 + hoje.month
    return meses_desde_o_fim <= MESES_DE_CARENCIA_APOS_O_ANO
