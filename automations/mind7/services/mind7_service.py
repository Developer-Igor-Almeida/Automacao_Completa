"""
Serviço responsável por consultar placas no Mind7.
"""

import re
import time

from automations.mind7.config.settings import (AFTER_TYPE_WAIT_SECONDS, DOCUMENT_INPUT_SELECTOR, MIND7_URL,
  PAGE_LOAD_WAIT_SECONDS,QUERY_BUTTON_TEXT,RESULT_POLL_INTERVAL_SECONDS,
  RESULT_WAIT_TIMEOUT_SECONDS,TYPE_DELAY_MS,CLOUDFLARE_SUCCESS_WAIT_SECONDS, CLOUDFLARE_POLL_INTERVAL_SECONDS
)

from automations.mind7.constants.query import (CAPTCHA_ERROR_MESSAGES,CAPTCHA_RESULT,OWNER_SECTION_KEYWORD,)
from automations.mind7.constants.messages import (MIND7_VALIDATION_WAIT_MESSAGE, WAITING_CLOUDFLARE_MESSAGE)

from automations.mind7.services.document_service import (extract_document_from_text,)

def query_plate(page, plate: str) -> str:
    _open_query_page(page)

    _fill_plate_input(page=page,plate=plate,)

    _wait_cloudflare_success(page)

    _click_query_button(page)

    return _wait_for_query_result(page=page,plate=plate,)


def _open_query_page(page) -> None:
    page.goto(MIND7_URL,wait_until="domcontentloaded",)
    time.sleep(PAGE_LOAD_WAIT_SECONDS)


def _fill_plate_input(page,plate: str,) -> None:
    input_field = page.locator(DOCUMENT_INPUT_SELECTOR)
    input_field.wait_for(timeout=15000)

    input_field.click()

    input_field.press("Control+A")
    input_field.press("Backspace")

    input_field.type(plate,delay=TYPE_DELAY_MS,)

    time.sleep(AFTER_TYPE_WAIT_SECONDS)


def _click_query_button(page) -> None:
    query_button = page.get_by_role("button",name=re.compile(QUERY_BUTTON_TEXT,re.I,),)

    query_button.click()


def _wait_for_query_result(page,plate: str,) -> str:
    normalized_plate = _normalize_plate_for_search(plate)

    start_time = time.time()

    while (time.time() - start_time < RESULT_WAIT_TIMEOUT_SECONDS):
        body_text = _get_page_text(page)

        normalized_body_text = (_normalize_body_text(body_text))

        upper_text = body_text.upper()

        if _has_captcha_error(upper_text):
            return CAPTCHA_RESULT

        if normalized_plate in normalized_body_text:
            document = extract_document_from_text(body_text)

            if document:
                return document

            if OWNER_SECTION_KEYWORD in upper_text:
                return ""

        time.sleep(RESULT_POLL_INTERVAL_SECONDS)

    return ""


def _get_page_text(page) -> str:
    return page.locator("body").inner_text(timeout=5000)


def _normalize_plate_for_search(plate: str,) -> str:
    return (plate.replace(" ", "").replace("-", "").upper())


def _normalize_body_text(text: str,) -> str:
    return (text.upper().replace(" ", "").replace("-", ""))


def _has_captcha_error(text: str,) -> bool:
    return any(message in text for message in CAPTCHA_ERROR_MESSAGES)

def wait_until_page_is_ready(page) -> None:
    
    start_time = time.time()

    while time.time() - start_time < 60:
        body_text = page.locator("body").inner_text(timeout=5000)
        upper_text = body_text.upper()

        if not _has_captcha_error(upper_text):
            return

        print(MIND7_VALIDATION_WAIT_MESSAGE,flush=True,)

        time.sleep(5)

def _wait_cloudflare_success(page) -> None:
    print(WAITING_CLOUDFLARE_MESSAGE, flush=True)

    start_time = time.time()

    while time.time() - start_time < CLOUDFLARE_SUCCESS_WAIT_SECONDS:
        body_text = page.locator("body").inner_text(timeout=5000).lower()

        if "sucesso" in body_text:
            return

        time.sleep(CLOUDFLARE_POLL_INTERVAL_SECONDS)