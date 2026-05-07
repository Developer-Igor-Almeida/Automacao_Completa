import streamlit as st

from backend.constants.ui import (METRIC_FINAL_RESULT_LABEL,METRIC_MIND7_INPUT_LABEL,METRIC_STATUS_LABEL,
    METRIC_TRACERS_FILE_LABEL, STATUS_OK,STATUS_PENDING,STATUS_RUNNING, STATUS_STOPPED,
)
from backend.core.paths import (FINAL_RESULT_FILE, MIND7_INPUT_EXCEL_FILE,TRACERS_EXCEL_FILE,)
from backend.core.state import is_process_running


def render_metrics() -> None:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            METRIC_TRACERS_FILE_LABEL,
            STATUS_OK if TRACERS_EXCEL_FILE.exists() else STATUS_PENDING,
        )

    with col2:
        st.metric(
            METRIC_MIND7_INPUT_LABEL,
            STATUS_OK if MIND7_INPUT_EXCEL_FILE.exists() else STATUS_PENDING,
        )

    with col3:
        st.metric(
            METRIC_FINAL_RESULT_LABEL,
            STATUS_OK if FINAL_RESULT_FILE.exists() else STATUS_PENDING,
        )

    with col4:
        st.metric(
            METRIC_STATUS_LABEL,
            STATUS_RUNNING if is_process_running() else STATUS_STOPPED,
        )

    st.divider()