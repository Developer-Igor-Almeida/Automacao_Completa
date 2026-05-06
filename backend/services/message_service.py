import streamlit as st

from backend.core.logs import corrigir_acentos_log
from backend.services.process_service import detectar_erro_usuario_saiu


def mensagem_amigavel_por_etapa(etapa, log_texto):
    texto = corrigir_acentos_log(log_texto).lower()

    if st.session_state.erro_pausado:
        return st.session_state.mensagem_erro_pausado

    if etapa == "Extração de placas do Tracers":
        if detectar_erro_usuario_saiu(texto):
            return (
                "⚠️ Problema detectado com o celular ou aplicativo Tracers.\n\n"
                "Verifique se o celular está conectado, desbloqueado e com o Tracers aberto."
            )

        if "finalizado" in texto:
            return "✅ Extração de placas finalizada com sucesso."

        return (
            "📱 Extração de placas em andamento.\n\n"
            "Mantenha o celular conectado, desbloqueado e com o aplicativo Tracers aberto."
        )

    if etapa == "Consulta de CPFs/CNPJs no Mind7":
        if "captcha" in texto:
            return (
                "⚠️ O Mind7 solicitou validação CAPTCHA.\n\n"
                "A automação tentará novamente as placas pendentes. "
                "Se necessário, resolva a validação no navegador."
            )

        if "conectado ao chrome" in texto:
            return (
                "🔎 Consulta no Mind7 em andamento.\n\n"
                "Não feche o Chrome e mantenha o usuário logado no Mind7."
            )

        if "finalizado" in texto:
            return "✅ Consulta no Mind7 finalizada com sucesso."

        return (
            "🔎 Preparando consulta no Mind7.\n\n"
            "Verifique se o Chrome está aberto e logado no sistema."
        )

    if "permissionerror" in texto or "permission denied" in texto:
        return (
            "⚠️ Não foi possível salvar o Excel.\n\n"
            "Feche a planilha se ela estiver aberta e tente novamente."
        )

    if "traceback" in texto or "runtimeerror" in texto:
        return (
            "⚠️ A automação encontrou um problema.\n\n"
            "Verifique se os sistemas estão abertos corretamente e tente novamente."
        )

    return ""