"""
Extract: Download e decode de arquivos DBC do DataSUS
"""

import logging

import pandas as pd
from pysus import ftp

logger = logging.getLogger(__name__)

# Grupo RD = AIH Reduzida, o conjunto reduzido de campos da Autorizacao de
# Internacao Hospitalar. E o grupo que o pipeline consome.
SIH_GROUP_REDUCED = "RD"


class DataSUSExtractor:
    """Extrator de dados do SIH/DataSUS"""

    def __init__(self) -> None:
        """Inicializa extrator"""
        logger.info("[EXTRACTOR] Inicializado")

    def extract(self, state: str, year: int, month: int) -> pd.DataFrame:
        """
        Download e decode de arquivo DBC do DataSUS

        Usa a API namespaced por origem (`pysus.ftp`), que serve o FTP do
        DataSUS por meio do espelho S3. A chamada direta `pysus.sih()` esta
        marcada como obsoleta e sera removida.

        Args:
            state: UF (2 letras)
            year: Ano (YYYY)
            month: Mês (1-12)

        Returns:
            DataFrame com dados brutos

        Raises:
            TypeError: Se a API devolver algo que não seja DataFrame
        """
        try:
            logger.info(f"[EXTRACT] Baixando: {state} {year}/{month:02d}")

            # A anotacao do pysus declara list[str] | pd.DataFrame, mas o
            # retorno real varia conforme os parametros. A checagem adiante
            # estreita o tipo e falha cedo se o contrato mudar.
            result = ftp.sih(
                state,
                year,
                month,
                group=SIH_GROUP_REDUCED,
                as_dataframe=True,
            )

            logger.info("[EXTRACT] Download concluído")

            if not isinstance(result, pd.DataFrame):
                raise TypeError(
                    f"Esperado DataFrame, recebido {type(result).__name__}"
                )

            logger.info(f"[EXTRACT] Registros carregados: {len(result):,}")
            logger.info(f"[EXTRACT] Colunas: {len(result.columns)}")

            return result

        except Exception as e:
            logger.error(f"[EXTRACT] Erro: {e}")
            raise
