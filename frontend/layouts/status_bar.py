import streamlit as st

from backend.constants.ui import (
    AUTOMATION_INTERRUPTED_MESSAGE,
    NO_AUTOMATION_RUNNING_MESSAGE,
    STOP_AUTOMATION_BUTTON_LABEL,
)
from backend.core.state import is_process_running
from backend.services.process_service import stop_process


def render_status_bar() -> None:
    _apply_status_bar_style()

    if is_process_running():
        _render_running_status()
    else:
        _render_idle_status()

    if st.session_state.get("is_paused_by_error", False):
        _render_error_status(st.session_state.get("paused_error_message", ""))

    st.divider()


def _apply_status_bar_style() -> None:
    st.markdown(
        """
        <style>
        .status-container {
            margin: 8px 0 14px 0;
        }

        .status-bar {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .status-running {
            color: #d29922;
        }

        .status-idle {
            color: #3fb950;
        }

        .status-error {
            color: #ff7b72;
        }

        .status-step {
            color: #ffffff;
            font-weight: 700;
        }

        .mini-progress-container {
            width: 100%;
            height: 6px;
            background-color: #1f2937;
            border-radius: 999px;
            overflow: hidden;
            margin-top: 6px;
        }

        .mini-progress-bar {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #3b82f6, #60a5fa);
            transition: width 0.4s ease;
        }

        .progress-label {
            font-size: 12px;
            color: #8b949e;
            margin-top: 4px;
        }

        div.stButton > button {
            border-radius: 8px;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _get_progress_percentage() -> int:
    total_steps = 4

    completed_steps = 0
    completed_steps += int(st.session_state.get("tracers_step_completed", False))
    completed_steps += int(st.session_state.get("send_step_completed", False))
    completed_steps += int(st.session_state.get("chrome_step_completed", False))
    completed_steps += int(st.session_state.get("consultation_step_completed", False))

    return int((completed_steps / total_steps) * 100)


def _render_progress_bar() -> None:
    progress = _get_progress_percentage()

    st.markdown(
        f"""
        <div class="mini-progress-container">
            <div class="mini-progress-bar" style="width: {progress}%;"></div>
        </div>
        <div class="progress-label">Progresso geral: {progress}%</div>
        """,
        unsafe_allow_html=True,
    )


def _render_running_status() -> None:
    current_step = st.session_state.get("current_step", "Processando...")

    st.markdown(
        f"""
        <div class="status-container">
            <div class="status-bar status-running">
                🟡 Automação em execução:
                <span class="status-step">{current_step}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _render_progress_bar()

    if st.button(STOP_AUTOMATION_BUTTON_LABEL, type="primary"):
        stop_process()
        _render_error_status(AUTOMATION_INTERRUPTED_MESSAGE)
        st.rerun()


def _render_idle_status() -> None:
    st.markdown(
        f"""
        <div class="status-container">
            <div class="status-bar status-idle">
                🟢 {NO_AUTOMATION_RUNNING_MESSAGE}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _render_progress_bar()


def _render_error_status(message: str) -> None:
    if not message:
        return

    st.markdown(
        f"""
        <div class="status-bar status-error">
            🔴 {message}
        </div>
        """,
        unsafe_allow_html=True,
    )