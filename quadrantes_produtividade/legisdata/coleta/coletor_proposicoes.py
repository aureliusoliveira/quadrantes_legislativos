# legisdata/coleta/coletor_proposicoes.py

import os
import wget
from .coletor_base import ColetorBase

DIRETORIO_RAW = os.path.join("data", "raw")


class ColetorProposicoes(ColetorBase):
    """
    Baixa os arquivos de proposições legislativas (.csv) por ano.
    """

    def __init__(self):
        super().__init__(tipo="proposicoes")

    def baixar(self, ano: int):
        if self._ja_baixado(ano):
            print(f"⏭️  Proposições {ano} já baixadas. Pulando...")
            return

        url = f"https://dadosabertos.camara.leg.br/arquivos/proposicoes/csv/proposicoes-{ano}.csv"
        print(f"🔽 Baixando proposições de {ano}...")

        try:
            destino = os.path.join(DIRETORIO_RAW, self.tipo)
            os.makedirs(destino, exist_ok=True)
            caminho_csv = os.path.join(destino, f"{ano}.csv")

            wget.download(url, out=caminho_csv)

            print(f"\n✅ Proposições {ano} salvas em: {caminho_csv}")
            self._atualizar_checkpoint(ano)

        except Exception as e:
            print(f"\n❌ Erro ao baixar proposições {ano}: {e}")
