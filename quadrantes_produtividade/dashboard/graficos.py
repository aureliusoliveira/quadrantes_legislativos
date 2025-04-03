import plotly.graph_objects as go

def grafico_quadrantes_interativo(df):
    # Cálculo das medianas
    mediana_produtividade = df["produtividade_legislativa"].median()
    mediana_gasto = df["gasto_ceap_ajustado"].median()

    # Ordena para o ranking
    df["ranking"] = df["pontuacao_legislativa"].rank(ascending=False, method="min").astype(int)

    # Scatter plot dos deputados
    scatter_partidos = []
    partidos = df["sgPartido"].unique()
    for partido in sorted(partidos):
        dados_partido = df[df["sgPartido"] == partido]
        trace = go.Scatter(
            x=dados_partido["produtividade_legislativa"],
            y=dados_partido["gasto_ceap_ajustado"],
            mode="markers",
            marker=dict(size=6, opacity=0.95),
            name=partido,
            customdata=dados_partido[["nome", "sgUF", "sgPartido", "quadrante", "ranking", 
                                    "temas_destaque", "pct_sucesso", "pct_fracasso", "pct_andamento"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b> (%{customdata[1]}-%{customdata[2]})<br>" +
                "🔹 <b>Quadrante:</b> %{customdata[3]}<br>" +
                "🥇 <b>Ranking:</b> %{customdata[4]}º<br>" +
                "📈 <b>Produtividade:</b> %{x:.1f}<br>" +
                "💰 <b>Gasto ajustado:</b> R$ %{y:,.2f}<br><br>" +
                "🗣️ Atuou majoritariamente em temas como <b>%{customdata[5]}</b>.<br>" +
                "📌 Suas proposições tiveram <b>%{customdata[6]:.1%}</b> de sucesso, "
                "<b>%{customdata[7]:.1%}</b> de fracasso e "
                "<b>%{customdata[8]:.1%}</b> ainda em tramitação." +
                "<extra></extra>"
            ),
        )
        scatter_partidos.append(trace)


    # Linhas de mediana com rótulos
    layout_shapes = [
        dict(
            type="line",
            x0=mediana_produtividade, x1=mediana_produtividade,
            y0=df["gasto_ceap_ajustado"].min(), y1=df["gasto_ceap_ajustado"].max(),
            line=dict(dash="dash", color="red")
        ),
        dict(
            type="line",
            x0=df["produtividade_legislativa"].min(), x1=df["produtividade_legislativa"].max(),
            y0=mediana_gasto, y1=mediana_gasto,
            line=dict(dash="dash", color="green")
        )
    ]

    # Anotações de texto nas medianas
    annotations = [
        dict(
            x=mediana_produtividade, y=df["gasto_ceap_ajustado"].max(),
            text=f"Mediana Produtividade ({mediana_produtividade:.1f})",
            showarrow=False
        ),
        dict(
            x=df["produtividade_legislativa"].max(), y=mediana_gasto,
            text=f"Mediana Gasto (R$ {mediana_gasto:,.2f})".replace(",", "."),
            showarrow=False,
            yshift=10
        )
    ]

    fig = go.Figure(data=scatter_partidos)
    fig.update_layout(
        title="Quadrantes da Produtividade Legislativa",
        xaxis_title="Produtividade Legislativa",
        yaxis=dict(
                title="Gasto CEAP Ajustado",
                tickformat=".",  # ativa separador de milhar
                tickprefix="R$ "),
        hovermode="closest",
        shapes=layout_shapes,
        annotations=annotations,
        height=850
    )

    return fig
