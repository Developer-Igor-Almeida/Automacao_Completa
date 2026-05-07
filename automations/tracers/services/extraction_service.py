"""
Serviço principal responsável pela coleta de veículos no Tracers.
"""

from automations.tracers.config.settings import (MAX_SCROLLS,MAX_SCREENS_WITHOUT_NEW_ITEMS,)

from automations.tracers.constants.messages import (APP_TOTAL_CASES_MESSAGE,EXPECTED_TOTAL_FOUND_MESSAGE,EXPECTED_TOTAL_REACHED_MESSAGE,
    EXCEL_SAVED_MESSAGE, FINAL_RECORDS_MESSAGE,FINAL_SUMMARY_TITLE,
    FINAL_TOTAL_EXCEL_MESSAGE,NEW_RECORDS_SCREEN_MESSAGE,NO_NEW_ITEMS_MESSAGE,
    SAVE_TO_EXCEL_MESSAGE,SAVING_EXCEL_MESSAGE,TOTAL_CLASSIFIED_MESSAGE,
    TOTAL_RECORDS_MESSAGE,TRACERS_COLLECTION_STARTED_MESSAGE,TRACERS_HEADER,
    TRACERS_INTERFACE_CONFIRMATION_MESSAGE,TRACERS_START_INSTRUCTIONS,TRACERS_TITLE,
)

from automations.tracers.services.adb_service import (capture_window_xml,swipe_up,)
from automations.tracers.services.parser_service import (extract_total_cases,parse_vehicle_records,)
from automations.tracers.services.xml_service import (extract_texts_from_xml,)
from backend.core.paths import (TRACERS_EXCEL_FILE,TRACERS_WINDOW_DUMP_FILE,)
from automations.tracers.services.statistics_service import append_new_excel_records, calculate_total_classified, create_empty_counters, create_seen_registry, update_statistics


def show_start_instructions() -> None:
    print(TRACERS_HEADER, flush=True)
    print(TRACERS_TITLE, flush=True)
    print(TRACERS_HEADER, flush=True)
    print("", flush=True)

    for instruction in TRACERS_START_INSTRUCTIONS:
        print(instruction, flush=True)

    print("", flush=True)
    print(TRACERS_INTERFACE_CONFIRMATION_MESSAGE,flush=True,)

def collect_vehicle_records() -> list[dict]:
    excel_records = []
    seen_registry = create_seen_registry()
    counters = create_empty_counters()
    screens_without_new_items = 0
    expected_total = None
    print("", flush=True)
    print(TRACERS_COLLECTION_STARTED_MESSAGE, flush=True)
    for current_screen in range(1, MAX_SCROLLS + 1):
        _print_current_screen(current_screen)
        capture_window_xml()
        texts = extract_texts_from_xml(TRACERS_WINDOW_DUMP_FILE)
        expected_total = _resolve_expected_total(expected_total=expected_total, texts=texts)
        records, statistics = parse_vehicle_records(texts)
        update_statistics(statistics=statistics, counters=counters, seen_registry=seen_registry)
        new_records = append_new_excel_records(records=records, excel_records=excel_records, seen_registry=seen_registry)
        _print_new_excel_records(new_records)
        total_classified = calculate_total_classified(counters)
        _print_screen_summary(new_records_count=len(new_records), total_excel_records=len(excel_records), total_classified=total_classified)
        if _should_stop_by_expected_total(expected_total=expected_total, total_classified=total_classified):
            break
        screens_without_new_items = _update_screens_without_new_items(screens_without_new_items=screens_without_new_items, new_records_count=len(new_records))
        if _should_stop_by_no_new_items(screens_without_new_items):
            break
        swipe_up()
    _print_final_summary(counters, excel_records, expected_total)
    return excel_records

def _print_final_summary(counters: dict, excel_records: list[dict], expected_total: int | None) -> None:
    print("", flush=True)
    print(TRACERS_HEADER, flush=True)
    print(FINAL_SUMMARY_TITLE, flush=True)
    print(TRACERS_HEADER, flush=True)
    print(f"{counters['com_valor_r']} placas encontradas de veículos que contêm valores em R$", flush=True)
    print(f"{counters['sem_modelo_nao_informado']} placas encontradas de veículos sem modelo e com valor Não informado", flush=True)
    print(f"{counters['sem_placa']} veículos encontrados que não contêm placa do carro", flush=True)
    print(f"{counters['completo_nao_informado']} placas encontradas de veículos com modelo e valor Não informado", flush=True)
    print("", flush=True)
    print(FINAL_TOTAL_EXCEL_MESSAGE.format(count=len(excel_records)), flush=True)
    if expected_total:
        print(APP_TOTAL_CASES_MESSAGE.format(count=expected_total), flush=True)

