"""
Serviços responsáveis por tratamento e extração de documentos.
"""

import re

from automations.mind7.constants.documents_constants import (
    CNPJ_LENGTH,
    CNPJ_TYPE,
    CPF_LENGTH,
    CPF_TYPE,
    PLATE_REMOVE_CHARACTERS,
)

from automations.mind7.constants.regex import (
    CNPJ_REGEX,
    CPF_REGEX,
    OWNER_BLOCK_REGEX,
    RAW_DOCUMENT_REGEX,
)


def normalize_plate(plate: str) -> str:
    normalized_plate = (str(plate or "").strip().upper())
    for character in PLATE_REMOVE_CHARACTERS:
        normalized_plate = normalized_plate.replace(character, "")
    return normalized_plate


def only_numbers(value: str) -> str:
    return re.sub(r"\D", "", str(value))


def format_cpf(cpf: str) -> str:
    cpf = only_numbers(cpf)
    if len(cpf) != CPF_LENGTH:
        return cpf
    return (f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}")


def format_cnpj(cnpj: str) -> str:
    cnpj = only_numbers(cnpj)
    if len(cnpj) != CNPJ_LENGTH:
        return cnpj
    return (f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}")


def get_document_type(value: str) -> str:
    document_length = len(only_numbers(value))
    if document_length == CPF_LENGTH:
        return CPF_TYPE
    if document_length == CNPJ_LENGTH:
        return CNPJ_TYPE
    return ""


def extract_document_from_text(text: str) -> str:
    owner_block = _extract_owner_block(text)
    if not owner_block:
        return ""
    formatted_document = (_extract_formatted_document(owner_block))
    if formatted_document:
        return formatted_document
    return _extract_raw_document(owner_block)


def _extract_owner_block(text: str) -> str:
    match = re.search(OWNER_BLOCK_REGEX, text, re.S | re.I)
    if not match:
        return ""
    return match.group(1)


def _extract_formatted_document(text: str) -> str:
    cpf_match = re.search(CPF_REGEX, text)
    if cpf_match:
        return format_cpf(cpf_match.group(0))
    cnpj_match = re.search(CNPJ_REGEX, text)
    if cnpj_match:
        return format_cnpj(cnpj_match.group(0))
    return ""


def _extract_raw_document(text: str) -> str:
    raw_match = re.search(RAW_DOCUMENT_REGEX, text)
    if not raw_match:
        return ""
    document = only_numbers(raw_match.group(0))
    document_type = get_document_type(document)
    if document_type == CPF_TYPE:
        return format_cpf(document)
    if document_type == CNPJ_TYPE:
        return format_cnpj(document)
    return ""