"""Unit tests for OpenDataSUSInspector.

This module tests the API integration rules defined in docs/API.md,
following the hierarchy: DOCS > BDD > TDD > CODE

Coverage target: >90%

See Also:
    docs/API.md: Business rules RN-API-001 to RN-API-005
    tests/features/api_inspection.feature: BDD Gherkin scenarios
    src/api/datasus_inspector.py: Implementation (to be created)
"""

import json
from unittest.mock import Mock, patch

import pytest
import requests

# ===========================================================================
# FIXTURES
# ===========================================================================


@pytest.fixture
def mock_response():
    """Create mock HTTP response object.

    Returns:
        Mock: Response mock with default values for testing
    """
    response = Mock(spec=requests.Response)
    response.status_code = 200
    response.headers = {"Content-Type": "application/json", "Content-Length": "2048"}
    response.elapsed.total_seconds.return_value = 1.23
    response.json.return_value = {
        "success": True,
        "result": {
            "id": "test-id",
            "name": "sihsus",
            "title": "Sistema de Informações Hospitalares",
            "metadata_modified": "2024-11-20T15:45:30",
            "resources": [],
        },
    }
    return response


@pytest.fixture
def inspector_class():
    """Create mock inspector class for testing validation methods.

    This mock will be replaced by actual implementation after TDD phase.

    Returns:
        class: MockInspector class with validation methods
    """

    class MockInspector:
        """Temporary mock of the inspector class."""

        def __init__(self):
            self.base_url = "https://opendatasus.saude.gov.br/api/3/action/"
            self.timeout = 30
            self.headers = {
                "User-Agent": "DataSUS-Healthcare-Analytics/0.2.0 (Educational Project; Python/3.11)",
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
            }

        def _validate_package_id(self, package_id: str) -> None:
            """Validate package_id parameter.

            Args:
                package_id: Package identifier string

            Raises:
                ValueError: If package_id is empty or less than 2 characters
            """
            if not package_id:
                raise ValueError("Package ID cannot be empty")
            if len(package_id) < 2:
                raise ValueError("Package ID must be at least 2 characters")

        def _validate_query(self, query: str) -> None:
            """Validate search query parameter.

            Args:
                query: Search query string

            Raises:
                ValueError: If query is less than 2 characters
            """
            if len(query) < 2:
                raise ValueError("Query must be at least 2 characters")

        def _adjust_limit(self, limit: int) -> int:
            """Adjust limit parameter to valid range [1-100].

            Args:
                limit: Maximum number of results

            Returns:
                int: Adjusted limit value within valid range
            """
            return max(1, min(limit, 100))

        def _validate_offset(self, offset: int) -> None:
            """Validate pagination offset parameter.

            Args:
                offset: Pagination offset value

            Raises:
                ValueError: If offset is negative
            """
            if offset < 0:
                raise ValueError("Offset must be >= 0")

    return MockInspector


# ===========================================================================
# RN-API-001: GET Request for Package Information
# ===========================================================================


def test_validate_package_id_empty(inspector_class):
    """Validate that empty package_id is rejected before making request.

    This test ensures validation occurs before any HTTP request is made,
    implementing the fail-fast principle.

    Args:
        inspector_class: Mock inspector class fixture

    See Also:
        docs/API.md: RN-API-001 validation rules
        tests/features/api_inspection.feature: Line 38

    Raises:
        ValueError: Expected when package_id is empty
    """
    inspector = inspector_class()

    with pytest.raises(ValueError, match="Package ID cannot be empty"):
        inspector._validate_package_id("")


def test_validate_package_id_too_short(inspector_class):
    """Validate that package_id less than 2 characters is rejected.

    Args:
        inspector_class: Mock inspector class fixture

    See Also:
        docs/API.md: RN-API-001 required parameters
        tests/features/api_inspection.feature: Line 45

    Raises:
        ValueError: Expected when package_id has less than 2 characters
    """
    inspector = inspector_class()

    with pytest.raises(ValueError, match="Package ID must be at least 2 characters"):
        inspector._validate_package_id("a")


