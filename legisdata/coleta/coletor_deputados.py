# legisdata/coleta/coletor_deputados.py

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import pandas as pd

from legisdata import config
from legisdata.utils.io import escrever_csv_atomico, obter_json

from .coletor_base import ColetorBase

URL_DEPUTADOS = "https://dadosabertos.camara.leg.br/api/v2/deputados"


class ColetorDeputados(ColetorBase):
    """Cadastro dos deputados da legislatura, com o detalhe de cada um.

    Reescrito por três motivos.

    **O cadastro muda.** O coletor antigo pulava id já presente no arquivo, e o
    arquivo era só acrescido. Quem trocou de partido, saiu para assumir cargo no
    Executivo ou foi substituído por suplente ficava congelado no estado do dia
    da primeira coleta — e a padronização filtra por `situacao == "Exercício"`,
    ou seja, o filtro que decide quem entra no ranking operava sobre dado velho.
    Agora todo o cadastro é rebaixado a cada carga.

    **A escrita era concorrente.** Cinco threads davam `to_csv(mode="a")` no
    mesmo arquivo. Aqui a thread só devolve o registro; a gravação é única e
    atômica, ao final.

    **A legislatura era implícita.** A listagem sem filtro devolve a legislatura
    corrente, então `QL_LEGISLATURA=56` coletava proposições de 2019-2022 e
    deputados de hoje. O filtro agora acompanha a legislatura alvo.
    """

    ARQUIVO = "deputados.csv"

    def __init__(
        self, max_workers: int = 8, legislatura: int | None = None, tentativas: int = 5
    ):
        super().__init__(tipo="deputados")
        self.max_workers = max_workers
        self.tentativas = tentativas
        self.legislatura = legislatura if legislatura is not None else config.LEGISLATURA_ALVO

    @property
    def caminho_saida(self) -> str:
        return os.path.join(config.DIRETORIO_RAW, self.tipo, self.ARQUIVO)

    def listar_ids(self) -> list[int]:
        """Ids de todos que exerceram mandato na legislatura, inclusive suplentes."""
        ids, pagina = [], 1
        while True:
            dados = obter_json(
                URL_DEPUTADOS,
                parametros={"idLegislatura": self.legislatura, "itens": 100, "pagina": pagina},
                tentativas=self.tentativas,
            )
            if not dados:
                break
            ids.extend(registro["id"] for registro in dados)
            pagina += 1
        return sorted(set(ids))

    def obter_detalhe(self, id_deputado: int) -> dict:
        detalhe = obter_json(f"{URL_DEPUTADOS}/{id_deputado}", tentativas=self.tentativas)
        if not detalhe:
            raise OSError(f"Detalhe vazio para o deputado {id_deputado}")
        return detalhe

    def baixar(self):
        ids = self.listar_ids()
        print(f"🔽 Baixando o cadastro de {len(ids)} deputados da {self.legislatura}ª legislatura...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # `map` propaga a primeira exceção: cadastro pela metade viraria
            # deputado sumindo do ranking sem nada acusar.
            detalhes = list(executor.map(self.obter_detalhe, ids))

        df = pd.DataFrame(detalhes)
        escrever_csv_atomico(df, self.caminho_saida)

        print(f"✅ {len(df)} deputados em {self.caminho_saida}")
        self.registrar_coleta(date.today().year)
