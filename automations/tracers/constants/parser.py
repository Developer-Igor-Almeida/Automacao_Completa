"""
Constantes utilizadas no parser do Tracers.
"""


TOTAL_CASES_REGEX = r"(\d+)\s+casos?"

EXACT_TEXTS_TO_IGNORE = {
    "Pesquisar",
    "Scanner de Placas",
}

TEXT_FRAGMENTS_TO_IGNORE_AS_MODEL = {
    "pesquisar",
    "scanner de placas",
}

MAX_PREVIOUS_VEHICLE_ITEMS = 4

STATISTIC_WITH_CURRENCY_VALUE = "com_valor_r"
STATISTIC_WITHOUT_MODEL_UNKNOWN_VALUE = "sem_modelo_nao_informado"
STATISTIC_WITHOUT_PLATE = "sem_placa"
STATISTIC_COMPLETE_UNKNOWN_VALUE = "completo_nao_informado"