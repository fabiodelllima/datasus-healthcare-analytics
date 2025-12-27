"""Configuração pytest para testes BDD com VCR.py.

Este módulo configura:
- Markers customizados para pytest-bdd
- VCR.py para gravar/replay HTTP requests (evita timeouts em CI)

See Also:
    docs/METHODOLOGY.md: Metodologia de testes
    docs/TOOLING.md: Ferramentas de qualidade
"""

from pathlib import Path

import pytest
import vcr

# ============================================================================
# Configuração de Paths
# ============================================================================

TESTS_DIR = Path(__file__).parent
FIXTURES_DIR = TESTS_DIR / "fixtures"
CASSETTES_DIR = FIXTURES_DIR / "cassettes"

# Criar diretório de cassettes se não existir
CASSETTES_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Configuração VCR.py
# ============================================================================

vcr_config = vcr.VCR(
    cassette_library_dir=str(CASSETTES_DIR),
    record_mode="once",  # type: ignore[arg-type]
    match_on=["uri", "method"],
    filter_headers=["User-Agent"],
    decode_compressed_response=True,
)


@pytest.fixture
def vcr_cassette():
    """Fixture para usar VCR.py em testes individuais.

    Usage:
        def test_api_call(vcr_cassette):
            with vcr_cassette("test_name"):
                response = requests.get(url)

    Returns:
        Callable que retorna context manager do VCR
    """

    def _cassette(name: str):
        return vcr_config.use_cassette(f"{name}.yaml")

    return _cassette


@pytest.fixture
def api_vcr():
    """Fixture VCR pré-configurada para API OpenDataSUS.

    Grava automaticamente cassette baseado no nome do teste.

    Usage:
        def test_package_info(api_vcr, request):
            with api_vcr(request):
                # Faz request real na primeira execução
                # Replay nas execuções seguintes
                pass
    """

    def _api_vcr(request):
        cassette_name = request.node.name
        return vcr_config.use_cassette(f"{cassette_name}.yaml")

    return _api_vcr


# ============================================================================
# Configuração Pytest
# ============================================================================


def pytest_configure(config):
    """Registrar markers customizados."""
    config.addinivalue_line("markers", "implemented: Funcionalidade implementada e testada")
    config.addinivalue_line("markers", "skip: Funcionalidade não implementada (pula teste)")
    config.addinivalue_line("markers", "wip: Work in Progress (planejado para versão futura)")
    config.addinivalue_line("markers", "future_v0_3_0: Funcionalidade planejada para v0.3.0")
    config.addinivalue_line("markers", "endpoint_disabled: Endpoint desabilitado na API externa")
    config.addinivalue_line("markers", "vcr: Teste usa VCR.py para HTTP mocking")


def pytest_collection_modifyitems(config, items):
    """Modificar coleta de testes para pular @wip automaticamente.

    Cenários marcados com @wip no feature file são pulados
    a menos que -m wip seja passado explicitamente.
    """
    # Se -m foi passado explicitamente, não modificar
    if config.getoption("-m"):
        return

    skip_wip = pytest.mark.skip(reason="WIP: Funcionalidade não implementada")

    for item in items:
        if "wip" in item.keywords:
            item.add_marker(skip_wip)


# ============================================================================
# Fixtures Compartilhadas
# ============================================================================


@pytest.fixture
def sample_package_response():
    """Fixture com resposta de exemplo para package_show.

    Útil para testes unitários que não precisam de HTTP real.
    """
    return {
        "success": True,
        "result": {
            "id": "test-package-id",
            "name": "registro-de-ocupacao-hospitalar-covid-19",
            "title": "Registro de Ocupação Hospitalar COVID-19",
            "organization": {"name": "ministerio-da-saude", "title": "Ministério da Saúde"},
            "resources": [],
            "metadata_modified": "2024-11-20T15:45:30",
        },
    }


@pytest.fixture
def sample_package_list():
    """Fixture com lista de packages de exemplo."""
    return [
        "acompanhamento-gestacional-siasi",
        "alimentar-nutricional-van-siasi",
        "registro-de-ocupacao-hospitalar-covid-19",
        "sihsus",
    ]
