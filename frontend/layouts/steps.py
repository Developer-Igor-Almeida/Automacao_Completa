"""
Layout das etapas da automação.

Responsável por:
- exibir as etapas da automação
- validar pré-requisitos visuais
- acionar serviços de automação
"""

import sys
from pathlib import Path

import streamlit as st

from backend.constants.process import TRACERS_STEP_NAME, MIND7_STEP_NAME
from backend.core.paths import (
    TRACERS_DIR,
    MIND7_DIR,
    TRACERS_LOG_FILE,
    MIND7_LOG_FILE,
    TRACERS_EXCEL_FILE,
    MIND7_INPUT_EXCEL_FILE,
    TRACERS_SCRIPT,
    MIND7_SCRIPT,
    MIND7_CHROME_BAT,
)
from backend.constants.messages import (
    OPEN_CHROME_BUTTON_LABEL,
    SEND_TO_MIND7_BUTTON_LABEL,
    START_MIND7_CONSULTATION_BUTTON_LABEL,
    TRACERS_START_BUTTON_LABEL,
)
from backend.core.state import (
    is_process_running,
    get_status_icon,
    set_step_status,
)
from backend.core.paths import (TRACERS_DIR,MIND7_DIR,TRACERS_LOG_FILE, MIND7_LOG_FILE,TRACERS_EXCEL_FILE, BASE_DIR,
 MIND7_INPUT_EXCEL_FILE,TRACERS_SCRIPT,MIND7_SCRIPT,MIND7_CHROME_BAT,)
from backend.constants.messages import (CHROME_OPENED_SUCCESS_MESSAGE,COPY_EXCEL_FIRST_MESSAGE,FILE_COPIED_SUCCESS_MESSAGE, FINISH_STEP_1_FIRST_MESSAGE,
 FINISH_STEP_2_FIRST_MESSAGE, FINISH_STEP_3_FIRST_MESSAGE, OPEN_CHROME_BUTTON_LABEL, RUN_TRACERS_FIRST_MESSAGE,SEND_TO_MIND7_BUTTON_LABEL,
    START_MIND7_CONSULTATION_BUTTON_LABEL, TRACERS_START_BUTTON_LABEL,)
from backend.core.state import (get_status_icon,is_process_running,set_step_status,)
from backend.services.process_service import start_process
from backend.services.file_service import copy_file
from backend.services.chrome_service import open_chrome_bat


def render_steps() -> None:
    """Renderiza todas as etapas da automação."""
    _apply_steps_style()
    _render_continue_after_error()

    left_column, right_column = st.columns(2, gap="large")

    with left_column:
        _render_tracers_step()
        _render_send_to_mind7_step()

    with right_column:
        _render_chrome_step()
        _render_mind7_consultation_step()

    st.divider()


