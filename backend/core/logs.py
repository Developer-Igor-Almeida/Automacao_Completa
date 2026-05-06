from pathlib import Path

from backend.core.paths import LOG_TRACERS, LOG_MIND7


def ler_log(log_path):
    if not log_path or not Path(log_path).exists():
        return ""

    return Path(log_path).read_text(encoding="utf-8", errors="ignore")


def corrigir_acentos_log(texto):
    if not texto:
        return ""

    correcoes = {
        "execuÃ§Ã£o": "execução",
        "automaÃ§Ã£o": "automação",
        "nÃ£o": "não",
        "estÃ¡": "está",
        "conexÃ£o": "conexão",
        "informaÃ§Ãµes": "informações",
        "veÃ­culo": "veículo",
        "prÃ³xima": "próxima",
        "validaÃ§Ã£o": "validação",
        "possÃ­vel": "possível",
        "cÃ³digo": "código",
        "usuÃ¡rio": "usuário",
        "aplicaÃ§Ã£o": "aplicação",
        "extraÃ§Ã£o": "extração",
    }

    for errado, certo in correcoes.items():
        texto = texto.replace(errado, certo)

    return texto


def limpar_logs():
    for log_file in [LOG_TRACERS, LOG_MIND7]:
        try:
            log_file.write_text("", encoding="utf-8")
        except Exception:
            pass