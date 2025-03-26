# legisdata/coleta/coletor_deputados.py

import os
import requests
from legisdata.config import DIRETORIO_RAW
from .coletor_base import ColetorBase


class ColetorDeputados(ColetorBase):
    """
    Baixa a base principal de identificação dos deputados federais.
    """

    def __init__(self):
        super().__init__(tipo="deputados")

    def baixar(self):
        if self._ja_baixado("geral"):
            print("⏭️  Dados dos deputados já baixados. Pulando...")
            return

        url = "https://dadosabertos.camara.leg.br/arquivos/deputados/csv/deputados.csv"
        print("🔽 Baixando base de identificação dos deputados...")

        try:
            destino = os.path.join(DIRETORIO_RAW, self.tipo)
            os.makedirs(destino, exist_ok=True)
            caminho_csv = os.path.join(destino, "deputados.csv")

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

            print(f"\n✅ Deputados salvos em: {caminho_csv}")
            self._atualizar_checkpoint("geral")

        except Exception as e:
            print(f"\n❌ Erro ao baixar dados dos deputados: {e}")
