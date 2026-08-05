# dashboard/app.py — página única: entrypoint do Streamlit Cloud e a visualização.
import pandas as pd
import streamlit as st
from graficos import grafico_quadrantes_interativo
from settings import INDICADORES_PATH

st.set_page_config(
    page_title="Quadrantes da Produtividade Legislativa",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("📊 Quadrantes da Produtividade Legislativa")

st.markdown("""
Cruza **quanto um deputado federal custa** com **quanto ele produz**, e posiciona
os parlamentares da 57ª legislatura (2023–2026) em quatro quadrantes.

Tudo vem dos [dados abertos da Câmara](https://dadosabertos.camara.leg.br/):
proposições de autoria, tramitação e a cota parlamentar (CEAP). Nenhum número
exibido aqui é digitado à mão — todos são reproduzíveis do dado bruto ao gráfico.
""")

esquerda, direita = st.columns(2)

with esquerda:
    st.subheader("O que isto mede")
    st.markdown("""
    - **Produtividade:** proposições de autoria, com pesos por tipo — uma PEC
      não vale o mesmo que um requerimento.
    - **Custo:** gasto CEAP, descontadas as passagens aéreas envolvendo Brasília,
      que penalizariam deputados de estados distantes.
    - **Quadrantes:** as linhas tracejadas são as **medianas** de cada eixo, e
      dividem os parlamentares em alta ou baixa produtividade, com alto ou baixo
      custo.
    """)

with direita:
    st.subheader("O que isto **não** mede")
    st.markdown("""
    - **Qualidade legislativa.** Volume não é mérito: apresentar muitos projetos
      ruins pontua bem aqui.
    - **Ética ou conduta.** Gasto dentro da cota é gasto legal.
    - **Trabalho invisível.** Relatoria, articulação, comissão e emenda não
      entram na contagem.
    """)

st.warning(
    "**Projeto em construção — os números estão em validação.** Alguns deputados "
    "aparecem com gasto CEAP implausivelmente baixo, o que sugere dado ausente "
    "sendo lido como gasto zero — e dado ausente vira posição de destaque no "
    "gráfico. As taxas de tramitação refletem a data da coleta, não o estado "
    "atual das proposições. As limitações conhecidas estão listadas abertamente "
    "no repositório; não cite estes números como definitivos.",
    icon="🚧",
)

df = pd.read_csv(INDICADORES_PATH, sep=";", encoding="utf-8")

# A coluna `ranking` do CSV é o ranking composto (produtividade + gasto) que o
# pipeline calcula. A página publica produtividade pura, então recalcula aqui em
# vez de usar a coluna — compor os dois eixos numa nota única exigiria arbitrar
# quanto um real vale em proposição, e essa decisão ainda não foi tomada.
# Até a consolidação dos repositórios isso acontecia dentro de
# grafico_quadrantes_interativo(), que mutava o DataFrame do chamador in-place.
df["ranking"] = (
    df["produtividade_legislativa"].rank(ascending=False, method="min").astype(int)
)

st.plotly_chart(grafico_quadrantes_interativo(df), width="stretch")
st.caption(
    "Passe o mouse sobre os pontos para ver o mini perfil do deputado. "
    "Clique nas legendas dos partidos para isolar ou esconder bancadas."
)

st.markdown("### 🏆 Ranking Parlamentar")
st.caption("Ordenado **apenas por produtividade legislativa** — o gasto é o segundo eixo do gráfico, não entra na posição.")

ranking_df = (
    df.sort_values("ranking")
    .reset_index(drop=True)[
        [
            "ranking",
            "nome",
            "sgPartido",
            "sgUF",
            "produtividade_legislativa",
            "gasto_ceap_ajustado",
        ]
    ]
    .rename(
        columns={
            "ranking": "Ranking",
            "nome": "Deputado",
            "sgPartido": "Partido",
            "sgUF": "UF",
            "produtividade_legislativa": "Produtividade",
            "gasto_ceap_ajustado": "Gasto CEAP Ajustado (R$)",
        }
    )
)

st.dataframe(ranking_df, width="stretch", height=600)

st.divider()
st.markdown(
    "Metodologia, limitações e código: "
    "[github.com/aureliusoliveira/quadrantes_legislativos]"
    "(https://github.com/aureliusoliveira/quadrantes_legislativos)"
)
