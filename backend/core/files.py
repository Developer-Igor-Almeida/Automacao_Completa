import csv
from io import StringIO

from openpyxl import load_workbook


def converter_xlsx_para_csv(caminho_xlsx):
    wb = load_workbook(caminho_xlsx, data_only=True)
    ws = wb.active

    output = StringIO()
    writer = csv.writer(output, delimiter=";")

    for row in ws.iter_rows(values_only=True):
        writer.writerow(["" if valor is None else valor for valor in row])

    return output.getvalue().encode("utf-8-sig")