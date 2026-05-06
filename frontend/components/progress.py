import streamlit as st

from backend.core.logs import ler_log
from backend.core.progress import calcular_progresso
from backend.core.state import processo_rodando


def mostrar_progresso_etapa(nome_etapa):
    if processo_rodando() and st.session_state.etapa == nome_etapa:
        log_texto = ler_log(st.session_state.log_atual)
        progresso = calcular_progresso(log_texto)

        st.progress(progresso / 100)
        st.caption(f"Executando... {progresso}%")