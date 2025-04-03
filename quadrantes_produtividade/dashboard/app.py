# dashboard/app.py
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Quadrantes da Produtividade Legislativa",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Quadrantes da Produtividade Legislativa")
st.markdown("Selecione uma página no menu lateral para começar.")

st.sidebar.success("Escolha uma aba acima ☝️")
