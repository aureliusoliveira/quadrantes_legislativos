# dashboard/app.py — página única: entrypoint do Streamlit Cloud e a visualização.
import pandas as pd
import streamlit as st
from graficos import grafico_quadrantes_interativo
from settings import DIAGRAMA_QUADRANTES, INDICADORES_PATH

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
    - **Quadrantes:** as linhas tracejadas são as **medianas** de cada eixo. O
      diagrama abaixo explica como ler cada canto.
    """)

with direita:
    st.subheader("O que isto **não** mede")
    st.markdown("""
    - **Qualidade legislativa.** Volume não é mérito: apresentar muitos projetos
      ruins pontua bem aqui.
    - **Ética ou conduta.** Gasto dentro da cota é gasto legal.
    - **Trabalho invisível.** Relatoria, articulação, comissão e emenda não
      entram na contagem.
    - **Tempo de mandato.** Não há normalização: quem serviu oito meses é
      comparado com quem serviu quatro anos.
    """)

st.warning(
    "**Projeto em construção. Os números estão em validação.** Quem entra neste "
    "ranking é decidido pelo estado de hoje: dos 647 parlamentares que exerceram "
    "mandato na 57ª legislatura, 508 aparecem aqui, porque a base filtra por "
    "quem ocupa a cadeira no momento da coleta. Mandato parcial é comparado com "
    "mandato inteiro, sem normalização por tempo. As taxas de tramitação "
    "refletem a data da coleta, não o estado atual das proposições. As "
    "limitações estão listadas abertamente no repositório; não cite estes "
    "números como definitivos.",
    icon="🚧",
)

with st.expander("⚖️ Este projeto tem viés. Qual é."):
    st.markdown("""
Não existe métrica neutra de trabalho legislativo. Escolher o que conta como
produção é decisão de valor, e ela foi tomada por uma pessoa: os pesos por tipo
de proposição não vêm de tabela oficial nem de consenso acadêmico. São juízo do
autor, e estão num arquivo aberto que qualquer pessoa pode contestar e refazer.

O viés declarado é a **democracia e a transparência**: gasto público deve ser
rastreável e metodologia deve ser auditável até o dado bruto.

Apresentar um índice como objetivo seria esconder as decisões tomadas para
construí-lo. Este painel não entrega veredito sobre parlamentar nenhum. Entrega
um instrumento, e a lista honesta do que ele não consegue ver.
""")

# A coluna `ranking` vem pronta do pipeline e é a composta. A página já a
# recalculou aqui como produtividade pura, o que descartava metade do método
# sem dizer a ninguém; a regra de negócio mora em legisdata, não nesta camada.
df = pd.read_csv(INDICADORES_PATH, sep=";", encoding="utf-8")

# Tamanho natural, não "stretch": o diagrama é vetor, e esticá-lo até a largura
# da página ampliaria a tipografia junto, comendo a tela antes do gráfico.
st.image(str(DIAGRAMA_QUADRANTES), width="content")

st.plotly_chart(grafico_quadrantes_interativo(df), width="stretch")
st.caption(
    "Passe o mouse sobre os pontos para ver o mini perfil do deputado. "
    "Clique nas legendas dos partidos para isolar ou esconder bancadas."
)

st.markdown("### 🏆 Ranking Parlamentar")
st.caption(
    "As **duas dimensões** entram na posição. Cada eixo é ordenado por conta "
    "própria (mais produtivo primeiro, menor gasto primeiro), e o que se soma "
    "são as duas posições: quanto menor a soma, melhor o lugar. Somar posições "
    "e não valores evita ter que arbitrar quanto um real vale em proposição, "
    "mas assume que os dois eixos pesam igual e descarta a magnitude da "
    "diferença. As colunas de posição por eixo estão na tabela para você "
    "refazer a conta."
)

ranking_df = (
    df.sort_values("ranking")
    .reset_index(drop=True)[
        [
            "ranking",
            "nome",
            "sgPartido",
            "sgUF",
            "ranking_leg",
            "ranking_gastos",
            "produtividade_legislativa",
            "gasto_ceap_ajustado",
        ]
    ]
    .rename(
        columns={
            "ranking": "Ranking",
            "nome": "Deputado",
            "ranking_leg": "Pos. produtividade",
            "ranking_gastos": "Pos. gasto",
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
