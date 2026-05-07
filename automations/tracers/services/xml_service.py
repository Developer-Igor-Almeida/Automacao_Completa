"""
Serviços responsáveis por leitura e tratamento do XML do Android UIAutomator.
"""

import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def clean_text(text: str) -> str:
    text = html.unescape(text or "")
    text = text.replace("\xa0", " ")
    text = " ".join(text.split()).strip()
    text = re.sub(r"^[^\wR$]+", "", text).strip()

    return text


def extract_texts_from_xml(xml_file: Path) -> list[str]:
    tree = ET.parse(xml_file)
    root = tree.getroot()

    extracted_texts = []

    for node in root.iter("node"):
        text = node.attrib.get("text", "")
        text = clean_text(text)

        if text:
            extracted_texts.append(text)

    return extracted_texts