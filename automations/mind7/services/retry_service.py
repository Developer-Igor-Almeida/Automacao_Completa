"""
Serviço responsável por pausas preventivas e retentativas
de placas que caíram em CAPTCHA no Mind7.
"""

import random
import time

from automations.mind7.config.settings import (CAPTCHA_WAIT_SECONDS,LONG_PAUSE_SECONDS,MAX_CAPTCHA_RETRIES,
    MAX_EXTRA_SUCCESS_RETRIES,PAUSE_EVERY_QUERIES,TIME_BETWEEN_QUERIES_SECONDS,
)
from automations.mind7.constants.messages import (BLANK_FOR_NEXT_RUN_MESSAGE,CAPTCHA_RETRY_MESSAGE,DOCUMENT_FOUND_RETRY_MESSAGE,
    DOCUMENT_NOT_FOUND_RETRY_MESSAGE, EXTRA_ATTEMPT_MESSAGE, PENDING_PLATES_MESSAGE,
    PREVENTIVE_PAUSE_MESSAGE, REMAINING_CAPTCHA_MESSAGE,RETRY_ATTEMPT_MESSAGE,
    RETRY_ERROR_MESSAGE,RETRYING_PLATE_MESSAGE, ROUND_SOLVED_MESSAGE,
    STOP_RETRY_MESSAGE,WAIT_BEFORE_RETRY_MESSAGE,
)
from automations.mind7.constants.query import (
    CAPTCHA_RESULT,
    DOCUMENT_NOT_FOUND_VALUE,
    EMPTY_DOCUMENT_VALUE,
    MAX_RETRY_WAIT_SECONDS,
    RETRY_BATCH_SIZE,
    RETRY_CAPTCHA,
    RETRY_PENDING,
    RETRY_SOLVED,
)

from automations.mind7.services.document_service import normalize_plate
from automations.mind7.services.mind7_service import query_plate


def preventive_pause(completed_queries: int) -> None:
    if completed_queries % PAUSE_EVERY_QUERIES == 0:
        print(PREVENTIVE_PAUSE_MESSAGE.format(seconds=LONG_PAUSE_SECONDS), flush=True)
        time.sleep(LONG_PAUSE_SECONDS)
        return
    time.sleep(_random_short_wait())

def retry_captcha_plates(page, worksheet, plate_column: int, document_column: int, captcha_rows: list[int]) -> list[int]:
    attempt = 1
    extra_attempts = 0
    while captcha_rows:
        if _retry_limit_reached(attempt, extra_attempts):
            break
        _print_retry_header(attempt, captcha_rows)
        wait_seconds = _calculate_retry_wait(attempt)
        print(WAIT_BEFORE_RETRY_MESSAGE.format(seconds=wait_seconds), flush=True)
        time.sleep(wait_seconds)
        pending_rows = captcha_rows.copy()
        random.shuffle(pending_rows)
        captcha_rows, solved_in_round = _retry_round(page=page, worksheet=worksheet, plate_column=plate_column, document_column=document_column, pending_rows=pending_rows)
        print(ROUND_SOLVED_MESSAGE.format(count=solved_in_round), flush=True)
        if _should_stop_after_attempt_limit(attempt=attempt, solved_in_round=solved_in_round):
            if solved_in_round > 0:
                extra_attempts += 1
                print(EXTRA_ATTEMPT_MESSAGE, flush=True)
            else:
                print(STOP_RETRY_MESSAGE, flush=True)
                break
        attempt += 1
    _print_remaining_captcha_rows(captcha_rows)
    return captcha_rows

def _retry_round(page, worksheet, plate_column: int, document_column: int, pending_rows: list[int]) -> tuple[list[int], int]:
    captcha_rows = []
    solved_in_round = 0
    for batch in _split_in_batches(pending_rows, RETRY_BATCH_SIZE):
        for row in batch:
            retry_status = _process_retry_row(page=page, worksheet=worksheet, row=row, plate_column=plate_column, document_column=document_column, captcha_rows=captcha_rows)
            if retry_status == RETRY_SOLVED:
                solved_in_round += 1
            if retry_status == RETRY_CAPTCHA:
                return captcha_rows, solved_in_round
            time.sleep(_random_short_wait())
        time.sleep(_random_batch_wait())
    return captcha_rows, solved_in_round