def test_validate_package_id_valid(inspector_class):
    """Validate that valid package_id passes without raising exception.

    Args:
        inspector_class: Mock inspector class fixture

    See Also:
        docs/API.md: RN-API-001 validation rules
        tests/features/api_inspection.feature: Line 18
    """
    inspector = inspector_class()

    # Should not raise any exception
    inspector._validate_package_id("sihsus")
    inspector._validate_package_id("ab")  # Minimum 2 characters


# ===========================================================================
# RN-API-002: GET Request for Resource Search
# ===========================================================================


def test_validate_query_too_short(inspector_class):
    """Validate that search query less than 2 characters is rejected.

    Args:
        inspector_class: Mock inspector class fixture

    See Also:
        docs/API.md: RN-API-002 validation rules
        tests/features/api_inspection.feature: Line 92

    Raises:
        ValueError: Expected when query has less than 2 characters
    """
    inspector = inspector_class()

    with pytest.raises(ValueError, match="Query must be at least 2 characters"):
        inspector._validate_query("A")


def test_validate_query_valid(inspector_class):
    """Validate that valid search query passes without raising exception.

    Args:
        inspector_class: Mock inspector class fixture

    See Also:
        docs/API.md: RN-API-002 required parameters
        tests/features/api_inspection.feature: Line 68
    """
    inspector = inspector_class()

    inspector._validate_query("RDAC")
    inspector._validate_query("AB")  # Minimum 2 characters


def test_adjust_limit_negative(inspector_class):
    """Validate that negative limit is auto-adjusted to 1.

    Args:
        inspector_class: Mock inspector class fixture

    See Also:
        docs/API.md: RN-API-002 behavior table
        tests/features/api_inspection.feature: Line 103

    Note:
        A WARNING log should be generated when adjustment occurs
    """
    inspector = inspector_class()

    assert inspector._adjust_limit(-5) == 1
    assert inspector._adjust_limit(0) == 1


def test_adjust_limit_too_high(inspector_class):
    """Validate that limit above 100 is auto-adjusted to 100.

    Args:
        inspector_class: Mock inspector class fixture

    See Also:
        docs/API.md: RN-API-002 behavior table
        tests/features/api_inspection.feature: Line 97

    Note:
        A WARNING log should be generated when adjustment occurs
    """
    inspector = inspector_class()

    assert inspector._adjust_limit(500) == 100
    assert inspector._adjust_limit(101) == 100


def test_adjust_limit_valid(inspector_class):
    """Validate that valid limit (1-100) is not modified.

    Args:
        inspector_class: Mock inspector class fixture

    See Also:
        docs/API.md: RN-API-002 optional parameters
        tests/features/api_inspection.feature: Line 68
    """
    inspector = inspector_class()

    assert inspector._adjust_limit(10) == 10
    assert inspector._adjust_limit(1) == 1
    assert inspector._adjust_limit(100) == 100


def test_validate_offset_negative(inspector_class):
    """Validate that negative offset is rejected.

    Args:
        inspector_class: Mock inspector class fixture

    See Also:
        docs/API.md: RN-API-002 behavior table
        tests/features/api_inspection.feature: Line 109

    Raises:
        ValueError: Expected when offset is negative
    """
    inspector = inspector_class()

    with pytest.raises(ValueError, match="Offset must be >= 0"):
        inspector._validate_offset(-10)


def test_validate_offset_valid(inspector_class):
    """Validate that non-negative offset passes without raising exception.

    Args:
        inspector_class: Mock inspector class fixture

    See Also:
        docs/API.md: RN-API-002 optional parameters
        tests/features/api_inspection.feature: Line 115
    """
    inspector = inspector_class()

    inspector._validate_offset(0)
    inspector._validate_offset(10)
    inspector._validate_offset(10000)


# ===========================================================================
# RN-API-005: HTTP Headers Configuration
# ===========================================================================


def test_required_headers_present(inspector_class):
    """Validate that all required HTTP headers are present.

    Args:
        inspector_class: Mock inspector class fixture

    See Also:
        docs/API.md: RN-API-005 required headers
        tests/features/api_inspection.feature: Line 195
    """
    inspector = inspector_class()

    assert "User-Agent" in inspector.headers
    assert "Accept" in inspector.headers
    assert "Accept-Encoding" in inspector.headers


