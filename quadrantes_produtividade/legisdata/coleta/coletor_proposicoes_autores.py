# legisdata/coleta/coletor_proposicoes_autores.py

import os
import requests
from legisdata.config import DIRETORIO_RAW
from .coletor_base import ColetorBase


class ColetorProposicoesAutores(ColetorBase):
    """
    Baixa os arquivos CSV que relacionam proposições legislativas aos seus autores.
    """

    def __init__(self):
        super().__init__(tipo="proposicoes_autores")

    def baixar(self, ano: int):
        if self._ja_baixado(ano):
            print(f"⏭️  Autores de proposições {ano} já baixados. Pulando...")
            return

        url = f"https://dadosabertos.camara.leg.br/arquivos/proposicoesAutores/csv/proposicoesAutores-{ano}.csv"
        print(f"🔽 Baixando autores das proposições de {ano}...")

        try:
            destino = os.path.join(DIRETORIO_RAW, self.tipo)
            os.makedirs(destino, exist_ok=True)
            caminho_csv = os.path.join(destino, f"{ano}.csv")

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

            print(f"\n✅ Autores de proposições {ano} salvos em: {caminho_csv}")
            self._atualizar_checkpoint(ano)

        except Exception as e:
            print(f"\n❌ Erro ao baixar autores de proposições {ano}: {e}")
