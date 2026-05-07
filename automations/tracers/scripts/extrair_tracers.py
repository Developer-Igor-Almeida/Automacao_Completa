import html
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from automations.tracers.config.settings import (EXCEL_FILE_NAME,MAX_SCROLLS,MAX_SCREENS_WITHOUT_NEW_ITEMS,
 REMOTE_XML_PATH, SWIPE_DURATION_MS, SWIPE_END_Y, SWIPE_START_Y, SWIPE_WAIT_SECONDS, SWIPE_X, XML_FILE_NAME,)
from openpyxl import Workbook
from backend.core.paths import (TRACERS_ADB_PATH,TRACERS_EXCEL_FILE,TRACERS_TEMP_DIR,TRACERS_WINDOW_DUMP_FILE,)


def aguardar_usuario_iniciar():
    print("=" * 50, flush=True)
    print("AUTOMAÇÃO TRACERS", flush=True)
    print("=" * 50, flush=True)
    print("", flush=True)
    print("Antes de continuar:", flush=True)
    print("1. Conecte o celular ou abra o emulador", flush=True)
    print("2. Abra o app TRACERS", flush=True)
    print("3. Deixe aberta a tela com a lista de veículos", flush=True)
    print("4. Não mexa no celular durante a coleta", flush=True)
    print("", flush=True)
    print("Confirmação feita pela interface. Iniciando coleta...", flush=True)


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
    if result.returncode != 0:
        raise RuntimeError(
            f"Erro ao executar: {' '.join(cmd)}\n\n"
            f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        )
    return result.stdout.strip()


def deve_ignorar_como_modelo(texto: str) -> bool:
    t = texto.lower().strip()

    if re.search(r"\d+\s+casos?", t):
        return True

    if "pesquisar" in t:
        return True

    if "scanner de placas" in t:
        return True

    return False


def capturar_xml():
    run([TRACERS_ADB_PATH, "shell", "uiautomator", "dump", "/sdcard/window_dump.xml"])
    run([TRACERS_ADB_PATH, "pull", "/sdcard/window_dump.xml", str(TRACERS_WINDOW_DUMP_FILE)])


def limpar_texto(texto: str) -> str:
    texto = html.unescape(texto or "")
    texto = texto.replace("\xa0", " ")
    texto = " ".join(texto.split()).strip()
    texto = re.sub(r"^[^\wR$]+", "", texto).strip()
    return texto


