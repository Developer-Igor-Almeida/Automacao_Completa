import os
import subprocess
import threading
import time

import psutil
import streamlit as st

from backend.core.logs import ler_log
from backend.core.paths import EXCEL_TRACERS, RESULTADO, LOG_TRACERS
from backend.core.state import processo_rodando


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
                processo_atual = psutil.Process(os.getpid())

                for filho in processo_atual.children(recursive=True):
                    try:
                        filho.terminate()
                    except Exception:
                        pass

                processo_atual.terminate()
                break

        except Exception:
            pass


def iniciar_monitor_conexao():
    if not st.session_state.monitor_iniciado:
        threading.Thread(target=monitorar_conexao, daemon=True).start()
        st.session_state.monitor_iniciado = True


def iniciar_processo(cmd, pasta, log_path, etapa):
    with open(log_path, "w", encoding="utf-8") as log:
        log.write(f"Iniciando etapa: {etapa}\n\n")

    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    try:
        log_file = open(log_path, "a", encoding="utf-8")

        p = subprocess.Popen(
            cmd,
            cwd=str(pasta),
            stdout=log_file,
            stderr=log_file,
            text=True,
            creationflags=flags,
            env=env,
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
                try:
                    filho.terminate()
                except Exception:
                    pass

            processo.terminate()

        except Exception:
            try:
                p.terminate()
            except Exception:
                pass

    if st.session_state.etapa == "Extração de placas do Tracers":
        st.session_state.etapa_tracers_erro = True

    if st.session_state.etapa == "Consulta de CPFs/CNPJs no Mind7":
        st.session_state.etapa_consulta_erro = True

    st.session_state.processo = None
    st.session_state.etapa = ""


def detectar_erro_usuario_saiu(log_texto):
    if not log_texto:
        return False

    from backend.core.logs import corrigir_acentos_log

    texto = corrigir_acentos_log(log_texto).lower()

    erros = [
        "no devices/emulators found",
        "device not found",
        "uiautomator",
        "window_dump",
        "adb.exe",
        "erro ao executar",
        "app_tracers_fechado",
        "não está aberto em primeiro plano",
        "nao esta aberto em primeiro plano",
    ]

    return any(e in texto for e in erros)


def pausar_por_erro_tracers():
    parar_processo()

    st.session_state.erro_pausado = True
    st.session_state.etapa_tracers_ok = False
    st.session_state.etapa_tracers_erro = True

    st.session_state.mensagem_erro_pausado = (
        "❌ O celular foi desconectado, o aplicativo Tracers foi fechado "
        "ou a tela correta não está aberta.\n\n"
        "Verifique:\n"
        "- Celular conectado\n"
        "- Depuração USB ativa\n"
        "- Aplicativo Tracers aberto\n"
        "- Tela da lista de veículos visível\n\n"
        "Depois clique em CONTINUAR."
    )

    try:
        with open(LOG_TRACERS, "a", encoding="utf-8") as log:
            log.write("\n\n==============================\n")
            log.write("ERRO AMIGÁVEL\n")
            log.write("==============================\n")
            log.write("O processo foi pausado porque o celular/app não estava disponível.\n")
            log.write("Verifique o celular e mantenha o aplicativo Tracers aberto na tela correta.\n")
    except Exception:
        pass


def detectar_finalizacao_processo():
    p = st.session_state.processo

    if p is not None and p.poll() is not None and st.session_state.etapa:
        codigo = p.returncode
        etapa_atual = st.session_state.etapa
        log_texto = ler_log(st.session_state.log_atual)

        if etapa_atual == "Extração de placas do Tracers":
            if detectar_erro_usuario_saiu(log_texto):
                pausar_por_erro_tracers()

            elif codigo == 0 and st.session_state.tracers_iniciado and EXCEL_TRACERS.exists():
                st.session_state.etapa_tracers_ok = True
                st.session_state.etapa_tracers_erro = False

            else:
                st.session_state.etapa_tracers_ok = False
                st.session_state.etapa_tracers_erro = True

        elif etapa_atual == "Consulta de CPFs/CNPJs no Mind7":
            if codigo == 0 and st.session_state.consulta_iniciada and RESULTADO.exists():
                st.session_state.etapa_consulta_ok = True
                st.session_state.etapa_consulta_erro = False
            else:
                st.session_state.etapa_consulta_ok = False
                st.session_state.etapa_consulta_erro = True

        if not st.session_state.erro_pausado:
            st.session_state.processo = None
            st.session_state.etapa = ""


def monitorar_erro_em_tempo_real():
    if not processo_rodando():
        return

    if st.session_state.etapa != "Extração de placas do Tracers":
        return

    log_texto = ler_log(st.session_state.log_atual)

    if detectar_erro_usuario_saiu(log_texto):
        pausar_por_erro_tracers()