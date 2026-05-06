"""
Padrões de erro identificados nos logs da automação.
"""

TRACERS_CONNECTION_ERRORS = [
    "no devices/emulators found",
    "device not found",
    "adb.exe",
]

TRACERS_UI_ERRORS = [
    "uiautomator",
    "window_dump",
]

TRACERS_APP_ERRORS = [
    "erro ao executar",
    "app_tracers_fechado",
    "não está aberto em primeiro plano",
    "nao esta aberto em primeiro plano",
]

TRACERS_RUNTIME_ERRORS = (
    TRACERS_CONNECTION_ERRORS
    + TRACERS_UI_ERRORS
    + TRACERS_APP_ERRORS
)