"""
Serviço responsável por interpretar os textos extraídos do XML
e transformar em registros de veículos.
"""

import re

from automations.tracers.constants.parser import (EXACT_TEXTS_TO_IGNORE,MAX_PREVIOUS_VEHICLE_ITEMS,STATISTIC_COMPLETE_UNKNOWN_VALUE,STATISTIC_WITH_CURRENCY_VALUE,STATISTIC_WITHOUT_MODEL_UNKNOWN_VALUE,
    STATISTIC_WITHOUT_PLATE,TEXT_FRAGMENTS_TO_IGNORE_AS_MODEL,TOTAL_CASES_REGEX,)
from automations.tracers.services.plate_service import (extract_plate,is_currency_value,is_unknown_value,is_value_line,normalize_text,)


def should_ignore_as_model(text: str) -> bool:
    normalized_text = text.lower().strip()
    return (_has_total_cases_text(normalized_text) or _has_ignored_model_fragment(normalized_text))

def extract_total_cases(texts: list[str]) -> int | None:
    for text in texts:
        total_cases = _extract_total_cases_from_text(text)
        if total_cases is not None:
            return total_cases
    return None

def parse_vehicle_records(texts: list[str]) -> tuple[list[dict], dict]:
    normalized_texts = _normalize_texts(texts)
    records_to_excel = []
    statistics = _create_empty_statistics()
    for current_index, current_text in enumerate(normalized_texts):
        if not is_value_line(current_text):
            continue
        record = _build_vehicle_record(texts=normalized_texts, current_index=current_index, value=current_text)
        _classify_record(record=record, statistics=statistics, records_to_excel=records_to_excel)
    return records_to_excel, statistics

def _normalize_texts(texts: list[str]) -> list[str]:
    return [normalize_text(text) for text in texts if text]

def _build_vehicle_record(texts: list[str], current_index: int, value: str) -> dict:
    previous_block = _get_previous_vehicle_block(texts=texts, current_index=current_index)
    plate, model = _extract_plate_and_model(previous_block)
    return {"placa": plate, "modelo": model, "valor": value}

def _create_empty_statistics() -> dict:
    return {
        STATISTIC_WITH_CURRENCY_VALUE: [],
        STATISTIC_WITHOUT_MODEL_UNKNOWN_VALUE: [],
        STATISTIC_WITHOUT_PLATE: [],
        STATISTIC_COMPLETE_UNKNOWN_VALUE: [],
    }

def _get_previous_vehicle_block(texts: list[str], current_index: int) -> list[str]:
    block = []
    start_index = max(current_index - MAX_PREVIOUS_VEHICLE_ITEMS, -1)
    for previous_index in range(current_index - 1, start_index, -1):
        previous_text = texts[previous_index]
        if _should_ignore_exact_text(previous_text):
            continue
        if is_value_line(previous_text):
            break
        block.insert(0, previous_text)
    return block

def _extract_plate_and_model(block: list[str]) -> tuple[str, str]:
    plate = ""
    model = ""
    for item in block:
        found_plate = extract_plate(item)
        if found_plate and not plate:
            plate = found_plate
            continue
        if _can_use_as_model(item=item, found_plate=found_plate, current_model=model):
            model = item
    return plate, model

def _classify_record(record: dict, statistics: dict, records_to_excel: list[dict]) -> None:
    if not record["placa"]:
        statistics[STATISTIC_WITHOUT_PLATE].append(record)
        return
    if is_currency_value(record["valor"]):
        statistics[STATISTIC_WITH_CURRENCY_VALUE].append(record)
        return
    if not is_unknown_value(record["valor"]):
        return
    statistic_key = _get_unknown_value_statistic_key(record)
    statistics[statistic_key].append(record)
    records_to_excel.append(record)

def _get_unknown_value_statistic_key(record: dict) -> str:
    if record["modelo"]:
        return STATISTIC_COMPLETE_UNKNOWN_VALUE
    return STATISTIC_WITHOUT_MODEL_UNKNOWN_VALUE

def _can_use_as_model(item: str, found_plate: str | None, current_model: str) -> bool:
    return (not found_plate and not current_model and not should_ignore_as_model(item))

def _should_ignore_exact_text(text: str) -> bool:
    return text in EXACT_TEXTS_TO_IGNORE

def _has_ignored_model_fragment(text: str) -> bool:
    return any(fragment in text for fragment in TEXT_FRAGMENTS_TO_IGNORE_AS_MODEL)

def _has_total_cases_text(text: str) -> bool:
    return bool(re.search(TOTAL_CASES_REGEX, text))

def _extract_total_cases_from_text(text: str) -> int | None:
    match = re.search(TOTAL_CASES_REGEX, text.lower())
    if not match:
        return None
    return int(match.group(1))