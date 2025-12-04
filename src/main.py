"""
Pipeline ETL principal
"""

import argparse
from src.extract.extractor import DataSUSExtractor
from src.transform.transformer import DataTransformer
from src.load.loader import DataLoader
from src.utils.logger import setup_logger
from src.config import DEFAULT_STATE, DEFAULT_YEAR, DEFAULT_MONTH

logger = setup_logger(__name__)


def main(state: str, year: int, month: int):
    """
    Executa pipeline ETL completo
    
    Args:
        state: UF (ex: 'AC')
        year: Ano (ex: 2024)
        month: Mês (1-12)
    """
    logger.info("=" * 70)
    logger.info("DataSUS Healthcare Analytics - Pipeline ETL")
    logger.info("=" * 70)
    logger.info(f"Estado: {state}, Período: {year}/{month:02d}")
    logger.info("=" * 70)
    
    try:
        # Extract
        extractor = DataSUSExtractor()
        df_raw = extractor.extract(state, year, month)
        
        # Transform
        transformer = DataTransformer()
        df_clean = transformer.transform(df_raw)
        
        # Load
        loader = DataLoader()
        result = loader.load(df_clean, state, year, month)
        
        logger.info("=" * 70)
        logger.info("[PIPELINE] Concluído com sucesso!")
        logger.info(f"[PIPELINE] CSV: {result['csv_path']}")
        logger.info(f"[PIPELINE] Parquet: {result['parquet_path']}")
        logger.info("=" * 70)
        
        return result
        
    except Exception as e:
        logger.error(f"[PIPELINE] Erro crítico: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pipeline ETL DataSUS')
    parser.add_argument('--state', type=str, default=DEFAULT_STATE,
                        help='UF (ex: AC, SP, RJ)')
    parser.add_argument('--year', type=int, default=DEFAULT_YEAR,
                        help='Ano (ex: 2024)')
    parser.add_argument('--month', type=int, default=DEFAULT_MONTH,
                        help='Mês (1-12)')
    
    args = parser.parse_args()
    main(args.state, args.year, args.month)
