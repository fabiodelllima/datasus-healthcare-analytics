"""
Logger: Configuração de logging
"""

import logging
import os
import sys
from datetime import datetime

from src.config import LOGS_DIR


def setup_logger(name: str = "datasus", level: int = logging.INFO) -> logging.Logger:
    """
    Configura logger com output para console e arquivo

    Args:
        name: Nome do logger
        level: Nível de logging

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remover handlers existentes
    logger.handlers.clear()

    # Formato
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(name)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler: Console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler: Arquivo
    log_file = os.path.join(LOGS_DIR, f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
