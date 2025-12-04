"""
Load: Salvamento em formato dual (CSV + Parquet)
"""

import logging
import os
from datetime import datetime
import pandas as pd
from src.config import PROCESSED_DIR

logger = logging.getLogger(__name__)


class DataLoader:
    """Carrega dados processados em storage dual-format"""
    
    def load(self, df: pd.DataFrame, state: str, year: int, month: int) -> dict:
        """
        Salva dados em CSV e Parquet
        
        Args:
            df: DataFrame processado
            state: UF
            year: Ano
            month: Mês
        
        Returns:
            Dict com paths e metadata
        """
        logger.info("[LOAD] Iniciando salvamento dual-format")
        
        # Criar diretório
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        
        # Nomenclatura
        filename_base = f"sih_{state}_{year}{month:02d}"
        csv_path = PROCESSED_DIR / f"{filename_base}.csv"
        parquet_path = PROCESSED_DIR / f"{filename_base}.parquet"
        
        # Salvar CSV
        logger.info(f"[LOAD] Salvando CSV: {csv_path}")
        df.to_csv(csv_path, index=False, encoding='utf-8')
        csv_size = os.path.getsize(csv_path) / 1024 / 1024
        
        # Salvar Parquet
        logger.info(f"[LOAD] Salvando Parquet: {parquet_path}")
        df.to_parquet(parquet_path, index=False, compression='snappy')
        parquet_size = os.path.getsize(parquet_path) / 1024 / 1024
        
        # Metadata
        metadata = {
            'state': state,
            'year': year,
            'month': month,
            'records': len(df),
            'columns': len(df.columns),
            'csv_size_mb': round(csv_size, 2),
            'parquet_size_mb': round(parquet_size, 2),
            'reduction_pct': round(((csv_size - parquet_size) / csv_size) * 100, 1),
            'processed_at': datetime.now().isoformat()
        }
        
        logger.info(f"[LOAD] CSV: {csv_size:.2f} MB, Parquet: {parquet_size:.2f} MB")
        logger.info(f"[LOAD] Redução: {metadata['reduction_pct']}%")
        
        return {
            'csv_path': str(csv_path),
            'parquet_path': str(parquet_path),
            'metadata': metadata
        }
