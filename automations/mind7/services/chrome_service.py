import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

from automations.mind7.config.settings import (CDP_CONNECTION_URL, CHROME_DEBUG_PORT, CHROME_PROFILE_DIR_NAME,
    CONNECTION_RETRIES,CONNECTION_RETRY_WAIT_SECONDS,MIND7_DOMAIN,
    MIND7_URL,POSSIBLE_CHROME_PATHS,
)

from backend.core.paths import MIND7_PROFILES_DIR

def find_chrome_path() -> Path:
    for chrome_path in POSSIBLE_CHROME_PATHS:
        if chrome_path.exists():
            return chrome_path
    raise FileNotFoundError("Google Chrome não encontrado no computador.")

def open_mind7_chrome() -> None:
    chrome_path = find_chrome_path()
    profile_dir = _get_chrome_profile_dir()
    subprocess.Popen([str(chrome_path), f"--remote-debugging-port={CHROME_DEBUG_PORT}", f"--user-data-dir={profile_dir}", "--start-maximized", MIND7_URL])

def connect_to_mind7_page():
    playwright = sync_playwright().start()
    try:
        browser = _connect_to_chrome_with_retry(playwright=playwright)
        context = _get_or_create_browser_context(browser)
        page = get_mind7_page(context)
        return playwright, browser, page
    except Exception:
        playwright.stop()
        raise

def get_mind7_page(context):
    for page in context.pages:
        if MIND7_DOMAIN in page.url:
            return page
    page = context.new_page()
    page.goto(MIND7_URL, wait_until="domcontentloaded")
    return page

def _connect_to_chrome_with_retry(playwright):
    last_error = None
    for _ in range(CONNECTION_RETRIES):
        try:
            return playwright.chromium.connect_over_cdp(CDP_CONNECTION_URL)
        except Exception as error:
            last_error = error
            time.sleep(CONNECTION_RETRY_WAIT_SECONDS)
    raise RuntimeError("Não foi possível conectar ao Chrome. Verifique se ele foi aberto pela etapa 3.") from last_error

def _get_or_create_browser_context(browser):
    if browser.contexts:
        return browser.contexts[0]
    return browser.new_context()

def _get_chrome_profile_dir() -> Path:
    profile_dir = MIND7_PROFILES_DIR / CHROME_PROFILE_DIR_NAME
    profile_dir.mkdir(parents=True, exist_ok=True)
    return profile_dir