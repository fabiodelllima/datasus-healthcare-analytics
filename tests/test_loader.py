"""
Testes para DataLoader
"""

import os
import shutil
import tempfile

import pandas as pd

from src.load.loader import DataLoader


class TestDataLoader:
    """Testes para salvamento dual-format"""

    def setup_method(self):
        """Criar diretório temporário para testes"""
        self.temp_dir = tempfile.mkdtemp()
        # Monkey patch PROCESSED_DIR
        import src.config

        self.original_dir = src.config.PROCESSED_DIR
        src.config.PROCESSED_DIR = self.temp_dir

    def teardown_method(self):
        """Remover diretório temporário"""
        shutil.rmtree(self.temp_dir)
        # Restaurar PROCESSED_DIR original
        import src.config

        src.config.PROCESSED_DIR = self.original_dir

    def test_save_csv_and_parquet(self):
        """Deve salvar CSV e Parquet com sucesso"""
        df = pd.DataFrame({"N_AIH": ["123", "456"], "IDADE": [25, 30], "VAL_TOT": [100.0, 200.0]})

        loader = DataLoader()
        metadata = loader.load(df, state="AC", year=2024, month=1)

        assert os.path.exists(metadata["csv_path"])
        assert os.path.exists(metadata["parquet_path"])
        assert metadata["records"] == 2
        assert metadata["columns"] == 3

    def test_metadata_completeness(self):
        """Metadata deve conter todas informações necessárias"""
        df = pd.DataFrame({"col": [1, 2, 3]})

        loader = DataLoader()
        metadata = loader.load(df, state="ES", year=2024, month=2)

        assert "state" in metadata
        assert "year" in metadata
        assert "month" in metadata
        assert "records" in metadata
        assert "columns" in metadata
        assert "csv_path" in metadata
        assert "parquet_path" in metadata
        assert "csv_size_mb" in metadata
        assert "parquet_size_mb" in metadata
        assert "timestamp" in metadata

        assert metadata["state"] == "ES"
        assert metadata["year"] == 2024
        assert metadata["month"] == 2
        assert metadata["records"] == 3