def extrair_textos(xml_path: Path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    textos = []
    for node in root.iter("node"):
        text = node.attrib.get("text", "")
        text = limpar_texto(text)
        if text:
            textos.append(text)

    return textos


def normalizar_texto(texto: str) -> str:
    return " ".join(texto.split()).strip()


def extrair_placa(texto: str) -> str | None:
    texto = normalizar_texto(texto).upper()

    m1 = re.search(r"\b([A-Z]{3}\s?[0-9][A-Z]\s?[0-9]{2})\b", texto)
    if m1:
        placa = re.sub(r"\s+", "", m1.group(1))
        return f"{placa[:3]} {placa[3:]}"

    m2 = re.match(r"^([A-Z]{3}\s?[0-9]{4})\b", texto)
    if m2:
        placa = re.sub(r"\s+", "", m2.group(1))
        return f"{placa[:3]} {placa[3:]}"

    return None


def is_valor_reais(texto: str) -> bool:
    return texto.lower().strip().startswith("r$")


def is_nao_informado(texto: str) -> bool:
    return texto.lower().strip() in {"não informado", "nao informado"}


def is_linha_valor(texto: str) -> bool:
    return is_valor_reais(texto) or is_nao_informado(texto)


def extrair_total_casos(textos):
    for texto in textos:
        match = re.search(r"(\d+)\s+casos?", texto.lower())
        if match:
            return int(match.group(1))
    return None


def parse_registros(textos):
    textos = [normalizar_texto(t) for t in textos if t]

    ignorar_exatos = {
        "Pesquisar",
        "Scanner de Placas",
    }

    registros_para_excel = []
    estatisticas = {
        "com_valor_r": [],
        "sem_modelo_nao_informado": [],
        "sem_placa": [],
        "completo_nao_informado": [],
    }

    for i, atual in enumerate(textos):
        if not is_linha_valor(atual):
            continue

        valor = atual
        bloco = []

        for j in range(i - 1, max(i - 5, -1), -1):
            anterior = textos[j]

            if anterior in ignorar_exatos:
                continue

            if is_linha_valor(anterior):
                break

            bloco.insert(0, anterior)

        placa = ""
        modelo = ""

        for item in bloco:
            placa_encontrada = extrair_placa(item)
            if placa_encontrada and not placa:
                placa = placa_encontrada
                continue

            if not placa_encontrada and not modelo and not deve_ignorar_como_modelo(item):
                modelo = item

        registro = {
            "placa": placa,
            "modelo": modelo,
            "valor": valor,
        }

        if not placa:
            estatisticas["sem_placa"].append(registro)
            continue

        if is_valor_reais(valor):
            estatisticas["com_valor_r"].append(registro)
            continue

        if is_nao_informado(valor):
            if modelo:
                estatisticas["completo_nao_informado"].append(registro)
            else:
                estatisticas["sem_modelo_nao_informado"].append(registro)

            registros_para_excel.append(registro)

    return registros_para_excel, estatisticas


def salvar_excel(registros, caminho: Path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Veiculos"

    ws.append(["Placa", "Modelo", "Valor"])

    for r in registros:
        ws.append([r["placa"], r["modelo"], r["valor"]])

    ws.column_dimensions["A"].width = 16
    ws.column_dimensions["B"].width = 55
    ws.column_dimensions["C"].width = 20

    wb.save(caminho)


def swipe_para_cima():
    run([
        TRACERS_ADB_PATH, "shell", "input", "swipe",
        str(SWIPE_X),
        str(SWIPE_START_Y),
        str(SWIPE_X),
        str(SWIPE_END_Y),
        str(SWIPE_DURATION_MS)
    ])
    time.sleep(SWIPE_WAIT_SECONDS)


def coletar_multiplas_telas():
    placas_vistas = set()
    registros_excel = []

    vistos_valor_r = set()
    vistos_sem_modelo = set()
    vistos_sem_placa = set()
    vistos_completo = set()

    contadores = {
        "com_valor_r": 0,
        "sem_modelo_nao_informado": 0,
        "sem_placa": 0,
        "completo_nao_informado": 0,
    }

    telas_sem_novidade = 0
    total_esperado = None

    for rodada in range(1, MAX_SCROLLS + 1):
        print(f"\n--- Tela {rodada}/{MAX_SCROLLS} ---", flush=True)

        capturar_xml()
        textos = extrair_textos(TRACERS_WINDOW_DUMP_FILE)

        if total_esperado is None:
            total_esperado = extrair_total_casos(textos)
            if total_esperado:
                print(f"Total esperado detectado no app: {total_esperado}", flush=True)

        registros, estatisticas = parse_registros(textos)

        novos_nesta_tela = 0

        for r in estatisticas["com_valor_r"]:
            chave = r["placa"].replace(" ", "").upper()
            if chave not in vistos_valor_r:
                vistos_valor_r.add(chave)
                contadores["com_valor_r"] += 1

        for r in estatisticas["sem_modelo_nao_informado"]:
            chave = r["placa"].replace(" ", "").upper()
            if chave not in vistos_sem_modelo:
                vistos_sem_modelo.add(chave)
                contadores["sem_modelo_nao_informado"] += 1

        for r in estatisticas["completo_nao_informado"]:
            chave = r["placa"].replace(" ", "").upper()
            if chave not in vistos_completo:
                vistos_completo.add(chave)
                contadores["completo_nao_informado"] += 1

        for r in estatisticas["sem_placa"]:
            chave = f"{r['modelo']}|{r['valor']}"
            if chave not in vistos_sem_placa:
                vistos_sem_placa.add(chave)
                contadores["sem_placa"] += 1

        for r in registros:
            chave = r["placa"].replace(" ", "").upper()

            if chave not in placas_vistas:
                placas_vistas.add(chave)
                registros_excel.append(r)
                novos_nesta_tela += 1
                print(f"Salvar no Excel: {r}", flush=True)

        total_classificado = (
            contadores["com_valor_r"]
            + contadores["sem_modelo_nao_informado"]
            + contadores["sem_placa"]
            + contadores["completo_nao_informado"]
        )

        print(f"Novos para Excel nesta tela: {novos_nesta_tela}", flush=True)
        print(f"Total para Excel: {len(registros_excel)}", flush=True)
        print(f"Total classificado: {total_classificado}", flush=True)

        if total_esperado and total_classificado >= total_esperado:
            print("\nTotal esperado atingido pela soma das categorias. Encerrando coleta.", flush=True)
            break

        if novos_nesta_tela == 0:
            telas_sem_novidade += 1
        else:
            telas_sem_novidade = 0

        if telas_sem_novidade >= MAX_SCREENS_WITHOUT_NEW_ITEMS:
            print("\nNenhuma novidade por várias telas seguidas. Encerrando coleta.", flush=True)
            break

        swipe_para_cima()

    print("\n" + "=" * 50, flush=True)
    print("RESUMO FINAL", flush=True)
    print("=" * 50, flush=True)
    print(f"{contadores['com_valor_r']} placas encontradas de veículos que contêm valores em R$", flush=True)
    print(f"{contadores['sem_modelo_nao_informado']} placas encontradas de veículos sem modelo e com valor Não informado", flush=True)
    print(f"{contadores['sem_placa']} veículos encontrados que não contêm placa do carro", flush=True)
    print(f"{contadores['completo_nao_informado']} placas encontradas de veículos com modelo e valor Não informado", flush=True)
    print("", flush=True)
    print(f"Total salvo no Excel: {len(registros_excel)}", flush=True)
    if total_esperado:
        print(f"Total de casos informado no app: {total_esperado}", flush=True)

    return registros_excel


if __name__ == "__main__":
    aguardar_usuario_iniciar()

    print("\nIniciando coleta automática...", flush=True)
    registros = coletar_multiplas_telas()

    print(f"\nTotal final de registros salvos no Excel: {len(registros)}", flush=True)
    print("Salvando Excel...", flush=True)
    salvar_excel(registros, TRACERS_EXCEL_FILE)
    print(f"Arquivo salvo em: {TRACERS_EXCEL_FILE}", flush=True)