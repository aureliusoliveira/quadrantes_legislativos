# legisdata/coleta/coletor_base.py

import os
from datetime import date, datetime

import pandas as pd

from legisdata import config
from legisdata.legislatura import ano_esta_aberto
from legisdata.utils.io import baixar_arquivo, escrever_csv_atomico

COLUNAS_DO_CHECKPOINT = ["tipo", "ano", "baixado_em"]


class ColetorBase:
    """Base dos coletores, com o controle do que já foi coletado.

    O checkpoint anterior registrava `(tipo, ano)` como baixado em definitivo.
    Isso funciona para fonte imutável, e nenhuma das fontes deste projeto é: o
    CEAP é republicado conforme a Câmara processa as despesas, e a situação de
    uma proposição muda enquanto ela tramita. O efeito foi o artefato publicado
    subestimar o gasto em R$ 177 milhões — ver docs/qualidade_dados.md.

    Agora o checkpoint distingue ano fechado, que não muda mais, de ano aberto,
    que é rebaixado a cada carga.
    """

    def __init__(self, tipo: str):
        self.tipo = tipo

    @property
    def _arquivo_checkpoint(self):
        # Lido a cada uso, e não no import, para que o teste possa isolar o
        # diretório sem depender da ordem de importação dos módulos.
        return config.ARQUIVO_CHECKPOINT

    def carregar_checkpoint(self) -> pd.DataFrame:
        if os.path.exists(self._arquivo_checkpoint):
            return pd.read_csv(self._arquivo_checkpoint)
        return pd.DataFrame(columns=COLUNAS_DO_CHECKPOINT)

    def registrar_coleta(self, ano: int) -> None:
        """Anota a coleta do ano, substituindo o registro anterior do par.

        O checkpoint antigo dava append, então uma carga mensal acumulava uma
        linha por mês por tipo por ano, indefinidamente.
        """
        df = self.carregar_checkpoint()
        if not df.empty:
            df = df[~((df["tipo"] == self.tipo) & (df["ano"].astype(int) == int(ano)))]

        nova = pd.DataFrame(
            [{"tipo": self.tipo, "ano": int(ano), "baixado_em": datetime.now().isoformat()}]
        )
        atualizado = pd.concat([df, nova], ignore_index=True)[COLUNAS_DO_CHECKPOINT]
        escrever_csv_atomico(atualizado, self._arquivo_checkpoint)

    def ja_coletado(self, ano: int) -> bool:
        df = self.carregar_checkpoint()
        if df.empty:
            return False
        return not df[(df["tipo"] == self.tipo) & (df["ano"].astype(int) == int(ano))].empty

    def deve_baixar(self, ano: int, hoje: date | None = None) -> bool:
        """Ano aberto sempre; ano fechado só na primeira vez."""
        if ano_esta_aberto(ano, hoje=hoje):
            return True
        return not self.ja_coletado(ano)

    def baixar(self, ano):
        raise NotImplementedError("Subclasses devem implementar o método baixar().")


class ColetorDeArquivoAnual(ColetorBase):
    """Baixa o arquivo anual que a Câmara publica para uma das bases.

    Quatro coletores tinham este mesmo corpo e diferiam só na URL — proposições,
    autores, temas e eventos. Aqui o corpo é um só e a subclasse declara de onde
    vem o arquivo.

    O arquivo é gravado **como a fonte publicou**, sem seleção de coluna nem
    conversão de tipo. A derivação acontece no carregamento, onde pode ser
    refeita sem uma nova coleta — que é o ponto de existir uma camada bruta.
    """

    URL = ""
    ROTULO = ""

    def caminho_do_ano(self, ano: int) -> str:
        return os.path.join(config.DIRETORIO_RAW, self.tipo, f"{ano}.csv")

    def baixar(self, ano: int):
        if not self.deve_baixar(ano):
            print(f"⏭️  {self.ROTULO} {ano}: ano fechado e já coletado.")
            return

        print(f"🔽 Baixando {self.ROTULO.lower()} de {ano}...")
        destino = baixar_arquivo(self.URL.format(ano=ano), self.caminho_do_ano(ano))

        print(f"✅ {self.ROTULO} {ano} em {destino} ({os.path.getsize(destino) / 1e6:.1f} MB)")
        self.registrar_coleta(ano)
