"""
Cálculo de progresso estimado da automação.

Responsável por:
- interpretar logs
- estimar percentual de execução
- limitar progresso visual enquanto o processo está rodando
"""

import re
from backend.constants.process import (CPF_PROGRESS_STEP_PERCENT,CPF_QUERY_PATTERN,FINISHED_PROGRESS_PERCENT,
    MAX_CPF_PROGRESS_PERCENT,MAX_RUNNING_PROGRESS_PERCENT,MIN_PROGRESS_PERCENT,SCREEN_PROGRESS_PATTERN,
)

from backend.core.logs import fix_broken_text_encoding

def calculate_progress(log_text: str) -> int:
    if not log_text:
        return 0

    normalized_text = fix_broken_text_encoding(log_text)

    if _is_finished(normalized_text):
        return FINISHED_PROGRESS_PERCENT

    screen_progress = _calculate_screen_progress(normalized_text)

    if screen_progress is not None:
        return screen_progress

    cpf_progress = _calculate_cpf_progress(normalized_text)

    if cpf_progress is not None:
        return cpf_progress

    return MIN_PROGRESS_PERCENT

def _is_finished(text: str) -> bool:
    return ("finalizado" in text.lower()or "Total salvo no Excel" in text)

def _calculate_screen_progress(text: str) -> int | None:
    matches = re.findall(SCREEN_PROGRESS_PATTERN, text)

    if not matches:
        return None

    current_screen, total_screens = matches[-1]
    current_screen = int(current_screen)
    total_screens = int(total_screens)

    if total_screens <= 0:
        return None

    progress = int((current_screen / total_screens) * 100)
    return min(progress, MAX_RUNNING_PROGRESS_PERCENT)

def _calculate_cpf_progress(text: str) -> int | None:
    matches = re.findall(CPF_QUERY_PATTERN, text)

    if not matches:
        return None

    progress = len(matches) * CPF_PROGRESS_STEP_PERCENT
    return min(progress, MAX_CPF_PROGRESS_PERCENT)