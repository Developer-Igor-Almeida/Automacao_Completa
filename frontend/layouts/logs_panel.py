"""
Painel visual de progresso e logs da automação.

Responsável por:
- exibir progresso estimado
- exibir mensagens amigáveis
- exibir logs técnicos
- permitir limpeza/atualização dos logs
"""

import streamlit as st

from backend.core.logs import (clear_logs,fix_broken_text_encoding,read_log,)
from backend.core.progress import calculate_progress
from backend.core.state import is_process_running
from backend.services.message_service import get_friendly_message_by_step


def render_logs_panel() -> None:
    _render_progress()
    _render_logs_actions()
    _render_execution_status()
    _render_technical_logs()

    st.divider()

def _render_progress() -> None:
    st.subheader("📊 Progresso em tempo real")

    log_text = read_log(st.session_state.current_log_file)
    progress = calculate_progress(log_text)

    st.progress(progress / 100)
    st.write(f"Progresso estimado: **{progress}%**")

def _render_logs_actions() -> None:
    st.subheader("📜 Logs organizados")

    col_log1, col_log2, _ = st.columns([1, 1, 4])

    with col_log1:
        if st.button("🧹 Limpar logs", disabled=is_process_running()):
            clear_logs()
            st.session_state.current_log_file = None
            st.success("Logs limpos com sucesso!")
            st.rerun()

    with col_log2:
        if st.button("🔄 Atualizar logs"):
            st.rerun()

def _render_execution_status() -> None:
    with st.expander("Status da execução", expanded=True):
        fixed_log_text = _get_fixed_current_log_text()

        message = get_friendly_message_by_step(st.session_state.current_step,fixed_log_text,)

        if message:
            st.info(message)
            return

        if fixed_log_text:
            st.success("Processo em andamento ou finalizado sem erro crítico.")
            return

        st.info("Nenhum processo iniciado ainda.")

def _render_technical_logs() -> None:
    with st.expander("Logs técnicos para suporte", expanded=False):
        fixed_log_text = _get_fixed_current_log_text()

        if fixed_log_text:
            st.code(fixed_log_text[-8000:])
            return

        st.info("Nenhum log técnico disponível.")

def _get_fixed_current_log_text() -> str:
    log_text = read_log(st.session_state.current_log_file)
    return fix_broken_text_encoding(log_text)