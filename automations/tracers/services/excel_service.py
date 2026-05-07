"""
Serviço responsável por salvar os registros extraídos do Tracers em Excel.
"""

from pathlib import Path
from openpyxl import Workbook


EXCEL_SHEET_TITLE = "Veiculos"
EXCEL_HEADERS = ["Placa", "Modelo", "Valor"]
COLUMN_WIDTHS = {"A": 16,"B": 55,"C": 20,}


def save_vehicle_records_to_excel(records: list[dict],output_file: Path,) -> None:
    workbook = Workbook()
    worksheet = workbook.active

    worksheet.title = EXCEL_SHEET_TITLE
    worksheet.append(EXCEL_HEADERS)

    for record in records:
        worksheet.append([record["placa"], record["modelo"],record["valor"],])

    for column, width in COLUMN_WIDTHS.items():
        worksheet.column_dimensions[column].width = width

    workbook.save(output_file)