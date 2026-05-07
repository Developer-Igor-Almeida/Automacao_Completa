"""
Ponto de entrada da aplicação Streamlit.

Responsável por:
- configurar a página
- validar estrutura do projeto
- inicializar estado
- iniciar monitoramentos
- renderizar a interface
"""

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from backend.core.paths import (MIND7_DIR,TRACERS_DIR,create_required_directories,required_directories_exist,)
from backend.core.state import (initialize_session_state,is_process_running,sync_state_with_existing_files,)
from backend.services.process_service import (detect_process_finished,monitor_realtime_errors,start_connection_monitor,)
from frontend.layouts.downloads import render_downloads
from frontend.layouts.header import render_header
from frontend.layouts.logs_panel import render_logs_panel
from frontend.layouts.metrics import render_metrics
from frontend.layouts.status_bar import render_status_bar
from frontend.layouts.steps import render_steps


st.set_page_config(page_title="Automação Tracers + Mind7",page_icon="🚗",layout="wide",)

def validate_project_structure() -> None:
    if required_directories_exist():
        create_required_directories()
        return

    if not TRACERS_DIR.exists():
        st.error(f"❌ Pasta do Tracers não encontrada:\n\n{TRACERS_DIR}")

    if not MIND7_DIR.exists():
        st.error(f"❌ Pasta do Mind7 não encontrada:\n\n{MIND7_DIR}")

    st.stop()


def main() -> None:
    validate_project_structure()
    initialize_session_state()
    start_connection_monitor()
    sync_state_with_existing_files()
    detect_process_finished()
    monitor_realtime_errors()

    if is_process_running():
        st_autorefresh(interval=2000, key="refresh_app")

    render_header()
    render_metrics()
    render_status_bar()
    render_steps()
    render_logs_panel()
    render_downloads()


if __name__ == "__main__":
    main()