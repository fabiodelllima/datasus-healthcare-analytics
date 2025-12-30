"""Testes para o módulo principal (main.py)."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.main import main


class TestMain:
    """Testes para função main do pipeline."""

    @patch("src.main.DataLoader")
    @patch("src.main.DataTransformer")
    @patch("src.main.DataSUSExtractor")
    def test_pipeline_success(
        self,
        mock_extractor_class: MagicMock,
        mock_transformer_class: MagicMock,
        mock_loader_class: MagicMock,
    ) -> None:
        """Verifica execução bem-sucedida do pipeline."""
        # Setup extractor mock
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = pd.DataFrame({"col": [1, 2, 3]})
        mock_extractor_class.return_value = mock_extractor

        # Setup transformer mock
        mock_transformer = MagicMock()
        mock_transformer.transform.return_value = pd.DataFrame({"col": [1, 2, 3]})
        mock_transformer_class.return_value = mock_transformer

        # Setup loader mock
        mock_loader = MagicMock()
        mock_loader.load.return_value = {
            "records": 3,
            "csv_path": "/path/to/file.csv",
            "parquet_path": "/path/to/file.parquet",
        }
        mock_loader_class.return_value = mock_loader

        # Execute - não deve lançar exceção
        main(state="AC", year=2024, month=1)

        # Verify
        mock_extractor.extract.assert_called_once_with("AC", 2024, 1)
        mock_transformer.transform.assert_called_once()
        mock_loader.load.assert_called_once()

    @patch("src.main.DataSUSExtractor")
    def test_pipeline_exception_propagates(
        self,
        mock_extractor_class: MagicMock,
    ) -> None:
        """Verifica que exceções são propagadas."""
        mock_extractor = MagicMock()
        mock_extractor.extract.side_effect = Exception("Test error")
        mock_extractor_class.return_value = mock_extractor

        with pytest.raises(Exception, match="Test error"):
            main(state="AC", year=2024, month=1)

    @patch("src.main.DataLoader")
    @patch("src.main.DataTransformer")
    @patch("src.main.DataSUSExtractor")
    def test_pipeline_different_state(
        self,
        mock_extractor_class: MagicMock,
        mock_transformer_class: MagicMock,
        mock_loader_class: MagicMock,
    ) -> None:
        """Verifica pipeline com estado diferente."""
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = pd.DataFrame({"col": [1]})
        mock_extractor_class.return_value = mock_extractor

        mock_transformer = MagicMock()
        mock_transformer.transform.return_value = pd.DataFrame({"col": [1]})
        mock_transformer_class.return_value = mock_transformer

        mock_loader = MagicMock()
        mock_loader.load.return_value = {
            "records": 1,
            "csv_path": "/path/to/es.csv",
            "parquet_path": "/path/to/es.parquet",
        }
        mock_loader_class.return_value = mock_loader

        main(state="ES", year=2023, month=6)

        mock_extractor.extract.assert_called_once_with("ES", 2023, 6)
