import sys
import time
import socket
import threading
import webbrowser
from pathlib import Path
from streamlit.web import bootstrap

PORTA = 3000
URL = f"http://localhost:{PORTA}"


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


BASE_DIR = get_base_dir()
APP_PATH = BASE_DIR / "app.py"


def porta_em_uso(porta):
    try:
        with socket.create_connection(("127.0.0.1", porta), timeout=1):
            return True
    except OSError:
        return False


def abrir_navegador_quando_pronto():
    for _ in range(30):
        if porta_em_uso(PORTA):
            time.sleep(1)
            webbrowser.open_new(URL)
            return
        time.sleep(1)


if __name__ == "__main__":
    if not APP_PATH.exists():
        print(f"ERRO: app.py não encontrado em: {APP_PATH}")
        input("Pressione ENTER para sair...")
        sys.exit(1)

    if porta_em_uso(PORTA):
        webbrowser.open_new(URL)
        sys.exit()

    threading.Thread(target=abrir_navegador_quando_pronto, daemon=True).start()

    bootstrap.run(
        str(APP_PATH),
        False,
        [
            "--server.port=3000",
            "--server.headless=true",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false",
            "--global.developmentMode=false",
            "--browser.gatherUsageStats=false",
        ],
        {}
    )