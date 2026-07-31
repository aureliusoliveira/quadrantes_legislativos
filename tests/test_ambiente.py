"""Testes de ambiente.

O pacote `legisdata` só é utilizável se todas as dependências que ele importa
estiverem declaradas no ambiente. Este teste falha quando o ambiente declarado
não cobre o que o código realmente importa — foi o caso do `requests`, que era
usado pela coleta sem constar do requirements.txt.

`main_coleta.py` fica de fora de propósito: o módulo não tem guarda
`if __name__ == "__main__"`, então importá-lo dispara a coleta inteira.
"""

import importlib
import os
import pkgutil
import subprocess

import pytest

import legisdata
from legisdata import config


def _modulos_do_pacote(pacote):
    return sorted(
        nome
        for _, nome, _ in pkgutil.walk_packages(pacote.__path__, pacote.__name__ + ".")
    )


@pytest.mark.parametrize("nome_modulo", _modulos_do_pacote(legisdata))
def test_modulo_importa_sem_dependencia_ausente(nome_modulo):
    importlib.import_module(nome_modulo)


@pytest.mark.parametrize(
    "diretorio",
    [config.DIRETORIO_RAW, config.DIRETORIO_PROCESSED, config.DIRETORIO_CHECKPOINT],
)
def test_diretorio_de_dados_nao_vai_para_o_git(diretorio):
    """O .gitignore precisa acompanhar os caminhos reais do config.

    O achatamento da árvore no Incremento 1 invalidou as entradas antigas
    (`quadrantes_produtividade/data/`), e sem isto a próxima coleta comitaria
    centenas de MB de dado bruto.
    """
    alvo = os.path.join(os.path.normpath(diretorio), "arquivo-qualquer.csv")
    resultado = subprocess.run(
        ["git", "check-ignore", "-q", alvo],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
    assert resultado.returncode == 0, f"{alvo} não está coberto pelo .gitignore"
