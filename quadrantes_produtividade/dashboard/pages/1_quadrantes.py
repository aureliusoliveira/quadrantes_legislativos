import streamlit as st
from utils.carregamento import carregar_dados
from graficos import grafico_quadrantes_interativo
from utils.perfis import gerar_mini_perfil_legislativo, gerar_perfil_detalhado

st.title("📊 Quadrantes da Produtividade Legislativa")

# Carregamento dos dados
dados = carregar_dados()
df = dados["resultados"]

# Gráfico interativo
fig = grafico_quadrantes_interativo(df)
st.plotly_chart(fig, use_container_width=True)

# CAPTURA DE INTERAÇÕES (hover e click)
hover_data = st.session_state.get("hoverData")
click_data = st.session_state.get("clickData")

# HoverData — não usado diretamente por st.plotly_chart
if hover_data and "points" in hover_data:
    nome = hover_data["points"][0]["customdata"][0]
    st.caption(f"🖱️ Passando o mouse sobre: {nome}")

# ClickData — detalhamento
if click_data and "points" in click_data:
    ponto = click_data["points"][0]
    nome = ponto["customdata"][0]
    partido = ponto["customdata"][1]
    uf = ponto["customdata"][2]

    id_dep = df[
        (df["nome"] == nome) & (df["siglaPartido"] == partido) & (df["siglaUf"] == uf)
    ]["idDeputado"].values[0]

    st.markdown("---")
    st.subheader(f"👤 Detalhamento: {nome} ({partido}-{uf})")

    perfil = gerar_perfil_detalhado(id_dep, dados)
    st.markdown(perfil)
