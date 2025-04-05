import os
import time
import requests
import warnings
import pandas as pd
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from .coletor_base import ColetorBase
from legisdata.config import DIRETORIO_RAW

# Carrega variáveis do .env
load_dotenv()

# Ignora proxies (como solicitado)
proxies = {}

class ColetorDeputados(ColetorBase):
    def __init__(self, max_workers=5):
        super().__init__(tipo="deputados")
        self.max_workers = max_workers
        self.caminho_saida = os.path.join(DIRETORIO_RAW, "deputados", "deputados.csv")
        self.ids_existentes = self._carregar_ids_existentes()

    def _carregar_ids_existentes(self):
        if os.path.exists(self.caminho_saida):
            df_existente = pd.read_csv(self.caminho_saida)
            return set(df_existente["id"].astype(int).tolist())
        return set()

    def _salvar_incremental(self, linha_dict):
        df_linha = pd.DataFrame([linha_dict])
        header = not os.path.exists(self.caminho_saida)
        df_linha.to_csv(self.caminho_saida, mode='a', header=header, index=False)

    def _obter_detalhes_deputado(self, id_deputado, tentativas=10, tempo_max=600):
        url = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{id_deputado}"
        for tentativa in range(tentativas):
            try:
                resp = requests.get(url, timeout=10, proxies=proxies)
                if resp.status_code == 200:
                    dados = resp.json().get("dados", {})
                    if dados:
                        self._salvar_incremental(dados)
                        print(f"[OK] {id_deputado}: {dados.get('nome')}")
                        return
                    else:
                        print(f"[{id_deputado}] Sem dados retornados.")
                        return
                else:
                    print(f"[{id_deputado}] Erro {resp.status_code}. Tentativa {tentativa + 1}/10")
            except Exception as e:
                print(f"[{id_deputado}] Exceção: {e}. Tentativa {tentativa + 1}/10")
            tempo_espera = min(2 ** tentativa, tempo_max)
            print(f"→ Esperando {tempo_espera}s antes da nova tentativa para {id_deputado}...")
            time.sleep(tempo_espera)

        warnings.warn(f"[{id_deputado}] Todas as tentativas falharam.")

    def baixar(self):
        url_lista = "https://dadosabertos.camara.leg.br/api/v2/deputados"
        resp = requests.get(url_lista, timeout=10, proxies=proxies)
        resp.raise_for_status()
        lista_ids = [dep["id"] for dep in resp.json().get("dados", [])]
        lista_ids = [i for i in lista_ids if i not in self.ids_existentes]

        print(f"🔎 Total de deputados: {len(lista_ids) + len(self.ids_existentes)}")
        print(f"✅ Já coletados: {len(self.ids_existentes)}")
        print(f"⏳ Restantes para coleta: {len(lista_ids)}")
        print(f"🚀 Iniciando com {self.max_workers} workers...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._obter_detalhes_deputado, dep_id): dep_id for dep_id in lista_ids}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    warnings.warn(f"[{futures[future]}] Erro não tratado na thread: {e}")
                time.sleep(0.5)

        print("✔️ Coleta de deputados concluída.")

if __name__ == "__main__":
    coletor = ColetorDeputados(max_workers=10)
    coletor.baixar()
    print("Coleta finalizada.")