"""Testes de ambiente.

O pacote `legisdata` só é utilizável se todas as dependências que ele importa
estiverem declaradas no ambiente. Este teste falha quando o ambiente declarado
não cobre o que o código realmente importa — foi o caso do `requests`, que era
usado pela coleta sem constar do requirements.txt.

`main_coleta.py` fica de fora de propósito: o módulo não tem guarda
`if __name__ == "__main__"`, então importá-lo dispara a coleta inteira.
"""

import importlib
import pkgutil

import pytest

import legisdata


def _modulos_do_pacote(pacote):
    return sorted(
        nome
        for _, nome, _ in pkgutil.walk_packages(pacote.__path__, pacote.__name__ + ".")
    )


@pytest.mark.parametrize("nome_modulo", _modulos_do_pacote(legisdata))
def test_modulo_importa_sem_dependencia_ausente(nome_modulo):
    importlib.import_module(nome_modulo)
