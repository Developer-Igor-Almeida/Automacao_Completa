import os
import subprocess
import sys
from pathlib import Path


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent

    return Path(_file_).resolve().parents[1]


def main() -> None:
    base_dir = get_base_dir()
    app_path = base_dir / "app.py"

    os.chdir(base_dir)

    subprocess.run([sys.executable,"-m","streamlit","run",str(app_path),"--server.headless=true",])


if _name_ == "_main_":
    main()