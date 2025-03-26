# legisdata/coleta/coletor_eventos_presenca.py

import os
import requests
from legisdata.config import DIRETORIO_RAW
from .coletor_base import ColetorBase


class ColetorEventos(ColetorBase):
    """
    Baixa os registros de presença dos deputados em eventos da Câmara por ano.
    """

    def __init__(self):
        super().__init__(tipo="eventos")

    def baixar(self, ano: int):
        if self._ja_baixado(ano):
            print(f"⏭️  Presenças em eventos {ano} já baixadas. Pulando...")
            return

        url = f"https://dadosabertos.camara.leg.br/arquivos/eventos/csv/eventos-{ano}.csv"
        print(f"🔽 Baixando presenças em eventos de {ano}...")

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

            print(f"\n✅ Presenças em eventos {ano} salvas em: {caminho_csv}")
            self._atualizar_checkpoint(ano)

        except Exception as e:
            print(f"\n❌ Erro ao baixar presenças em eventos {ano}: {e}")
