import pandas as pd
import plotly.graph_objects as go


def _frase_de_eficacia(linha):
    """Descreve o destino das proposições, ou diz que não há o que descrever.

    Parlamentar sem nenhuma proposição no universo medido tem taxa nula, não
    zero — e "0,0% de sucesso" seria afirmar fracasso onde não houve medição.
    Ver docs/universo_e_pesos.md.
    """
    if pd.isna(linha["pct_sucesso"]):
        return "📌 Sem proposições no universo medido — não há taxa de tramitação."
    return (
        f"📌 Suas proposições tiveram <b>{linha['pct_sucesso']:.1%}</b> de sucesso, "
        f"<b>{linha['pct_fracasso']:.1%}</b> de fracasso e "
        f"<b>{linha['pct_andamento']:.1%}</b> ainda em tramitação."
    )


def _frase_de_temas(linha):
    if pd.isna(linha["temas_destaque"]):
        return "🗣️ Sem temas registrados nas proposições."
    return f"🗣️ Atuou majoritariamente em temas como <b>{linha['temas_destaque']}</b>."


def grafico_quadrantes_interativo(df):
    # Cálculo das medianas
    mediana_produtividade = df["produtividade_legislativa"].median()
    mediana_gasto = df["gasto_ceap_ajustado"].median()

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
            customdata=dados_partido.assign(
                frase_temas=dados_partido.apply(_frase_de_temas, axis=1),
                frase_eficacia=dados_partido.apply(_frase_de_eficacia, axis=1),
            )[["nome", "sgUF", "sgPartido", "quadrante", "ranking",
               "frase_temas", "frase_eficacia"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b> (%{customdata[1]}-%{customdata[2]})<br>" +
                "🔹 <b>Quadrante:</b> %{customdata[3]}<br>" +
                "🥇 <b>Ranking:</b> %{customdata[4]}º<br>" +
                "📈 <b>Produtividade:</b> %{x:.1f}<br>" +
                "💰 <b>Gasto ajustado:</b> R$ %{y:,.2f}<br><br>" +
                "%{customdata[5]}<br>" +
                "%{customdata[6]}" +
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
            showarrow=False,
            yshift=15
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
