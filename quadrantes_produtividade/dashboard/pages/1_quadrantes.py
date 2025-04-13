import streamlit as st
import pandas as pd
from graficos import grafico_quadrantes_interativo
from settings import INDICADORES_PATH

st.set_page_config(page_title="Quadrantes da Produtividade", layout="wide")
st.title("📊 Quadrantes da Produtividade Legislativa")
st.markdown("""
Este dashboard apresenta os Quadrantes da Produtividade Legislativa, uma proposta de visualização que avalia os deputados federais da 57ª legislatura (2023–2026).

🧠 Como construímos o ranking parlamentar?
O ranking de produtividade legislativa foi definido com base em dois critérios principais:

Produtividade legislativa

Gasto ajustado com o mandato

Cada um desses critérios gerou um ranking independente: um ordenando os deputados do mais ao menos produtivo, outro do que menos gastou para o que mais gastou.
A pontuação final foi calculada a partir da composição desses dois rankings, resultando em uma média que define a posição de cada parlamentar no ranking geral.

📈 Produtividade legislativa
Leva em conta:

A quantidade e o tipo de proposições apresentadas (com pesos diferentes por relevância)

Os temas mais frequentes de atuação

A situação das proposições (em tramitação, aprovadas ou rejeitadas)

💰 Gasto ajustado com o mandato
Consideramos o total gasto com a cota parlamentar (CEAP), mas excluímos as despesas com passagens aéreas envolvendo Brasília, já que são comuns a todos os mandatos. Isso torna a comparação mais justa entre deputados de diferentes estados.

🟦 Os Quadrantes
Com base nos valores medianos de produtividade e gasto, os parlamentares são distribuídos em quatro quadrantes:

Alta produtividade e baixo custo

Alta produtividade e alto custo

Baixa produtividade e baixo custo

Baixa produtividade e alto custo
            

### 🧑‍💻 Como explorar:
- **Passe o mouse sobre os pontos** para ver o mini perfil do deputado.
- **Clique nas legendas dos partidos** para filtrar a visualização.
- Abaixo, veja o **ranking completo** dos parlamentares.
""")


# Carregamento dos dados
df = pd.read_csv(INDICADORES_PATH, sep=";", encoding="utf-8")

# Filtros interativos
#col1 = st.columns(1)[0]
#ufs = sorted(df["sgUF"].dropna().unique())
#filtro_uf = col1.multiselect("Filtrar por UF:", ufs, default=ufs)

# Aplicar filtros
#df_filtrado = df[
#    (df["sgUF"].isin(filtro_uf))
#]

#if df_filtrado.empty:
#    st.warning("Nenhum deputado encontrado com os filtros selecionados.")
#    st.stop()

# Gráfico interativo
fig = grafico_quadrantes_interativo(df_filtrado)
st.plotly_chart(fig, use_container_width=True)

# Ranking
st.markdown("### 🏆 Ranking Parlamentar")
ranking_df = df_filtrado.sort_values("ranking").reset_index(drop=True)

# Seleciona colunas úteis para exibição
colunas_exibidas = [
    "ranking", "nome", "sgPartido", "sgUF",
    "produtividade_legislativa", "gasto_ceap_ajustado"
]

# Renomeia colunas para legibilidade
ranking_df = ranking_df[colunas_exibidas].rename(columns={
    "ranking": "Ranking",
    "nome": "Deputado",
    "sgPartido": "Partido",
    "sgUF": "UF",
    "produtividade_legislativa": "Produtividade",
    "gasto_ceap_ajustado": "Gasto CEAP Ajustado (R$)"
})

# Formata valores de gasto
#ranking_df["Gasto CEAP Ajustado (R$)"] = ranking_df["Gasto CEAP Ajustado (R$)"].apply(
#    lambda x: f"R$ {x:,.0f}".replace(",", ".")
#)

# Exibe tabela
st.dataframe(ranking_df, use_container_width=True, height=600)
