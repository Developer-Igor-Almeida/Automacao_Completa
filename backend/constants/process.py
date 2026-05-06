"""
Constantes relacionadas aos processos da automação.
"""

TRACERS_STEP_NAME = "Extração de placas do Tracers"
MIND7_STEP_NAME = "Consulta de CPFs/CNPJs no Mind7"

STREAMLIT_PORT = 8501

MONITOR_INITIAL_DELAY_SECONDS = 20
MONITOR_CHECK_INTERVAL_SECONDS = 10

STEP_ERROR_STATE_KEYS = {
    TRACERS_STEP_NAME: "tracers_step_error",
    MIND7_STEP_NAME: "consultation_step_error",
}