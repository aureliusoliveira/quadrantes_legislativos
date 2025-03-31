# -*- coding: utf-8 -*-
"""
Created on Sun Mar 30 20:22:10 2025

@author: Aurelius
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# === 1. Carregamento da base ===
df = pd.read_csv("resultados.csv", sep=",")  # ajuste o separador se necessário
df.columns = df.columns.str.strip()

# === 2. Preparo dos dados ===
x = df["indice_produtividade"]
y = df["total_gastos"]
labels = df["nomeCivil"]

# Medianas para traçar os quadrantes
x_median = x.median()
y_median = y.median()

# === 3. Criação do gráfico ===
fig, ax = plt.subplots(figsize=(12, 7))

# Pontos (scatter plot)
ax.scatter(x, y, alpha=0.7, s=40, color='royalblue')

# Linhas de quadrante
ax.axvline(x=x_median, color='gray', linestyle='--')
ax.axhline(y=y_median, color='gray', linestyle='--')

# Eixos e título
ax.set_xlabel("Produtividade Ponderada", fontsize=12)
ax.set_ylabel("Gasto Total Ajustado (R$)", fontsize=12)
ax.set_title("Quadrantes: Custo x Produtividade Legislativa", fontsize=14, weight='bold')

# Formatação do eixo Y como reais (BRL)
ax.yaxis.set_major_formatter(
    ticker.FuncFormatter(lambda x, _: f"R${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
)

# Estilo visual
plt.grid(True, linestyle="--", alpha=0.3)
plt.tight_layout()

# === 4. Exibir ou salvar ===
plt.show()
# plt.savefig("quadrantes_produtividade.png", dpi=300)
