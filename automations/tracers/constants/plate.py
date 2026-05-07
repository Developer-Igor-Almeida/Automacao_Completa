"""
Constantes utilizadas na identificação de placas e valores.
"""

MERCOSUL_PLATE_REGEX = r"\b([A-Z]{3}\s?[0-9][A-Z]\s?[0-9]{2})\b"

OLD_PLATE_REGEX = r"^([A-Z]{3}\s?[0-9]{4})\b"

WHITESPACE_REGEX = r"\s+"

UNKNOWN_VALUES = {
    "não informado",
    "nao informado",
}

CURRENCY_PREFIX = "r$"

