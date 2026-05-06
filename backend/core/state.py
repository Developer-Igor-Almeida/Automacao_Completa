import streamlit as st
from backend.core.paths import EXCEL_TRACERS, EXCEL_MIND7, RESULTADO

VALORES_INICIAIS = {
    "processo": None,
    "etapa": "",
    "log_atual": None,
    "monitor_iniciado": False,
    "erro_pausado": False,
    "mensagem_erro_pausado": "",
    "etapa_tracers_ok": False,
    "etapa_envio_ok": False,
    "etapa_chrome_ok": False,
    "etapa_consulta_ok": False,
    "etapa_tracers_erro": False,
    "etapa_envio_erro": False,
    "etapa_chrome_erro": False,
    "etapa_consulta_erro": False,
    "tracers_iniciado": False,
    "consulta_iniciada": False,
}


def inicializar_estado():
    for chave, valor in VALORES_INICIAIS.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


def processo_rodando():
    p = st.session_state.processo
    return p is not None and p.poll() is None


def icone_status(ok, erro):
    if ok:
        return " ✅"
    if erro:
        return " ❌"
    return ""

def sincronizar_estado_por_arquivos():
    """Mantém o app utilizável após refresh/restart quando os arquivos já existem."""
    if EXCEL_TRACERS.exists() and not st.session_state.etapa_tracers_erro:
        st.session_state.etapa_tracers_ok = True

    if EXCEL_MIND7.exists() and not st.session_state.etapa_envio_erro:
        st.session_state.etapa_envio_ok = True

    if RESULTADO.exists() and not st.session_state.etapa_consulta_erro:
        st.session_state.etapa_consulta_ok = True
