"""
Configuração de logging
"""

import logging
import sys
from pathlib import Path
from src.config import LOGS_DIR, LOG_FORMAT, LOG_DATE_FORMAT


def setup_logger(name: str, log_file: str = "etl_pipeline.log") -> logging.Logger:
    """
    Configura logger com output para console e arquivo
    
    Args:
        name: Nome do logger
        log_file: Nome do arquivo de log
    
    Returns:
        Logger configurado
    """
    # Criar diretório logs
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / log_file
    
    # Configurar logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    
    # Handler arquivo
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # Adicionar handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
