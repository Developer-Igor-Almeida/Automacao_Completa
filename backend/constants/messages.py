"""
Mensagens exibidas ao usuário.
"""

PROCESS_START_ERROR_MESSAGE = "❌ Erro ao iniciar processo: {error}"
TRACERS_FRIENDLY_LOG_TITLE = "ERRO AMIGÁVEL"
MIND7_FINISHED_MESSAGE = "✅ Consulta no Mind7 finalizada com sucesso."
TRACERS_FINISHED_MESSAGE = "✅ Extração de placas finalizada com sucesso."

TRACERS_START_BUTTON_LABEL = "▶️ Iniciar extração de placas"
SEND_TO_MIND7_BUTTON_LABEL = "📤 Copiar arquivo para Mind7"
OPEN_CHROME_BUTTON_LABEL = "🌐 Abrir Chrome para login"
START_MIND7_BUTTON_LABEL = "🔎 Iniciar consulta no Mind7"

TRACERS_START_BUTTON_LABEL = ("▶️ Iniciar extração de placas")

SEND_TO_MIND7_BUTTON_LABEL = ("📤 Copiar arquivo para Mind7")

OPEN_CHROME_BUTTON_LABEL = ("🌐 Abrir Chrome para login")

START_MIND7_CONSULTATION_BUTTON_LABEL = ("🔎 Iniciar consulta no Mind7")

FINISH_STEP_1_FIRST_MESSAGE = ("Conclua a etapa 1 primeiro.")

FINISH_STEP_2_FIRST_MESSAGE = ("Conclua a etapa 2 primeiro.")

FINISH_STEP_3_FIRST_MESSAGE = ("Conclua a etapa 3 primeiro.")

RUN_TRACERS_FIRST_MESSAGE = ("Execute a extração de placas primeiro.")

COPY_EXCEL_FIRST_MESSAGE = ("Copie o Excel para o Mind7 primeiro.")

FILE_COPIED_SUCCESS_MESSAGE = ("Arquivo copiado para entrada do Mind7.")

CHROME_OPENED_SUCCESS_MESSAGE = ("Chrome aberto. Faça login no Mind7.")

TRACERS_DISCONNECTED_MESSAGE = (
    "❌ O celular foi desconectado, o aplicativo Tracers foi fechado "
    "ou a tela correta não está aberta.\n\n"
    "Verifique:\n"
    "- Celular conectado\n"
    "- Depuração USB ativa\n"
    "- Aplicativo Tracers aberto\n"
    "- Tela da lista de veículos visível\n\n"
    "Depois clique em CONTINUAR.")

TRACERS_FRIENDLY_LOG_MESSAGE = (
    "O processo foi pausado porque o celular/app não estava disponível.\n"
    "Verifique o celular e mantenha o aplicativo Tracers aberto na tela correta.\n")

TRACERS_RUNTIME_ERROR_MESSAGE = (
    "⚠️ Problema detectado com o celular ou aplicativo Tracers.\n\n"
    "Verifique se o celular está conectado, desbloqueado e com o Tracers aberto.")

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

MIND7_PREPARING_MESSAGE = (
    "🔎 Preparando consulta no Mind7.\n\n"
    "Verifique se o Chrome está aberto e logado no sistema.")

FILE_PERMISSION_ERROR_MESSAGE = (
    "⚠️ Não foi possível salvar o Excel.\n\n"
    "Feche a planilha se ela estiver aberta e tente novamente.")

GENERIC_AUTOMATION_ERROR_MESSAGE = (
    "⚠️ A automação encontrou um problema.\n\n"
    "Verifique se os sistemas estão abertos corretamente e tente novamente.")