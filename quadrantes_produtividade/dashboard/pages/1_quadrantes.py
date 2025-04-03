import streamlit as st
import pandas as pd
from graficos import grafico_quadrantes_interativo
from settings import INDICADORES_PATH

st.set_page_config(page_title="Quadrantes da Produtividade", layout="wide")
st.title("📊 Quadrantes da Produtividade Legislativa")
st.markdown("""
Este dashboard apresenta os Quadrantes da Produtividade Legislativa, uma proposta de visualização que avalia os deputados federais da 57ª legislatura (2023–2026).
            
Este gráfico interativo posiciona cada deputado federal de acordo com dois eixos:

- **Eixo X:** Pontuação de produtividade legislativa, calculada a partir do número e relevância das proposições apresentadas, com pesos diferenciados por tipo (ex: PECs, PLs, PLPs). Cada proposição recebe um peso e os autores acumulam pontos conforme sua participação.
- **Eixo Y:** Gasto ajustado com a cota parlamentar (CEAP), considera os valores pagos com a Cota para o Exercício da Atividade Parlamentar (CEAP), excluindo despesas com passagens aéreas para Brasília.

As **linhas tracejadas** indicam as medianas de produtividade e gasto, dividindo o gráfico em quatro quadrantes:

1. 🟢 **Alta produtividade e baixo custo**
2. 🔴 **Baixa produtividade e alto custo**
3. 🟡 **Alta produtividade e alto custo**
4. ⚫ **Baixa produtividade e baixo custo**

### 🧑‍💻 Como explorar:
- **Passe o mouse sobre os pontos** para ver o mini perfil do deputado.
- **Clique nas legendas dos partidos** para filtrar a visualização.
- **Use os filtros acima** para focar por estado (UF).
- Abaixo, veja o **ranking completo** dos parlamentares.
""")


# Carregamento dos dados
df = pd.read_csv(INDICADORES_PATH)

# Filtros interativos
col1 = st.columns(1)[0]
ufs = sorted(df["sgUF"].dropna().unique())
filtro_uf = col1.multiselect("Filtrar por UF:", ufs, default=ufs)

# Aplicar filtros
df_filtrado = df[
    (df["sgUF"].isin(filtro_uf))
]

if df_filtrado.empty:
    st.warning("Nenhum deputado encontrado com os filtros selecionados.")
    st.stop()

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
ranking_df["Gasto CEAP Ajustado (R$)"] = ranking_df["Gasto CEAP Ajustado (R$)"].apply(
    lambda x: f"R$ {x:,.0f}".replace(",", ".")
)

# Exibe tabela
st.dataframe(ranking_df, use_container_width=True, height=600)
