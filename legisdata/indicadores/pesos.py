# legisdata/indicadores/pesos.py

import pandas as pd


class MapaDePesos:
    """Peso de cada tipo de proposição, e o universo que conta como produção.

    O mapa responde a duas perguntas com a mesma tabela. *Quanto vale* cada tipo
    entra na produtividade. *Se vale alguma coisa* define o universo do produto:
    peso zero declara que aquele tipo não é produção legislativa do parlamentar,
    e o que não é produção também não deveria contar como sucesso ou fracasso de
    tramitação. Ver docs/universo_e_pesos.md.
    """

    def __init__(self, caminho: str):
        self.caminho = caminho
        try:
            tabela = pd.read_csv(caminho, sep=";")
            self.pesos = dict(zip(tabela["siglaTipo"], tabela["peso"]))
        except Exception as e:
            raise ValueError(f"Erro ao carregar o mapa de pesos: {e}") from e

    def aplicar(self, proposicoes: pd.DataFrame) -> pd.DataFrame:
        """Anota o peso de cada proposição, recusando tipo não declarado.

        Um tipo fora do mapa não pode virar peso zero em silêncio: seria a
        Câmara criando uma sigla e a produtividade daquele tipo desaparecendo
        sem nenhum sinal, com o número errado seguindo para o dashboard. Peso
        zero continua possível — mas declarado como linha do mapa.
        """
        desconhecidos = sorted(set(proposicoes["siglaTipo"].dropna()) - set(self.pesos))
        if desconhecidos:
            raise ValueError(
                "Tipos de proposição ausentes do mapa de pesos: "
                f"{', '.join(desconhecidos)}. "
                f"Declare o peso de cada um em {self.caminho} — inclusive "
                "quando o peso pretendido for zero."
            )

        anotadas = proposicoes.copy()
        anotadas["peso"] = anotadas["siglaTipo"].map(self.pesos)
        return anotadas

    def producao(self, proposicoes: pd.DataFrame) -> pd.DataFrame:
        """As proposições que contam como produção legislativa."""
        anotadas = self.aplicar(proposicoes)
        return anotadas[anotadas["peso"] > 0]
