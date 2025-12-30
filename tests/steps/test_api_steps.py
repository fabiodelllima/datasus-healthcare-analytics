"""Step definitions para testes BDD da API OpenDataSUS.

Implementa cenários marcados como @implemented usando VCR.py
para gravar/replay HTTP requests (evita timeouts em CI).

See Also:
    docs/API.md: Regras de negócio
    tests/features/api_inspection.feature: Cenários BDD
    tests/conftest.py: Configuração VCR.py
"""

from pathlib import Path

import pytest
import vcr
from pytest_bdd import given, parsers, scenarios, then, when

from src.api.datasus_inspector import OpenDataSUSInspector

# Carregar cenários do arquivo .feature
scenarios("../features/api_inspection.feature")

# ============================================================================
# Configuração VCR.py para este módulo
# ============================================================================

CASSETTES_DIR = Path(__file__).parent.parent / "fixtures" / "cassettes"
CASSETTES_DIR.mkdir(parents=True, exist_ok=True)

# Mapeamento de package_id para nome da cassette
CASSETTE_MAP = {
    "registro-de-ocupacao-hospitalar-covid-19": "package_show_covid_hospital_occupancy.yaml",
    "nonexistent-package-xyz": "package_show_nonexistent.yaml",
}

# Configuração VCR específica para testes BDD
api_vcr = vcr.VCR(
    cassette_library_dir=str(CASSETTES_DIR),
    record_mode="none",  # type: ignore[arg-type]  # Apenas replay, não grava
    match_on=["uri", "method"],
    filter_headers=["User-Agent"],
    decode_compressed_response=True,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def inspector():
    """Fixture que fornece instância do inspector."""
    return OpenDataSUSInspector()


@pytest.fixture
def context():
    """Fixture para armazenar contexto entre steps."""
    return {}


# ============================================================================
# Background
# ============================================================================


@given("an OpenDataSUS API inspector is initialized", target_fixture="inspector")
def inspector_initialized():
    """Inicializa o inspector."""
    return OpenDataSUSInspector()


# ============================================================================
# RN-API-001: package_show
# ============================================================================


@when(parsers.parse('I query package "{package_id}"'))
def query_package(inspector, context, package_id):
    """Executa query para um package usando VCR.py.

    Processa placeholders:
    - <empty> → string vazia ""

    VCR.py faz replay de cassettes pré-gravadas.
    """
    # Converter placeholder <empty> para string vazia
    if package_id == "<empty>":
        package_id = ""
        # Para package vazio, não faz request (validação local)
        try:
            context["response"] = inspector.get_package_info(package_id)
            context["error"] = None
        except Exception as e:
            context["response"] = None
            context["error"] = e
        return

    # Obter nome da cassette do mapeamento
    cassette_name = CASSETTE_MAP.get(package_id)
    if not cassette_name:
        # Fallback para nome genérico
        cassette_name = f"package_show_{package_id.replace('-', '_')[:30]}.yaml"

    try:
        with api_vcr.use_cassette(cassette_name):  # type: ignore[attr-defined]
            context["response"] = inspector.get_package_info(package_id)
            context["error"] = None
    except Exception as e:
        context["response"] = None
        context["error"] = e


@then("the response should contain package metadata")
def response_contains_metadata(context):
    """Verifica que response contém metadados."""
    assert context["response"] is not None, (
        f"Expected response but got None. Error: {context.get('error')}"
    )
    assert isinstance(context["response"], dict)


@then("metadata should include name, title, organization")
def metadata_includes_required_fields(context):
    """Verifica campos obrigatórios."""
    response = context["response"]
    assert "name" in response, f"Missing 'name' in response: {response.keys()}"
    assert "title" in response, f"Missing 'title' in response: {response.keys()}"
    assert "organization" in response, f"Missing 'organization' in response: {response.keys()}"


@then("the response should be None")
def response_is_none(context):
    """Verifica que response é None."""
    assert context["response"] is None


@then("no exception should be raised")
def no_exception_raised(context):
    """Verifica que nenhuma exceção foi levantada."""
    assert context["error"] is None, f"Unexpected error: {context['error']}"


@then("a ValueError should be raised")
def valueerror_raised(context):
    """Verifica que ValueError foi levantada."""
    assert context["error"] is not None, "Expected ValueError but got None"
    assert isinstance(context["error"], ValueError), (
        f"Expected ValueError but got: {type(context['error']).__name__}"
    )


@then(parsers.parse('error message should be "{expected_message}"'))
def error_message_matches(context, expected_message):
    """Verifica mensagem de erro."""
    assert str(context["error"]) == expected_message


# ============================================================================
# RN-API-003: package_list
# ============================================================================


@when("I list all packages")
def list_all_packages(inspector, context):
    """Lista todos os packages usando VCR.py."""
    cassette_name = "package_list.yaml"

    try:
        with api_vcr.use_cassette(cassette_name):  # type: ignore[attr-defined]
            context["response"] = inspector.list_packages()
            context["error"] = None
    except Exception as e:
        context["response"] = None
        context["error"] = e


@then("the response should contain a list")
def response_is_list(context):
    """Verifica que response é uma lista."""
    assert context["response"] is not None, (
        f"Expected list but got None. Error: {context.get('error')}"
    )
    assert isinstance(context["response"], list)


@then(parsers.parse("list should have at least {min_count:d} packages"))
def list_has_minimum_packages(context, min_count):
    """Verifica tamanho mínimo da lista."""
    assert len(context["response"]) >= min_count, (
        f"Expected at least {min_count} packages, got {len(context['response'])}"
    )


# ============================================================================
# RN-API-005: Headers
# ============================================================================


@when("inspector makes any request")
def inspector_makes_request(inspector, context):
    """Captura headers usados pelo inspector."""
    context["headers"] = inspector.headers


@then("headers should include User-Agent")
def headers_include_user_agent(context):
    """Verifica presença de User-Agent."""
    assert "User-Agent" in context["headers"]


@then("headers should include Accept")
def headers_include_accept(context):
    """Verifica presença de Accept."""
    assert "Accept" in context["headers"]


@then("headers should include Accept-Encoding")
def headers_include_accept_encoding(context):
    """Verifica presença de Accept-Encoding."""
    assert "Accept-Encoding" in context["headers"]
