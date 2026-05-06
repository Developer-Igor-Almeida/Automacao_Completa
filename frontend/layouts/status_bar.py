import streamlit as st

from backend.core.state import processo_rodando
from backend.services.process_service import parar_processo


def render_status_bar():
    if processo_rodando():
        st.warning(f"Processo em execução: {st.session_state.etapa}")

        if st.button("🛑 PARAR AUTOMAÇÃO", type="primary"):
            parar_processo()
            st.error("Automação interrompida.")
            st.rerun()
    else:
        st.success("Nenhuma automação em execução no momento.")

    if st.session_state.erro_pausado:
        st.error(st.session_state.mensagem_erro_pausado)

    st.divider()