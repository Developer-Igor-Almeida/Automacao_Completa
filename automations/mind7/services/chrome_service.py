"""
Serviço responsável por abrir e conectar no Chrome usado pelo Mind7.
"""

import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

from automations.mind7.config.settings import (
    CHROME_DEBUG_PORT,
    MIND7_URL,
    POSSIBLE_CHROME_PATHS,
)

from backend.core.paths import MIND7_PROFILES_DIR


def find_chrome_path() -> Path:
    for chrome_path in POSSIBLE_CHROME_PATHS:
        if chrome_path.exists():
            return chrome_path

    raise FileNotFoundError(
        "Google Chrome não encontrado no computador."
    )


def open_mind7_chrome() -> None:
    chrome_path = find_chrome_path()

    profile_dir = (
        MIND7_PROFILES_DIR / "perfil_chrome"
    )

    profile_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    subprocess.Popen([
        str(chrome_path),
        f"--remote-debugging-port={CHROME_DEBUG_PORT}",
        f"--user-data-dir={profile_dir}",
        "--start-maximized",
        MIND7_URL,
    ])


def connect_to_mind7_page():
    playwright = sync_playwright().start()

    browser = playwright.chromium.connect_over_cdp(
        f"http://localhost:{CHROME_DEBUG_PORT}"
    )

    context = browser.contexts[0]

    page = get_mind7_page(context)

    return playwright, browser, page


def get_mind7_page(context):
    for page in context.pages:
        if "mind-7.org" in page.url:
            return page

    page = context.new_page()

    page.goto(
        MIND7_URL,
        wait_until="domcontentloaded",
    )

    return page