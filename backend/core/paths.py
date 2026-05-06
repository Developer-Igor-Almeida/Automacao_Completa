from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

AUTOMATIONS = BASE_DIR / "automations"

TRACERS = AUTOMATIONS / "tracers"
MIND7 = AUTOMATIONS / "mind7"

LOG_DIR = BASE_DIR / "logs"
LOG_TRACERS = LOG_DIR / "tracers.log"
LOG_MIND7 = LOG_DIR / "mind7.log"

TRACERS_SCRIPTS = TRACERS / "scripts"
TRACERS_SAIDA = TRACERS / "saida"

MIND7_SCRIPTS = MIND7 / "scripts"
MIND7_ENTRADA = MIND7 / "entrada"
MIND7_SAIDA = MIND7 / "saida"

EXCEL_TRACERS = TRACERS_SAIDA / "veiculos_tracers.xlsx"
EXCEL_MIND7 = MIND7_ENTRADA / "veiculos_tracers.xlsx"

RESULTADO = MIND7_SAIDA / "veiculos_tracers_com_cpf.xlsx"
CPFS = MIND7_SAIDA / "somente_cpfs.xlsx"
CPFS_CNPJS = MIND7_SAIDA / "cpfs_e_cnpjs.xlsx"
CNPJS = MIND7_SAIDA / "somente_cnpjs.xlsx"

SCRIPT_TRACERS = TRACERS_SCRIPTS / "extrair_tracers.py"
SCRIPT_MIND7 = MIND7_SCRIPTS / "consultar_mind7.py"
BAT_CHROME_MIND7 = MIND7_SCRIPTS / "abrir_chrome_mind7.bat"


def criar_pastas():
    LOG_DIR.mkdir(exist_ok=True)
    TRACERS_SAIDA.mkdir(parents=True, exist_ok=True)
    MIND7_ENTRADA.mkdir(parents=True, exist_ok=True)
    MIND7_SAIDA.mkdir(parents=True, exist_ok=True)


def pastas_obrigatorias_existem():
    return TRACERS.exists() and MIND7.exists()