"""
Serviços responsáveis por leitura, escrita
e exportação de Excel do Mind7.
"""

from openpyxl import Workbook

from automations.mind7.constants.documents_constants import (CNPJ_TYPE,CPF_TYPE,)

from automations.mind7.constants.excel import (CNPJ_COLUMN_NAME,CNPJ_OUTPUT_KEY,CPF_CNPJ_OUTPUT_KEY,
    CPF_COLUMN_NAME,CPF_OUTPUT_KEY,DOCUMENT_COLUMN_NAME,
    DOCUMENT_TYPE_COLUMN_NAME,IGNORED_DOCUMENT_VALUES,
)

from automations.mind7.services.document_service import (format_cnpj,format_cpf, get_document_type,only_numbers,)
from backend.core.paths import (CNPJ_ONLY_FILE, CPF_CNPJ_FILE,CPF_ONLY_FILE,)

DOCUMENTS_OUTPUT_CONFIG = {
    CPF_OUTPUT_KEY: {
        "file": CPF_ONLY_FILE,
        "sheet_title": "CPFs",
        "headers": [CPF_COLUMN_NAME],
        "types": {CPF_TYPE},
    },
    CPF_CNPJ_OUTPUT_KEY: {
        "file": CPF_CNPJ_FILE,
        "sheet_title": "CPFs e CNPJs",
        "headers": [DOCUMENT_COLUMN_NAME, DOCUMENT_TYPE_COLUMN_NAME],
        "types": {CPF_TYPE, CNPJ_TYPE},
    },
    CNPJ_OUTPUT_KEY: {
        "file": CNPJ_ONLY_FILE,
        "sheet_title": "CNPJs",
        "headers": [CNPJ_COLUMN_NAME],
        "types": {CNPJ_TYPE},
    },
}

def find_column(worksheet, column_name: str) -> int | None:
    for column in range(1, worksheet.max_column + 1):
        value = worksheet.cell(row=1, column=column).value
        if (value and str(value).strip().lower() == column_name.lower()):
            return column
    return None

def ensure_column(worksheet, column_name: str) -> int:
    column = find_column(worksheet, column_name)
    if column:
        return column
    new_column = (worksheet.max_column + 1)
    worksheet.cell(row=1, column=new_column).value = column_name
    return new_column

def save_filtered_documents(worksheet, document_column: int) -> None:
    seen_documents = _create_seen_documents()
    workbooks = _create_output_workbooks()
    for row in range(2, worksheet.max_row + 1):
        document_data = _extract_document_data(worksheet=worksheet, row=row, document_column=document_column)
        if not document_data:
            continue
        _append_document_to_outputs(document_data=document_data, seen_documents=seen_documents, workbooks=workbooks)
    _save_output_workbooks(workbooks)

def _extract_document_data(worksheet, row: int, document_column: int) -> dict | None:
    value = worksheet.cell(row=row, column=document_column).value
    if not value:
        return None
    value = str(value).strip()
    if (value.lower() in IGNORED_DOCUMENT_VALUES):
        return None
    document_type = get_document_type(value)
    if not document_type:
        return None
    return {
        "type": document_type,
        "numbers": only_numbers(value),
        "formatted": (format_cpf(value) if document_type == CPF_TYPE else format_cnpj(value)),
    }

def _create_seen_documents() -> dict:
    return {
        CPF_OUTPUT_KEY: set(),
        CPF_CNPJ_OUTPUT_KEY: set(),
        CNPJ_OUTPUT_KEY: set(),
    }

def _create_output_workbooks() -> dict:
    workbooks = {}
    for key, config in (DOCUMENTS_OUTPUT_CONFIG.items()):
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = config["sheet_title"]
        worksheet.append(config["headers"])
        worksheet.column_dimensions["A"].width = 24
        if (len(config["headers"]) > 1):
            worksheet.column_dimensions["B"].width = 12
        workbooks[key] = (workbook, worksheet)
    return workbooks

def _append_document_to_outputs(document_data: dict, seen_documents: dict, workbooks: dict) -> None:
    document_type = document_data["type"]
    document_numbers = document_data["numbers"]
    formatted_document = document_data["formatted"]
    for key, config in (DOCUMENTS_OUTPUT_CONFIG.items()):
        if (document_type not in config["types"]):
            continue
        if (document_numbers in seen_documents[key]):
            continue
        seen_documents[key].add(document_numbers)
        _, worksheet = workbooks[key]
        if key == CPF_CNPJ_OUTPUT_KEY:
            worksheet.append([formatted_document, document_type])
        else:
            worksheet.append([formatted_document])

def _save_output_workbooks(workbooks: dict) -> None:
    for key, config in (DOCUMENTS_OUTPUT_CONFIG.items()):
        workbook, _ = workbooks[key]
        workbook.save(config["file"])