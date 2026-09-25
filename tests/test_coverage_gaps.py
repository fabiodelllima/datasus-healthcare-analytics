"""Testes para cobrir gaps de coverage."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from src.analytics.kpis import KPICalculator
from src.api.datasus_inspector import OpenDataSUSInspector


class TestKPICalculatorEdgeCases:
    """Testes para casos edge do KPICalculator."""

    def test_volume_group_by_month_missing_column(self) -> None:
        """Verifica erro quando DT_INTER falta para group_by month."""
        df = pd.DataFrame({"VAL_TOT": [100, 200]})
        calc = KPICalculator()

        with pytest.raises(KeyError, match="DT_INTER"):
            calc.volume(df, group_by="month")

    def test_volume_group_by_invalid_column(self) -> None:
        """Verifica erro quando coluna de group_by não existe."""
        df = pd.DataFrame({"VAL_TOT": [100, 200]})
        calc = KPICalculator()

        with pytest.raises(KeyError, match="INVALID"):
            calc.volume(df, group_by="INVALID")

    def test_revenue_group_by_invalid_column(self) -> None:
        """Verifica erro quando coluna de group_by não existe em revenue."""
        df = pd.DataFrame({"VAL_TOT": [100.0, 200.0]})
        calc = KPICalculator()

        with pytest.raises(KeyError, match="INVALID"):
            calc.revenue(df, group_by="INVALID")


class TestOpenDataSUSInspectorEdgeCases:
    """Testes para casos edge do OpenDataSUSInspector."""

    def test_validate_package_id_too_short(self) -> None:
        """Verifica validação de package_id muito curto."""
        inspector = OpenDataSUSInspector()

        with pytest.raises(ValueError, match="at least 2 characters"):
            inspector._validate_package_id("a")

    @patch("src.api.datasus_inspector.requests.get")
    def test_get_package_info_html_response(self, mock_get: MagicMock) -> None:
        """Verifica tratamento quando API retorna HTML."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_get.return_value = mock_response

        inspector = OpenDataSUSInspector()

        with pytest.raises(ValueError, match="HTML"):
            inspector.get_package_info("test-package")

    @patch("src.api.datasus_inspector.requests.get")
    def test_get_package_info_timeout(self, mock_get: MagicMock) -> None:
        """Verifica tratamento de timeout."""
        mock_get.side_effect = requests.Timeout()

        inspector = OpenDataSUSInspector()

        with pytest.raises(requests.Timeout):
            inspector.get_package_info("test-package")

    @patch("src.api.datasus_inspector.requests.get")
    def test_get_package_info_connection_error(self, mock_get: MagicMock) -> None:
        """Verifica tratamento de erro de conexão."""
        mock_get.side_effect = requests.ConnectionError("Network error")

        inspector = OpenDataSUSInspector()

        with pytest.raises(requests.ConnectionError):
            inspector.get_package_info("test-package")

    @patch("src.api.datasus_inspector.requests.get")
    def test_list_packages_empty_result(self, mock_get: MagicMock) -> None:
        """Verifica warning quando lista de packages vem vazia."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "result": []}
        mock_get.return_value = mock_response

        inspector = OpenDataSUSInspector()
        result = inspector.list_packages()

        assert result == []

    @patch("src.api.datasus_inspector.requests.get")
    def test_list_packages_timeout(self, mock_get: MagicMock) -> None:
        """Verifica tratamento de timeout em list_packages."""
        mock_get.side_effect = requests.Timeout()

        inspector = OpenDataSUSInspector()

        with pytest.raises(requests.Timeout):
            inspector.list_packages()

    @patch("src.api.datasus_inspector.requests.get")
    def test_list_packages_request_exception(self, mock_get: MagicMock) -> None:
        """Verifica tratamento de RequestException em list_packages."""
        mock_get.side_effect = requests.RequestException("Generic error")

        inspector = OpenDataSUSInspector()

        with pytest.raises(requests.RequestException):
            inspector.list_packages()


class TestExtractorEdgeCases:
    """Testes para casos edge do Extractor."""

    @patch("src.extract.extractor.ftp")
    def test_extract_success(self, mock_ftp: MagicMock) -> None:
        """Verifica extração bem-sucedida."""
        from src.extract.extractor import DataSUSExtractor

        # A API 2.x devolve o DataFrame direto quando as_dataframe=True,
        # sem o ParquetSet intermediario da serie 0.x.
        mock_ftp.sih.return_value = pd.DataFrame({"N_AIH": [1, 2, 3], "VAL_TOT": [100, 200, 300]})

        extractor = DataSUSExtractor()
        result = extractor.extract(state="AC", year=2024, month=1)

        assert len(result) == 3
        mock_ftp.sih.assert_called_once_with("AC", 2024, 1, group="RD", as_dataframe=True)

    @patch("src.extract.extractor.ftp")
    def test_extract_rejects_non_dataframe(self, mock_ftp: MagicMock) -> None:
        """Verifica que retorno fora do contrato falha cedo."""
        from src.extract.extractor import DataSUSExtractor

        # Com download=False a API devolve caminhos, nao DataFrame. O
        # extractor deve recusar em vez de propagar o tipo errado adiante.
        mock_ftp.sih.return_value = ["public/data/ftp/sih/RD/2024/01/AC/RDAC2401.parquet"]

        extractor = DataSUSExtractor()

        with pytest.raises(TypeError, match="Esperado DataFrame"):
            extractor.extract(state="AC", year=2024, month=1)

    @patch("src.extract.extractor.ftp")
    def test_extract_exception(self, mock_ftp: MagicMock) -> None:
        """Verifica tratamento de exceção no extract."""
        from src.extract.extractor import DataSUSExtractor

        mock_ftp.sih.side_effect = Exception("FTP error")

        extractor = DataSUSExtractor()

        with pytest.raises(Exception, match="FTP error"):
            extractor.extract(state="AC", year=2024, month=1)
