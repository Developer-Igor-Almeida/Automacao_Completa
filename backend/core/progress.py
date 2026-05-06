import re

from backend.core.logs import corrigir_acentos_log


def calcular_progresso(log_texto):
    if not log_texto:
        return 0

    texto = corrigir_acentos_log(log_texto)

    if "finalizado" in texto.lower():
        return 100

    if "Total salvo no Excel" in texto:
        return 100

    match_tela = re.findall(r"Tela\s+(\d+)/(\d+)", texto)
    if match_tela:
        atual, total = match_tela[-1]
        atual = int(atual)
        total = int(total)

        if total > 0:
            return min(int((atual / total) * 100), 99)

    match_cpf = re.findall(r"Consultando placa:", texto)
    if match_cpf:
        return min(len(match_cpf) * 5, 95)

    return 5