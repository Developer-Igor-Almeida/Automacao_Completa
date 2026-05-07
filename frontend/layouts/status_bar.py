import streamlit as st

from backend.constants.ui import (AUTOMATION_INTERRUPTED_MESSAGE, NO_AUTOMATION_RUNNING_MESSAGE, PROCESS_RUNNING_MESSAGE, STOP_AUTOMATION_BUTTON_LABEL,)
from backend.core.state import is_process_running
from backend.services.process_service import stop_process

def render_status_bar() -> None:
    if is_process_running():
        st.warning(PROCESS_RUNNING_MESSAGE.format(step=st.session_state.current_step,))

        if st.button(STOP_AUTOMATION_BUTTON_LABEL, type="primary"):
            stop_process()
            st.error(AUTOMATION_INTERRUPTED_MESSAGE)
            st.rerun()
    else:
        st.success(NO_AUTOMATION_RUNNING_MESSAGE)

    if st.session_state.is_paused_by_error:
        st.error(st.session_state.paused_error_message)

    st.divider()