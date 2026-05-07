
"""
Serviço responsável por controlar estatísticas e duplicidades
durante a coleta do Tracers.
"""

from automations.tracers.constants.parser import (
    STATISTIC_COMPLETE_UNKNOWN_VALUE,
    STATISTIC_WITH_CURRENCY_VALUE,
    STATISTIC_WITHOUT_MODEL_UNKNOWN_VALUE,
    STATISTIC_WITHOUT_PLATE,
)


SEEN_PLATES_KEY = "plates"


def create_empty_counters() -> dict:
    return {
        STATISTIC_WITH_CURRENCY_VALUE: 0,
        STATISTIC_WITHOUT_MODEL_UNKNOWN_VALUE: 0,
        STATISTIC_WITHOUT_PLATE: 0,
        STATISTIC_COMPLETE_UNKNOWN_VALUE: 0,
    }


def create_seen_registry() -> dict:
    return {
        SEEN_PLATES_KEY: set(),
        STATISTIC_WITH_CURRENCY_VALUE: set(),
        STATISTIC_WITHOUT_MODEL_UNKNOWN_VALUE: set(),
        STATISTIC_WITHOUT_PLATE: set(),
        STATISTIC_COMPLETE_UNKNOWN_VALUE: set(),
    }


def update_statistics(statistics: dict, counters: dict, seen_registry: dict) -> None:
    _update_plate_based_counter(records=statistics[STATISTIC_WITH_CURRENCY_VALUE], seen_items=seen_registry[STATISTIC_WITH_CURRENCY_VALUE], counters=counters, counter_key=STATISTIC_WITH_CURRENCY_VALUE)
    _update_plate_based_counter(records=statistics[STATISTIC_WITHOUT_MODEL_UNKNOWN_VALUE], seen_items=seen_registry[STATISTIC_WITHOUT_MODEL_UNKNOWN_VALUE], counters=counters, counter_key=STATISTIC_WITHOUT_MODEL_UNKNOWN_VALUE)
    _update_plate_based_counter(records=statistics[STATISTIC_COMPLETE_UNKNOWN_VALUE], seen_items=seen_registry[STATISTIC_COMPLETE_UNKNOWN_VALUE], counters=counters, counter_key=STATISTIC_COMPLETE_UNKNOWN_VALUE)
    _update_without_plate_counter(records=statistics[STATISTIC_WITHOUT_PLATE], seen_items=seen_registry[STATISTIC_WITHOUT_PLATE], counters=counters)


def append_new_excel_records(records: list[dict], excel_records: list[dict], seen_registry: dict) -> list[dict]:
    new_records = []
    for record in records:
        key = _get_plate_key(record)
        if key in seen_registry[SEEN_PLATES_KEY]:
            continue
        seen_registry[SEEN_PLATES_KEY].add(key)
        excel_records.append(record)
        new_records.append(record)
    return new_records


def calculate_total_classified(counters: dict) -> int:
    return sum(counters.values())


def _update_plate_based_counter(records: list[dict], seen_items: set, counters: dict, counter_key: str) -> None:
    for record in records:
        key = _get_plate_key(record)
        if key in seen_items:
            continue
        seen_items.add(key)
        counters[counter_key] += 1


def _update_without_plate_counter(records: list[dict], seen_items: set, counters: dict) -> None:
    for record in records:
        key = _get_without_plate_key(record)
        if key in seen_items:
            continue
        seen_items.add(key)
        counters[STATISTIC_WITHOUT_PLATE] += 1


def _get_plate_key(record: dict) -> str:
    return record["placa"].replace(" ", "").upper()


def _get_without_plate_key(record: dict) -> str:
    return f"{record['modelo']}|{record['valor']}"