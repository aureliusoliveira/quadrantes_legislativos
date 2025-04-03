import plotly.graph_objects as go

def grafico_quadrantes_interativo(df):
    # Cálculo das medianas
    mediana_produtividade = df["produtividade_legislativa"].median()
    mediana_gasto = df["gasto_ceap_ajustado"].median()

    # Ordena para o ranking
    df["ranking"] = df["pontuacao_legislativa"].rank(ascending=False, method="min").astype(int)

    # Scatter plot dos deputados
    scatter = go.Scatter(
        x=df["produtividade_legislativa"],
        y=df["gasto_ceap_ajustado"],
        mode="markers",
        marker=dict(size=10, color="blue", opacity=0.7),
        customdata=df[["nome", "siglaPartido", "siglaUf", "quadrante", "ranking"]],
        hovertemplate=(
            "<b>%{customdata[0]}</b> (%{customdata[1]}-%{customdata[2]})<br>" +
            "Produtividade: %{x:.1f}<br>" +
            "Gasto ajustado: R$ %{y:,.2f}<br>" +
            "Quadrante: %{customdata[3]}<br>" +
            "Ranking: %{customdata[4]}º<extra></extra>"
        ),
        name="Deputados"
    )

    # Linhas de mediana
    shapes = [
        dict(type="line", x0=mediana_produtividade, x1=mediana_produtividade, y0=df["gasto_ceap_ajustado"].min(), y1=df["gasto_ceap_ajustado"].max(),
             line=dict(dash="dash", color="red"), name="Mediana Produtividade"),
        dict(type="line", x0=df["produtividade_legislativa"].min(), x1=df["produtividade_legislativa"].max(),
             y0=mediana_gasto, y1=mediana_gasto, line=dict(dash="dash", color="green"), name="Mediana Gasto")
    ]

    fig = go.Figure(data=[scatter])
    fig.update_layout(
        title="Quadrantes da Produtividade Legislativa",
        xaxis_title="Produtividade Legislativa",
        yaxis_title="Gasto CEAP Ajustado (R$)",
        hovermode="closest",
        shapes=shapes
    )

    return fig