def show_start_instructions() -> None:
    print(TRACERS_HEADER, flush=True)
    print(TRACERS_TITLE, flush=True)
    print(TRACERS_HEADER, flush=True)
    print("", flush=True)
    for instruction in TRACERS_START_INSTRUCTIONS:
        print(instruction, flush=True)
    print("", flush=True)
    print(TRACERS_INTERFACE_CONFIRMATION_MESSAGE, flush=True)

def collect_vehicle_records() -> list[dict]:
    excel_records = []
    seen_registry = create_seen_registry()
    counters = create_empty_counters()
    screens_without_new_items = 0
    expected_total = None
    print("", flush=True)
    print(TRACERS_COLLECTION_STARTED_MESSAGE, flush=True)
    for current_screen in range(1, MAX_SCROLLS + 1):
        _print_current_screen(current_screen)
        capture_window_xml()
        texts = extract_texts_from_xml(TRACERS_WINDOW_DUMP_FILE)
        expected_total = _resolve_expected_total(expected_total=expected_total, texts=texts)
        records, statistics = parse_vehicle_records(texts)
        update_statistics(statistics=statistics, counters=counters, seen_registry=seen_registry)
        new_records = append_new_excel_records(records=records, excel_records=excel_records, seen_registry=seen_registry)
        _print_new_excel_records(new_records)
        total_classified = calculate_total_classified(counters)
        _print_screen_summary(new_records_count=len(new_records), total_excel_records=len(excel_records), total_classified=total_classified)
        if _should_stop_by_expected_total(expected_total=expected_total, total_classified=total_classified):
            break
        screens_without_new_items = _update_screens_without_new_items(screens_without_new_items=screens_without_new_items, new_records_count=len(new_records))
        if _should_stop_by_no_new_items(screens_without_new_items):
            break
        swipe_up()
    _print_final_summary(counters, excel_records, expected_total)
    return excel_records

def _print_final_summary(counters: dict, excel_records: list[dict], expected_total: int | None) -> None:
    print("", flush=True)
    print(TRACERS_HEADER, flush=True)
    print(FINAL_SUMMARY_TITLE, flush=True)
    print(TRACERS_HEADER, flush=True)
    print(f"{counters['com_valor_r']} placas encontradas de veículos que contêm valores em R$", flush=True)
    print(f"{counters['sem_modelo_nao_informado']} placas encontradas de veículos sem modelo e com valor Não informado", flush=True)
    print(f"{counters['sem_placa']} veículos encontrados que não contêm placa do carro", flush=True)
    print(f"{counters['completo_nao_informado']} placas encontradas de veículos com modelo e valor Não informado", flush=True)
    print("", flush=True)
    print(FINAL_TOTAL_EXCEL_MESSAGE.format(count=len(excel_records)), flush=True)
    if expected_total:
        print(APP_TOTAL_CASES_MESSAGE.format(count=expected_total), flush=True)

def _print_new_excel_records(records: list[dict]) -> None:
    for record in records:
        print(SAVE_TO_EXCEL_MESSAGE.format(record=record), flush=True)

def _print_current_screen(current_screen: int) -> None:
    print(f"\n--- Tela {current_screen}/{MAX_SCROLLS} ---", flush=True)

def _resolve_expected_total(expected_total: int | None, texts: list[str]) -> int | None:
    if expected_total is not None:
        return expected_total
    expected_total = extract_total_cases(texts)
    if expected_total:
        print(EXPECTED_TOTAL_FOUND_MESSAGE.format(total=expected_total), flush=True)
    return expected_total

def _print_screen_summary(new_records_count: int, total_excel_records: int, total_classified: int) -> None:
    print(NEW_RECORDS_SCREEN_MESSAGE.format(count=new_records_count), flush=True)
    print(TOTAL_RECORDS_MESSAGE.format(count=total_excel_records), flush=True)
    print(TOTAL_CLASSIFIED_MESSAGE.format(count=total_classified), flush=True)

def _should_stop_by_expected_total(expected_total: int | None, total_classified: int) -> bool:
    if not expected_total:
        return False
    if total_classified < expected_total:
        return False
    print("", flush=True)
    print(EXPECTED_TOTAL_REACHED_MESSAGE, flush=True)
    return True

def _update_screens_without_new_items(screens_without_new_items: int, new_records_count: int) -> int:
    if new_records_count == 0:
        return screens_without_new_items + 1
    return 0

def _should_stop_by_no_new_items(screens_without_new_items: int) -> bool:
    if screens_without_new_items < MAX_SCREENS_WITHOUT_NEW_ITEMS:
        return False
    print("", flush=True)
    print(NO_NEW_ITEMS_MESSAGE, flush=True)
    return True