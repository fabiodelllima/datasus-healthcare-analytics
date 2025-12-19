"""
Load: Salvamento em formato dual (CSV + Parquet)
"""

import logging
import os
from datetime import datetime
from typing import Any

import pandas as pd

from src.config import PROCESSED_DIR

logger = logging.getLogger(__name__)


class DataLoader:
    """Carrega dados processados em storage dual-format"""

    def load(self, df: pd.DataFrame, state: str, year: int, month: int) -> dict[str, Any]:
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
        try:
            logger.info(f"[LOAD] Salvando: {state} {year}/{month:02d}")

            # Criar diretório se não existir
            os.makedirs(PROCESSED_DIR, exist_ok=True)

            # Gerar nomes de arquivo
            base_name = f"SIH_{state}_{year}{month:02d}"
            csv_path = os.path.join(PROCESSED_DIR, f"{base_name}.csv")
            parquet_path = os.path.join(PROCESSED_DIR, f"{base_name}.parquet")

            # Salvar CSV
            logger.info(f"[LOAD] Salvando CSV: {csv_path}")
            df.to_csv(csv_path, index=False, encoding="utf-8")

            # Salvar Parquet
            logger.info(f"[LOAD] Salvando Parquet: {parquet_path}")
            df.to_parquet(parquet_path, index=False, engine="pyarrow")

            # Metadata
            metadata = {
                "state": state,
                "year": year,
                "month": month,
                "records": len(df),
                "columns": len(df.columns),
                "csv_path": csv_path,
                "parquet_path": parquet_path,
                "csv_size_mb": os.path.getsize(csv_path) / (1024 * 1024),
                "parquet_size_mb": os.path.getsize(parquet_path) / (1024 * 1024),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"[LOAD] CSV: {metadata['csv_size_mb']:.2f} MB")
            logger.info(f"[LOAD] Parquet: {metadata['parquet_size_mb']:.2f} MB")
            logger.info(f"[LOAD] Concluído: {len(df):,} registros")

            return metadata

        except Exception as e:
            logger.error(f"[LOAD] Erro: {e}")
            raise
