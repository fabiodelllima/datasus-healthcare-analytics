"""OpenDataSUS API Inspector.

Este módulo implementa client para consulta de metadados na API OpenDataSUS (CKAN),
permitindo descoberta de datasets e exploração de recursos disponíveis no portal.

IMPORTANTE: Dados SIH tradicionais (internações via FTP) NÃO estão disponíveis
via API CKAN. A API serve apenas para datasets publicados no portal OpenDataSUS.

See Also:
    docs/API.md: Regras de negócio RN-API-001 a RN-API-005
    tests/features/api_inspection.feature: Cenários BDD
"""

import logging
import re
from typing import Any

import requests


class TerminalFormatter:
    """Formatador de output para terminal com cores ANSI e box drawing.

    Implementa RN-API-004: Formatação de Output Terminal.

    Símbolos permitidos:
        - Status: ✓ ✗
        - Box Drawing: ┌ ┐ └ ┘ ─ │ ├ ┤
        - Tags: [OK] [ERROR] [WARNING] [INFO]

    See Also:
        docs/API.md: RN-API-004
    """

    # ANSI color codes
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    # Regex para remover códigos ANSI (usado para calcular largura visual)
    ANSI_PATTERN = re.compile(r"\033\[[0-9;]*m")

    @classmethod
    def _visible_len(cls, text: str) -> int:
        """Calcula largura visível do texto (sem códigos ANSI)."""
        return len(cls.ANSI_PATTERN.sub("", text))

    @classmethod
    def success(cls, text: str) -> str:
        """Formata texto de sucesso (verde)."""
        return f"{cls.GREEN}{text}{cls.RESET}"

    @classmethod
    def error(cls, text: str) -> str:
        """Formata texto de erro (vermelho)."""
        return f"{cls.RED}{text}{cls.RESET}"

    @classmethod
    def warning(cls, text: str) -> str:
        """Formata texto de warning (amarelo)."""
        return f"{cls.YELLOW}{text}{cls.RESET}"

    @classmethod
    def info(cls, text: str) -> str:
        """Formata texto de info (azul)."""
        return f"{cls.BLUE}{text}{cls.RESET}"

    @classmethod
    def bold(cls, text: str) -> str:
        """Formata texto em negrito."""
        return f"{cls.BOLD}{text}{cls.RESET}"

    @classmethod
    def header(cls, text: str) -> str:
        """Formata texto de header (cyan + bold)."""
        return f"{cls.BOLD}{cls.CYAN}{text}{cls.RESET}"

    @classmethod
    def box(cls, title: str, content: list[str], width: int = 60) -> str:
        """Cria uma box com título e conteúdo.

        Args:
            title: Título da box
            content: Lista de linhas de conteúdo
            width: Largura da box (padrão: 60)

        Returns:
            String formatada com box drawing
        """
        lines = []
        inner_width = width - 2

        # Top border
        lines.append(f"┌{'─' * inner_width}┐")

        # Title (centralizado considerando largura visual)
        title_colored = cls.header(title)
        title_visible_len = len(title)
        padding_total = inner_width - title_visible_len
        padding_left = padding_total // 2
        padding_right = padding_total - padding_left
        lines.append(f"│{' ' * padding_left}{title_colored}{' ' * padding_right}│")

        # Separator
        lines.append(f"├{'─' * inner_width}┤")

        # Content
        for line in content:
            visible_len = cls._visible_len(line)
            # Truncar linha se necessário (baseado em largura visual)
            if visible_len > inner_width - 2:
                # Truncar preservando códigos ANSI é complexo, simplificar
                plain = cls.ANSI_PATTERN.sub("", line)
                line = plain[: inner_width - 5] + "..."
                visible_len = len(line)

            # Padding baseado em largura visual
            padding_needed = inner_width - visible_len - 1
            lines.append(f"│ {line}{' ' * padding_needed}│")

        # Bottom border
        lines.append(f"└{'─' * inner_width}┘")

        return "\n".join(lines)

    @classmethod
    def status_tag(cls, status: str) -> str:
        """Retorna tag de status formatada.

        Args:
            status: 'ok', 'error', 'warning', 'info'

        Returns:
            Tag formatada com cor
        """
        tags = {
            "ok": cls.success("[OK]"),
            "error": cls.error("[ERROR]"),
            "warning": cls.warning("[WARNING]"),
            "info": cls.info("[INFO]"),
        }
        return tags.get(status.lower(), f"[{status.upper()}]")

    @classmethod
    def check_mark(cls, success: bool = True) -> str:
        """Retorna símbolo de check ou X."""
        if success:
            return cls.success("✓")
        return cls.error("✗")


