import os
import wget
import zipfile
import tempfile
import shutil
import pandas as pd
from datetime import datetime
from legisdata.config import (
    DIRETORIO_RAW,
    DIRETORIO_CHECKPOINT,
    ARQUIVO_CHECKPOINT,
    URL_CEAP_ZIP
)



class ColetorBase:
    """
    Classe base para coletores de arquivos da Câmara.
    Define a lógica de checkpoint comum a todas as coletas.
    """

    def __init__(self, tipo: str):
        self.tipo = tipo
        self.checkpoint_file = ARQUIVO_CHECKPOINT
        os.makedirs(DIRETORIO_CHECKPOINT, exist_ok=True)

    def _carregar_checkpoint(self):
        if os.path.exists(self.checkpoint_file):
            return pd.read_csv(self.checkpoint_file)
        else:
            return pd.DataFrame(columns=["tipo", "ano", "baixado_em"])

    def _atualizar_checkpoint(self, ano):
        df = self._carregar_checkpoint()
        nova_linha = pd.DataFrame([{
            "tipo": self.tipo,
            "ano": ano,
            "baixado_em": datetime.now().isoformat()
        }])
        df = pd.concat([df, nova_linha], ignore_index=True)
        df.to_csv(self.checkpoint_file, index=False)

    def _ja_baixado(self, ano):
        df = self._carregar_checkpoint()
        return not df[(df["tipo"] == self.tipo) & (df["ano"] == ano)].empty

    def baixar(self, ano):
        raise NotImplementedError("Subclasses devem implementar o método baixar().")


class ColetorGastosCEAP(ColetorBase):
    """
    Baixa e extrai os arquivos CEAP da Câmara (.zip por ano).
    """

    def __init__(self):
        super().__init__(tipo="gastos")

    def baixar(self, ano: int):
        if self._ja_baixado(ano):
            print(f"⏭️  Gastos {ano} já baixado. Pulando...")
            return

        url = URL_CEAP_ZIP.format(ano=ano)

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

            print(f"\n✅ CEAP {ano} salvo em: {destino}\\{ano}.csv")
            self._atualizar_checkpoint(ano)

        except Exception as e:
            print(f"\n❌ Erro ao baixar gastos {ano}: {e}")

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

class ColetorProposicoes(ColetorBase):
    """
    Baixa os arquivos de proposições legislativas (.csv) por ano.
    Fonte: https://dadosabertos.camara.leg.br/arquivos/proposicoes/csv/proposicoes-{ano}.csv
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

