import streamlit as st

from backend.constants.ui import STEP_PROGRESS_CAPTION
from backend.core.logs import read_log
from backend.core.progress import calculate_progress
from backend.core.state import is_process_running


def render_step_progress(step_name: str) -> None:
    if not is_process_running():
        return

    if st.session_state.current_step != step_name:
        return

    log_text = read_log(st.session_state.current_log_file)
    progress = calculate_progress(log_text)

    st.progress(progress / 100)
    st.caption(STEP_PROGRESS_CAPTION.format(progress=progress))