class OpenDataSUSInspector:
    """Client para inspeção da API OpenDataSUS.

    Esta classe implementa os métodos para consultar metadados de datasets
    disponíveis no portal OpenDataSUS, seguindo as regras de negócio
    documentadas em docs/API.md.

    Attributes:
        base_url: URL base da API OpenDataSUS
        timeout: Timeout padrão para requisições (30 segundos)
        headers: Headers HTTP obrigatórios
        formatter: Formatador de output terminal

    Example:
        >>> inspector = OpenDataSUSInspector()
        >>> packages = inspector.list_packages()
        >>> print(f"Total: {len(packages)}")
        Total: 83

    See Also:
        docs/API.md: RN-API-001 a RN-API-005
    """

    def __init__(
        self,
        base_url: str = "https://opendatasus.saude.gov.br/api/3/action/",
        timeout: int = 30,
        version: str = "0.2.6",
    ) -> None:
        """Inicializa o inspector da API OpenDataSUS.

        Args:
            base_url: URL base da API (padrão: opendatasus.saude.gov.br)
            timeout: Timeout em segundos (padrão: 30s)
            version: Versão do projeto para User-Agent

        See Also:
            docs/API.md: RN-API-005 configuração de headers
        """
        self.base_url = base_url
        self.timeout = timeout
        self.headers = {
            "User-Agent": f"DataSUS-Healthcare-Analytics/{version} (Educational Project; Python/3.11)",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
        }
        self.logger = logging.getLogger(__name__)
        self.fmt = TerminalFormatter()

    def _validate_package_id(self, package_id: str) -> None:
        """Valida parâmetro package_id.

        Args:
            package_id: Identificador do package

        Raises:
            ValueError: Se package_id vazio ou < 2 caracteres

        See Also:
            docs/API.md: RN-API-001 regras de validação
        """
        if not package_id:
            raise ValueError("Package ID cannot be empty")
        if len(package_id) < 2:
            raise ValueError("Package ID must be at least 2 characters")

    def get_package_info(self, package_id: str) -> dict[str, Any] | None:
        """Obtém informações detalhadas de um package específico.

        Args:
            package_id: Identificador do package

        Returns:
            Dict com metadados do package, ou None se não encontrado

        Raises:
            ValueError: Se package_id inválido
            requests.Timeout: Se requisição exceder 30s
            requests.ConnectionError: Se erro de conexão

        Example:
            >>> inspector = OpenDataSUSInspector()
            >>> info = inspector.get_package_info('registro-de-ocupacao-hospitalar-covid-19')
            >>> print(info['title'])
            'Registro de Ocupação Hospitalar COVID-19'

        See Also:
            docs/API.md: RN-API-001 package_show endpoint
        """
        self._validate_package_id(package_id)

        url = f"{self.base_url}package_show"
        params = {"id": package_id}

        self.logger.info(f"Request to package_show: package_id={package_id}")

        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)

            # 404 retorna None (package não existe), não levanta exceção
            if response.status_code == 404:
                self.logger.info(f"Package '{package_id}' not found (404)")
                return None

            response.raise_for_status()

            # Verificar Content-Type
            content_type = response.headers.get("Content-Type", "")
            if "text/html" in content_type:
                self.logger.warning(f"API returned HTML instead of JSON: {url}")
                raise ValueError("API returned HTML (possible maintenance or error page)")

            data = response.json()

            if not data.get("success"):
                self.logger.info(f"Package '{package_id}' not found in OpenDataSUS")
                return None

            self.logger.info(f"Package '{package_id}' found successfully")
            result: dict[str, Any] = data["result"]
            return result

        except requests.Timeout:
            self.logger.warning(f"Request timeout after {self.timeout}s: {url}")
            raise
        except requests.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise

    def list_packages(self) -> list[str]:
        """Lista todos os packages disponíveis no portal.

        Returns:
            Lista de IDs dos packages

        Raises:
            requests.Timeout: Se requisição exceder 30s
            requests.RequestException: Se erro de rede

        Example:
            >>> inspector = OpenDataSUSInspector()
            >>> packages = inspector.list_packages()
            >>> print(packages[:3])
            ['acompanhamento-gestacional-siasi', 'alimentar-nutricional-van-siasi', ...]

        See Also:
            docs/API.md: RN-API-003 package_list endpoint
        """
        url = f"{self.base_url}package_list"

        self.logger.info("Retrieving package list")

        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()

            # Verificar Content-Type antes de parsear JSON
            content_type = response.headers.get("Content-Type", "")
            if "text/html" in content_type:
                self.logger.warning(f"API returned HTML instead of JSON: {url}")
                raise requests.RequestException(
                    "API returned HTML (portal may be under maintenance)"
                )

            data = response.json()

            if data.get("success"):
                packages = data["result"]
                if not packages:
                    self.logger.warning("API returned empty package list (expected 50+ packages)")
                else:
                    self.logger.info(f"Retrieved {len(packages)} packages")
                result: list[str] = packages
                return result

            return []

        except requests.Timeout:
            self.logger.warning(f"Request timeout after {self.timeout}s: {url}")
            raise
        except requests.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise

    def display_package_info(self, package_id: str) -> str:
        """Exibe informações de um package formatadas para terminal.

        Implementa RN-API-004: Formatação de Output Terminal.

        Args:
            package_id: Identificador do package

        Returns:
            String formatada com box drawing e cores ANSI

        Example:
            >>> inspector = OpenDataSUSInspector()
            >>> print(inspector.display_package_info('covid-19'))
        """
        info = self.get_package_info(package_id)

        if info is None:
            return self.fmt.box(
                "Package Not Found",
                [
                    f"{self.fmt.check_mark(False)} Package: {package_id}",
                    f"{self.fmt.status_tag('error')} Não encontrado no OpenDataSUS",
                ],
            )

        # Extrair campos relevantes
        title = info.get("title", "N/A")
        name = info.get("name", "N/A")
        num_resources = len(info.get("resources", []))
        org = info.get("organization", {}).get("title", "N/A")
        state = info.get("state", "N/A")
        created = info.get("metadata_created", "N/A")[:10]

        content = [
            f"{self.fmt.check_mark(True)} Status: {self.fmt.status_tag('ok')} Encontrado",
            "",
            f"{self.fmt.bold('Título:')} {title}",
            f"{self.fmt.bold('Nome:')} {name}",
            f"{self.fmt.bold('Organização:')} {org}",
            f"{self.fmt.bold('Estado:')} {state}",
            f"{self.fmt.bold('Criado em:')} {created}",
            f"{self.fmt.bold('Recursos:')} {num_resources}",
        ]

        return self.fmt.box(f"Package: {package_id}", content)

    def display_packages_list(self, limit: int = 10) -> str:
        """Exibe lista de packages formatada para terminal.

        Implementa RN-API-004: Formatação de Output Terminal.

        Args:
            limit: Número máximo de packages a exibir (padrão: 10)

        Returns:
            String formatada com box drawing e cores ANSI

        Example:
            >>> inspector = OpenDataSUSInspector()
            >>> print(inspector.display_packages_list(5))
        """
        packages = self.list_packages()

        if not packages:
            return self.fmt.box(
                "OpenDataSUS Packages",
                [
                    f"{self.fmt.check_mark(False)} Nenhum package encontrado",
                    f"{self.fmt.status_tag('warning')} Verifique conexão com API",
                ],
            )

        content = [
            f"{self.fmt.check_mark(True)} Status: {self.fmt.status_tag('ok')} Conectado",
            f"{self.fmt.bold('Total packages:')} {len(packages)}",
            "",
            self.fmt.bold("Primeiros packages:"),
        ]

        for i, pkg in enumerate(packages[:limit], 1):
            content.append(f"  {i:2d}. {pkg}")

        if len(packages) > limit:
            content.append(f"  ... e mais {len(packages) - limit} packages")

        return self.fmt.box("OpenDataSUS Packages", content, width=70)

    def display_status(self) -> str:
        """Exibe status da conexão com API formatado para terminal.

        Returns:
            String formatada com status da API
        """
        content = [
            f"{self.fmt.bold('API URL:')} {self.base_url}",
            f"{self.fmt.bold('Timeout:')} {self.timeout}s",
            "",
        ]

        # Testar conexão
        try:
            packages = self.list_packages()
            content.extend(
                [
                    f"{self.fmt.check_mark(True)} Conexão: {self.fmt.status_tag('ok')}",
                    f"{self.fmt.check_mark(True)} Packages: {len(packages)} disponíveis",
                ]
            )
        except requests.Timeout:
            content.extend(
                [
                    f"{self.fmt.check_mark(False)} Conexão: {self.fmt.status_tag('error')}",
                    f"  Timeout após {self.timeout}s",
                ]
            )
        except requests.RequestException as e:
            content.extend(
                [
                    f"{self.fmt.check_mark(False)} Conexão: {self.fmt.status_tag('error')}",
                    f"  Erro: {str(e)[:40]}",
                ]
            )

        return self.fmt.box("OpenDataSUS API Status", content)
