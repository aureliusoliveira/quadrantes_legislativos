# legisdata/coleta/coletor_gastos.py

import os
import shutil
import tempfile

from legisdata import config
from legisdata.utils.io import baixar_arquivo, extrair_csv_de_zip

from .coletor_base import ColetorBase


class ColetorGastosCEAP(ColetorBase):
    """Baixa o arquivo anual de despesas da cota parlamentar (CEAP).

    A fonte é republicada: a Câmara reprocessa e reemite o arquivo do ano
    conforme as despesas são liquidadas. Por isso o ano aberto é rebaixado a
    cada carga — ver ColetorBase.
    """

    def __init__(self):
        super().__init__(tipo="gastos")

    def baixar(self, ano: int):
        if not self.deve_baixar(ano):
            print(f"⏭️  Gastos {ano}: ano fechado e já coletado.")
            return

        url = f"http://www.camara.leg.br/cotas/Ano-{ano}.csv.zip"
        print(f"🔽 Baixando CEAP {ano}...")

        temporario = tempfile.mkdtemp()
        try:
            zip_path = baixar_arquivo(url, os.path.join(temporario, f"{ano}.zip"))
            caminho_csv = extrair_csv_de_zip(zip_path, temporario)

            destino = os.path.join(config.DIRETORIO_RAW, self.tipo, f"{ano}.csv")
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            # `move` no mesmo sistema de arquivos é rename: o arquivo da carga
            # anterior só é substituído depois do download completo.
            shutil.move(caminho_csv, destino)

            print(f"✅ CEAP {ano} em {destino}")
            self.registrar_coleta(ano)
        finally:
            shutil.rmtree(temporario, ignore_errors=True)
