"""
Centralizador de caminhos da aplicação.

Esse módulo contém todos os diretórios e arquivos utilizados
pelo sistema.

Objetivos:
- evitar caminhos duplicados
- facilitar manutenção
- simplificar refatorações
- melhorar legibilidade
- padronizar acessos a arquivos

Todo novo path da aplicação deve ser criado aqui.
"""

from pathlib import Path

# =========================================================
# BASE DIRECTORIES
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]
AUTOMATIONS_DIR = BASE_DIR / "automations"
TRACERS_DIR = AUTOMATIONS_DIR / "tracers"
MIND7_DIR = AUTOMATIONS_DIR / "mind7"
LOGS_DIR = BASE_DIR / "logs"


# =========================================================
# LOG FILES
# =========================================================

TRACERS_LOG_FILE = LOGS_DIR / "tracers.log"
MIND7_LOG_FILE = LOGS_DIR / "mind7.log"


# =========================================================
# TRACERS
# =========================================================

TRACERS_SCRIPTS_DIR = TRACERS_DIR / "scripts"
TRACERS_TOOLS_DIR = TRACERS_DIR / "tools"
TRACERS_TEMP_DIR = TRACERS_DIR / "temp"
TRACERS_RESULT_DIR = TRACERS_DIR / "result"
TRACERS_PLATFORM_TOOLS_DIR = (TRACERS_TOOLS_DIR / "platform-tools")
TRACERS_ADB_PATH = (TRACERS_PLATFORM_TOOLS_DIR / "adb.exe")
TRACERS_WINDOW_DUMP_FILE = (TRACERS_TEMP_DIR / "window_dump.xml")
TRACERS_SCRIPT = (TRACERS_SCRIPTS_DIR / "extrair_tracers.py")
TRACERS_EXCEL_FILE = (TRACERS_RESULT_DIR / "veiculos_tracers.xlsx")


# =========================================================
# MIND7
# =========================================================

MIND7_SCRIPTS_DIR = MIND7_DIR / "scripts"
MIND7_PROFILES_DIR = MIND7_DIR / "profiles"
MIND7_RESULT_DIR = MIND7_DIR / "result"
MIND7_INPUT_DIR = (MIND7_RESULT_DIR / "entrada")
MIND7_OUTPUT_DIR = (MIND7_RESULT_DIR / "saida")
MIND7_SCRIPT = (MIND7_SCRIPTS_DIR / "consultar_mind7.py")
MIND7_CHROME_BAT = (MIND7_SCRIPTS_DIR / "abrir_chrome_mind7.bat")
MIND7_INPUT_EXCEL_FILE = (MIND7_INPUT_DIR / "veiculos_tracers.xlsx")

# =========================================================
# OUTPUT FILES
# =========================================================

FINAL_RESULT_FILE = (MIND7_OUTPUT_DIR / "veiculos_tracers_com_cpf.xlsx")
CPF_ONLY_FILE = (MIND7_OUTPUT_DIR / "somente_cpfs.xlsx")
CPF_CNPJ_FILE = (MIND7_OUTPUT_DIR / "cpfs_e_cnpjs.xlsx")
CNPJ_ONLY_FILE = (MIND7_OUTPUT_DIR / "somente_cnpjs.xlsx")


# =========================================================
# HELPERS
# =========================================================

def create_required_directories():
    LOGS_DIR.mkdir(exist_ok=True)
    TRACERS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MIND7_INPUT_DIR.mkdir(parents=True, exist_ok=True)
    MIND7_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def required_directories_exist():
    return TRACERS_DIR.exists() and MIND7_DIR.exists()

def create_required_directories() -> None:
    LOGS_DIR.mkdir(exist_ok=True)
    TRACERS_RESULT_DIR.mkdir(parents=True,exist_ok=True,)
    TRACERS_TEMP_DIR.mkdir(parents=True,exist_ok=True,)
    MIND7_INPUT_DIR.mkdir(parents=True,exist_ok=True,)
    MIND7_OUTPUT_DIR.mkdir(parents=True,exist_ok=True,)