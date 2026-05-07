"""
Serviço responsável por abrir o Chrome usado na automação Mind7.
"""

import os
import subprocess
from pathlib import Path


def open_chrome_bat(bat_file: Path, working_dir: Path) -> None:
    if os.name == "nt":
        subprocess.Popen(["cmd", "/c", str(bat_file)], cwd=str(working_dir),shell=False,)
        return
        
    subprocess.Popen([str(bat_file)],cwd=str(working_dir),shell=False,)