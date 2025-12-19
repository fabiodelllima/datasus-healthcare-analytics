"""
Main: Ponto de entrada do pipeline ETL
"""

import argparse

from src.config import DATASUS_CONFIG
from src.extract.extractor import DataSUSExtractor
from src.load.loader import DataLoader
from src.transform.transformer import DataTransformer
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()


def main(state: str, year: int, month: int):
    """
    Executa pipeline ETL completo

    Args:
        state: UF (2 letras)
        year: Ano (YYYY)
        month: Mês (1-12)
    """
    try:
        logger.info("=" * 70)
        logger.info("DataSUS Healthcare Analytics - Pipeline ETL")
        logger.info("=" * 70)
        logger.info(f"Estado: {state}, Período: {year}/{month:02d}")
        logger.info("=" * 70)

        # 1. EXTRACT
        extractor = DataSUSExtractor()
        df_raw = extractor.extract(state, year, month)
        logger.info(f"[EXTRACT] ✓ Registros brutos: {len(df_raw):,}")

        # 2. TRANSFORM
        transformer = DataTransformer()
        df_clean = transformer.transform(df_raw)
        logger.info(f"[TRANSFORM] ✓ Registros limpos: {len(df_clean):,}")

        # 3. LOAD
        loader = DataLoader()
        metadata = loader.load(df_clean, state, year, month)
        logger.info(f"[LOAD] ✓ Salvos: {metadata['records']:,} registros")

        # SUCESSO
        logger.info("=" * 70)
        logger.info("[SUCCESS] Pipeline concluído com sucesso!")
        logger.info(f"CSV: {metadata['csv_path']}")
        logger.info(f"Parquet: {metadata['parquet_path']}")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"[PIPELINE] Erro crítico: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DataSUS ETL Pipeline")
    parser.add_argument(
        "--state",
        type=str,
        default=DATASUS_CONFIG["default_state"],
        help="UF (2 letras, ex: AC, SP)",
    )
    parser.add_argument(
        "--year", type=int, default=DATASUS_CONFIG["default_year"], help="Ano (ex: 2024)"
    )
    parser.add_argument(
        "--month", type=int, default=DATASUS_CONFIG["default_month"], help="Mês (1-12)"
    )

    args = parser.parse_args()
    main(args.state, args.year, args.month)