def _process_retry_row(page, worksheet, row: int, plate_column: int, document_column: int, captcha_rows: list[int]) -> str:
    plate = _get_plate_from_row(worksheet=worksheet, row=row, plate_column=plate_column)
    if not plate:
        return RETRY_PENDING
    print(RETRYING_PLATE_MESSAGE.format(plate=plate), flush=True)
    try:
        document = query_plate(page, plate)
        return _handle_retry_result(worksheet=worksheet, row=row, document_column=document_column, plate=plate, document=document, captcha_rows=captcha_rows)
    except Exception as error:
        print(RETRY_ERROR_MESSAGE.format(plate=plate, error=error), flush=True)
        _set_document_value(worksheet=worksheet, row=row, document_column=document_column, value=EMPTY_DOCUMENT_VALUE)
        captcha_rows.append(row)
        return RETRY_PENDING

def _handle_retry_result(worksheet, row: int, document_column: int, plate: str, document: str, captcha_rows: list[int]) -> bool:
    if document == CAPTCHA_RESULT:
        print(CAPTCHA_RETRY_MESSAGE.format(plate=plate), flush=True)
        _set_document_value(worksheet=worksheet, row=row, document_column=document_column, value=EMPTY_DOCUMENT_VALUE)
        captcha_rows.append(row)
        return False
    if document:
        print(DOCUMENT_FOUND_RETRY_MESSAGE.format(plate=plate, document=document), flush=True)
        _set_document_value(worksheet=worksheet, row=row, document_column=document_column, value=document)
        return True
    print(DOCUMENT_NOT_FOUND_RETRY_MESSAGE.format(plate=plate), flush=True)
    _set_document_value(worksheet=worksheet, row=row, document_column=document_column, value=DOCUMENT_NOT_FOUND_VALUE)
    return True

def _handle_retry_result(worksheet, row: int, document_column: int, plate: str, document: str, captcha_rows: list[int]) -> str:
    if document == CAPTCHA_RESULT:
        print(CAPTCHA_RETRY_MESSAGE.format(plate=plate), flush=True)
        _set_document_value(worksheet=worksheet, row=row, document_column=document_column, value=EMPTY_DOCUMENT_VALUE)
        captcha_rows.append(row)
        return RETRY_CAPTCHA
    if document:
        print(DOCUMENT_FOUND_RETRY_MESSAGE.format(plate=plate, document=document), flush=True)
        _set_document_value(worksheet=worksheet, row=row, document_column=document_column, value=document)
        return RETRY_SOLVED
    print(DOCUMENT_NOT_FOUND_RETRY_MESSAGE.format(plate=plate), flush=True)
    _set_document_value(worksheet=worksheet, row=row, document_column=document_column, value=DOCUMENT_NOT_FOUND_VALUE)
    return RETRY_SOLVED

def _set_document_value(worksheet, row: int, document_column: int, value: str) -> None:
    worksheet.cell(row=row, column=document_column).value = value

def _calculate_retry_wait(attempt: int) -> int:
    return min(CAPTCHA_WAIT_SECONDS * attempt, MAX_RETRY_WAIT_SECONDS)

def _retry_limit_reached(attempt: int, extra_attempts: int) -> bool:
    return attempt > MAX_CAPTCHA_RETRIES and extra_attempts >= MAX_EXTRA_SUCCESS_RETRIES

def _should_stop_after_attempt_limit(attempt: int, solved_in_round: int) -> bool:
    return attempt >= MAX_CAPTCHA_RETRIES

def _split_in_batches(items: list[int], batch_size: int) -> list[list[int]]:
    return [items[index:index + batch_size] for index in range(0, len(items), batch_size)]

def _random_short_wait() -> float:
    return random.uniform(TIME_BETWEEN_QUERIES_SECONDS * 0.8, TIME_BETWEEN_QUERIES_SECONDS * 1.4)

def _random_batch_wait() -> float:
    return random.uniform(5, 12)

def _print_retry_header(attempt: int, captcha_rows: list[int]) -> None:
    print("", flush=True)
    print(RETRY_ATTEMPT_MESSAGE.format(attempt=attempt), flush=True)
    print(PENDING_PLATES_MESSAGE.format(count=len(captcha_rows)), flush=True)

def _print_remaining_captcha_rows(captcha_rows: list[int]) -> None:
    if not captcha_rows:
        return
    print(REMAINING_CAPTCHA_MESSAGE.format(count=len(captcha_rows)), flush=True)
    print(BLANK_FOR_NEXT_RUN_MESSAGE, flush=True)
    
def _get_plate_from_row(worksheet, row, plate_column):
    value = worksheet.cell(row=row, column=plate_column).value
    return str(value).strip() if value else ""