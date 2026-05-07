"""
Layout de download dos arquivos gerados.

Responsável por:
- listar relatórios disponíveis
- bloquear download antes da conclusão das etapas
- converter Excel para CSV quando necessário
"""

import streamlit as st

from backend.constants.downloads import (CNPJ_ONLY_CSV_LABEL,CNPJ_ONLY_EXCEL_LABEL,CPF_CNPJ_CSV_LABEL,
    CPF_CNPJ_EXCEL_LABEL,CPF_ONLY_CSV_LABEL,CPF_ONLY_EXCEL_LABEL,
    CSV_MIME_TYPE,DOWNLOAD_BLOCKED_MESSAGE,DOWNLOAD_BUTTON_LABEL,
    EXCEL_MIME_TYPE,FILE_NOT_GENERATED_MESSAGE,FULL_RESULT_CSV_LABEL,
    FULL_RESULT_EXCEL_LABEL,
)
from backend.core.files import convert_excel_to_csv_bytes
from backend.core.paths import (CNPJ_ONLY_FILE,CPF_CNPJ_FILE,CPF_ONLY_FILE,FINAL_RESULT_FILE,)


DOWNLOAD_OPTIONS = {
    FULL_RESULT_EXCEL_LABEL: FINAL_RESULT_FILE,
    CPF_ONLY_EXCEL_LABEL: CPF_ONLY_FILE,
    CPF_CNPJ_EXCEL_LABEL: CPF_CNPJ_FILE,
    CNPJ_ONLY_EXCEL_LABEL: CNPJ_ONLY_FILE,
    FULL_RESULT_CSV_LABEL: FINAL_RESULT_FILE,
    CPF_ONLY_CSV_LABEL: CPF_ONLY_FILE,
    CPF_CNPJ_CSV_LABEL: CPF_CNPJ_FILE,
    CNPJ_ONLY_CSV_LABEL: CNPJ_ONLY_FILE,
}

def render_downloads() -> None:
    st.subheader("📥 Baixar arquivo")

    if not _all_steps_completed():
        st.warning(DOWNLOAD_BLOCKED_MESSAGE)

    selected_option = st.selectbox("Escolha o arquivo para baixar:", list(DOWNLOAD_OPTIONS.keys()), disabled=not _all_steps_completed(),)
    selected_file = DOWNLOAD_OPTIONS[selected_option]

    if not _all_steps_completed():
        st.button(DOWNLOAD_BUTTON_LABEL, disabled=True)
        return

    if not selected_file.exists():
        st.info(FILE_NOT_GENERATED_MESSAGE)
        return

    download_data, file_name, mime_type = _prepare_download_file(selected_option,selected_file,)
    st.download_button(DOWNLOAD_BUTTON_LABEL, data=download_data, file_name=file_name, mime=mime_type, type="primary",)

def _all_steps_completed() -> bool:
    return (st.session_state.tracers_step_completed and st.session_state.send_step_completed and 
    st.session_state.chrome_step_completed and st.session_state.consultation_step_completed
    )

def _prepare_download_file(option: str, selected_file):
    if "CSV" in option:
        return (convert_excel_to_csv_bytes(selected_file), f"{selected_file.stem}.csv", CSV_MIME_TYPE,)
    return (selected_file.read_bytes(), selected_file.name, EXCEL_MIME_TYPE,)