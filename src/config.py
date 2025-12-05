"""
Configurações do projeto
"""

import os

# Diretórios
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

# Criar diretórios se não existirem
for directory in [DATA_DIR, RAW_DIR, PROCESSED_DIR, LOGS_DIR, OUTPUTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Configurações DataSUS
DATASUS_CONFIG = {
    "default_state": "AC",
    "default_year": 2024,
    "default_month": 1,
}
