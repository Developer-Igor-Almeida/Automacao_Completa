import subprocess
import sys
import time
import webbrowser
from pathlib import Path

if getattr(sys, "frozen", False):
    exe_dir = Path(sys.executable).resolve().parent

    if (exe_dir / "app.py").exists():
        base_dir = exe_dir
    else:
        base_dir = exe_dir.parent
else:
    base_dir = Path(__file__).resolve().parents[1]

app_path = base_dir / "app.py"
python_exe = base_dir / "python" / "python.exe"

subprocess.Popen(
    [
        str(python_exe),
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port", "8501",
        "--server.address", "localhost",
        "--server.headless", "true",
        "--server.fileWatcherType", "none",
        "--browser.gatherUsageStats", "false",
        "--global.developmentMode", "false",
    ],
    cwd=base_dir,
)

time.sleep(5)
webbrowser.open("http://localhost:8501")