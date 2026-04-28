from pathlib import Path
from playwright.sync_api import sync_playwright
from openpyxl import load_workbook
import re
import time

URL_CONSULTA = "https://mind-7.org/painel/consultas/placa/"

BASE_DIR = Path(__file__).parent
ENTRADA_DIR = BASE_DIR / "entrada"
SAIDA_DIR = BASE_DIR / "saida"

EXCEL_ENTRADA = ENTRADA_DIR / "veiculos_tracers.xlsx"
EXCEL_SAIDA = SAIDA_DIR / "veiculos_tracers_com_cpf.xlsx"
EXCEL_SOMENTE_CPFS = SAIDA_DIR / "somente_cpfs.xlsx"
EXCEL_CPFS_CNPJS = SAIDA_DIR / "cpfs_e_cnpjs.xlsx"
EXCEL_SOMENTE_CNPJS = SAIDA_DIR / "somente_cnpjs.xlsx"

COLUNA_PLACA = "Placa"
COLUNA_CPF = "CPF"

TEMPO_ENTRE_CONSULTAS = 8
PAUSA_A_CADA_CONSULTAS = 5
TEMPO_PAUSA_LONGA = 60

SAIDA_DIR.mkdir(parents=True, exist_ok=True)


def limpar_placa(placa):
    return str(placa or "").strip().upper().replace(" ", "").replace("-", "")

def apenas_numeros(valor):
    return re.sub(r"\D", "", str(valor))

def formatar_cpf(cpf):
    cpf = apenas_numeros(cpf)
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

def formatar_cnpj(cnpj):
    cnpj = apenas_numeros(cnpj)
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj


def encontrar_coluna(ws, nome_coluna):
    for col in range(1, ws.max_column + 1):
        valor = ws.cell(row=1, column=col).value
        if valor and str(valor).strip().lower() == nome_coluna.lower():
            return col
    return None


def garantir_coluna(ws, nome_coluna):
    col = encontrar_coluna(ws, nome_coluna)
    if col:
        return col

    nova_col = ws.max_column + 1
    ws.cell(row=1, column=nova_col).value = nome_coluna
    return nova_col


def obter_pagina_mind7(contexto):
    for pagina in contexto.pages:
        if "mind-7.org" in pagina.url:
            return pagina

    pagina = contexto.new_page()
    pagina.goto(URL_CONSULTA, wait_until="domcontentloaded")
    return pagina


