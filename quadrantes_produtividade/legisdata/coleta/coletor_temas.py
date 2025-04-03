import os
import time
import requests
import warnings
import pandas as pd
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from legisdata.coleta.coletor_base import ColetorBase
from legisdata.config import DIRETORIO_RAW

# Carrega variáveis do .env
load_dotenv()

# Define proxies se existirem
proxies = {
    "http": os.getenv("HTTP_PROXY"),
    "https": os.getenv("HTTPS_PROXY")
}
proxies = {k: v for k, v in proxies.items() if v}


class ColetorTemas(ColetorBase):
    def __init__(self, max_workers=5):
        super().__init__(tipo="temas")
        self.max_workers = max_workers
        self.caminho_saida = os.path.join(DIRETORIO_RAW, "temas_proposicoes.csv")
        self.temas_existentes = self._carregar_ids_existentes()

    def _carregar_ids_existentes(self):
        if os.path.exists(self.caminho_saida):
            df_existente = pd.read_csv(self.caminho_saida)
            return set(df_existente["idProposicao"].astype(int).tolist())
        return set()

    def _salvar_incremental(self, linhas_dict):
        df_linhas = pd.DataFrame(linhas_dict)
        header = not os.path.exists(self.caminho_saida)
        df_linhas.to_csv(self.caminho_saida, mode='a', header=header, index=False)

    def _obter_temas_proposicao(self, id_proposicao, tentativas=10, tempo_max=600):
        url = f"https://dadosabertos.camara.leg.br/api/v2/proposicoes/{id_proposicao}/temas"
        for tentativa in range(tentativas):
            try:
                resp = requests.get(url, timeout=10, proxies=proxies)
                if resp.status_code == 200:
                    dados = resp.json().get("dados", [])
                    if dados:
                        registros = [{
                            "idProposicao": id_proposicao,
                            "tema": item.get("tema", "").strip(),
                            "codTema": item.get("codTema")
                        } for item in dados]
                        self._salvar_incremental(registros)
                        print(f"[OK] {id_proposicao}: {len(registros)} tema(s) encontrados.")
                        return
                    else:
                        print(f"[OK] {id_proposicao}: sem temas associados.")
                        return
                else:
                    print(f"[{id_proposicao}] Erro {resp.status_code}. Tentativa {tentativa + 1}/10")
            except Exception as e:
                print(f"[{id_proposicao}] Exceção: {e}. Tentativa {tentativa + 1}/10")
            tempo_espera = min(2 ** tentativa, tempo_max)
            print(f"→ Esperando {tempo_espera}s antes da nova tentativa para {id_proposicao}...")
            time.sleep(tempo_espera)

        warnings.warn(f"[{id_proposicao}] Todas as tentativas falharam.")

    def baixar(self, df_proposicoes: pd.DataFrame):
        lista_ids = df_proposicoes["id"].dropna().astype(int).unique().tolist()
        lista_ids = [i for i in lista_ids if i not in self.temas_existentes]

        print(f"🔎 Total de proposições: {len(df_proposicoes)}")
        print(f"✅ Já coletadas: {len(self.temas_existentes)}")
        print(f"⏳ Restantes para coleta: {len(lista_ids)}")
        print(f"🚀 Iniciando com {self.max_workers} workers...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._obter_temas_proposicao, id_prop): id_prop for id_prop in lista_ids}
            for i, future in enumerate(as_completed(futures), 1):
                id_finalizado = futures[future]
                try:
                    future.result()
                except Exception as e:
                    warnings.warn(f"[{id_finalizado}] Erro não tratado na thread: {e}")
                time.sleep(0.7)

        print("✔️ Coleta de temas concluída.")
