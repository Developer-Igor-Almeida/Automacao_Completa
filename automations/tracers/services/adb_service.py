"""
Serviços responsáveis pela comunicação com o Android via ADB.
"""

import subprocess
import time

from automations.tracers.config.settings import (
    REMOTE_XML_PATH,
    SWIPE_DURATION_MS,
    SWIPE_END_Y,
    SWIPE_START_Y,
    SWIPE_WAIT_SECONDS,
    SWIPE_X,
)
from automations.tracers.constants.adb import (ADB_ERROR_MESSAGE, ADB_PULL_COMMAND,ADB_SHELL_COMMAND, INPUT_COMMAND,SWIPE_COMMAND,UIAUTOMATOR_COMMAND,UIAUTOMATOR_DUMP_COMMAND,)

from backend.core.paths import (
    TRACERS_ADB_PATH,
    TRACERS_WINDOW_DUMP_FILE,
)


def run_adb_command(command: list) -> str:
    result = subprocess.run(command, capture_output=True, text=True, shell=False)
    if result.returncode != 0:
        raise RuntimeError(ADB_ERROR_MESSAGE.format(command=" ".join(map(str, command)), stdout=result.stdout, stderr=result.stderr))
    return result.stdout.strip()


def capture_window_xml() -> None:
    _dump_window_xml()
    _pull_window_xml()


def swipe_up() -> None:
    run_adb_command(_build_swipe_command())
    time.sleep(SWIPE_WAIT_SECONDS)


def _dump_window_xml() -> None:
    run_adb_command([TRACERS_ADB_PATH, ADB_SHELL_COMMAND, UIAUTOMATOR_COMMAND, UIAUTOMATOR_DUMP_COMMAND, REMOTE_XML_PATH])


def _pull_window_xml() -> None:
    run_adb_command([TRACERS_ADB_PATH, ADB_PULL_COMMAND, REMOTE_XML_PATH, str(TRACERS_WINDOW_DUMP_FILE)])


def _build_swipe_command() -> list:
    return [TRACERS_ADB_PATH, ADB_SHELL_COMMAND, INPUT_COMMAND, SWIPE_COMMAND, str(SWIPE_X), str(SWIPE_START_Y), str(SWIPE_X), str(SWIPE_END_Y), str(SWIPE_DURATION_MS)]