import subprocess
import webbrowser
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent
APP = BASE_DIR / "app.py"

subprocess.Popen([
    "streamlit",
    "run",
    str(APP),
    "--server.headless=true",
    "--server.port=8501"
])

time.sleep(3)
webbrowser.open("http://localhost:8501")