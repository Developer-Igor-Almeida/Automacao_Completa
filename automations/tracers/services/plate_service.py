"""
Serviços responsáveis por tratamento e identificação de placas.
"""

import re

from automations.tracers.constants.plate import (
    CURRENCY_PREFIX,
    MERCOSUL_PLATE_REGEX,
    OLD_PLATE_REGEX,
    UNKNOWN_VALUES,
    WHITESPACE_REGEX,
)


def normalize_text(text: str) -> str:
    return " ".join(
        str(text or "").split()
    ).strip()


def extract_plate(text: str) -> str | None:
    normalized_text = normalize_text(text).upper()

    mercosul_plate = _extract_plate_by_regex(
        text=normalized_text,
        regex=MERCOSUL_PLATE_REGEX,
        use_match=False,
    )

    if mercosul_plate:
        return mercosul_plate

    return _extract_plate_by_regex(
        text=normalized_text,
        regex=OLD_PLATE_REGEX,
        use_match=True,
    )


def is_currency_value(text: str) -> bool:
    return (
        normalize_text(text)
        .lower()
        .startswith(CURRENCY_PREFIX)
    )


def is_unknown_value(text: str) -> bool:
    return (
        normalize_text(text)
        .lower()
        in UNKNOWN_VALUES
    )


def is_value_line(text: str) -> bool:
    return (
        is_currency_value(text)
        or is_unknown_value(text)
    )


def _extract_plate_by_regex(
    text: str,
    regex: str,
    use_match: bool,
) -> str | None:
    match = (
        re.match(regex, text)
        if use_match
        else re.search(regex, text)
    )

    if not match:
        return None

    return _format_plate(
        match.group(1)
    )


def _format_plate(plate: str) -> str:
    normalized_plate = re.sub(
        WHITESPACE_REGEX,
        "",
        plate,
    )

    return (
        f"{normalized_plate[:3]} "
        f"{normalized_plate[3:]}"
    )