import streamlit as st
import subprocess
import shutil
import psutil
import re
import os
import csv
from io import StringIO
from pathlib import Path
from openpyxl import load_workbook
from streamlit_autorefresh import st_autorefresh
import threading
import time

MONITOR_INICIADO = False


def monitorar_conexao():
    time.sleep(20)

    while True:
        time.sleep(10)

        try:
            conexoes = psutil.net_connections(kind="inet")

            conexoes_ativas = [
                c for c in conexoes
                if c.laddr
                and c.laddr.port == 8501
                and c.status == psutil.CONN_ESTABLISHED
            ]

            if len(conexoes_ativas) == 0:
                processo = psutil.Process(os.getpid())

                for filho in processo.children(recursive=True):
                    try:
                        filho.terminate()
                    except Exception:
                        pass

                processo.terminate()
                break

        except Exception:
            pass


if not MONITOR_INICIADO:
    threading.Thread(target=monitorar_conexao, daemon=True).start()
    MONITOR_INICIADO = True

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

# =========================
# SESSION STATE
# =========================

if "processo" not in st.session_state:
    st.session_state.processo = None

if "etapa" not in st.session_state:
    st.session_state.etapa = ""

if "log_atual" not in st.session_state:
    st.session_state.log_atual = None

for chave in [
    "etapa_tracers_ok",
    "etapa_envio_ok",
    "etapa_chrome_ok",
    "etapa_consulta_ok",
    "etapa_tracers_erro",
    "etapa_envio_erro",
    "etapa_chrome_erro",
    "etapa_consulta_erro",
    "tracers_iniciado",
    "consulta_iniciada",
]:
    if chave not in st.session_state:
        st.session_state[chave] = False


def processo_rodando():
    p = st.session_state.processo
    return p is not None and p.poll() is None


def icone_status(ok, erro):
    if ok:
        return " ✅"
    if erro:
        return " ❌"
    return ""


def detectar_finalizacao_processo():
    p = st.session_state.processo

    if p is not None and p.poll() is not None and st.session_state.etapa:
        codigo = p.returncode

        if st.session_state.etapa == "Extração de placas do Tracers":
            if codigo == 0 and st.session_state.tracers_iniciado and EXCEL_TRACERS.exists():
                st.session_state.etapa_tracers_ok = True
                st.session_state.etapa_tracers_erro = False
            else:
                st.session_state.etapa_tracers_ok = False
                st.session_state.etapa_tracers_erro = True

        elif st.session_state.etapa == "Consulta de CPFs/CNPJs no Mind7":
            if codigo == 0 and st.session_state.consulta_iniciada and RESULTADO.exists():
                st.session_state.etapa_consulta_ok = True
                st.session_state.etapa_consulta_erro = False
            else:
                st.session_state.etapa_consulta_ok = False
                st.session_state.etapa_consulta_erro = True

        st.session_state.processo = None
        st.session_state.etapa = ""


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

    if st.session_state.etapa == "Extração de placas do Tracers":
        st.session_state.etapa_tracers_erro = True

    if st.session_state.etapa == "Consulta de CPFs/CNPJs no Mind7":
        st.session_state.etapa_consulta_erro = True

    st.session_state.processo = None
    st.session_state.etapa = ""


def ler_log(log_path):
    if not log_path or not Path(log_path).exists():
        return ""

    return Path(log_path).read_text(encoding="utf-8", errors="ignore")


def limpar_logs():
    for log_file in [LOG_TRACERS, LOG_MIND7]:
        try:
            log_file.write_text("", encoding="utf-8")
        except Exception:
            pass

    st.session_state.log_atual = None


def converter_xlsx_para_csv(caminho_xlsx):
    wb = load_workbook(caminho_xlsx)
    ws = wb.active

    output = StringIO()
    writer = csv.writer(output, delimiter=";")

    for row in ws.iter_rows(values_only=True):
        writer.writerow([
            "" if valor is None else valor
            for valor in row
        ])

    return output.getvalue().encode("utf-8-sig")


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


