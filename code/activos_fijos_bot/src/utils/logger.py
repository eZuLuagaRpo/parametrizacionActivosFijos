"""
Configuración centralizada de logging para todo el bot.

Por qué un módulo propio y no logging.basicConfig() suelto en cada archivo:
    Un RPA que corre desatendido (sin nadie mirando la consola) depende
    completamente de sus logs para poder diagnosticar qué pasó en cada
    corrida. Si cada módulo configura su propio logging, se pisan
    formatos y niveles entre sí. Aquí se configura una única vez y el
    resto del proyecto solo llama a get_logger(__name__).

Los logs quedan tanto en consola (para cuando se corre en primer plano)
como en un archivo rotativo por día en LOG_DIR (para revisar corridas
desatendidas, p. ej. si el bot corre como tarea programada).
"""

import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from src.config import settings

_CONFIGURED = False


def _configure_root_logger():
    global _CONFIGURED
    if _CONFIGURED:
        return

    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = TimedRotatingFileHandler(
        filename=log_dir / "activos_fijos_bot.log",
        when="midnight",
        backupCount=30,  # conserva 30 días de historial de corridas
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    _CONFIGURED = True


def get_logger(name):
    """
    Retorna un logger ya configurado (consola + archivo rotativo diario).

    Args:
        name (str): Nombre del logger, normalmente __name__ del módulo
            que lo solicita, para poder identificar el origen del mensaje.

    Returns:
        logging.Logger
    """
    _configure_root_logger()
    return logging.getLogger(name)
