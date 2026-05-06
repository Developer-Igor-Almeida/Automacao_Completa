"""
Mensagens exibidas ao usuário.
"""

TRACERS_DISCONNECTED_MESSAGE = (
    "❌ O celular foi desconectado, o aplicativo Tracers foi fechado "
    "ou a tela correta não está aberta.\n\n"
    "Verifique:\n"
    "- Celular conectado\n"
    "- Depuração USB ativa\n"
    "- Aplicativo Tracers aberto\n"
    "- Tela da lista de veículos visível\n\n"
    "Depois clique em CONTINUAR.")

PROCESS_START_ERROR_MESSAGE = "❌ Erro ao iniciar processo: {error}"

TRACERS_FRIENDLY_LOG_TITLE = "ERRO AMIGÁVEL"

TRACERS_FRIENDLY_LOG_MESSAGE = (
    "O processo foi pausado porque o celular/app não estava disponível.\n"
    "Verifique o celular e mantenha o aplicativo Tracers aberto na tela correta.\n")

TRACERS_RUNTIME_ERROR_MESSAGE = (
    "⚠️ Problema detectado com o celular ou aplicativo Tracers.\n\n"
    "Verifique se o celular está conectado, desbloqueado e com o Tracers aberto.")

TRACERS_FINISHED_MESSAGE = "✅ Extração de placas finalizada com sucesso."

TRACERS_RUNNING_MESSAGE = (
    "📱 Extração de placas em andamento.\n\n"
    "Mantenha o celular conectado, desbloqueado e com o aplicativo Tracers aberto.")

MIND7_CAPTCHA_MESSAGE = (
    "⚠️ O Mind7 solicitou validação CAPTCHA.\n\n"
    "A automação tentará novamente as placas pendentes. "
    "Se necessário, resolva a validação no navegador.")

MIND7_RUNNING_MESSAGE = (
    "🔎 Consulta no Mind7 em andamento.\n\n"
    "Não feche o Chrome e mantenha o usuário logado no Mind7.")

MIND7_FINISHED_MESSAGE = "✅ Consulta no Mind7 finalizada com sucesso."

MIND7_PREPARING_MESSAGE = (
    "🔎 Preparando consulta no Mind7.\n\n"
    "Verifique se o Chrome está aberto e logado no sistema.")

FILE_PERMISSION_ERROR_MESSAGE = (
    "⚠️ Não foi possível salvar o Excel.\n\n"
    "Feche a planilha se ela estiver aberta e tente novamente.")

GENERIC_AUTOMATION_ERROR_MESSAGE = (
    "⚠️ A automação encontrou um problema.\n\n"
    "Verifique se os sistemas estão abertos corretamente e tente novamente.")