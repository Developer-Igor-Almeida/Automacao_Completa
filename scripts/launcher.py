import subprocess
import webbrowser
import time
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
APP = BASE_DIR / "app.py"

def iniciar_streamlit():
    subprocess.Popen([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP),
        "--server.headless=true",
        "--server.port=8501"
    ])

def abrir_navegador():
    time.sleep(3)
    webbrowser.open("http://localhost:8501")

if __name__ == "__main__":
    iniciar_streamlit()
    abrir_navegador()