"""
Painel visual de logs da automação.

Responsável por:
- exibir mensagens amigáveis
- exibir logs técnicos
- permitir limpeza/atualização dos logs
"""

import streamlit as st

from backend.core.logs import (
    clear_logs,
    fix_broken_text_encoding,
    read_log,
)
from backend.core.state import is_process_running
from backend.services.message_service import (
    get_friendly_message_by_step,
)


def render_logs_panel() -> None:
    _render_logs_actions()
    _render_execution_status()
    _render_technical_logs()

    st.divider()


def _render_logs_actions() -> None:
    st.subheader("📜 Logs organizados")

    col_log1, col_log2, _ = st.columns([1, 1, 4])

    with col_log1:
        if st.button(
            "🧹 Limpar logs",
            disabled=is_process_running(),
        ):
            clear_logs()

            st.session_state.current_log_file = None

            st.success("Logs limpos com sucesso!")

            st.rerun()

    with col_log2:
        if st.button("🔄 Atualizar logs"):
            st.rerun()


def _render_execution_status() -> None:
    with st.expander(
        "Status da execução",
        expanded=True,
    ):
        fixed_log_text = _get_fixed_current_log_text()

        current_step = st.session_state.get(
            "current_step",
            "",
        )

        message = get_friendly_message_by_step(
            current_step,
            fixed_log_text,
        )

        if message:
            st.info(message)
            return

        if fixed_log_text:
            st.success(
                "Processo em andamento ou finalizado sem erro crítico."
            )
            return

        st.info("Nenhum processo iniciado ainda.")


def _render_technical_logs() -> None:
    with st.expander(
        "Logs técnicos para suporte",
        expanded=False,
    ):
        fixed_log_text = _get_fixed_current_log_text()

        if fixed_log_text:
            st.markdown(
                f"""
                <div style="
                    max-height: 420px;
                    overflow-y: auto;
                    overflow-x: auto;
                    background-color: #0e1117;
                    padding: 16px;
                    border-radius: 8px;
                    font-family: monospace;
                    white-space: pre;
                    font-size: 14px;
                ">{fixed_log_text}</div>
                """,
                unsafe_allow_html=True,
            )
            return

        st.info("Nenhum log técnico disponível.")


def _get_fixed_current_log_text() -> str:
    current_log_file = st.session_state.get(
        "current_log_file",
        None,
    )

    log_text = read_log(current_log_file)

    return fix_broken_text_encoding(log_text)