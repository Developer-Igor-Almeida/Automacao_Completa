import streamlit as st

from backend.core.paths import EXCEL_TRACERS, EXCEL_MIND7, RESULTADO
from backend.core.state import processo_rodando


def render_metrics():
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Arquivo Tracers", "OK" if EXCEL_TRACERS.exists() else "Pendente")

    with col2:
        st.metric("Entrada Mind7", "OK" if EXCEL_MIND7.exists() else "Pendente")

    with col3:
        st.metric("Resultado Final", "OK" if RESULTADO.exists() else "Pendente")

    with col4:
        st.metric("Status", "Rodando" if processo_rodando() else "Parado")

    st.divider()