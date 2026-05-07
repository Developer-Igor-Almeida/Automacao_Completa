"""
Layout das etapas da automação.

Responsável por:
- exibir os botões das etapas
- validar pré-requisitos visuais
- acionar serviços de automação
"""

import sys
import streamlit as st

from backend.constants.process import TRACERS_STEP_NAME, MIND7_STEP_NAME
from backend.core.paths import (TRACERS_DIR,MIND7_DIR,TRACERS_LOG_FILE, MIND7_LOG_FILE,TRACERS_EXCEL_FILE, 
 MIND7_INPUT_EXCEL_FILE,TRACERS_SCRIPT,MIND7_SCRIPT,MIND7_CHROME_BAT,)
from backend.constants.messages import (CHROME_OPENED_SUCCESS_MESSAGE,COPY_EXCEL_FIRST_MESSAGE,FILE_COPIED_SUCCESS_MESSAGE, FINISH_STEP_1_FIRST_MESSAGE,
 FINISH_STEP_2_FIRST_MESSAGE, FINISH_STEP_3_FIRST_MESSAGE, OPEN_CHROME_BUTTON_LABEL, RUN_TRACERS_FIRST_MESSAGE,SEND_TO_MIND7_BUTTON_LABEL,
    START_MIND7_CONSULTATION_BUTTON_LABEL, TRACERS_START_BUTTON_LABEL,)
from backend.core.state import is_process_running, get_status_icon
from backend.services.process_service import start_process
from frontend.components.progress import render_step_progress
from backend.services.file_service import copy_file
from backend.services.chrome_service import open_chrome_bat

def render_steps() -> None:
    _render_continue_after_error()
    left_column, right_column = st.columns(2)

    with left_column:
        _render_tracers_step()
        _render_send_to_mind7_step()

    with right_column:
        _render_chrome_step()
        _render_mind7_consultation_step()

    st.divider()

def _render_continue_after_error() -> None:
    if not st.session_state.is_paused_by_error:
        return

    if st.button("▶️ Continuar após correção", type="primary"):
        st.session_state.is_paused_by_error = False
        st.session_state.paused_error_message = ""
        st.session_state.tracers_step_error = False
        st.session_state.tracers_started = True
        start_process([sys.executable, "-u", str(TRACERS_SCRIPT)],TRACERS_DIR,TRACERS_LOG_FILE,TRACERS_STEP_NAME,)
        st.rerun()

def _render_tracers_step() -> None:
    st.subheader("1. Extrair placas do Tracers")

    if not TRACERS_SCRIPT.exists():
        st.error(f"Arquivo extrair_tracers.py não encontrado em:\n{TRACERS_SCRIPT}")
        return

    button_text = (TRACERS_START_BUTTON_LABEL + get_status_icon(st.session_state.tracers_step_completed, st.session_state.tracers_step_error,))

    if st.button(button_text, disabled=is_process_running()):
        set_step_status("tracers",completed=False,error=False,)
        st.session_state.is_paused_by_error = False
        st.session_state.paused_error_message = ""
        st.session_state.tracers_started = True
        start_process([sys.executable, "-u", str(TRACERS_SCRIPT)], TRACERS_DIR,TRACERS_LOG_FILE, TRACERS_STEP_NAME,)
        st.rerun()

    render_step_progress(TRACERS_STEP_NAME)

def _render_send_to_mind7_step() -> None:
    st.subheader("2. Enviar Excel para Mind7")

    button_text = (SEND_TO_MIND7_BUTTON_LABEL + get_status_icon(st.session_state.send_step_completed,st.session_state.send_step_error,))

    if not st.session_state.tracers_step_completed:
        st.info("Conclua a etapa 1 primeiro.")

    if not TRACERS_EXCEL_FILE.exists():
        st.info("Execute a extração de placas primeiro.")
        return

    if st.button(button_text,disabled=is_process_running() or not st.session_state.tracers_step_completed,):
        try:
            copy_file(TRACERS_EXCEL_FILE, MIND7_INPUT_EXCEL_FILE)
            set_step_status("send",completed=True,error=False,)
            st.success("Arquivo copiado para entrada do Mind7.")
            st.rerun()

        except Exception as error:
            set_step_status("send",completed=False,error=True,)
            st.error(f"Erro ao copiar arquivo: {error}")

def _render_chrome_step() -> None:
    st.subheader("3. Abrir Chrome Mind7")
    button_text = (OPEN_CHROME_BUTTON_LABEL + get_status_icon(st.session_state.chrome_step_completed, st.session_state.chrome_step_error,))
    if not st.session_state.send_step_completed:
        st.info("Conclua a etapa 2 primeiro.")

    if not MIND7_CHROME_BAT.exists():
        st.error(f"Arquivo abrir_chrome_mind7.bat não encontrado em:\n{MIND7_CHROME_BAT}")
        return

    if st.button(button_text,disabled=is_process_running() or not st.session_state.send_step_completed,):
        try:
            open_chrome_bat(MIND7_CHROME_BAT, MIND7_DIR)
            set_step_status("chrome",completed=True,error=False,)
            st.success("Chrome aberto. Faça login no Mind7.")
            st.rerun()

        except Exception as error:
            set_step_status("chrome",completed=False,error=True,)
            st.error(f"Erro ao abrir Chrome: {error}")

def _render_mind7_consultation_step() -> None:
    st.subheader("4. Buscar CPFs/CNPJs")
    button_text = (START_MIND7_CONSULTATION_BUTTON_LABEL + get_status_icon(st.session_state.consultation_step_completed,st.session_state.consultation_step_error,))

    if not st.session_state.chrome_step_completed:
        st.info("Conclua a etapa 3 primeiro.")

    if not MIND7_SCRIPT.exists():
        st.error(f"Arquivo consultar_mind7.py não encontrado em:\n{MIND7_SCRIPT}")
        return

    if not MIND7_INPUT_EXCEL_FILE.exists():
        st.info("Copie o Excel para o Mind7 primeiro.")
        return

    if st.button(button_text,disabled=is_process_running() or not st.session_state.chrome_step_completed,):
        set_step_status("consultation",completed=False,error=False,)
        st.session_state.consultation_started = True
        start_process([sys.executable, "-u", str(MIND7_SCRIPT)],MIND7_DIR,MIND7_LOG_FILE,MIND7_STEP_NAME,)
        st.rerun()

    render_step_progress(MIND7_STEP_NAME)