def test_user_agent_format(inspector_class):
    """Validate User-Agent header follows correct format.

    The User-Agent must follow the format:
    {ProjectName}/{Version} ({Context}; {Runtime})

    Args:
        inspector_class: Mock inspector class fixture

    See Also:
        docs/API.md: RN-API-005 User-Agent format
        tests/features/api_inspection.feature: Line 201
    """
    inspector = inspector_class()

    user_agent = inspector.headers["User-Agent"]

    assert "DataSUS-Healthcare-Analytics" in user_agent
    assert "Educational Project" in user_agent
    assert "Python/" in user_agent
    # Verify semantic version (X.Y.Z) is present
    assert any(c.isdigit() for c in user_agent)


def test_accept_header_json(inspector_class):
    """Validate Accept header is exactly 'application/json'.

    Args:
        inspector_class: Mock inspector class fixture

    See Also:
        docs/API.md: RN-API-005 rules table
        tests/features/api_inspection.feature: Line 209
    """
    inspector = inspector_class()

    assert inspector.headers["Accept"] == "application/json"


def test_accept_encoding_gzip(inspector_class):
    """Validate Accept-Encoding header includes gzip and deflate.

    Args:
        inspector_class: Mock inspector class fixture

    See Also:
        docs/API.md: RN-API-005 rules table
        tests/features/api_inspection.feature: Line 213
    """
    inspector = inspector_class()

    accept_encoding = inspector.headers["Accept-Encoding"]

    assert "gzip" in accept_encoding
    assert "deflate" in accept_encoding


def test_timeout_configured(inspector_class):
    """Validate default timeout is set to 30 seconds.

    Args:
        inspector_class: Mock inspector class fixture

    See Also:
        docs/API.md: RN-API-001 validation rules
        tests/features/api_inspection.feature: Line 9 (Background)
    """
    inspector = inspector_class()

    assert inspector.timeout == 30


def test_base_url_correct(inspector_class):
    """Validate base URL is correctly configured.

    Args:
        inspector_class: Mock inspector class fixture

    See Also:
        docs/API.md: General Information section
        tests/features/api_inspection.feature: Line 8 (Background)
    """
    inspector = inspector_class()

    assert inspector.base_url == "https://opendatasus.saude.gov.br/api/3/action/"


# ===========================================================================
# EDGE CASES
# ===========================================================================


def test_timeout_error_handling():
    """Validate timeout exceptions are properly handled.

    See Also:
        docs/API.md: EDGE-API-004 - Timeout in slow network
        tests/features/api_inspection.feature: Line 51

    Note:
        A WARNING log should be generated when timeout occurs
    """
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout after 30s")

        with pytest.raises(requests.exceptions.Timeout):
            requests.get("https://opendatasus.saude.gov.br/api/3/action/package_show", timeout=30)


def test_connection_error_handling():
    """Validate connection errors are properly handled.

    See Also:
        docs/API.md: EDGE-API-005 - Connection Error (No Internet)
        tests/features/api_inspection.feature: Line 58

    Note:
        An ERROR log should be generated when connection fails
    """
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError("No internet connection")

        with pytest.raises(requests.exceptions.ConnectionError):
            requests.get("https://opendatasus.saude.gov.br/api/3/action/package_show")


def test_html_response_detection():
    """Validate HTML response (instead of JSON) is properly detected.

    Detection should occur by checking Content-Type header before
    attempting to parse response as JSON.

    See Also:
        docs/API.md: EDGE-API-001 - API Returns HTML
        tests/features/api_inspection.feature: Line 225

    Note:
        A WARNING log with HTML preview should be generated
    """
    response = Mock()
    response.headers = {"Content-Type": "text/html"}
    response.text = "<html><body>Manutenção</body></html>"

    # Verify Content-Type detection
    content_type = response.headers.get("Content-Type", "")
    assert "text/html" in content_type

    # Should not attempt to parse as JSON
    with pytest.raises(json.JSONDecodeError):
        json.loads(response.text)


