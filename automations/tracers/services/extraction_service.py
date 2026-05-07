"""
Serviço principal responsável pela coleta de veículos no Tracers.
"""

from automations.tracers.config.settings import (
    MAX_SCROLLS,
    MAX_SCREENS_WITHOUT_NEW_ITEMS,
)

from automations.tracers.constants.messages import (
    APP_TOTAL_CASES_MESSAGE,
    EXPECTED_TOTAL_FOUND_MESSAGE,
    EXPECTED_TOTAL_REACHED_MESSAGE,
    EXCEL_SAVED_MESSAGE,
    FINAL_RECORDS_MESSAGE,
    FINAL_SUMMARY_TITLE,
    FINAL_TOTAL_EXCEL_MESSAGE,
    NEW_RECORDS_SCREEN_MESSAGE,
    NO_NEW_ITEMS_MESSAGE,
    SAVE_TO_EXCEL_MESSAGE,
    SAVING_EXCEL_MESSAGE,
    TOTAL_CLASSIFIED_MESSAGE,
    TOTAL_RECORDS_MESSAGE,
    TRACERS_COLLECTION_STARTED_MESSAGE,
    TRACERS_HEADER,
    TRACERS_INTERFACE_CONFIRMATION_MESSAGE,
    TRACERS_START_INSTRUCTIONS,
    TRACERS_TITLE,
)

from automations.tracers.services.adb_service import (
    capture_window_xml,
    swipe_up,
)

from automations.tracers.services.parser_service import (
    extract_total_cases,
    parse_vehicle_records,
)

from automations.tracers.services.xml_service import (
    extract_texts_from_xml,
)

from backend.core.paths import (
    TRACERS_EXCEL_FILE,
    TRACERS_WINDOW_DUMP_FILE,
)


def show_start_instructions() -> None:
    print(TRACERS_HEADER, flush=True)
    print(TRACERS_TITLE, flush=True)
    print(TRACERS_HEADER, flush=True)
    print("", flush=True)

    for instruction in TRACERS_START_INSTRUCTIONS:
        print(instruction, flush=True)

    print("", flush=True)

    print(
        TRACERS_INTERFACE_CONFIRMATION_MESSAGE,
        flush=True,
    )


def collect_vehicle_records() -> list[dict]:
    viewed_plates = set()
    excel_records = []

    viewed_currency_records = set()
    viewed_unknown_model_records = set()
    viewed_records_without_plate = set()
    viewed_complete_unknown_records = set()

    counters = {
        "com_valor_r": 0,
        "sem_modelo_nao_informado": 0,
        "sem_placa": 0,
        "completo_nao_informado": 0,
    }

    screens_without_new_items = 0
    expected_total = None

    print("", flush=True)
    print(TRACERS_COLLECTION_STARTED_MESSAGE, flush=True)

    for current_screen in range(1, MAX_SCROLLS + 1):
        print(
            f"\n--- Tela {current_screen}/{MAX_SCROLLS} ---",
            flush=True,
        )

        capture_window_xml()

        texts = extract_texts_from_xml(
            TRACERS_WINDOW_DUMP_FILE
        )

        if expected_total is None:
            expected_total = extract_total_cases(texts)

            if expected_total:
                print(
                    EXPECTED_TOTAL_FOUND_MESSAGE.format(
                        total=expected_total,
                    ),
                    flush=True,
                )

        records, statistics = parse_vehicle_records(texts)

        new_records_in_screen = 0

        for record in statistics["com_valor_r"]:
            key = record["placa"].replace(" ", "").upper()

            if key not in viewed_currency_records:
                viewed_currency_records.add(key)
                counters["com_valor_r"] += 1

        for record in statistics["sem_modelo_nao_informado"]:
            key = record["placa"].replace(" ", "").upper()

            if key not in viewed_unknown_model_records:
                viewed_unknown_model_records.add(key)
                counters["sem_modelo_nao_informado"] += 1

        for record in statistics["completo_nao_informado"]:
            key = record["placa"].replace(" ", "").upper()

            if key not in viewed_complete_unknown_records:
                viewed_complete_unknown_records.add(key)
                counters["completo_nao_informado"] += 1

        for record in statistics["sem_placa"]:
            key = f"{record['modelo']}|{record['valor']}"

            if key not in viewed_records_without_plate:
                viewed_records_without_plate.add(key)
                counters["sem_placa"] += 1

        for record in records:
            key = record["placa"].replace(" ", "").upper()

            if key not in viewed_plates:
                viewed_plates.add(key)

                excel_records.append(record)

                new_records_in_screen += 1

                print(
                    SAVE_TO_EXCEL_MESSAGE.format(
                        record=record,
                    ),
                    flush=True,
                )

        total_classified = (
            counters["com_valor_r"]
            + counters["sem_modelo_nao_informado"]
            + counters["sem_placa"]
            + counters["completo_nao_informado"]
        )

        print(
            NEW_RECORDS_SCREEN_MESSAGE.format(
                count=new_records_in_screen,
            ),
            flush=True,
        )

        print(
            TOTAL_RECORDS_MESSAGE.format(
                count=len(excel_records),
            ),
            flush=True,
        )

        print(
            TOTAL_CLASSIFIED_MESSAGE.format(
                count=total_classified,
            ),
            flush=True,
        )

        if expected_total and total_classified >= expected_total:
            print("", flush=True)
            print(
                EXPECTED_TOTAL_REACHED_MESSAGE,
                flush=True,
            )
            break

        if new_records_in_screen == 0:
            screens_without_new_items += 1
        else:
            screens_without_new_items = 0

        if (
            screens_without_new_items
            >= MAX_SCREENS_WITHOUT_NEW_ITEMS
        ):
            print("", flush=True)
            print(NO_NEW_ITEMS_MESSAGE, flush=True)
            break

        swipe_up()

    _print_final_summary(
        counters,
        excel_records,
        expected_total,
    )

    return excel_records


def _print_final_summary(counters: dict,excel_records: list[dict],expected_total: int | None,) -> None:
    print("", flush=True)
    print(TRACERS_HEADER, flush=True)
    print(FINAL_SUMMARY_TITLE, flush=True)
    print(TRACERS_HEADER, flush=True)
    print(f"{counters['com_valor_r']} placas encontradas "f"de veículos que contêm valores em R$",flush=True,)

    print(
        f"{counters['sem_modelo_nao_informado']} placas "
        f"encontradas de veículos sem modelo "
        f"e com valor Não informado",
        flush=True,
    )

    print(
        f"{counters['sem_placa']} veículos encontrados "
        f"que não contêm placa do carro",
        flush=True,
    )

    print(
        f"{counters['completo_nao_informado']} placas "
        f"encontradas de veículos com modelo "
        f"e valor Não informado",
        flush=True,
    )

    print("", flush=True)

    print(
        FINAL_TOTAL_EXCEL_MESSAGE.format(
            count=len(excel_records),
        ),
        flush=True,
    )

    if expected_total:
        print(
            APP_TOTAL_CASES_MESSAGE.format(
                count=expected_total,
            ),
            flush=True,
        )