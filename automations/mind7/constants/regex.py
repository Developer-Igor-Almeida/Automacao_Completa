"""
Expressões regulares utilizadas no Mind7.
"""

CPF_REGEX = r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"

CNPJ_REGEX = (r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b")

RAW_DOCUMENT_REGEX = r"\b\d{11,14}\b"

OWNER_BLOCK_REGEX = (
    r"PROPRIETÁRIO"
    r"(.*?)"
    r"(IMPORTAÇÃO|DÉBITOS|RESTRIÇÕES|$)"
)