import subprocess
import xml.etree.ElementTree as ET
import re
import html
import time
from pathlib import Path
from openpyxl import Workbook

BASE_DIR = Path(__file__).parent
ADB = str(BASE_DIR / "platform-tools" / "adb.exe")

OUT_DIR = BASE_DIR / "saida"
XML_FILE = BASE_DIR / "window_dump.xml"
XLSX_FILE = OUT_DIR / "veiculos_tracers.xlsx"

OUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_ROLAGENS = 3000
TEMPO_ESPERA_APOS_SWIPE = 0.8

SWIPE_X = 500
SWIPE_Y_INICIO = 1550
SWIPE_Y_FIM = 850
SWIPE_DURACAO_MS = 350

MAX_TELAS_SEM_NOVIDADE = 15


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


def run(cmd, check=True):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=False)

    if check and result.returncode != 0:
        raise RuntimeError(
            f"Erro ao executar: {' '.join(cmd)}\n\n"
            f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        )

    return result

def obter_app_em_primeiro_plano():
    comandos = [
        [ADB, "shell", "dumpsys", "window"],
        [ADB, "shell", "dumpsys", "activity", "activities"],
    ]

    texto_total = ""

    for cmd in comandos:
        resultado = run(cmd, check=False)
        texto_total += "\n" + (resultado.stdout or "")
        texto_total += "\n" + (resultado.stderr or "")

    texto = texto_total.lower()

    padroes = [
        r"mcurrentfocus=.*?\s([a-z0-9_.]+)\/",
        r"mfocusedapp=.*?\s([a-z0-9_.]+)\/",
        r"topresumedactivity=.*?\s([a-z0-9_.]+)\/",
        r"resumedactivity:.*?\s([a-z0-9_.]+)\/",
    ]

    for padrao in padroes:
        match = re.search(padrao, texto)
        if match:
            return match.group(1)

    return texto


def validar_tracers_aberto():
    app_atual = obter_app_em_primeiro_plano()

    if "br.app.tracers" not in app_atual and "tracers" not in app_atual:
        raise RuntimeError(
            "APP_TRACERS_FECHADO: O aplicativo Tracers não está aberto em primeiro plano. "
            "Abra o Tracers na tela da lista de veículos e tente novamente."
        )

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
    validar_tracers_aberto()

    run([ADB, "shell", "uiautomator", "dump", "/sdcard/window_dump.xml"])
    run([ADB, "shell", "test", "-f", "/sdcard/window_dump.xml"])
    run([ADB, "pull", "/sdcard/window_dump.xml", str(XML_FILE)])


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
    validar_tracers_aberto()

    run([
        ADB, "shell", "input", "swipe",
        str(SWIPE_X),
        str(SWIPE_Y_INICIO),
        str(SWIPE_X),
        str(SWIPE_Y_FIM),
        str(SWIPE_DURACAO_MS)
    ])

    time.sleep(TEMPO_ESPERA_APOS_SWIPE)


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

    for rodada in range(1, MAX_ROLAGENS + 1):
        print(f"\n--- Tela {rodada}/{MAX_ROLAGENS} ---", flush=True)

        capturar_xml()
        textos = extrair_textos(XML_FILE)

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

        if telas_sem_novidade >= MAX_TELAS_SEM_NOVIDADE:
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
    salvar_excel(registros, XLSX_FILE)
    print(f"Arquivo salvo em: {XLSX_FILE}", flush=True)