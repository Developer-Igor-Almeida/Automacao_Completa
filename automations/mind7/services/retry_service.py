"""
Serviço responsável por pausas preventivas e retentativas
de placas que caíram em CAPTCHA no Mind7.
"""

import time

from automations.mind7.config.settings import (
    CAPTCHA_WAIT_SECONDS,
    LONG_PAUSE_SECONDS,
    MAX_CAPTCHA_RETRIES,
    MAX_EXTRA_SUCCESS_RETRIES,
    PAUSE_EVERY_QUERIES,
    TIME_BETWEEN_QUERIES_SECONDS,
)
from automations.mind7.services.document_service import normalize_plate
from automations.mind7.services.mind7_service import (
    CAPTCHA_RESULT,
    query_plate,
)


def preventive_pause(completed_queries: int) -> None:
    if completed_queries % PAUSE_EVERY_QUERIES == 0:
        print(
            f"Pausa preventiva de {LONG_PAUSE_SECONDS}s "
            "para reduzir CAPTCHA...",
            flush=True,
        )

        time.sleep(LONG_PAUSE_SECONDS)
        return

    time.sleep(TIME_BETWEEN_QUERIES_SECONDS)


def retry_captcha_plates(
    page,
    worksheet,
    plate_column: int,
    document_column: int,
    captcha_rows: list[int],
) -> list[int]:
    attempt = 1
    extra_attempts = 0

    while captcha_rows:
        if (
            attempt > MAX_CAPTCHA_RETRIES
            and extra_attempts >= MAX_EXTRA_SUCCESS_RETRIES
        ):
            break

        print(
            f"\nTentativa {attempt} para placas com CAPTCHA.",
            flush=True,
        )
        print(
            f"Placas pendentes: {len(captcha_rows)}",
            flush=True,
        )
        print(
            f"Aguardando {CAPTCHA_WAIT_SECONDS}s antes de tentar novamente...",
            flush=True,
        )

        time.sleep(CAPTCHA_WAIT_SECONDS)

        pending_rows = captcha_rows
        captcha_rows = []
        solved_in_round = 0

        for row in pending_rows:
            original_plate = worksheet.cell(
                row=row,
                column=plate_column,
            ).value

            plate = normalize_plate(original_plate)

            if not plate:
                continue

            print(f"Retentando placa: {plate}", flush=True)

            try:
                document = query_plate(page, plate)

                if document == CAPTCHA_RESULT:
                    print(
                        f"CAPTCHA novamente na placa {plate}. "
                        "Vai tentar novamente depois.",
                        flush=True,
                    )

                    worksheet.cell(
                        row=row,
                        column=document_column,
                    ).value = ""

                    captcha_rows.append(row)

                elif document:
                    print(
                        f"CPF/CNPJ encontrado para {plate}: {document}",
                        flush=True,
                    )

                    worksheet.cell(
                        row=row,
                        column=document_column,
                    ).value = document

                    solved_in_round += 1

                else:
                    print(
                        f"CPF/CNPJ não encontrado para {plate}.",
                        flush=True,
                    )

                    worksheet.cell(
                        row=row,
                        column=document_column,
                    ).value = "Não encontrado"

                    solved_in_round += 1

                time.sleep(TIME_BETWEEN_QUERIES_SECONDS)

            except Exception as error:
                print(
                    f"Erro ao retentar {plate}: {error}",
                    flush=True,
                )

                worksheet.cell(
                    row=row,
                    column=document_column,
                ).value = ""

                captcha_rows.append(row)

        print(
            f"Resolvidas nesta rodada: {solved_in_round}",
            flush=True,
        )

        if attempt >= MAX_CAPTCHA_RETRIES:
            if solved_in_round > 0:
                extra_attempts += 1
                print(
                    "Houve progresso. Permitindo tentativa extra.",
                    flush=True,
                )
            else:
                print(
                    "Nenhuma placa foi resolvida nesta rodada. "
                    "Encerrando retentativas.",
                    flush=True,
                )
                break

        attempt += 1

    if captcha_rows:
        print(
            f"\nAinda restaram {len(captcha_rows)} placas com CAPTCHA.",
            flush=True,
        )
        print(
            "Elas ficarão em branco para próxima execução.",
            flush=True,
        )

    return captcha_rows