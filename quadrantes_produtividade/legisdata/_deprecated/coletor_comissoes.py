# legisdata/coleta/coletor_comissoes.py

import os
import requests
from legisdata.config import DIRETORIO_RAW
from ..coleta.coletor_base import ColetorBase


class ColetorComissoes(ColetorBase):
    """
    Baixa os dados de composição das comissões da Câmara dos Deputados.
    """

    def __init__(self):
        super().__init__(tipo="comissoes")

    def baixar(self):
        if self._ja_baixado("geral"):
            print("⏭️  Comissões já baixadas. Pulando...")
            return

        url = "https://dadosabertos.camara.leg.br/arquivos/comissoesMembros/csv/comissoesMembros.csv"
        print("🔽 Baixando dados de composição das comissões...")

        try:
            destino = os.path.join(DIRETORIO_RAW, self.tipo)
            os.makedirs(destino, exist_ok=True)
            caminho_csv = os.path.join(destino, "comissoes.csv")

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

            print(f"\n✅ Comissões salvas em: {caminho_csv}")
            self._atualizar_checkpoint("geral")

        except Exception as e:
            print(f"\n❌ Erro ao baixar comissões: {e}")
