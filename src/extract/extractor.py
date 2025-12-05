"""
Extract: Download e decode de arquivos DBC do DataSUS
"""

import logging

import pandas as pd
from pysus.online_data.SIH import download

logger = logging.getLogger(__name__)


class DataSUSExtractor:
    """Extrator de dados do SIH/DataSUS"""

    def __init__(self):
        """Inicializa extrator"""
        logger.info("[EXTRACTOR] Inicializado")

    def extract(self, state: str, year: int, month: int) -> pd.DataFrame:
        """
        Download e decode de arquivo DBC do DataSUS

        Args:
            state: UF (2 letras)
            year: Ano (YYYY)
            month: Mês (1-12)

        Returns:
            DataFrame com dados brutos
        """
        try:
            logger.info(f"[EXTRACT] Baixando: {state} {year}/{month:02d}")

            # Download retorna ParquetSet
            # Grupo RD = AIH Reduzida (dados reduzidos)
            parquet_set = download(
                states=state,
                years=year,
                months=month,
                groups="RD",  # AIH Reduzida
            )

            logger.info("[EXTRACT] Download concluído")

            # ParquetSet tem método to_dataframe()
            df = parquet_set.to_dataframe()

            logger.info(f"[EXTRACT] Registros carregados: {len(df):,}")
            logger.info(f"[EXTRACT] Colunas: {len(df.columns)}")

            return df  # type: ignore[no-any-return]

        except Exception as e:
            logger.error(f"[EXTRACT] Erro: {e}")
            raise
