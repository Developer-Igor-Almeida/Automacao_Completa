import streamlit as st
import subprocess
import shutil
import psutil
import re
import os
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Automação Tracers + Mind7",
    page_icon="🚗",
    layout="wide"
)

BASE_DIR = Path(__file__).parent

TRACERS = BASE_DIR / "tracers" 
MIND7 = BASE_DIR / "mind7" 

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_TRACERS = LOG_DIR / "tracers.log"
LOG_MIND7 = LOG_DIR / "mind7.log"

EXCEL_TRACERS = TRACERS / "saida" / "veiculos_tracers.xlsx"
EXCEL_MIND7 = MIND7 / "entrada" / "veiculos_tracers.xlsx"

RESULTADO = MIND7 / "saida" / "veiculos_tracers_com_cpf.xlsx"
CPFS = MIND7 / "saida" / "somente_cpfs.xlsx"
CPFS_CNPJS = MIND7 / "saida" / "cpfs_e_cnpjs.xlsx"
CNPJS = MIND7 / "saida" / "somente_cnpjs.xlsx"

if not TRACERS.exists():
    st.error(f"❌ Pasta do Tracers não encontrada:\n\n{TRACERS}")
    st.stop()

if not MIND7.exists():
    st.error(f"❌ Pasta do Mind7 não encontrada:\n\n{MIND7}")
    st.stop()

(TRACERS / "saida").mkdir(exist_ok=True)
(MIND7 / "entrada").mkdir(exist_ok=True)
(MIND7 / "saida").mkdir(exist_ok=True)

if "processo" not in st.session_state:
    st.session_state.processo = None

if "etapa" not in st.session_state:
    st.session_state.etapa = ""

if "log_atual" not in st.session_state:
    st.session_state.log_atual = None


def processo_rodando():
    p = st.session_state.processo
    return p is not None and p.poll() is None


def iniciar_processo(cmd, pasta, log_path, etapa):
    with open(log_path, "w", encoding="utf-8") as log:
        log.write(f"Iniciando etapa: {etapa}\n\n")

    log_file = open(log_path, "a", encoding="utf-8")

    flags = 0
    if os.name == "nt":
        flags = subprocess.CREATE_NO_WINDOW

    try:
        p = subprocess.Popen(
            cmd,
            cwd=pasta,
            stdout=log_file,
            stderr=log_file,
            text=True,
            creationflags=flags
        )

        st.session_state.processo = p
        st.session_state.etapa = etapa
        st.session_state.log_atual = log_path

    except Exception as e:
        st.error(f"❌ Erro ao iniciar processo: {e}")


def parar_processo():
    p = st.session_state.processo

    if p and p.poll() is None:
        try:
            processo = psutil.Process(p.pid)
            for filho in processo.children(recursive=True):
                filho.terminate()
            processo.terminate()
        except Exception:
            p.terminate()

    st.session_state.processo = None
    st.session_state.etapa = ""


def ler_log(log_path):
    if not log_path or not Path(log_path).exists():
        return ""

    return Path(log_path).read_text(encoding="utf-8", errors="ignore")


def calcular_progresso(log_texto):
    if not log_texto:
        return 0

    if "Finalizado" in log_texto or "FINALIZADO" in log_texto:
        return 100

    if "Total salvo no Excel" in log_texto:
        return 100

    match_tela = re.findall(r"Tela\s+(\d+)/(\d+)", log_texto)
    if match_tela:
        atual, total = match_tela[-1]
        atual = int(atual)
        total = int(total)
        if total > 0:
            return min(int((atual / total) * 100), 99)

    match_cpf = re.findall(r"Consultando placa:", log_texto)
    if match_cpf:
        return min(len(match_cpf) * 5, 95)

    return 5


if processo_rodando():
    st_autorefresh(interval=1500, key="refresh_app")


