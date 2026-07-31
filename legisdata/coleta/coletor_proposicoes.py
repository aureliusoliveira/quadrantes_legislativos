import os
import time
import requests
import pandas as pd
from legisdata.config import DIRETORIO_RAW
from .coletor_base import ColetorBase


class ColetorProposicoes(ColetorBase):
    """
    Coleta os dados de proposições legislativas por ano.
    Estratégia híbrida:
    1. Tenta baixar CSV consolidado.
    2. Se falhar, coleta via API com retries.
    """

    def __init__(self):
        super().__init__(tipo="proposicoes")

    def baixar(self, ano: int):
        if self._ja_baixado(ano):
            print(f"⏭️  Proposições {ano} já baixadas. Pulando...")
            return

        try:
            self._baixar_via_api(ano)
            #self._baixar_csv(ano)
            self._atualizar_checkpoint(ano)
        except Exception as e:
            print(f"⚠️ Erro no download do CSV de {ano}: {e}")
            print(f"🔁 Tentando coletar via API com retries...")
            try:
                self._baixar_via_api(ano)
                self._atualizar_checkpoint(ano)
            except Exception as e_api:
                print(f"❌ Falha também na coleta via API: {e_api}")

    def _baixar_csv(self, ano: int):
        url = f"https://dadosabertos.camara.leg.br/arquivos/proposicoes/csv/proposicoes-{ano}.csv"
        destino = os.path.join(DIRETORIO_RAW, self.tipo)
        os.makedirs(destino, exist_ok=True)
        caminho_csv = os.path.join(destino, f"{ano}.csv")

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, stream=True, timeout=60)
        response.raise_for_status()

        with open(caminho_csv, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"\n✅ Proposições {ano} baixadas via CSV: {caminho_csv}")

    def _baixar_via_api(self, ano: int):
        base_url = f"https://dadosabertos.camara.leg.br/api/v2/proposicoes?ano={ano}&itens=100&ordem=ASC&ordenarPor=id"
        headers = {"User-Agent": "Mozilla/5.0"}
        pagina = 1
        resultados = []
        tentativas_max = 3

        while True:
            url = f"{base_url}&pagina={pagina}"

            for tentativa in range(1, tentativas_max + 1):
                try:
                    response = requests.get(url, headers=headers, timeout=60)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    print(f"⚠️ Erro na página {pagina} (tentativa {tentativa}): {e}")
                    if tentativa == tentativas_max:
                        raise e
                    time.sleep(5 * tentativa)

            data = response.json()
            if "dados" not in data or not data["dados"]:
                break

            resultados.extend(data["dados"])
            pagina += 1

        if not resultados:
            raise ValueError("Nenhuma proposição retornada pela API.")

        df = pd.DataFrame(resultados)
        destino = os.path.join(DIRETORIO_RAW, self.tipo)
        os.makedirs(destino, exist_ok=True)
        caminho_csv = os.path.join(destino, f"{ano}.csv")
        df.to_csv(caminho_csv, index=False, encoding="utf-8-sig")

        print(f"\n✅ Proposições {ano} baixadas via API: {caminho_csv}")
