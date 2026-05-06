import streamlit as st

from backend.core.files import converter_xlsx_para_csv
from backend.core.paths import (
    RESULTADO,
    CPFS,
    CPFS_CNPJS,
    CNPJS,
)


def render_downloads():
    st.subheader("📥 Baixar arquivo")

    todas_etapas_concluidas = (
        st.session_state.etapa_tracers_ok
        and st.session_state.etapa_envio_ok
        and st.session_state.etapa_chrome_ok
        and st.session_state.etapa_consulta_ok
    )

    if not todas_etapas_concluidas:
        st.warning(
            "Finalize as 4 etapas da automação antes de baixar o relatório."
        )

    arquivos_disponiveis = {
        "Resultado completo - Excel": RESULTADO,
        "Somente CPFs - Excel": CPFS,
        "CPFs + CNPJs - Excel": CPFS_CNPJS,
        "Somente CNPJs - Excel": CNPJS,
        "Resultado completo - CSV": RESULTADO,
        "Somente CPFs - CSV": CPFS,
        "CPFs + CNPJs - CSV": CPFS_CNPJS,
        "Somente CNPJs - CSV": CNPJS,
    }

    opcao_download = st.selectbox(
        "Escolha o arquivo para baixar:",
        list(arquivos_disponiveis.keys()),
        disabled=not todas_etapas_concluidas,
    )

    arquivo_escolhido = arquivos_disponiveis[opcao_download]

    if not todas_etapas_concluidas:
        st.button("📥 Baixar arquivo selecionado", disabled=True)
        return

    if not arquivo_escolhido.exists():
        st.info("Esse arquivo ainda não foi gerado.")
        return

    if "CSV" in opcao_download:
        dados = converter_xlsx_para_csv(arquivo_escolhido)
        nome_arquivo = arquivo_escolhido.stem + ".csv"
        mime = "text/csv"
    else:
        dados = arquivo_escolhido.read_bytes()
        nome_arquivo = arquivo_escolhido.name
        mime = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.download_button(
        "📥 Baixar arquivo selecionado",
        data=dados,
        file_name=nome_arquivo,
        mime=mime,
        type="primary",
    )