st.markdown("""
<style>
.big-title {
    font-size: 38px;
    font-weight: 800;
    margin-bottom: 5px;
}
.subtitle {
    font-size: 18px;
    color: #666;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="big-title">🚗 Automação Completa Tracers + Mind7</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Fluxo automatizado: Tracers → Excel → Mind7 → CPF/CNPJ → Resultado Final</div>',
    unsafe_allow_html=True
)

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Arquivo Tracers", "OK" if EXCEL_TRACERS.exists() else "Pendente")

with col2:
    st.metric("Entrada Mind7", "OK" if EXCEL_MIND7.exists() else "Pendente")

with col3:
    st.metric("Resultado Final", "OK" if RESULTADO.exists() else "Pendente")

with col4:
    st.metric("Status", "Rodando" if processo_rodando() else "Parado")

st.divider()

if processo_rodando():
    st.warning(f"Processo em execução: {st.session_state.etapa}")

    if st.button("🛑 PARAR AUTOMAÇÃO", type="primary"):
        parar_processo()
        st.error("Automação interrompida.")
        st.rerun()
else:
    st.success("Nenhuma automação em execução no momento.")

st.divider()

col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("1. Extrair placas do Tracers")

    if not (TRACERS / "extrair_tracers.py").exists():
        st.error(f"Arquivo extrair_tracers.py não encontrado em:\n{TRACERS}")
    else:
        if st.button("▶️ Iniciar extração de placas", disabled=processo_rodando()):
            iniciar_processo(
                ["python", "-u", "extrair_tracers.py"],
                TRACERS,
                LOG_TRACERS,
                "Extração de placas do Tracers"
            )
            st.rerun()

    st.subheader("2. Enviar Excel para Mind7")

    if EXCEL_TRACERS.exists():
        if st.button("📤 Copiar arquivo para Mind7", disabled=processo_rodando()):
            shutil.copy2(EXCEL_TRACERS, EXCEL_MIND7)
            st.success("Arquivo copiado para entrada do Mind7.")
    else:
        st.info("Execute a extração de placas primeiro.")

with col_dir:
    st.subheader("3. Abrir Chrome Mind7")

    chrome_bat = MIND7 / "abrir_chrome_mind7.bat"

    if not chrome_bat.exists():
        st.error(f"Arquivo abrir_chrome_mind7.bat não encontrado em:\n{chrome_bat}")
    else:
        if st.button("🌐 Abrir Chrome para login", disabled=processo_rodando()):
            try:
                subprocess.Popen(
                    ["cmd", "/c", str(chrome_bat)],
                    cwd=str(MIND7),
                    shell=False
                )
                st.success("Chrome aberto. Faça login no Mind7.")
            except Exception as e:
                st.error(f"Erro ao abrir Chrome: {e}")

    st.subheader("4. Buscar CPFs/CNPJs")

    if not (MIND7 / "consultar_mind7.py").exists():
        st.error(f"Arquivo consultar_mind7.py não encontrado em:\n{MIND7}")
    elif EXCEL_MIND7.exists():
        if st.button("🔎 Iniciar consulta no Mind7", disabled=processo_rodando()):
            iniciar_processo(
                ["python", "-u", "consultar_mind7.py"],
                MIND7,
                LOG_MIND7,
                "Consulta de CPFs/CNPJs no Mind7"
            )
            st.rerun()
    else:
        st.info("Copie o Excel para o Mind7 primeiro.")

st.divider()

st.subheader("📊 Progresso em tempo real")

log_texto = ler_log(st.session_state.log_atual)
progresso = calcular_progresso(log_texto)

st.progress(progresso / 100)
st.write(f"Progresso estimado: **{progresso}%**")

st.subheader("📜 Logs organizados")

with st.expander("Ver logs da execução", expanded=True):
    if log_texto:
        st.code(log_texto[-8000:])
    else:
        st.info("Nenhum log iniciado ainda.")

st.divider()

st.subheader("📥 Resultados")

col_down1, col_down2, col_down3, col_down4 = st.columns(4)

with col_down1:
    if RESULTADO.exists():
        with open(RESULTADO, "rb") as file:
            st.download_button(
                "📥 Resultado completo",
                file,
                file_name="veiculos_tracers_com_cpf.xlsx"
            )
    else:
        st.info("Resultado completo ainda não gerado.")

with col_down2:
    if CPFS.exists():
        with open(CPFS, "rb") as file:
            st.download_button(
                "📥 Somente CPFs",
                file,
                file_name="somente_cpfs.xlsx"
            )
    else:
        st.info("CPFs ainda não gerado.")

with col_down3:
    if CPFS_CNPJS.exists():
        with open(CPFS_CNPJS, "rb") as file:
            st.download_button(
                "📥 CPFs + CNPJs",
                file,
                file_name="cpfs_e_cnpjs.xlsx"
            )
    else:
        st.info("CPFs + CNPJs ainda não gerado.")

with col_down4:
    if CNPJS.exists():
        with open(CNPJS, "rb") as file:
            st.download_button(
                "📥 Somente CNPJs",
                file,
                file_name="somente_cnpjs.xlsx"
            )
    else:
        st.info("CNPJs ainda não gerado.")