def extrair_documento_do_texto(texto):
    bloco_prop = re.search(
        r"PROPRIETÁRIO(.*?)(IMPORTAÇÃO|DÉBITOS|RESTRIÇÕES|$)",
        texto,
        re.S | re.I
    )

    if not bloco_prop:
        return ""

    bloco = bloco_prop.group(1)

    # CPF com máscara
    match = re.search(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", bloco)
    if match:
        return formatar_cpf(match.group(0))

    # CNPJ com máscara
    match = re.search(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b", bloco)
    if match:
        return formatar_cnpj(match.group(0))

    # CPF ou CNPJ sem máscara
    match = re.search(r"\b\d{11,14}\b", bloco)
    if match:
        numero = apenas_numeros(match.group(0))

        if len(numero) == 11:
            return formatar_cpf(numero)

        if len(numero) == 14:
            return formatar_cnpj(numero)

    return ""


def esperar_cpf_ou_fim(pagina, timeout_segundos=8):
    inicio = time.time()

    while time.time() - inicio < timeout_segundos:
        texto = pagina.locator("body").inner_text(timeout=5000)

        if (
            "CAPTCHA" in texto.upper()
            or "não foi possível validar sua consulta" in texto.lower()
            or "nao foi possivel validar sua consulta" in texto.lower()
        ):
            return "CAPTCHA"

        documento = extrair_documento_do_texto(texto)
        if documento:
            return documento

        if "PROPRIETÁRIO" in texto.upper():
            return ""

        time.sleep(0.5)

    return ""


def consultar_placa(pagina, placa):
    print(f"Consultando placa: {placa}")

    pagina.goto(URL_CONSULTA, wait_until="domcontentloaded")
    time.sleep(1.5)

    campo = pagina.locator("#documento")
    campo.wait_for(timeout=15000)

    campo.click()
    campo.press("Control+A")
    campo.press("Backspace")
    campo.type(placa, delay=120)

    time.sleep(2.5)

    botao_consultar = pagina.get_by_role("button", name=re.compile("Consultar", re.I))
    botao_consultar.click()

    placa_sem_espaco = placa.replace(" ", "").upper()

    inicio = time.time()
    while time.time() - inicio < 15:
        texto = pagina.locator("body").inner_text(timeout=5000)
        texto_upper = texto.upper()
        texto_limpo = texto_upper.replace(" ", "").replace("-", "")

        if (
            "NÃO FOI POSSÍVEL VALIDAR SUA CONSULTA" in texto_upper
            or "NAO FOI POSSIVEL VALIDAR SUA CONSULTA" in texto_upper
        ):
            return "CAPTCHA"

        if placa_sem_espaco in texto_limpo:
            documento = extrair_documento_do_texto(texto)

            if documento:
                return documento

            if "PROPRIETÁRIO" in texto_upper:
                return ""

        time.sleep(0.5)

    return ""

def tipo_documento(valor):
    numeros = apenas_numeros(valor)

    if len(numeros) == 11:
        return "CPF"

    if len(numeros) == 14:
        return "CNPJ"

    return ""


def salvar_documentos_filtrados(ws, col_cpf):
    from openpyxl import Workbook

    arquivos = {
        "cpf": {
            "caminho": EXCEL_SOMENTE_CPFS,
            "titulo": "CPFs",
            "cabecalho": ["CPF"],
            "tipos": {"CPF"},
        },
        "cpf_cnpj": {
            "caminho": EXCEL_CPFS_CNPJS,
            "titulo": "CPFs e CNPJs",
            "cabecalho": ["Documento", "Tipo"],
            "tipos": {"CPF", "CNPJ"},
        },
        "cnpj": {
            "caminho": EXCEL_SOMENTE_CNPJS,
            "titulo": "CNPJs",
            "cabecalho": ["CNPJ"],
            "tipos": {"CNPJ"},
        },
    }

    documentos_vistos = {
        "cpf": set(),
        "cpf_cnpj": set(),
        "cnpj": set(),
    }

    workbooks = {}

    for chave, config in arquivos.items():
        wb = Workbook()
        ws_doc = wb.active
        ws_doc.title = config["titulo"]
        ws_doc.append(config["cabecalho"])
        ws_doc.column_dimensions["A"].width = 24
        if len(config["cabecalho"]) > 1:
            ws_doc.column_dimensions["B"].width = 12

        workbooks[chave] = (wb, ws_doc)

    for row in range(2, ws.max_row + 1):
        valor = ws.cell(row=row, column=col_cpf).value

        if not valor:
            continue

        valor = str(valor).strip()

        if valor.lower() in {"não encontrado", "nao encontrado", "erro", "captcha"}:
            continue

        tipo = tipo_documento(valor)
        numeros = apenas_numeros(valor)

        if not tipo:
            continue

        documento_formatado = formatar_cpf(valor) if tipo == "CPF" else formatar_cnpj(valor)

        for chave, config in arquivos.items():
            if tipo not in config["tipos"]:
                continue

            if numeros in documentos_vistos[chave]:
                continue

            documentos_vistos[chave].add(numeros)

            wb_doc, ws_doc = workbooks[chave]

            if chave == "cpf_cnpj":
                ws_doc.append([documento_formatado, tipo])
            else:
                ws_doc.append([documento_formatado])

    for chave, config in arquivos.items():
        wb_doc, _ = workbooks[chave]
        wb_doc.save(config["caminho"])

def salvar_excel_somente_cpfs(ws, col_cpf, caminho):
    from openpyxl import Workbook

    wb_cpfs = Workbook()
    ws_cpfs = wb_cpfs.active
    ws_cpfs.title = "CPFs"

    ws_cpfs.append(["CPF"])

    cpfs_vistos = set()

    for row in range(2, ws.max_row + 1):
        cpf = ws.cell(row=row, column=col_cpf).value

        if not cpf:
            continue

        cpf = str(cpf).strip()

        if cpf.lower() in {
            "não encontrado",
            "nao encontrado",
            "erro",
            "captcha"
        }:
            continue

        chave = re.sub(r"\D", "", cpf)

        if len(chave) == 11 and chave not in cpfs_vistos:
            cpfs_vistos.add(chave)
            ws_cpfs.append([formatar_cpf(cpf)])

    ws_cpfs.column_dimensions["A"].width = 20
    wb_cpfs.save(caminho)


def main():
    if not EXCEL_ENTRADA.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado:\n{EXCEL_ENTRADA}\n\n"
            f"Coloque o arquivo veiculos_tracers.xlsx dentro da pasta entrada."
        )

    wb = load_workbook(EXCEL_ENTRADA)
    ws = wb.active

    col_placa = encontrar_coluna(ws, COLUNA_PLACA)
    if not col_placa:
        raise Exception("Coluna 'Placa' não encontrada no Excel.")

    col_cpf = garantir_coluna(ws, COLUNA_CPF)

    consultas_realizadas = 0

    with sync_playwright() as p:
        navegador = p.chromium.connect_over_cdp("http://localhost:9222")
        contexto = navegador.contexts[0]
        pagina = obter_pagina_mind7(contexto)

        print("Conectado ao Chrome.")
        print("Mind7 logado confirmado pela interface.")
        print("Não feche o Chrome durante a execução.")

        for row in range(2, ws.max_row + 1):
            placa_original = ws.cell(row=row, column=col_placa).value
            placa = limpar_placa(placa_original)

            if not placa:
                continue

            cpf_atual = ws.cell(row=row, column=col_cpf).value
            if cpf_atual and str(cpf_atual).strip().upper() != "CAPTCHA":
                print(f"Pulando {placa}: CPF já preenchido.")
                continue

            try:
                cpf = consultar_placa(pagina, placa)

                if cpf == "CAPTCHA":
                    print(f"CAPTCHA encontrado na placa {placa}. Marcando e seguindo para a próxima.")
                    ws.cell(row=row, column=col_cpf).value = "CAPTCHA"

                elif cpf:
                    print(f"CPF encontrado para {placa}: {cpf}")
                    ws.cell(row=row, column=col_cpf).value = cpf

                else:
                    print(f"CPF não encontrado para {placa}.")
                    ws.cell(row=row, column=col_cpf).value = "Não encontrado"

                wb.save(EXCEL_SAIDA)
                salvar_documentos_filtrados(ws, col_cpf)

                consultas_realizadas += 1

                if consultas_realizadas % PAUSA_A_CADA_CONSULTAS == 0:
                    print(f"Pausa preventiva de {TEMPO_PAUSA_LONGA}s para reduzir CAPTCHA...")
                    time.sleep(TEMPO_PAUSA_LONGA)
                else:
                    time.sleep(TEMPO_ENTRE_CONSULTAS)

            except Exception as e:
                print(f"Erro ao consultar {placa}: {e}")
                ws.cell(row=row, column=col_cpf).value = "Erro"

                wb.save(EXCEL_SAIDA)
                salvar_documentos_filtrados(ws, col_cpf)

    wb.save(EXCEL_SAIDA)
    salvar_documentos_filtrados(ws, col_cpf)

    print("Finalizado.")
    print(f"Somente CPFs: {EXCEL_SOMENTE_CPFS}")
    print(f"CPFs e CNPJs: {EXCEL_CPFS_CNPJS}")
    print(f"Somente CNPJs: {EXCEL_SOMENTE_CNPJS}")


if __name__ == "__main__":
    main()