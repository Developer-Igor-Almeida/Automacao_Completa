"""
Serviços responsáveis pela comunicação com o Android via ADB.
"""

import subprocess
import time

from automations.tracers.config.settings import (REMOTE_XML_PATH,SWIPE_DURATION_MS,SWIPE_END_Y,SWIPE_START_Y,SWIPE_WAIT_SECONDS,SWIPE_X,)
from backend.core.paths import (TRACERS_ADB_PATH,TRACERS_WINDOW_DUMP_FILE,)


def run_adb_command(command: list) -> str:
    result = subprocess.run(command,capture_output=True,text=True,shell=False,)

    if result.returncode != 0:
        raise RuntimeError(
            f"Erro ao executar: {' '.join(map(str, command))}\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )

    return result.stdout.strip()


def capture_window_xml() -> None:
    run_adb_command([TRACERS_ADB_PATH,"shell","uiautomator","dump",REMOTE_XML_PATH,])
    run_adb_command([TRACERS_ADB_PATH, "pull",REMOTE_XML_PATH,str(TRACERS_WINDOW_DUMP_FILE),])


def swipe_up() -> None:
    run_adb_command([
        TRACERS_ADB_PATH,"shell",
        "input",
        "swipe",
        str(SWIPE_X),
        str(SWIPE_START_Y),
        str(SWIPE_X),
        str(SWIPE_END_Y),
        str(SWIPE_DURATION_MS),
    ])

    time.sleep(SWIPE_WAIT_SECONDS)