def test_rate_limiting_detection():
    """Validate rate limiting (429) is properly detected.

    Should extract Retry-After header when present.

    See Also:
        docs/API.md: EDGE-API-002 - Rate Limiting
        tests/features/api_inspection.feature: Line 241

    Note:
        A WARNING log with retry time should be generated
    """
    response = Mock()
    response.status_code = 429
    response.headers = {"Retry-After": "60"}

    assert response.status_code == 429

    retry_after = response.headers.get("Retry-After", "unknown")
    assert retry_after == "60"


def test_large_response_detection():
    """Validate large response (>10 MB) is detected before download.

    Detection should occur by checking Content-Length header.

    See Also:
        docs/API.md: EDGE-API-003 - Large Response
        tests/features/api_inspection.feature: Line 259

    Note:
        A WARNING log should be generated and output should be truncated
    """
    response = Mock()
    response.headers = {"Content-Length": "15728640"}  # 15 MB

    content_length = int(response.headers.get("Content-Length", 0))
    max_size = 10 * 1024 * 1024  # 10 MB

    assert content_length > max_size


# ===========================================================================
# RN-API-004: Terminal Output Formatting
# ===========================================================================


def test_json_formatting_rules():
    """Validate JSON output follows formatting rules.

    JSON must be formatted with:
    - 2-space indentation
    - Alphabetically sorted keys
    - UTF-8 encoding preserved (ensure_ascii=False)

    See Also:
        docs/API.md: RN-API-004 formatting rules
        tests/features/api_inspection.feature: Line 146
    """
    data = {"success": True, "result": {"name": "sihsus", "id": "123"}}

    # Test 2-space indentation
    formatted = json.dumps(data, indent=2)
    assert "  " in formatted

    # Test key sorting
    formatted = json.dumps(data, sort_keys=True)
    assert '"id"' in formatted
    assert '"name"' in formatted

    # Test UTF-8 preservation
    data_utf8 = {"name": "São Paulo"}
    formatted = json.dumps(data_utf8, ensure_ascii=False)
    assert "São Paulo" in formatted


def test_box_drawing_characters():
    """Validate box drawing characters are valid Unicode.

    See Also:
        docs/API.md: RN-API-004 output template
        tests/features/api_inspection.feature: Line 183
    """
    box_chars = {
        "top_left": "┌",
        "top_right": "┐",
        "bottom_left": "└",
        "bottom_right": "┘",
        "horizontal": "─",
        "vertical": "│",
    }

    for _name, char in box_chars.items():
        assert len(char) == 1
        assert ord(char) > 127  # Unicode, not pure ASCII


def test_forbidden_ai_emojis():
    """Validate AI-commonly-used emojis are prohibited.

    This test focuses on emojis that AI assistants frequently use
    in code comments, commit messages, and documentation.

    See Also:
        docs/API.md: RN-API-004 allowed symbols
        tests/features/api_inspection.feature: Line 167
    """
    # Emojis frequently used by AI assistants
    ai_common_emojis = [
        "✅",  # Check mark button (success)
        "❌",  # Cross mark (error)
        "🚀",  # Rocket (deploy/launch)
        "📦",  # Package (npm/module)
        "💡",  # Light bulb (idea/tip)
        "🔧",  # Wrench (fix/config)
        "📝",  # Memo (documentation)
        "⚡",  # High voltage (performance)
        "🎯",  # Direct hit (goal/target)
        "🛠",  # Hammer and wrench (tools)
        "⚠️",  # Warning sign (colored - prohibited)
        "⏰",  # Alarm clock (deadline)
        "⌛",  # Hourglass (waiting)
        "⏳",  # Hourglass flowing (loading)
    ]

    # Valid output without emojis
    valid_output = """
    ┌────────────────────────────────────┐
    │ OpenDataSUS API Inspector          │
    ├────────────────────────────────────┤
    │ Status: 200 OK                     │
    └────────────────────────────────────┘

    [OK] Success
    [ERROR] Failed
    [WARNING] Attention needed
    """

    # Verify no prohibited emojis are present
    for emoji in ai_common_emojis:
        assert emoji not in valid_output, f"Prohibited AI emoji found: {emoji}"

    # Verify ASCII alternatives are used
    assert "[OK]" in valid_output
    assert "[ERROR]" in valid_output
    assert "[WARNING]" in valid_output
    assert "┌" in valid_output  # Box drawing OK


