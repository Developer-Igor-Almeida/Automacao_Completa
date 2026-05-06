import os
import shutil
import subprocess
import sys

import streamlit as st

from backend.core.paths import (TRACERS,MIND7,LOG_TRACERS,LOG_MIND7, EXCEL_TRACERS, EXCEL_MIND7, RESULTADO, SCRIPT_TRACERS,SCRIPT_MIND7,BAT_CHROME_MIND7,)
from backend.core.state import processo_rodando, icone_status
from backend.services.process_service import iniciar_processo
from frontend.components.progress import mostrar_progresso_etapa


def render_steps():
    _render_continuar_apos_erro()

    col_esq, col_dir = st.columns(2)

    with col_esq:
        _render_etapa_tracers()
        _render_etapa_envio_mind7()

    with col_dir:
        _render_etapa_chrome()
        _render_etapa_consulta_mind7()

    st.divider()


def _render_continuar_apos_erro():
    if not st.session_state.erro_pausado:
        return

    if st.button("▶️ Continuar após correção", type="primary"):
        st.session_state.erro_pausado = False
        st.session_state.mensagem_erro_pausado = ""
        st.session_state.etapa_tracers_erro = False
        st.session_state.tracers_iniciado = True

        iniciar_processo(
            [sys.executable, "-u", str(SCRIPT_TRACERS)],
            TRACERS,
            LOG_TRACERS,
            "Extração de placas do Tracers",
        )

        st.rerun()


def _render_etapa_tracers():
    st.subheader("1. Extrair placas do Tracers")

    if not SCRIPT_TRACERS.exists():
        st.error(f"Arquivo extrair_tracers.py não encontrado em:\n{SCRIPT_TRACERS}")
        return

    texto_botao_tracers = (
        "▶️ Iniciar extração de placas"
        + icone_status(
            st.session_state.etapa_tracers_ok,
            st.session_state.etapa_tracers_erro,
        )
    )

    if st.button(texto_botao_tracers, disabled=processo_rodando()):
        st.session_state.etapa_tracers_ok = False
        st.session_state.etapa_tracers_erro = False
        st.session_state.erro_pausado = False
        st.session_state.mensagem_erro_pausado = ""
        st.session_state.tracers_iniciado = True

        iniciar_processo(
            [sys.executable, "-u", str(SCRIPT_TRACERS)],
            TRACERS,
            LOG_TRACERS,
            "Extração de placas do Tracers",
        )

        st.rerun()

    mostrar_progresso_etapa("Extração de placas do Tracers")


def _render_etapa_envio_mind7():
    st.subheader("2. Enviar Excel para Mind7")

    texto_botao_envio = (
        "📤 Copiar arquivo para Mind7"
        + icone_status(
            st.session_state.etapa_envio_ok,
            st.session_state.etapa_envio_erro,
        )
    )

    if not st.session_state.etapa_tracers_ok:
        st.info("Conclua a etapa 1 primeiro.")

    if not EXCEL_TRACERS.exists():
        st.info("Execute a extração de placas primeiro.")
        return

    if st.button(
        texto_botao_envio,
        disabled=processo_rodando() or not st.session_state.etapa_tracers_ok,
    ):
        try:
            shutil.copy2(EXCEL_TRACERS, EXCEL_MIND7)
            st.session_state.etapa_envio_ok = True
            st.session_state.etapa_envio_erro = False
            st.success("Arquivo copiado para entrada do Mind7.")
            st.rerun()

        except Exception as e:
            st.session_state.etapa_envio_ok = False
            st.session_state.etapa_envio_erro = True
            st.error(f"Erro ao copiar arquivo: {e}")


def _render_etapa_chrome():
    st.subheader("3. Abrir Chrome Mind7")

    texto_botao_chrome = (
        "🌐 Abrir Chrome para login"
        + icone_status(
            st.session_state.etapa_chrome_ok,
            st.session_state.etapa_chrome_erro,
        )
    )

    if not st.session_state.etapa_envio_ok:
        st.info("Conclua a etapa 2 primeiro.")

    if not BAT_CHROME_MIND7.exists():
        st.error(f"Arquivo abrir_chrome_mind7.bat não encontrado em:\n{BAT_CHROME_MIND7}")
        return

    if st.button(
        texto_botao_chrome,
        disabled=processo_rodando() or not st.session_state.etapa_envio_ok,
    ):
        try:
            if os.name == "nt":
                subprocess.Popen(
                    ["cmd", "/c", str(BAT_CHROME_MIND7)],
                    cwd=str(MIND7),
                    shell=False,
                )
            else:
                subprocess.Popen(
                    [str(BAT_CHROME_MIND7)],
                    cwd=str(MIND7),
                    shell=False,
                )

            st.session_state.etapa_chrome_ok = True
            st.session_state.etapa_chrome_erro = False
            st.success("Chrome aberto. Faça login no Mind7.")
            st.rerun()

        except Exception as e:
            st.session_state.etapa_chrome_ok = False
            st.session_state.etapa_chrome_erro = True
            st.error(f"Erro ao abrir Chrome: {e}")


def _render_etapa_consulta_mind7():
    st.subheader("4. Buscar CPFs/CNPJs")

    texto_botao_consulta = (
        "🔎 Iniciar consulta no Mind7"
        + icone_status(
            st.session_state.etapa_consulta_ok,
            st.session_state.etapa_consulta_erro,
        )
    )

    if not st.session_state.etapa_chrome_ok:
        st.info("Conclua a etapa 3 primeiro.")

    if not SCRIPT_MIND7.exists():
        st.error(f"Arquivo consultar_mind7.py não encontrado em:\n{SCRIPT_MIND7}")
        return

    if not EXCEL_MIND7.exists():
        st.info("Copie o Excel para o Mind7 primeiro.")
        return

    if st.button(
        texto_botao_consulta,
        disabled=processo_rodando() or not st.session_state.etapa_chrome_ok,
    ):
        st.session_state.etapa_consulta_ok = False
        st.session_state.etapa_consulta_erro = False
        st.session_state.consulta_iniciada = True

        iniciar_processo(
            [sys.executable, "-u", str(SCRIPT_MIND7)],
            MIND7,
            LOG_MIND7,
            "Consulta de CPFs/CNPJs no Mind7",
        )

        st.rerun()

    mostrar_progresso_etapa("Consulta de CPFs/CNPJs no Mind7")