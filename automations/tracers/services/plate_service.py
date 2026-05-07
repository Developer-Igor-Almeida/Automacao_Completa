"""
Serviços responsáveis por tratamento e identificação de placas.
"""

import re

UNKNOWN_VALUES = {"não informado","nao informado",}


def normalize_text(text: str) -> str:
    return " ".join(text.split()).strip()

def extract_plate(text: str) -> str | None:
    text = normalize_text(text).upper()

    mercosul_match = re.search(
        r"\b([A-Z]{3}\s?[0-9][A-Z]\s?[0-9]{2})\b",
        text,
    )

    if mercosul_match:
        plate = re.sub(r"\s+", "", mercosul_match.group(1))
        return f"{plate[:3]} {plate[3:]}"

    old_pattern_match = re.match(
        r"^([A-Z]{3}\s?[0-9]{4})\b",
        text,
    )

    if old_pattern_match:
        plate = re.sub(r"\s+", "", old_pattern_match.group(1))
        return f"{plate[:3]} {plate[3:]}"

    return None

def is_currency_value(text: str) -> bool:
    return text.lower().strip().startswith("r$")

def is_unknown_value(text: str) -> bool:
    return text.lower().strip() in UNKNOWN_VALUES

def is_value_line(text: str) -> bool:
    return (is_currency_value(text) or is_unknown_value(text))