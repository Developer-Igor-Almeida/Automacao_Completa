"""
Serviços responsáveis por leitura e tratamento do XML do Android UIAutomator.
"""

import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from automations.tracers.constants.xml import (
    INVALID_TEXT_PREFIX_REGEX,
    NON_BREAKING_SPACE,
    NORMAL_SPACE,
    XML_NODE_TAG,
    XML_TEXT_ATTRIBUTE,
)


def clean_text(text: str) -> str:
    text = html.unescape(text or "")
    text = text.replace(NON_BREAKING_SPACE, NORMAL_SPACE)
    text = " ".join(text.split()).strip()
    text = re.sub(INVALID_TEXT_PREFIX_REGEX, "", text).strip()
    return text


def extract_texts_from_xml(xml_file: Path) -> list[str]:
    root = _get_xml_root(xml_file)
    return [cleaned_text for node in root.iter(XML_NODE_TAG) if (cleaned_text := clean_text(node.attrib.get(XML_TEXT_ATTRIBUTE, "")))]


def _get_xml_root(xml_file: Path):
    try:
        tree = ET.parse(xml_file)
        return tree.getroot()
    except ET.ParseError as error:
        raise RuntimeError(f"XML inválido ou corrompido: {xml_file}") from error
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Arquivo XML não encontrado: {xml_file}") from error