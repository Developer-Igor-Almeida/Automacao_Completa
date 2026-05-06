import streamlit as st
from streamlit_autorefresh import st_autorefresh
from backend.core.paths import criar_pastas, pastas_obrigatorias_existem, TRACERS, MIND7
from backend.core.state import (inicializar_estado,sincronizar_estado_por_arquivos,processo_rodando,)
from backend.services.process_service import (iniciar_monitor_conexao,detectar_finalizacao_processo,monitorar_erro_em_tempo_real,)
from frontend.layouts.header import render_header
from frontend.layouts.metrics import render_metrics
from frontend.layouts.status_bar import render_status_bar
from frontend.layouts.steps import render_steps
from frontend.layouts.logs_panel import render_logs_panel
from frontend.layouts.downloads import render_downloads

st.set_page_config(page_title="Automação Tracers + Mind7",page_icon="🚗",layout="wide",)

def validar_estrutura():
    if not pastas_obrigatorias_existem():
        if not TRACERS.exists():
            st.error(f"❌ Pasta do Tracers não encontrada:\n\n{TRACERS}")

        if not MIND7.exists():st.error(f"❌ Pasta do Mind7 não encontrada:\n\n{MIND7}")
        st.stop()
    criar_pastas()

def main():
    validar_estrutura()
    inicializar_estado()
    iniciar_monitor_conexao()
    sincronizar_estado_por_arquivos()
    detectar_finalizacao_processo()
    monitorar_erro_em_tempo_real()
    if processo_rodando():st_autorefresh(interval=2000, key="refresh_app")
    render_header()
    render_metrics()
    render_status_bar()
    render_steps()
    render_logs_panel()
    render_downloads()

if __name__ == "__main__":
    main()