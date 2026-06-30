import streamlit as st

st.set_page_config(
    page_title="Desigualdade Educacional no Brasil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Redireciona automaticamente para a página de Visão Geral
st.switch_page("pages/01_visao_geral.py")
