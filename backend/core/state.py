"""
Gerenciamento de estado da aplicação.
Responsável por:
- inicializar session_state
- controlar status da automação
- persistir estados visuais
- controlar execução dos processos
"""

import streamlit as st
from backend.constants.ui import STATUS_ICONS
from backend.core.paths import (TRACERS_EXCEL_FILE,MIND7_INPUT_EXCEL_FILE,FINAL_RESULT_FILE,)

INITIAL_SESSION_STATE = {
    "process": None,
    "current_step": "",
    "current_log_file": None,
    "monitor_started": False,
    "is_paused_by_error": False,
    "paused_error_message": "",
    "tracers_step_completed": False,
    "send_step_completed": False,
    "chrome_step_completed": False,
    "consultation_step_completed": False,
    "tracers_step_error": False,
    "send_step_error": False,
    "chrome_step_error": False,
    "consultation_step_error": False,
    "tracers_started": False,
    "consultation_started": False,
}

FILE_STATE_SYNC_RULES = [
    {
        "file": TRACERS_EXCEL_FILE,
        "error_key": "tracers_step_error",
        "completed_key": "tracers_step_completed",
    },
    {
        "file": MIND7_INPUT_EXCEL_FILE,
        "error_key": "send_step_error",
        "completed_key": "send_step_completed",
    },
    {
        "file": FINAL_RESULT_FILE,
        "error_key": "consultation_step_error",
        "completed_key": "consultation_step_completed",
    },
]

STEP_STATE_PREFIXES = {
    "tracers": "tracers",
    "send": "send",
    "chrome": "chrome",
    "consultation": "consultation",
}


def initialize_session_state() -> None:
    for key, value in INITIAL_SESSION_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value

def is_process_running() -> bool:
    process = st.session_state.process
    return process is not None and process.poll() is None

def get_status_icon(success: bool, error: bool) -> str:
    if success:
        return STATUS_ICONS["success"]

    if error:
        return STATUS_ICONS["error"]

    return STATUS_ICONS["pending"]

def sync_state_with_existing_files() -> None:
    """
    Mantém o estado visual correto caso os arquivos
    já existam após reiniciar o Streamlit.
    """

    for rule in FILE_STATE_SYNC_RULES:
        file_exists = rule["file"].exists()
        has_error = st.session_state[rule["error_key"]]

        if file_exists and not has_error:
            st.session_state[rule["completed_key"]] = True

def set_step_status(step_name: str,completed: bool | None = None,error: bool | None = None,) -> None:
    """
    Atualiza os estados visuais de uma etapa.
    """
    prefix = STEP_STATE_PREFIXES[step_name]
    
    if completed is not None:
        st.session_state[f"{prefix}_step_completed"] = completed

    if error is not None:
        st.session_state[f"{prefix}_step_error"] = error