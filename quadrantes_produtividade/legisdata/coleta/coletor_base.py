# legisdata/coleta/coletor_base.py

import os
import pandas as pd
from datetime import datetime

DIRETORIO_CHECKPOINT = os.path.join("checkpoints")
ARQUIVO_CHECKPOINT = os.path.join(DIRETORIO_CHECKPOINT, "arquivos_baixados.csv")


class ColetorBase:
    """
    Classe base para todos os coletores de dados da Câmara.
    Gerencia checkpoint por tipo + ano.
    """

    def __init__(self, tipo: str):
        self.tipo = tipo
        os.makedirs(DIRETORIO_CHECKPOINT, exist_ok=True)

    def _carregar_checkpoint(self):
        if os.path.exists(ARQUIVO_CHECKPOINT):
            return pd.read_csv(ARQUIVO_CHECKPOINT)
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
        df.to_csv(ARQUIVO_CHECKPOINT, index=False)

    def _ja_baixado(self, ano):
        df = self._carregar_checkpoint()
        return not df[(df["tipo"] == self.tipo) & (df["ano"] == ano)].empty

    def baixar(self, ano):
        raise NotImplementedError("Subclasses devem implementar o método baixar().")
