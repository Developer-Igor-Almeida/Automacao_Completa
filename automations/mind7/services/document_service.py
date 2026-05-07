"""
Serviços responsáveis por tratamento e extração de documentos.
"""

import re


def normalize_plate(plate: str) -> str:
    return (
        str(plate or "")
        .strip()
        .upper()
        .replace(" ", "")
        .replace("-", "")
    )


def only_numbers(value: str) -> str:
    return re.sub(r"\D", "", str(value))


def format_cpf(cpf: str) -> str:
    cpf = only_numbers(cpf)

    if len(cpf) == 11:
        return (
            f"{cpf[:3]}."
            f"{cpf[3:6]}."
            f"{cpf[6:9]}-"
            f"{cpf[9:]}"
        )

    return cpf


def format_cnpj(cnpj: str) -> str:
    cnpj = only_numbers(cnpj)

    if len(cnpj) == 14:
        return (
            f"{cnpj[:2]}."
            f"{cnpj[2:5]}."
            f"{cnpj[5:8]}/"
            f"{cnpj[8:12]}-"
            f"{cnpj[12:]}"
        )

    return cnpj


def get_document_type(value: str) -> str:
    numbers = only_numbers(value)

    if len(numbers) == 11:
        return "CPF"

    if len(numbers) == 14:
        return "CNPJ"

    return ""


def extract_document_from_text(text: str) -> str:
    owner_block = re.search(
        r"PROPRIETÁRIO(.*?)(IMPORTAÇÃO|DÉBITOS|RESTRIÇÕES|$)",
        text,
        re.S | re.I,
    )

    if not owner_block:
        return ""

    block = owner_block.group(1)

    cpf_match = re.search(
        r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",
        block,
    )

    if cpf_match:
        return format_cpf(cpf_match.group(0))

    cnpj_match = re.search(
        r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b",
        block,
    )

    if cnpj_match:
        return format_cnpj(cnpj_match.group(0))

    raw_match = re.search(
        r"\b\d{11,14}\b",
        block,
    )

    if raw_match:
        number = only_numbers(raw_match.group(0))

        if len(number) == 11:
            return format_cpf(number)

        if len(number) == 14:
            return format_cnpj(number)

    return ""