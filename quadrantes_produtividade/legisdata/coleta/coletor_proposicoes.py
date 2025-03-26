# legisdata/coleta/coletor_proposicoes.py

import os
import requests
from http.client import IncompleteRead
from legisdata.config import DIRETORIO_RAW
from .coletor_base import ColetorBase


class ColetorProposicoes(ColetorBase):
    def __init__(self):
        super().__init__(tipo="proposicoes")

    def baixar(self, ano: int):
        if self._ja_baixado(ano):
            print(f"⏭️  Proposições {ano} já baixadas. Pulando...")
            return

        url = f"https://dadosabertos.camara.leg.br/arquivos/proposicoes/csv/proposicoes-{ano}.csv"
        print(f"🔽 Baixando proposições de {ano}...")

        destino = os.path.join(DIRETORIO_RAW, self.tipo)
        os.makedirs(destino, exist_ok=True)
        caminho_csv = os.path.join(destino, f"{ano}.csv")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "text/csv"
            }

            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()

            with open(caminho_csv, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"\n✅ Proposições {ano} salvas em: {caminho_csv}")
            self._atualizar_checkpoint(ano)

        except IncompleteRead as e:
            print(f"\n⚠️ IncompleteRead ignorado para proposições {ano}: {e}")
            self._atualizar_checkpoint(ano)  # ainda marca como baixado

        except Exception as e:
            print(f"\n❌ Erro ao baixar proposições {ano}: {e}")
