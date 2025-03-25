# legisdata/coleta/coletor_gastos.py

import os
import wget
import zipfile
import tempfile
import shutil
from .coletor_base import ColetorBase

DIRETORIO_RAW = os.path.join("data", "raw")


class ColetorGastosCEAP(ColetorBase):
    """
    Baixa e extrai arquivos de gastos parlamentares (CEAP).
    """

    def __init__(self):
        super().__init__(tipo="gastos")

    def baixar(self, ano: int):
        if self._ja_baixado(ano):
            print(f"⏭️  Gastos {ano} já baixado. Pulando...")
            return

        url = f"http://www.camara.leg.br/cotas/Ano-{ano}.csv.zip"
        print(f"🔽 Baixando arquivo CEAP {ano}...")

        try:
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, f"{ano}.zip")
            wget.download(url, out=zip_path)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            arquivo_csv = next(f for f in os.listdir(temp_dir) if f.endswith(".csv"))
            caminho_csv = os.path.join(temp_dir, arquivo_csv)

            destino = os.path.join(DIRETORIO_RAW, self.tipo)
            os.makedirs(destino, exist_ok=True)
            shutil.move(caminho_csv, os.path.join(destino, f"{ano}.csv"))

            print(f"\n✅ CEAP {ano} salvo em: {destino}/{ano}.csv")
            self._atualizar_checkpoint(ano)

        except Exception as e:
            print(f"\n❌ Erro ao baixar gastos {ano}: {e}")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
