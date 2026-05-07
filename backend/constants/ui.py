"""
Constantes visuais da interface.
"""

SUCCESS_ICON = " ✅"
ERROR_ICON = " ❌"
PENDING_ICON = ""

APP_TITLE = "🚗 Automação Completa Tracers + Mind7"
APP_SUBTITLE = "Fluxo automatizado: Tracers → Excel → Mind7 → CPF/CNPJ → Resultado Final"

METRIC_TRACERS_FILE_LABEL = "Arquivo Tracers"
METRIC_MIND7_INPUT_LABEL = "Entrada Mind7"
METRIC_FINAL_RESULT_LABEL = "Resultado Final"
METRIC_STATUS_LABEL = "Status"

STATUS_OK = "OK"
STATUS_PENDING = "Pendente"
STATUS_RUNNING = "Rodando"
STATUS_STOPPED = "Parado"

STOP_AUTOMATION_BUTTON_LABEL = "🛑 PARAR AUTOMAÇÃO"
AUTOMATION_INTERRUPTED_MESSAGE = "Automação interrompida."
NO_AUTOMATION_RUNNING_MESSAGE = "Nenhuma automação em execução no momento."
PROCESS_RUNNING_MESSAGE = "Processo em execução: {step}"

STEP_PROGRESS_CAPTION = "Executando... {progress}%"

STATUS_ICONS = {
    "success": SUCCESS_ICON,
    "error": ERROR_ICON,
    "pending": PENDING_ICON,
}