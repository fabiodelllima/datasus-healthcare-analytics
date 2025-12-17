# language: en
Feature: OpenDataSUS API Inspection
  As a developer of DataSUS Healthcare Analytics project
  I want to query OpenDataSUS API via terminal
  So that I can explore dataset metadata without using Postman/Insomnia

  Background:
    Given the OpenDataSUS API is available at "https://opendatasus.saude.gov.br/api/3/action/"
    And the default timeout is 30 seconds
    And HTTP headers are configured correctly

  # ===========================================================================
  # RN-API-001: GET Request for Package Information
  # ===========================================================================

  Scenario: Query valid package returns complete metadata
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    Then the status code should be 200
    And the field "success" should be true
    And the field "result" should contain "id"
    And the field "result" should contain "name"
    And the field "result" should contain "title"
    And the field "result" should contain "metadata_modified"
    And the field "result" should contain "resources"
    And the response time should be less than 5 seconds
    And the log should contain "[INFO] Request to package_show: package_id=sihsus"

  Scenario: Query non-existent package returns handled error
    Given the package_id is "invalid123"
    When I make a GET request to "/api/3/action/package_show"
    Then the status code should be 200
    And the field "success" should be false
    And the field "error" should be present
    And the return value should be None
    And the log should contain "[INFO] Package 'invalid123' not found in OpenDataSUS"

  Scenario: Empty package ID should be rejected before request
    Given the package_id is ""
    When I attempt a GET request to "/api/3/action/package_show"
    Then a ValidationError should be raised
    And the error message should contain "Package ID cannot be empty"
    And no HTTP request should be made

  Scenario: Package ID too short should be rejected
    Given the package_id is "a"
    When I attempt a GET request to "/api/3/action/package_show"
    Then a ValidationError should be raised
    And the error message should contain "Package ID must be at least 2 characters"

  Scenario: Timeout on request should be handled
    Given the package_id is "sihsus"
    And the API takes more than 30 seconds to respond
    When I make a GET request to "/api/3/action/package_show"
    Then a Timeout exception should be raised
    And the log should contain "[WARNING] Request timeout after 30s"

  Scenario: Network error should be handled
    Given the package_id is "sihsus"
    And there is no internet connection
    When I attempt a GET request to "/api/3/action/package_show"
    Then a RequestException should be raised
    And the log should contain "[ERROR] Network error connecting to OpenDataSUS API"

  # ===========================================================================
  # RN-API-002: GET Request for Resource Search
  # ===========================================================================

  Scenario: Resource search with valid query returns list
    Given the query is "RDAC"
    And the limit is 10
    When I make a GET request to "/api/3/action/resource_search"
    Then the status code should be 200
    And the field "success" should be true
    And the field "result.count" should be a number
    And the field "result.results" should be a list
    And the log should contain "[INFO] Found"

  Scenario: Search with no results returns empty list
    Given the query is "xpto999"
    And the limit is 10
    When I make a GET request to "/api/3/action/resource_search"
    Then the status code should be 200
    And the field "success" should be true
    And the field "result.count" should be 0
    And the field "result.results" should be an empty list
    And the log should contain "[INFO] No resources found for query 'xpto999'"

  Scenario: Query too short should be rejected
    Given the query is "A"
    When I attempt a GET request to "/api/3/action/resource_search"
    Then a ValidationError should be raised
    And the error message should contain "Query must be at least 2 characters"

  Scenario: Limit out of range should be auto-adjusted
    Given the query is "RDAC"
    And the limit is 500
    When I make a GET request to "/api/3/action/resource_search"
    Then the limit should be adjusted to 100
    And the log should contain "[WARNING] Limit adjusted to valid range [1-100]"
    And the request should continue with limit=100

  Scenario: Negative limit should be adjusted to 1
    Given the query is "RDAC"
    And the limit is -5
    When I make a GET request to "/api/3/action/resource_search"
    Then the limit should be adjusted to 1
    And the log should contain "[WARNING] Limit adjusted to valid range [1-100]"

  Scenario: Negative offset should be rejected
    Given the query is "RDAC"
    And the offset is -10
    When I attempt a GET request to "/api/3/action/resource_search"
    Then a ValidationError should be raised
    And the error message should contain "Offset must be >= 0"

  Scenario: Pagination beyond results returns empty list
    Given the query is "RDAC"
    And the offset is 10000
    When I make a GET request to "/api/3/action/resource_search"
    Then the status code should be 200
    And the field "result.results" should be an empty list

  # ===========================================================================
  # RN-API-003: GET Request for Package List
  # ===========================================================================

  Scenario: List packages returns non-empty list
    When I make a GET request to "/api/3/action/package_list"
    Then the status code should be 200
    And the field "success" should be true
    And the field "result" should be a list
    And the field "result" should have at least 1 element
    And the log should contain "[INFO] Retrieved"

  Scenario: Empty package list indicates anomaly
    When I make a GET request to "/api/3/action/package_list"
    And the API returns an empty list
    Then the status code should be 200
    And the log should contain "[WARNING] API returned empty package list"

  Scenario: Timeout when listing packages
    When I make a GET request to "/api/3/action/package_list"
    And the API takes more than 30 seconds to respond
    Then a Timeout exception should be raised
    And the log should contain "[WARNING] Request timeout after 30s"

  # ===========================================================================
  # RN-API-004: Terminal Output Formatting
  # ===========================================================================

  Scenario: Success output should have formatted box header
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    And the request is successful
    Then the output should contain box header with "┌─"
    And the output should contain "OpenDataSUS API Inspector"
    And the output should contain "Endpoint: /api/3/action/package_show"
    And the output should contain "Package: sihsus"
    And the output should contain "Status: 200 OK"
    And the output should contain "Time:" followed by time in seconds

  Scenario: Success output should have formatted JSON
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    And the request is successful
    Then the JSON should be indented with 2 spaces
    And the keys should be in alphabetical order
    And UTF-8 characters should be preserved
    And the encoding should be UTF-8

  Scenario: Success output should have box footer with statistics
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    And the request is successful
    Then the output should contain box footer with "Response Stats"
    And the output should contain "Size:" followed by size in KB/MB
    And the output should contain "Resources:" followed by number
    And the output should contain "Last Updated:" followed by date

  Scenario: Error output should have error symbol
    Given the package_id is "invalid123"
    When I make a GET request to "/api/3/action/package_show"
    And the request returns an error
    Then the output should contain "✗ ERROR:"
    And the output should contain the error message
    And the error JSON should be formatted

  Scenario: Output should not contain colored emojis
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    Then the output should not contain "✅"
    And the output should not contain "❌"
    And the output should not contain "🚀"
    And the output should not contain "📦"
    And the output should use only allowed ASCII/Unicode symbols

  Scenario: Box drawing symbols should be used correctly
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    Then the output should use "┌" for top-left
    And the output should use "┐" for top-right
    And the output should use "└" for bottom-left
    And the output should use "┘" for bottom-right
    And the output should use "─" for horizontal
    And the output should use "│" for vertical

  # ===========================================================================
  # RN-API-005: HTTP Headers Configuration
  # ===========================================================================

  Scenario: Required headers should be present
    Given I will make a request to any endpoint
    When the headers are prepared
    Then the header "User-Agent" should be present
    And the header "Accept" should be present
    And the header "Accept-Encoding" should be present

  Scenario: User-Agent should have correct format
    Given I will make a request to any endpoint
    When the headers are prepared
    Then the User-Agent should contain "DataSUS-Healthcare-Analytics"
    And the User-Agent should contain the project version
    And the User-Agent should contain "Educational Project"
    And the User-Agent should contain "Python/"

  Scenario: Accept header should be application/json
    Given I will make a request to any endpoint
    When the headers are prepared
    Then the header "Accept" should be exactly "application/json"

  Scenario: Accept-Encoding header should include gzip
    Given I will make a request to any endpoint
    When the headers are prepared
    Then the header "Accept-Encoding" should contain "gzip"
    And the header "Accept-Encoding" should contain "deflate"

  # ===========================================================================
  # EDGE-API-001: API Returns HTML Instead of JSON
  # ===========================================================================

  Scenario: API returning HTML should be detected
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    And the API returns Content-Type "text/html"
    Then a ValueError should be raised
    And the message should contain "API returned HTML"
    And the log should contain "[WARNING] API returned HTML instead of JSON"
    And the log should contain HTML preview

  Scenario: HTML should not be parsed as JSON
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    And the API returns HTML "<html><body>Manutenção</body></html>"
    Then no attempt should be made to parse JSON
    And a ValueError should be raised before json.loads()

  # ===========================================================================
  # EDGE-API-002: Rate Limiting (429 Too Many Requests)
  # ===========================================================================

  Scenario: Rate limiting should be detected
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    And the API returns status code 429
    Then the log should contain "[WARNING] Rate limited by API"
    And the message should inform wait time
    And no automatic retry should be done

  Scenario: Retry-After header should be extracted
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    And the API returns status code 429
    And the header "Retry-After" is "60"
    Then the log should contain "Retry after: 60s"
    And the output should suggest waiting 60 seconds

  Scenario: Rate limiting without Retry-After header
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    And the API returns status code 429
    And there is no "Retry-After" header
    Then the log should contain "Retry after: unknown"
    And the output should suggest waiting before trying again

  # ===========================================================================
  # EDGE-API-003: Large Response (> 10 MB)
  # ===========================================================================

  Scenario: Large response should be detected before download
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    And the header "Content-Length" is "15728640"
    Then the log should contain "[WARNING] Large response detected: 15.0 MB"
    And the output should be truncated to 1000 characters
    And it should offer to save to file

  Scenario: Response smaller than 10 MB should not be truncated
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    And the header "Content-Length" is "2048"
    Then the complete output should be displayed
    And no size warning should be logged

  # ===========================================================================
  # EDGE-API-004: Timeout on Slow Network
  # ===========================================================================

  Scenario: Timeout should display friendly message
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    And the request exceeds 30 seconds
    Then a Timeout exception should be raised
    And the log should contain "[WARNING] Request timeout after 30s"
    And the output should contain "Request timeout after 30 seconds"
    And the output should list possible causes
    And the output should suggest trying again

  Scenario: Timeout should not increase automatically
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    And the first attempt results in timeout
    Then the timeout for next attempt should remain 30s
    And no automatic increment should occur

  # ===========================================================================
  # EDGE-API-005: Connection Error (No Internet)
  # ===========================================================================

  Scenario: Connection error should be detected
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    And there is no internet connection
    Then a ConnectionError should be raised
    And the log should contain "[ERROR] Connection error"
    And the output should contain "Failed to connect to API"

  Scenario: Connection error message should be informative
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    And there is a connection error
    Then the output should list possible causes
    And the output should mention "No internet connection"
    And the output should mention "Firewall blocking request"
    And the output should mention "DNS resolution failed"
    And the output should suggest checking connection

  # ===========================================================================
  # Quality Metrics
  # ===========================================================================

  Scenario: All requests should be logged
    Given the package_id is "sihsus"
    When I make a GET request to "/api/3/action/package_show"
    Then the log should contain the complete request URL
    And the log should contain the parameters used
    And the log should contain the response status code
    And the log should contain the response time

  Scenario: Performance should be within expected range
    Given the package_id is "sihsus"
    And the network is stable
    When I make a GET request to "/api/3/action/package_show"
    Then the response time should be less than 5 seconds
    And the log should record the exact time

  Scenario Outline: Parameter validation before making request
    Given the <parameter> is <value>
    When I attempt a GET request to <endpoint>
    Then <action> should occur

    Examples:
      | parameter  | value        | endpoint              | action                  |
      | package_id | ""           | /package_show         | ValidationError raised  |
      | package_id | "a"          | /package_show         | ValidationError raised  |
      | query      | "A"          | /resource_search      | ValidationError raised  |
      | limit      | -5           | /resource_search      | Auto-adjust to 1        |
      | limit      | 500          | /resource_search      | Auto-adjust to 100      |
      | offset     | -10          | /resource_search      | ValidationError raised  |
