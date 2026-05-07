"""
Constantes utilizadas na comunicação ADB do Tracers.
"""

ADB_SHELL_COMMAND = "shell"
ADB_PULL_COMMAND = "pull"

UIAUTOMATOR_COMMAND = "uiautomator"
UIAUTOMATOR_DUMP_COMMAND = "dump"

INPUT_COMMAND = "input"
SWIPE_COMMAND = "swipe"

ADB_ERROR_MESSAGE = (
    "Erro ao executar: {command}\n\n"
    "STDOUT:\n{stdout}\n\n"
    "STDERR:\n{stderr}"
)