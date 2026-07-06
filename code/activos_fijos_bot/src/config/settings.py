"""
Carga de configuración del bot a partir de variables de entorno (.env).

Por qué .env y no valores en el código:
    Este proyecto se desarrolla en un PC personal (sin acceso a Appian/SAP)
    y luego se traslada al PC de la empresa. Las URLs, credenciales y rutas
    de descarga son distintas en cada entorno (y entre ambientes CP1/EP1 de
    SAP). Mantener todo en variables de entorno permite mover el mismo
    código entre PCs y ambientes sin tocar una sola línea.

Nunca importe credenciales de este módulo a un log ni las imprima en pantalla.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Carga el archivo .env ubicado en la raíz del proyecto (activos_fijos_bot/.env).
# find_dotenv no se usa a propósito: preferimos una ruta explícita y predecible
# en vez de que dotenv "adivine" el archivo subiendo directorios.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_ENV_PATH = _PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=_ENV_PATH)


def _get_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "si", "sí", "yes")


def _get_int(name, default):
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return int(value)


# -------------------------------------------------
# APPIAN
# -------------------------------------------------
APPIAN_URL = os.getenv("APPIAN_URL", "")
APPIAN_USER = os.getenv("APPIAN_USER", "")
APPIAN_PASSWORD = os.getenv("APPIAN_PASSWORD", "")
APPIAN_BROWSER = os.getenv("APPIAN_BROWSER", "edge")
APPIAN_TIMEOUT = _get_int("APPIAN_TIMEOUT", 90)
APPIAN_TIMEOUT_FILES = _get_int("APPIAN_TIMEOUT_FILES", 600)

# Directorio donde appian-flow descarga los adjuntos del caso (el Excel del usuario).
# Debe ser una ruta absoluta que exista en el PC donde corre el bot.
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", str(_PROJECT_ROOT / "downloads"))

# Directorio donde se dejan los Excels ya transformados al formato Z_AM_MASIVA (Fase 2).
OUTPUT_DIR = os.getenv("OUTPUT_DIR", str(_PROJECT_ROOT / "output"))

# TODO-PENDIENTE-ACCESO-REAL: nombre del reporte de Process HQ (si se llega a usar
# download_report como mecanismo alterno/complementario de descubrimiento de casos).
APPIAN_REPORT_FLOW_NAME = os.getenv("APPIAN_REPORT_FLOW_NAME", "")
APPIAN_REPORT_NAME = os.getenv("APPIAN_REPORT_NAME", "")

# -------------------------------------------------
# SAP (se completa en la Fase 3 — placeholders por ahora)
# -------------------------------------------------
# TODO-PENDIENTE-ACCESO-REAL: confirmar si el login web de SAP difiere entre
# los ambientes CP1 (pruebas) y EP1 (productivo), y si requiere usuario/clave
# o autenticación integrada (SSO). Ver GUIA_MODIFICACION.md, sección de SAP.
SAP_ENVIRONMENT = os.getenv("SAP_ENVIRONMENT", "CP1")  # CP1 o EP1
SAP_URL = os.getenv("SAP_URL", "")
SAP_USER = os.getenv("SAP_USER", "")
SAP_PASSWORD = os.getenv("SAP_PASSWORD", "")
SAP_BROWSER = os.getenv("SAP_BROWSER", "edge")
SAP_TIMEOUT = _get_int("SAP_TIMEOUT", 90)

# Salvaguarda para no ejecutar cargas reales en SAP por accidente mientras se
# valida el bot. Debe quedar en True hasta que el usuario confirme
# explícitamente que se puede desmarcar "Ejecución de test" en Z_AM_MASIVA.
# Ver checklist de traslado en GUIA_MODIFICACION.md.
SAP_MODO_PRUEBA = _get_bool("SAP_MODO_PRUEBA", True)

# -------------------------------------------------
# GENERAL
# -------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", str(_PROJECT_ROOT / "logs"))

# Intervalo (en segundos) entre revisiones de la bandeja de Appian.
POLL_INTERVAL_SECONDS = _get_int("POLL_INTERVAL_SECONDS", 300)
