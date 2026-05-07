"""
Serviço de execução e monitoramento de processos.

Responsável por:
- iniciar subprocessos da automação
- encerrar processos filhos
- monitorar conexão ativa do Streamlit
- detectar finalização das etapas
- pausar a automação quando houver erro no Tracers
"""

import logging
import os
import subprocess
import threading
import time

import psutil
import streamlit as st

from backend.constants.errors import TRACERS_RUNTIME_ERRORS
from backend.constants.messages import (PROCESS_START_ERROR_MESSAGE,TRACERS_DISCONNECTED_MESSAGE,TRACERS_FRIENDLY_LOG_MESSAGE,TRACERS_FRIENDLY_LOG_TITLE,)
from backend.constants.process import (MIND7_STEP_NAME,MONITOR_CHECK_INTERVAL_SECONDS,MONITOR_INITIAL_DELAY_SECONDS,STEP_ERROR_STATE_KEYS,STREAMLIT_PORT,TRACERS_STEP_NAME,)
from backend.core.logs import (fix_broken_text_encoding, read_log,)
from backend.core.paths import (FINAL_RESULT_FILE,TRACERS_EXCEL_FILE,TRACERS_LOG_FILE,)
from backend.core.state import is_process_running

logger = logging.getLogger(__name__)

PROCESS_FINISH_HANDLERS = {
    TRACERS_STEP_NAME: lambda return_code, log_text: _handle_tracers_finished(return_code, log_text),
    MIND7_STEP_NAME: lambda return_code, log_text: _handle_mind7_finished(return_code),
}

def monitor_streamlit_connection(initial_delay: int = 20, check_interval: int = 10,) -> None:
    """
    Encerra a árvore de processos atual quando não houver conexão ativa
    no Streamlit.
    """
    time.sleep(initial_delay)

    while True:
        time.sleep(check_interval)

        try:
            has_active_connections = bool(_get_active_streamlit_connections())
        except Exception:
            logger.exception("Erro ao verificar conexões ativas do Streamlit")
            continue

        if not has_active_connections:
            _terminate_current_process_tree()
            return

def start_connection_monitor() -> None:
    """
    Inicia o monitor de conexão do Streamlit apenas uma vez.
    """
    if st.session_state.monitor_started:
        return
    monitor_thread = threading.Thread(target=monitor_streamlit_connection,daemon=True,name="streamlit-connection-monitor",)
    monitor_thread.start()
    st.session_state.monitor_started = True
    logger.info("Monitor de conexão iniciado")

def start_process(command: list[str],working_dir,log_file_path,step_name: str,) -> None:
    """
    Inicia um subprocesso da automação e registra o processo
    no estado da aplicação.
    """
    try:
        _reset_log_file(log_file_path, step_name)
        process = _create_subprocess(command=command,working_dir=working_dir,log_file_path=log_file_path,)
        _save_process_state(process=process,step_name=step_name,log_file_path=log_file_path,)
        logger.info("Processo iniciado: %s", step_name)

    except Exception as error:
        logger.exception("Erro ao iniciar processo: %s", step_name)
        st.error(PROCESS_START_ERROR_MESSAGE.format(error=error))

def _create_subprocess(command, working_dir, log_file_path):
    log_file = open(log_file_path, "a", encoding="utf-8")
    return subprocess.Popen(command,cwd=str(working_dir),stdout=log_file,stderr=log_file,text=True,creationflags=_get_creation_flags(),env=_build_process_env(),)

def _save_process_state(process, step_name, log_file_path):
    st.session_state.process = process
    st.session_state.current_step = step_name
    st.session_state.current_log_file = log_file_path

def _get_creation_flags():
    return subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

def stop_process(mark_as_error: bool = True) -> None:
    """
    Encerra o processo atual e limpa o estado da execução.

    Por padrão, marca a etapa atual como erro, pois normalmente
    essa função é chamada quando o usuário interrompe a automação.
    """
    process = st.session_state.process

    if process and process.poll() is None:
        _terminate_process_tree(process)

    if mark_as_error:
        _mark_current_step_as_error()

    _clear_process_state()

def _clear_process_state() -> None:
    st.session_state.process = None
    st.session_state.current_step = ""

