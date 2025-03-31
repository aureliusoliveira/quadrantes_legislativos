import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# === 1. Carregar os dados ===
df = pd.read_csv("resultados.csv", sep=",")
df.columns = df.columns.str.strip()

# === 2. Calcular medianas ===
x_med = df["indice_produtividade"].median()
y_med = df["total_gastos"].median()

# === 3. Gráfico principal (sem facet_col) ===
fig = px.scatter(
    df,
    x="indice_produtividade",
    y="total_gastos",
    hover_name="nomeCivil",
    color="siglaPartido",
    hover_data=["siglaUf", "siglaPartido", "total_gastos", "indice_produtividade"],
    title="Quadrantes: Custo x Produtividade Legislativa",
    labels={
        "indice_produtividade": "Produtividade Ponderada",
        "total_gastos": "Gasto Total Ajustado (R$)"
    }
)

# === 4. Linhas de mediana ===
fig.add_shape(
    type="line",
    x0=x_med, x1=x_med,
    y0=df["total_gastos"].min(), y1=df["total_gastos"].max(),
    line=dict(color="gray", dash="dash")
)
fig.add_shape(
    type="line",
    x0=df["indice_produtividade"].min(), x1=df["indice_produtividade"].max(),
    y0=y_med, y1=y_med,
    line=dict(color="gray", dash="dash")
)

# === 5. Anotações das medianas ===
fig.add_annotation(
    x=x_med, y=df["total_gastos"].max(), showarrow=False,
    text="Mediana Produtividade", font=dict(size=10, color="gray")
)
fig.add_annotation(
    x=df["indice_produtividade"].max(), y=y_med, showarrow=False,
    text="Mediana Gastos", font=dict(size=10, color="gray")
)

# === 6. Formatação brasileira ===
fig.update_yaxes(
    tickformat=".2f",
    tickprefix="R$",
    separatethousands=True
)

# === 7. Layout final ===
fig.update_layout(
    hovermode="closest",
    height=700,
    margin=dict(t=60, b=40, l=60, r=20),
    legend_title_text="Partido"
)

# === 8. Salvar e abrir ===
pio.write_html(fig, file="quadrantes_interativo_limpo.html", auto_open=True)