def _apply_steps_style() -> None:
    """Aplica estilos customizados nas etapas."""
    st.markdown(
        """
        <style>
        .step-title {
            font-size: 25px;
            font-weight: 800;
            margin-top: 18px;
            margin-bottom: 8px;
            color: #ffffff;
        }

        .step-hint {
            font-size: 14px;
            color: #8b949e;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .step-success {
            font-size: 14px;
            color: #3fb950;
            margin-bottom: 12px;
        }

        .step-error {
            font-size: 14px;
            color: #ff7b72;
            margin-bottom: 12px;
        }

        .step-warning {
            font-size: 14px;
            color: #d29922;
            margin-bottom: 12px;
        }

        div.stButton > button {
            border-radius: 8px;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_step_title(number: int, icon: str, title: str) -> None:
    """Renderiza o título visual de cada etapa."""
    st.markdown(
        f'<div class="step-title">{number}. {icon} {title}</div>',
        unsafe_allow_html=True,
    )


def _render_hint(message: str, icon: str = "⚠️") -> None:
    """Renderiza uma mensagem discreta no lugar dos blocos azuis."""
    st.markdown(
        f'<div class="step-hint">{icon} {message}</div>',
        unsafe_allow_html=True,
    )


def _render_success(message: str) -> None:
    """Renderiza mensagem de sucesso discreta."""
    st.markdown(
        f'<div class="step-success">✅ {message}</div>',
        unsafe_allow_html=True,
    )


def _render_error(message: str) -> None:
    """Renderiza mensagem de erro discreta."""
    st.markdown(
        f'<div class="step-error">❌ {message}</div>',
        unsafe_allow_html=True,
    )


def _file_exists_or_show_error(file_path: Path, description: str) -> bool:
    """Valida se um arquivo existe e exibe erro caso não exista."""
    if file_path.exists():
        return True

    _render_error(f"{description} não encontrado em: {file_path}")
    return False


def _build_button_label(label: str, completed: bool, error: bool) -> str:
    """Monta o texto do botão com o ícone de status."""
    return label + get_status_icon(completed, error)


def _render_continue_after_error() -> None:
    """Exibe botão para continuar após correção de erro."""
    if not st.session_state.is_paused_by_error:
        return

    if st.button("▶️ Continuar após correção", type="primary"):
        st.session_state.is_paused_by_error = False
        st.session_state.paused_error_message = ""
        st.session_state.tracers_step_error = False
        st.session_state.tracers_started = True

        start_process(
            [sys.executable, "-u", str(TRACERS_SCRIPT)],
            TRACERS_DIR,
            TRACERS_LOG_FILE,
            TRACERS_STEP_NAME,
        )

        start_process([sys.executable, "-u", str(TRACERS_SCRIPT)],BASE_DIR,TRACERS_LOG_FILE,TRACERS_STEP_NAME,)
        st.rerun()


def _render_tracers_step() -> None:
    """Etapa 1: Extrair placas do Tracers."""
    _render_step_title(1, "🚘", "Extrair placas do Tracers")

    if not _file_exists_or_show_error(
        TRACERS_SCRIPT,
        "Arquivo extrair_tracers.py",
    ):
        return

    button_text = _build_button_label(
        TRACERS_START_BUTTON_LABEL,
        st.session_state.tracers_step_completed,
        st.session_state.tracers_step_error,
    )

    if st.button(button_text, disabled=is_process_running()):
        set_step_status("tracers", completed=False, error=False)

        st.session_state.is_paused_by_error = False
        st.session_state.paused_error_message = ""
        st.session_state.tracers_started = True

        start_process(
            [sys.executable, "-u", str(TRACERS_SCRIPT)],
            TRACERS_DIR,
            TRACERS_LOG_FILE,
            TRACERS_STEP_NAME,
        )

        st.rerun()



def _render_send_to_mind7_step() -> None:
    """Etapa 2: Enviar Excel para Mind7."""
    _render_step_title(2, "📄", "Enviar Excel para Mind7")

    button_text = _build_button_label(
        SEND_TO_MIND7_BUTTON_LABEL,
        st.session_state.send_step_completed,
        st.session_state.send_step_error,
    )

    if not st.session_state.tracers_step_completed:
        _render_hint("Conclua a etapa 1 primeiro")
        return

    if not TRACERS_EXCEL_FILE.exists():
        _render_hint("Execute a extração de placas primeiro", "📁")
        return

    if st.button(button_text, disabled=is_process_running()):
        try:
            copy_file(TRACERS_EXCEL_FILE, MIND7_INPUT_EXCEL_FILE)

            set_step_status("send", completed=True, error=False)
            _render_success("Arquivo copiado para entrada do Mind7.")

            st.rerun()

        except Exception as error:
            set_step_status("send", completed=False, error=True)
            _render_error(f"Erro ao copiar arquivo: {error}")


def _render_chrome_step() -> None:
    """Etapa 3: Abrir Chrome Mind7."""
    _render_step_title(3, "🌐", "Abrir Chrome Mind7")

    button_text = _build_button_label(
        OPEN_CHROME_BUTTON_LABEL,
        st.session_state.chrome_step_completed,
        st.session_state.chrome_step_error,
    )

    if not st.session_state.send_step_completed:
        _render_hint("Conclua a etapa 2 primeiro")
        return

    if not _file_exists_or_show_error(
        MIND7_CHROME_BAT,
        "Arquivo abrir_chrome_mind7.bat",
    ):
        return

    if st.button(button_text, disabled=is_process_running()):
        try:
            open_chrome_bat(MIND7_CHROME_BAT, MIND7_DIR)

            set_step_status("chrome", completed=True, error=False)
            _render_success("Chrome aberto. Faça login no Mind7.")

            st.rerun()

        except Exception as error:
            set_step_status("chrome", completed=False, error=True)
            _render_error(f"Erro ao abrir Chrome: {error}")


def _render_mind7_consultation_step() -> None:
    """Etapa 4: Buscar CPFs/CNPJs."""
    _render_step_title(4, "🔎", "Buscar CPFs/CNPJs")

    button_text = _build_button_label(
        START_MIND7_CONSULTATION_BUTTON_LABEL,
        st.session_state.consultation_step_completed,
        st.session_state.consultation_step_error,
    )

    if not st.session_state.chrome_step_completed:
        _render_hint("Conclua a etapa 3 primeiro")
        return

    if not _file_exists_or_show_error(
        MIND7_SCRIPT,
        "Arquivo consultar_mind7.py",
    ):
        return

    if not MIND7_INPUT_EXCEL_FILE.exists():
        _render_hint("Copie o Excel para o Mind7 primeiro", "📄")
        return

    if st.button(button_text, disabled=is_process_running()):
        set_step_status("consultation", completed=False, error=False)
        st.session_state.consultation_started = True

        start_process(
            [sys.executable, "-u", str(MIND7_SCRIPT)],
            MIND7_DIR,
            MIND7_LOG_FILE,
            MIND7_STEP_NAME,
        )

        st.rerun()