def detect_tracers_runtime_error(log_text: str) -> bool:
    """
    Verifica se o log contém erros que indicam problema
    com celular, ADB, UIAutomator ou app Tracers.
    """
    if not log_text:
        return False

    normalized_text = corrigir_acentos_log(log_text).lower()
    return any(error_pattern in normalized_text for error_pattern in TRACERS_RUNTIME_ERRORS)

def pause_tracers_due_to_error():
    stop_process()

    st.session_state.is_paused_by_error = True
    st.session_state.tracers_step_completed = False
    st.session_state.tracers_step_error = True

    st.session_state.paused_error_message = TRACERS_DISCONNECTED_MESSAGE

    _write_tracers_friendly_error_log()

def detect_process_finished() -> None:
    process = st.session_state.process
    current_step = st.session_state.current_step

    if process is None or process.poll() is None or not current_step:
        return

    return_code = process.returncode
    log_text = read_log(st.session_state.current_log_file)

    handler = PROCESS_FINISH_HANDLERS.get(current_step)

    if handler:
        handler(return_code, log_text)
    else:
        logger.warning("Etapa sem handler de finalização: %s", current_step)

    if not st.session_state.is_paused_by_error:
        _clear_process_state()

def monitor_realtime_errors() -> None:
    if not is_process_running():
        return

    if st.session_state.current_step != TRACERS_STEP_NAME:
        return

    log_text = read_log(st.session_state.current_log_file)

    if detect_tracers_runtime_error(log_text):
        pause_tracers_due_to_error()

def _clear_process_state() -> None:
    st.session_state.process = None
    st.session_state.current_step = ""

def _get_active_streamlit_connections() -> list:
    connections = psutil.net_connections(kind="inet")
    return [
        connection
        for connection in connections
        if connection.laddr
        and connection.laddr.port == STREAMLIT_PORT
        and connection.status == psutil.CONN_ESTABLISHED
    ]

def _terminate_children(parent_process: psutil.Process) -> None:
    for child in parent_process.children(recursive=True):
        try:
            child.terminate()
        except Exception:
            logger.exception("Erro ao encerrar processo filho")

def _terminate_current_process_tree() -> None:
    current_process = psutil.Process(os.getpid())
    _terminate_children(current_process)
    current_process.terminate()

def _terminate_process_tree(process: subprocess.Popen) -> None:
    try:
        parent_process = psutil.Process(process.pid)
        _terminate_children(parent_process)
        parent_process.terminate()

    except Exception:
        logger.exception("Erro ao encerrar árvore de processos")
        try:
            process.terminate()
        except Exception:
            logger.exception("Erro ao encerrar processo principal")

def _mark_current_step_as_error() -> None:
    error_key = STEP_ERROR_STATE_KEYS.get(st.session_state.current_step)
    if error_key:
        st.session_state[error_key] = True

def _reset_log_file(log_file_path, step_name):
    with open(log_file_path, "w", encoding="utf-8") as log_file:
        log_file.write(f"Iniciando etapa: {step_name}\n\n")

def _build_process_env() -> dict:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    return env

def _write_tracers_friendly_error_log() -> None:
    try:
        with open(TRACERS_LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write("\n\n==============================\n")
            log_file.write(f"{TRACERS_FRIENDLY_LOG_TITLE}\n")
            log_file.write("==============================\n")
            log_file.write(f"{TRACERS_FRIENDLY_LOG_MESSAGE}\n")

    except Exception:
        logger.exception("Erro ao escrever log amigável do Tracers")

def _set_tracers_step_status(completed: bool,has_error: bool,) -> None:
    st.session_state.tracers_step_completed = completed
    st.session_state.tracers_step_error = has_error

def _set_mind7_step_status(completed: bool,has_error: bool,) -> None:
    st.session_state.consultation_step_completed = completed
    st.session_state.consultation_step_error = has_error

def _handle_tracers_finished(return_code: int,log_text: str,) -> None:

    if detect_tracers_runtime_error(log_text):
        pause_tracers_due_to_error()
        return

    success = (return_code == 0 and st.session_state.tracers_started and TRACERS_EXCEL_FILE.exists())
    _set_tracers_step_status(completed=success,has_error=not success,)

def _handle_mind7_finished(return_code: int,) -> None:
    success = (return_code == 0 and st.session_state.consultation_started and FINAL_RESULT_FILE.exists())
    _set_mind7_step_status(completed=success,has_error=not success,)