detectar_finalizacao_processo()

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
        texto_botao_tracers = (
            "▶️ Iniciar extração de placas"
            + icone_status(
                st.session_state.etapa_tracers_ok,
                st.session_state.etapa_tracers_erro
            )
        )

        if st.button(texto_botao_tracers, disabled=processo_rodando()):
            st.session_state.etapa_tracers_ok = False
            st.session_state.etapa_tracers_erro = False
            st.session_state.tracers_iniciado = True

            iniciar_processo(
                ["python", "-u", "extrair_tracers.py"],
                TRACERS,
                LOG_TRACERS,
                "Extração de placas do Tracers"
            )
            st.rerun()

    st.subheader("2. Enviar Excel para Mind7")

    texto_botao_envio = (
        "📤 Copiar arquivo para Mind7"
        + icone_status(
            st.session_state.etapa_envio_ok,
            st.session_state.etapa_envio_erro
        )
    )

    if not st.session_state.etapa_tracers_ok:
        st.info("Conclua a etapa 1 primeiro.")

    if EXCEL_TRACERS.exists():
        if st.button(
            texto_botao_envio,
            disabled=processo_rodando() or not st.session_state.etapa_tracers_ok
        ):
            try:
                shutil.copy2(EXCEL_TRACERS, EXCEL_MIND7)
                st.session_state.etapa_envio_ok = True
                st.session_state.etapa_envio_erro = False
                st.success("Arquivo copiado para entrada do Mind7.")
                st.rerun()
            except Exception as e:
                st.session_state.etapa_envio_ok = False
                st.session_state.etapa_envio_erro = True
                st.error(f"Erro ao copiar arquivo: {e}")
    else:
        st.info("Execute a extração de placas primeiro.")

with col_dir:
    st.subheader("3. Abrir Chrome Mind7")

    chrome_bat = MIND7 / "abrir_chrome_mind7.bat"

    texto_botao_chrome = (
        "🌐 Abrir Chrome para login"
        + icone_status(
            st.session_state.etapa_chrome_ok,
            st.session_state.etapa_chrome_erro
        )
    )

    if not st.session_state.etapa_envio_ok:
        st.info("Conclua a etapa 2 primeiro.")

    if not chrome_bat.exists():
        st.error(f"Arquivo abrir_chrome_mind7.bat não encontrado em:\n{chrome_bat}")
    else:
        if st.button(
            texto_botao_chrome,
            disabled=processo_rodando() or not st.session_state.etapa_envio_ok
        ):
            try:
                subprocess.Popen(
                    ["cmd", "/c", str(chrome_bat)],
                    cwd=str(MIND7),
                    shell=False
                )
                st.session_state.etapa_chrome_ok = True
                st.session_state.etapa_chrome_erro = False
                st.success("Chrome aberto. Faça login no Mind7.")
                st.rerun()
            except Exception as e:
                st.session_state.etapa_chrome_ok = False
                st.session_state.etapa_chrome_erro = True
                st.error(f"Erro ao abrir Chrome: {e}")

    st.subheader("4. Buscar CPFs/CNPJs")

    texto_botao_consulta = (
        "🔎 Iniciar consulta no Mind7"
        + icone_status(
            st.session_state.etapa_consulta_ok,
            st.session_state.etapa_consulta_erro
        )
    )

    if not st.session_state.etapa_chrome_ok:
        st.info("Conclua a etapa 3 primeiro.")

    if not (MIND7 / "consultar_mind7.py").exists():
        st.error(f"Arquivo consultar_mind7.py não encontrado em:\n{MIND7}")
    elif EXCEL_MIND7.exists():
        if st.button(
            texto_botao_consulta,
            disabled=processo_rodando() or not st.session_state.etapa_chrome_ok
        ):
            st.session_state.etapa_consulta_ok = False
            st.session_state.etapa_consulta_erro = False
            st.session_state.consulta_iniciada = True

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

col_log1, col_log2, col_log3 = st.columns([1, 1, 4])

with col_log1:
    if st.button("🧹 Limpar logs", disabled=processo_rodando()):
        limpar_logs()
        st.success("Logs limpos com sucesso!")
        st.rerun()

with col_log2:
    if st.button("🔄 Atualizar logs"):
        st.rerun()

with st.expander("Ver logs da execução", expanded=True):
    log_texto = ler_log(st.session_state.log_atual)

    if log_texto:
        st.code(log_texto[-8000:])
    else:
        st.info("Nenhum log iniciado ainda.")

st.divider()

st.subheader("📥 Baixar arquivo")

todas_etapas_concluidas = (
    st.session_state.etapa_tracers_ok
    and st.session_state.etapa_envio_ok
    and st.session_state.etapa_chrome_ok
    and st.session_state.etapa_consulta_ok
)

if not todas_etapas_concluidas:
    st.warning("Finalize as 4 etapas da automação antes de baixar o relatório.")

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
    disabled=not todas_etapas_concluidas
)

arquivo_escolhido = arquivos_disponiveis[opcao_download]

if not todas_etapas_concluidas:
    st.button("📥 Baixar arquivo selecionado", disabled=True)
elif not arquivo_escolhido.exists():
    st.info("Esse arquivo ainda não foi gerado.")
else:
    if "CSV" in opcao_download:
        dados = converter_xlsx_para_csv(arquivo_escolhido)
        nome_arquivo = arquivo_escolhido.stem + ".csv"
        mime = "text/csv"
    else:
        dados = arquivo_escolhido.read_bytes()
        nome_arquivo = arquivo_escolhido.name
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    st.download_button(
        "📥 Baixar arquivo selecionado",
        data=dados,
        file_name=nome_arquivo,
        mime=mime,
        type="primary"
    )