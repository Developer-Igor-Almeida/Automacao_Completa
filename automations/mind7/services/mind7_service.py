"""
Serviço responsável por consultar placas no Mind7.
"""

import re
import time

from automations.mind7.config.settings import (
    AFTER_TYPE_WAIT_SECONDS,
    DOCUMENT_INPUT_SELECTOR,
    MIND7_URL,
    PAGE_LOAD_WAIT_SECONDS,
    QUERY_BUTTON_TEXT,
    RESULT_POLL_INTERVAL_SECONDS,
    RESULT_WAIT_TIMEOUT_SECONDS,
    TYPE_DELAY_MS,
)
from automations.mind7.services.document_service import (
    extract_document_from_text,
)


CAPTCHA_RESULT = "CAPTCHA"


def query_plate(page, plate: str) -> str:
    print(f"Consultando placa: {plate}", flush=True)

    page.goto(MIND7_URL, wait_until="domcontentloaded")
    time.sleep(PAGE_LOAD_WAIT_SECONDS)

    input_field = page.locator(DOCUMENT_INPUT_SELECTOR)
    input_field.wait_for(timeout=15000)

    input_field.click()
    input_field.press("Control+A")
    input_field.press("Backspace")
    input_field.type(plate, delay=TYPE_DELAY_MS)

    time.sleep(AFTER_TYPE_WAIT_SECONDS)

    query_button = page.get_by_role(
        "button",
        name=re.compile(QUERY_BUTTON_TEXT, re.I),
    )

    query_button.click()

    clean_plate = plate.replace(" ", "").upper()

    start_time = time.time()

    while time.time() - start_time < RESULT_WAIT_TIMEOUT_SECONDS:
        body_text = page.locator("body").inner_text(timeout=5000)

        upper_text = body_text.upper()
        clean_text = upper_text.replace(" ", "").replace("-", "")

        if _has_captcha_error(upper_text):
            return CAPTCHA_RESULT

        if clean_plate in clean_text:
            document = extract_document_from_text(body_text)

            if document:
                return document

            if "PROPRIETÁRIO" in upper_text:
                return ""

        time.sleep(RESULT_POLL_INTERVAL_SECONDS)

    return ""


def _has_captcha_error(text: str) -> bool:
    return (
        "NÃO FOI POSSÍVEL VALIDAR SUA CONSULTA" in text
        or "NAO FOI POSSIVEL VALIDAR SUA CONSULTA" in text
    )