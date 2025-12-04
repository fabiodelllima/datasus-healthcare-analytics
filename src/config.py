"""
Configurações do projeto
"""

from pathlib import Path

# Diretórios
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
LOGS_DIR = PROJECT_ROOT / "logs"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# DataSUS
DATASUS_FTP = "ftp.datasus.gov.br"
DATASUS_PATH = "/dissemin/publicos/SIHSUS/200801_/Dados/"

# Processamento
PYTHON_VERSION = "3.11"
DEFAULT_STATE = "AC"
DEFAULT_YEAR = 2024
DEFAULT_MONTH = 1

# Validações
MAX_IDADE = 120
MAX_DIAS_PERM = 365
MAX_VAL_TOT = 1000000
MIN_VAL_TOT = 0

# Logging
LOG_FORMAT = "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
