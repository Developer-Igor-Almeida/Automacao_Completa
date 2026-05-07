"""
Configurações da automação Mind7.
"""

from pathlib import Path


# =========================================================
# URLS
# =========================================================

MIND7_URL = "https://mind-7.org/painel/consultas/placa/"


# =========================================================
# CHROME
# =========================================================

CHROME_DEBUG_PORT = 9222

POSSIBLE_CHROME_PATHS = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(
        rf"{Path.home()}\AppData\Local\Google\Chrome\Application\chrome.exe"
    ),
]


# =========================================================
# EXCEL
# =========================================================

PLATE_COLUMN_NAME = "Placa"
DOCUMENT_COLUMN_NAME = "CPF"


# =========================================================
# TIMING
# =========================================================

TIME_BETWEEN_QUERIES_SECONDS = 8
PAUSE_EVERY_QUERIES = 5
LONG_PAUSE_SECONDS = 60


# =========================================================
# CAPTCHA
# =========================================================

MAX_CAPTCHA_RETRIES = 5
MAX_EXTRA_SUCCESS_RETRIES = 10
CAPTCHA_WAIT_SECONDS = 60


# =========================================================
# PLAYWRIGHT
# =========================================================

DOCUMENT_INPUT_SELECTOR = "#documento"

QUERY_BUTTON_TEXT = "Consultar"

PAGE_LOAD_WAIT_SECONDS = 1.5

TYPE_DELAY_MS = 120

AFTER_TYPE_WAIT_SECONDS = 2.5

RESULT_WAIT_TIMEOUT_SECONDS = 15

RESULT_POLL_INTERVAL_SECONDS = 0.5