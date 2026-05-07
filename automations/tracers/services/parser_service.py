"""
Serviço responsável por interpretar os textos extraídos do XML
e transformar em registros de veículos.
"""

import re

from automations.tracers.services.plate_service import (
    extract_plate,
    is_currency_value,
    is_unknown_value,
    is_value_line,
    normalize_text,
)


EXACT_TEXTS_TO_IGNORE = {
    "Pesquisar",
    "Scanner de Placas",
}

STATISTICS_KEYS = {
    "with_currency_value": "com_valor_r",
    "without_model_unknown_value": "sem_modelo_nao_informado",
    "without_plate": "sem_placa",
    "complete_unknown_value": "completo_nao_informado",
}


def should_ignore_as_model(text: str) -> bool:
    normalized_text = text.lower().strip()

    if re.search(r"\d+\s+casos?", normalized_text):
        return True

    if "pesquisar" in normalized_text:
        return True

    if "scanner de placas" in normalized_text:
        return True

    return False


def extract_total_cases(texts: list[str]) -> int | None:
    for text in texts:
        match = re.search(r"(\d+)\s+casos?", text.lower())

        if match:
            return int(match.group(1))

    return None


def parse_vehicle_records(texts: list[str]) -> tuple[list[dict], dict]:
    normalized_texts = [
        normalize_text(text)
        for text in texts
        if text
    ]

    records_to_excel = []
    statistics = _create_empty_statistics()

    for current_index, current_text in enumerate(normalized_texts):
        if not is_value_line(current_text):
            continue

        value = current_text
        previous_block = _get_previous_vehicle_block(
            normalized_texts,
            current_index,
        )

        plate, model = _extract_plate_and_model(previous_block)

        record = {
            "placa": plate,
            "modelo": model,
            "valor": value,
        }

        _classify_record(
            record=record,
            statistics=statistics,
            records_to_excel=records_to_excel,
        )

    return records_to_excel, statistics


def _create_empty_statistics() -> dict:
    return {
        "com_valor_r": [],
        "sem_modelo_nao_informado": [],
        "sem_placa": [],
        "completo_nao_informado": [],
    }


def _get_previous_vehicle_block(
    texts: list[str],
    current_index: int,
    max_previous_items: int = 4,
) -> list[str]:
    block = []

    start_index = max(current_index - max_previous_items, -1)

    for previous_index in range(current_index - 1, start_index, -1):
        previous_text = texts[previous_index]

        if previous_text in EXACT_TEXTS_TO_IGNORE:
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

        if (
            not found_plate
            and not model
            and not should_ignore_as_model(item)
        ):
            model = item

    return plate, model


def _classify_record(record: dict,statistics: dict,records_to_excel: list[dict],) -> None:
    plate = record["placa"]
    value = record["valor"]
    model = record["modelo"]

    if not plate:
        statistics["sem_placa"].append(record)
        return

    if is_currency_value(value):
        statistics["com_valor_r"].append(record)
        return

    if is_unknown_value(value):
        if model:
            statistics["completo_nao_informado"].append(record)
        else:
            statistics["sem_modelo_nao_informado"].append(record)

        records_to_excel.append(record)