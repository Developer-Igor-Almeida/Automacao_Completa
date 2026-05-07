"""
Utilitários para leitura, limpeza e normalização de logs.

Responsável por:
- ler arquivos de log
- limpar logs da aplicação
- corrigir textos com encoding quebrado
"""

import logging
from pathlib import Path
from backend.constants.encoding import (BROKEN_TEXT_REPLACEMENTS,DEFAULT_ENCODING,)
from backend.core.paths import (MIND7_LOG_FILE,TRACERS_LOG_FILE,)

logger = logging.getLogger(__name__)

def read_log(log_path: Path | None) -> str:
    if not log_path or not Path(log_path).exists():
        return ""

    return Path(log_path).read_text(encoding=DEFAULT_ENCODING,errors="ignore",)

def fix_broken_text_encoding(text: str) -> str:
    if not text:
        return ""

    for broken_text, fixed_text in BROKEN_TEXT_REPLACEMENTS.items():
        text = text.replace(broken_text, fixed_text)

    return text

def clear_logs() -> None:
    for log_file in [TRACERS_LOG_FILE, MIND7_LOG_FILE]:
        try:
            log_file.write_text("", encoding=DEFAULT_ENCODING)
        except Exception:
            logger.exception("Erro ao limpar arquivo de log: %s", log_file)