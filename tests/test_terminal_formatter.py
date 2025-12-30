"""Testes para TerminalFormatter e métodos display do API Inspector."""

from unittest.mock import MagicMock, patch

from src.api.datasus_inspector import OpenDataSUSInspector, TerminalFormatter


class TestTerminalFormatter:
    """Testes para classe TerminalFormatter."""

    def test_visible_len_plain_text(self) -> None:
        """Verifica cálculo de largura sem códigos ANSI."""
        result = TerminalFormatter._visible_len("Hello World")
        assert result == 11

    def test_visible_len_with_ansi(self) -> None:
        """Verifica cálculo de largura com códigos ANSI."""
        colored = f"{TerminalFormatter.GREEN}Hello{TerminalFormatter.RESET}"
        result = TerminalFormatter._visible_len(colored)
        assert result == 5

    def test_success_formatting(self) -> None:
        """Verifica formatação de sucesso."""
        result = TerminalFormatter.success("OK")
        assert "\033[92m" in result
        assert "OK" in result
        assert "\033[0m" in result

    def test_error_formatting(self) -> None:
        """Verifica formatação de erro."""
        result = TerminalFormatter.error("FAIL")
        assert "\033[91m" in result
        assert "FAIL" in result

    def test_warning_formatting(self) -> None:
        """Verifica formatação de warning."""
        result = TerminalFormatter.warning("WARN")
        assert "\033[93m" in result
        assert "WARN" in result

    def test_info_formatting(self) -> None:
        """Verifica formatação de info."""
        result = TerminalFormatter.info("INFO")
        assert "\033[94m" in result
        assert "INFO" in result

    def test_bold_formatting(self) -> None:
        """Verifica formatação em negrito."""
        result = TerminalFormatter.bold("BOLD")
        assert "\033[1m" in result
        assert "BOLD" in result

    def test_header_formatting(self) -> None:
        """Verifica formatação de header."""
        result = TerminalFormatter.header("HEADER")
        assert "\033[1m" in result
        assert "\033[96m" in result
        assert "HEADER" in result

    def test_check_mark_success(self) -> None:
        """Verifica check mark de sucesso."""
        result = TerminalFormatter.check_mark(True)
        assert "✓" in result
        assert "\033[92m" in result

    def test_check_mark_failure(self) -> None:
        """Verifica check mark de falha."""
        result = TerminalFormatter.check_mark(False)
        assert "✗" in result
        assert "\033[91m" in result

    def test_status_tag_ok(self) -> None:
        """Verifica tag OK."""
        result = TerminalFormatter.status_tag("ok")
        assert "[OK]" in result
        assert "\033[92m" in result

    def test_status_tag_error(self) -> None:
        """Verifica tag ERROR."""
        result = TerminalFormatter.status_tag("error")
        assert "[ERROR]" in result
        assert "\033[91m" in result

    def test_status_tag_warning(self) -> None:
        """Verifica tag WARNING."""
        result = TerminalFormatter.status_tag("warning")
        assert "[WARNING]" in result
        assert "\033[93m" in result

    def test_status_tag_info(self) -> None:
        """Verifica tag INFO."""
        result = TerminalFormatter.status_tag("info")
        assert "[INFO]" in result
        assert "\033[94m" in result

    def test_status_tag_unknown(self) -> None:
        """Verifica tag desconhecida."""
        result = TerminalFormatter.status_tag("custom")
        assert "[CUSTOM]" in result

    def test_box_basic(self) -> None:
        """Verifica box básica."""
        result = TerminalFormatter.box("Title", ["Line 1", "Line 2"])
        assert "┌" in result
        assert "┐" in result
        assert "└" in result
        assert "┘" in result
        assert "─" in result
        assert "│" in result
        assert "Title" in result
        assert "Line 1" in result
        assert "Line 2" in result

    def test_box_with_colored_content(self) -> None:
        """Verifica box com conteúdo colorido."""
        colored_line = TerminalFormatter.success("Success!")
        result = TerminalFormatter.box("Test", [colored_line])
        assert "Success!" in result
        assert "┌" in result

    def test_box_truncates_long_lines(self) -> None:
        """Verifica truncamento de linhas longas."""
        long_line = "A" * 100
        result = TerminalFormatter.box("Test", [long_line], width=40)
        assert "..." in result


class TestOpenDataSUSInspectorDisplay:
    """Testes para métodos display do OpenDataSUSInspector."""

    @patch.object(OpenDataSUSInspector, "get_package_info")
    def test_display_package_info_found(self, mock_get_package: MagicMock) -> None:
        """Verifica display de package encontrado."""
        mock_get_package.return_value = {
            "title": "Test Package",
            "name": "test-package",
            "organization": {"title": "Test Org"},
            "state": "active",
            "metadata_created": "2024-01-15T10:00:00",
            "resources": [{"id": "1"}],
        }

        inspector = OpenDataSUSInspector()
        result = inspector.display_package_info("test-package")

        assert "Test Package" in result
        assert "test-package" in result
        assert "Test Org" in result
        assert "active" in result
        assert "2024-01-15" in result
        assert "┌" in result

    @patch.object(OpenDataSUSInspector, "get_package_info")
    def test_display_package_info_not_found(self, mock_get_package: MagicMock) -> None:
        """Verifica display de package não encontrado."""
        mock_get_package.return_value = None

        inspector = OpenDataSUSInspector()
        result = inspector.display_package_info("nonexistent")

        assert "Not Found" in result
        assert "nonexistent" in result
        assert "✗" in result

    @patch.object(OpenDataSUSInspector, "list_packages")
    def test_display_packages_list_success(self, mock_list: MagicMock) -> None:
        """Verifica display de lista de packages."""
        mock_list.return_value = ["pkg1", "pkg2", "pkg3", "pkg4", "pkg5"]

        inspector = OpenDataSUSInspector()
        result = inspector.display_packages_list(limit=3)

        assert "pkg1" in result
        assert "pkg2" in result
        assert "pkg3" in result
        assert "e mais 2 packages" in result
        assert "✓" in result

    @patch.object(OpenDataSUSInspector, "list_packages")
    def test_display_packages_list_empty(self, mock_list: MagicMock) -> None:
        """Verifica display de lista vazia."""
        mock_list.return_value = []

        inspector = OpenDataSUSInspector()
        result = inspector.display_packages_list()

        assert "Nenhum package encontrado" in result
        assert "✗" in result

    @patch.object(OpenDataSUSInspector, "list_packages")
    def test_display_status_success(self, mock_list: MagicMock) -> None:
        """Verifica display de status OK."""
        mock_list.return_value = ["pkg1", "pkg2", "pkg3"]

        inspector = OpenDataSUSInspector()
        result = inspector.display_status()

        assert "Conexão" in result
        assert "[OK]" in result
        assert "3 disponíveis" in result

    @patch.object(OpenDataSUSInspector, "list_packages")
    def test_display_status_timeout(self, mock_list: MagicMock) -> None:
        """Verifica display de status com timeout."""
        import requests

        mock_list.side_effect = requests.Timeout()

        inspector = OpenDataSUSInspector()
        result = inspector.display_status()

        assert "Conexão" in result
        assert "[ERROR]" in result
        assert "Timeout" in result

    @patch.object(OpenDataSUSInspector, "list_packages")
    def test_display_status_request_error(self, mock_list: MagicMock) -> None:
        """Verifica display de status com erro de request."""
        import requests

        mock_list.side_effect = requests.RequestException("Connection failed")

        inspector = OpenDataSUSInspector()
        result = inspector.display_status()

        assert "Conexão" in result
        assert "[ERROR]" in result
        assert "Erro:" in result