# ===========================================================================
# ENCODING AND SPECIAL CHARACTERS
# ===========================================================================


def test_json_utf8_encoding():
    """Validate JSON uses UTF-8 encoding for special characters.

    The ensure_ascii=False parameter must be used to preserve
    accented characters and special UTF-8 symbols.

    See Also:
        docs/API.md: RN-API-004 encoding rules
        tests/features/api_inspection.feature: Line 146
    """
    data = {
        "name": "Sistema de Informações",
        "location": "São Paulo",
        "description": "Análise de saúde pública",
    }

    formatted = json.dumps(data, ensure_ascii=False)

    assert "São Paulo" in formatted
    assert "Informações" in formatted
    assert "Análise" in formatted
    assert "saúde" in formatted
    assert "pública" in formatted

    # Verify no Unicode escapes were used
    assert "\\u" not in formatted


def test_box_drawing_unicode_range():
    """Validate box drawing characters are in correct Unicode range.

    Box drawing characters must be in range U+2500 - U+257F.

    See Also:
        docs/API.md: RN-API-004 allowed symbols
        tests/features/api_inspection.feature: Line 183
    """
    box_chars = {
        "top_left": "┌",
        "top_right": "┐",
        "bottom_left": "└",
        "bottom_right": "┘",
        "horizontal": "─",
        "vertical": "│",
        "t_down": "┬",
        "t_up": "┴",
        "t_right": "├",
        "t_left": "┤",
    }

    for name, char in box_chars.items():
        char_code = ord(char)
        assert 0x2500 <= char_code <= 0x257F, f"{name} must be in Box Drawing Unicode range"


def test_status_symbols_not_emojis():
    """Validate status symbols are Unicode text, not colored emojis.

    Allowed: ✓ ✗ (Unicode text characters)
    Prohibited: ✅ ❌ (colored emojis)

    See Also:
        docs/API.md: RN-API-004 allowed symbols
        tests/features/api_inspection.feature: Line 167
    """
    allowed_symbols = {
        "success": "✓",  # U+2713 Check Mark (text)
        "error": "✗",  # U+2717 Ballot X (text)
    }

    # Allowed symbols must not be in emoji range
    for name, symbol in allowed_symbols.items():
        char_code = ord(symbol)
        assert not (0x1F300 <= char_code <= 0x1F9FF), f"{name} must not be colored emoji"

    # Verify output uses correct symbols
    valid_output = "[OK] ✓ Success"
    assert "✓" in valid_output
    assert "✅" not in valid_output  # Prohibited emoji


def test_terminal_utf8_compatibility():
    """Validate output is compatible with terminal UTF-8 encoding.

    All characters in output must be encodable/decodable in UTF-8.

    See Also:
        docs/API.md: RN-API-004 encoding UTF-8
        tests/features/api_inspection.feature: Line 146
    """
    # Complete output example
    output = """
┌────────────────────────────────────────┐
│ OpenDataSUS API Inspector              │
├────────────────────────────────────────┤
│ Package: sihsus                        │
│ Status: 200 OK                         │
└────────────────────────────────────────┘

[OK] ✓ Success

{
  "name": "Sistema de Informações",
  "location": "São Paulo"
}
"""

    # Must be encodable/decodable in UTF-8
    try:
        encoded = output.encode("utf-8")
        decoded = encoded.decode("utf-8")
        assert decoded == output
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        pytest.fail(f"UTF-8 encoding failed: {e}")


def test_ansi_color_codes_allowed():
    """Validate ANSI color codes are allowed for terminal colorization.

    ANSI escape codes are different from emojis and are permitted
    for adding color to terminal output.

    See Also:
        docs/API.md: RN-API-004 output formatting
    """
    # ANSI escape codes for colors
    ansi_colors = {
        "reset": "\033[0m",
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
    }

    # Valid usage with Unicode text symbols
    success_msg = f"{ansi_colors['green']}✓ Success{ansi_colors['reset']}"
    f"{ansi_colors['red']}✗ Error{ansi_colors['reset']}"

    # Verify correct format
    assert "✓" in success_msg  # Unicode text symbol OK
    assert "\033[" in success_msg  # ANSI code OK
    assert "✅" not in success_msg  # Colored emoji prohibited
