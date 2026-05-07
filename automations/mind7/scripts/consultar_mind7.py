"""
Entrada principal da automação Mind7.

Responsável apenas por:
- abrir Excel
- conectar ao Chrome
- orquestrar consultas
- salvar resultados
"""

import time

from openpyxl import load_workbook

from automations.mind7.config.settings import (DOCUMENT_COLUMN_NAME,PLATE_COLUMN_NAME,)

from automations.mind7.services.chrome_service import (connect_to_mind7_page,)

from automations.mind7.services.document_service import ( normalize_plate,)

from automations.mind7.services.excel_service import (ensure_column,find_column,save_filtered_documents,)

from automations.mind7.services.mind7_service import (CAPTCHA_RESULT,query_plate,)

from automations.mind7.services.retry_service import (preventive_pause,retry_captcha_plates,)

from backend.core.paths import (FINAL_RESULT_FILE,MIND7_INPUT_EXCEL_FILE,)


def main() -> None:
    print("=" * 50, flush=True)
    print("AUTOMAÇÃO MIND7", flush=True)
    print("=" * 50, flush=True)

    workbook = load_workbook(MIND7_INPUT_EXCEL_FILE)
    worksheet = workbook.active

    plate_column = find_column(
        worksheet,
        PLATE_COLUMN_NAME,
    )

    if not plate_column:
        raise ValueError(
            f"Coluna '{PLATE_COLUMN_NAME}' não encontrada."
        )

    document_column = ensure_column(
        worksheet,
        DOCUMENT_COLUMN_NAME,
    )

    playwright, browser, page = connect_to_mind7_page()

    print(
        "Conectado ao Chrome e pronto para consultas.",
        flush=True,
    )

    captcha_rows = []
    completed_queries = 0

    try:
        for row in range(2, worksheet.max_row + 1):
            original_plate = worksheet.cell(
                row=row,
                column=plate_column,
            ).value

            plate = normalize_plate(original_plate)

            if not plate:
                continue

            print(
                f"\n[{row-1}/{worksheet.max_row-1}] "
                f"Consultando placa: {plate}",
                flush=True,
            )

            try:
                document = query_plate(page, plate)

                if document == CAPTCHA_RESULT:
                    print(
                        f"CAPTCHA detectado para {plate}",
                        flush=True,
                    )

                    worksheet.cell(
                        row=row,
                        column=document_column,
                    ).value = ""

                    captcha_rows.append(row)

                elif document:
                    print(
                        f"Documento encontrado: {document}",
                        flush=True,
                    )

                    worksheet.cell(
                        row=row,
                        column=document_column,
                    ).value = document

                else:
                    print(
                        "Nenhum documento encontrado.",
                        flush=True,
                    )

                    worksheet.cell(
                        row=row,
                        column=document_column,
                    ).value = "Não encontrado"

                completed_queries += 1

                preventive_pause(completed_queries)

            except Exception as error:
                print(
                    f"Erro ao consultar placa {plate}: {error}",
                    flush=True,
                )

                worksheet.cell(
                    row=row,
                    column=document_column,
                ).value = "Erro"

        if captcha_rows:
            retry_captcha_plates(
                page=page,
                worksheet=worksheet,
                plate_column=plate_column,
                document_column=document_column,
                captcha_rows=captcha_rows,
            )

        print("\nSalvando resultado final...", flush=True)

        workbook.save(FINAL_RESULT_FILE)

        save_filtered_documents(
            worksheet,
            document_column,
        )

        print(
            f"Resultado salvo em: {FINAL_RESULT_FILE}",
            flush=True,
        )

        print("\nProcesso finalizado.", flush=True)

    finally:
        time.sleep(2)

        browser.close()
        playwright.stop()


if __name__ == "__main__":
    main()