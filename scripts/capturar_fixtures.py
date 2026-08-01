"""Recaptura as fixtures de contrato a partir das fontes reais da Câmara.

Uso:  uv run python scripts/capturar_fixtures.py

As fixtures são amostras minúsculas — algumas linhas de cada fonte. O que
importa nelas é a forma, não o volume: nome de coluna, tipo, e os casos de borda
que o pipeline precisa tratar (situação ausente, autoria de órgão sem id de
deputado). Ao recapturar, confira o diff antes de commitar: mudança de coluna
aqui é mudança de contrato, e é justamente o que os testes existem para acusar.
"""

import csv
import io
import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from legisdata.utils.io import USER_AGENT  # noqa: E402

DESTINO = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "api"
ANO = 2025

FONTES_JSON = {
    "deputados_lista.json": "https://dadosabertos.camara.leg.br/api/v2/deputados?itens=3",
    "deputado_detalhe.json": "https://dadosabertos.camara.leg.br/api/v2/deputados/204554",
}

FONTES_CSV = {
    "proposicoes_consolidado.csv": (
        f"https://dadosabertos.camara.leg.br/arquivos/proposicoes/csv/proposicoes-{ANO}.csv"
    ),
    "proposicoes_temas.csv": (
        "https://dadosabertos.camara.leg.br/arquivos/proposicoesTemas/csv/"
        f"proposicoesTemas-{ANO}.csv"
    ),
    "proposicoes_autores.csv": (
        "https://dadosabertos.camara.leg.br/arquivos/proposicoesAutores/csv/"
        f"proposicoesAutores-{ANO}.csv"
    ),
}

# Quantas linhas guardar de cada CSV, e o que a amostra precisa conter. O
# predicado existe porque as primeiras linhas do arquivo nem sempre trazem o
# caso de borda: em autores, as de cima são todas do Senado.
AMOSTRAS = {
    "proposicoes_consolidado.csv": [(3, lambda linha: True)],
    "proposicoes_temas.csv": [(5, lambda linha: True)],
    "proposicoes_autores.csv": [
        (2, lambda linha: not linha["idDeputadoAutor"].strip()),
        (5, lambda linha: bool(linha["idDeputadoAutor"].strip())),
    ],
}


def baixar_inicio(url, bytes_maximos=900_000):
    """Só o começo do arquivo: os consolidados passam de 50 MB."""
    resposta = requests.get(
        url,
        headers={"User-Agent": USER_AGENT, "Range": f"bytes=0-{bytes_maximos}"},
        timeout=120,
    )
    resposta.raise_for_status()
    return resposta.content.decode("utf-8-sig", errors="ignore")


def capturar_csv(nome, url):
    leitor = csv.DictReader(io.StringIO(baixar_inicio(url)), delimiter=";")
    grupos = [(quantas, criterio, []) for quantas, criterio in AMOSTRAS[nome]]

    for linha in leitor:
        # O Range corta o arquivo no meio de uma linha; a última fica com campos
        # faltando e não representa o que a fonte publica.
        if any(valor is None for valor in linha.values()):
            continue
        for quantas, criterio, colhidas in grupos:
            if len(colhidas) < quantas and criterio(linha):
                colhidas.append(linha)
        if all(len(colhidas) == quantas for quantas, _, colhidas in grupos):
            break

    registros = [linha for _, _, colhidas in grupos for linha in colhidas]
    with open(DESTINO / nome, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=leitor.fieldnames, delimiter=";", quoting=csv.QUOTE_ALL
        )
        escritor.writeheader()
        escritor.writerows(registros)
    return f"{len(registros)} linhas, {len(leitor.fieldnames)} colunas"


def capturar_json(nome, url):
    resposta = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=60)
    resposta.raise_for_status()
    conteudo = {"dados": resposta.json()["dados"]}
    (DESTINO / nome).write_text(
        json.dumps(conteudo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    dados = conteudo["dados"]
    return f"{len(dados) if isinstance(dados, list) else 1} registro(s)"


if __name__ == "__main__":
    for nome, url in FONTES_JSON.items():
        print(f"{nome}: {capturar_json(nome, url)}")
    for nome, url in FONTES_CSV.items():
        print(f"{nome}: {capturar_csv(nome, url)}")
