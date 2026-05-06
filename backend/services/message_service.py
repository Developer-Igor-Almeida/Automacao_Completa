"""
Serviço responsável por escolher mensagens amigáveis
com base na etapa atual e no conteúdo dos logs.
"""

import streamlit as st

from backend.constants.messages import (TRACERS_RUNTIME_ERROR_MESSAGE,TRACERS_FINISHED_MESSAGE,TRACERS_RUNNING_MESSAGE,
MIND7_CAPTCHA_MESSAGE,MIND7_RUNNING_MESSAGE,MIND7_FINISHED_MESSAGE,
MIND7_PREPARING_MESSAGE,FILE_PERMISSION_ERROR_MESSAGE,GENERIC_AUTOMATION_ERROR_MESSAGE,)
from backend.constants.process import TRACERS_STEP_NAME, MIND7_STEP_NAME
from backend.core.logs import corrigir_acentos_log
from backend.services.process_service import detect_tracers_runtime_error

MESSAGE_RULES_BY_STEP = {
    TRACERS_STEP_NAME: [
        (detect_tracers_runtime_error, TRACERS_RUNTIME_ERROR_MESSAGE),
        (lambda text: "finalizado" in text, TRACERS_FINISHED_MESSAGE),
        (lambda text: True, TRACERS_RUNNING_MESSAGE),
    ],
    MIND7_STEP_NAME: [
        (lambda text: "captcha" in text, MIND7_CAPTCHA_MESSAGE),
        (lambda text: "conectado ao chrome" in text, MIND7_RUNNING_MESSAGE),
        (lambda text: "finalizado" in text, MIND7_FINISHED_MESSAGE),
        (lambda text: True, MIND7_PREPARING_MESSAGE),
    ],
}

GENERIC_MESSAGE_RULES = [
    (lambda text: "permissionerror" in text or "permission denied" in text, FILE_PERMISSION_ERROR_MESSAGE,),
    (lambda text: "traceback" in text or "runtimeerror" in text,GENERIC_AUTOMATION_ERROR_MESSAGE,),
]

def get_friendly_message_by_step(step_name: str, log_text: str) -> str:
    normalized_text = corrigir_acentos_log(log_text).lower()
    if st.session_state.is_paused_by_error:
        return st.session_state.paused_error_message

    rules = MESSAGE_RULES_BY_STEP.get(step_name,GENERIC_MESSAGE_RULES,)
    return _resolve_message_from_rules(rules=rules,text=normalized_text,)

def _resolve_message_from_rules(rules: list, text: str) -> str:
    for condition, message in rules:
        if condition(text):
            return message
    return ""