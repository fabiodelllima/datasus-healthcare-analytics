"""OpenDataSUS API Inspector.

Este módulo implementa client para consulta de metadados na API OpenDataSUS (CKAN),
permitindo descoberta de datasets e exploração de recursos disponíveis no portal.

IMPORTANTE: Dados SIH tradicionais (internações via FTP) NÃO estão disponíveis
via API CKAN. A API serve apenas para datasets publicados no portal OpenDataSUS.

See Also:
    docs/API.md: Regras de negócio RN-API-001 e RN-API-003
    tests/features/api_inspection.feature: Cenários BDD
"""

import logging
from typing import Any

import requests


class OpenDataSUSInspector:
    """Client para inspeção da API OpenDataSUS.

    Esta classe implementa os métodos para consultar metadados de datasets
    disponíveis no portal OpenDataSUS, seguindo as regras de negócio
    documentadas em docs/API.md.

    Attributes:
        base_url: URL base da API OpenDataSUS
        timeout: Timeout padrão para requisições (30 segundos)
        headers: Headers HTTP obrigatórios

    Example:
        >>> inspector = OpenDataSUSInspector()
        >>> packages = inspector.list_packages()
        >>> print(f"Total: {len(packages)}")
        Total: 83

    See Also:
        docs/API.md: RN-API-001 e RN-API-003
    """

    def __init__(
        self,
        base_url: str = "https://opendatasus.saude.gov.br/api/3/action/",
        timeout: int = 30,
        version: str = "0.2.0",
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
            requests.RequestException: Se erro de rede

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
        except requests.RequestException as e:
            self.logger.error(f"Request error: {e}")
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
