"""
Extract: Download e decode de arquivos DBC do DataSUS
"""

import logging
from pysus.online_data import SIH
import pandas as pd

logger = logging.getLogger(__name__)


class DataSUSExtractor:
    """Extrai dados do DataSUS via pysus"""
    
    def __init__(self):
        self.sih = SIH()
    
    def extract(self, state: str, year: int, month: int) -> pd.DataFrame:
        """
        Extrai dados do SIH/DataSUS
        
        Args:
            state: UF (ex: 'AC', 'SP')
            year: Ano (ex: 2024)
            month: Mês (1-12)
        
        Returns:
            DataFrame com dados brutos
        """
        logger.info(f"[EXTRACT] Iniciando download: {state} {year}/{month:02d}")
        
        try:
            df = self.sih.download(state=state, year=year, month=month, group='RD')
            logger.info(f"[EXTRACT] Sucesso: {len(df)} registros, {len(df.columns)} colunas")
            return df
        except Exception as e:
            logger.error(f"[EXTRACT] Erro ao baixar dados: {e}")
            raise
