import streamlit as st

from backend.core.logs import ler_log, limpar_logs, corrigir_acentos_log
from backend.core.progress import calcular_progresso
from backend.core.state import processo_rodando
from backend.services.message_service import mensagem_amigavel_por_etapa


def render_logs_panel():
    st.subheader("📊 Progresso em tempo real")

    log_texto = ler_log(st.session_state.log_atual)
    progresso = calcular_progresso(log_texto)

    st.progress(progresso / 100)
    st.write(f"Progresso estimado: **{progresso}%**")

    st.subheader("📜 Logs organizados")

    col_log1, col_log2, _ = st.columns([1, 1, 4])

    with col_log1:
        if st.button("🧹 Limpar logs", disabled=processo_rodando()):
            limpar_logs()
            st.session_state.log_atual = None
            st.success("Logs limpos com sucesso!")
            st.rerun()

    with col_log2:
        if st.button("🔄 Atualizar logs"):
            st.rerun()

    with st.expander("Status da execução", expanded=True):
        log_texto_corrigido = corrigir_acentos_log(
            ler_log(st.session_state.log_atual)
        )

        mensagem = mensagem_amigavel_por_etapa(
            st.session_state.etapa,
            log_texto_corrigido,
        )

        if mensagem:
            st.info(mensagem)
        elif log_texto_corrigido:
            st.success("Processo em andamento ou finalizado sem erro crítico.")
        else:
            st.info("Nenhum processo iniciado ainda.")

    with st.expander("Logs técnicos para suporte", expanded=False):
        log_texto_corrigido = corrigir_acentos_log(
            ler_log(st.session_state.log_atual)
        )

        if log_texto_corrigido:
            st.code(log_texto_corrigido[-8000:])
        else:
            st.info("Nenhum log técnico disponível.")

    st.divider()