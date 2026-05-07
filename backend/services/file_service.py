"""
Serviço para operações de arquivos entre etapas da automação.
"""

import shutil
from pathlib import Path


def copy_file(source_file: Path, target_file: Path) -> None:
    target_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_file, target_file)