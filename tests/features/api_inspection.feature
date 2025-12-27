Feature: OpenDataSUS API Inspection
  Como analista de dados
  Quero consultar metadados da API OpenDataSUS
  Para descobrir datasets disponíveis

  Background:
    Given an OpenDataSUS API inspector is initialized

  # ====================================================================
  # RN-API-001: package_show (IMPLEMENTADO)
  # ====================================================================
  
  @implemented
  Scenario: Query valid package returns complete metadata
    When I query package "registro-de-ocupacao-hospitalar-covid-19"
    Then the response should contain package metadata
    And metadata should include name, title, organization

  @implemented
  Scenario: Query nonexistent package returns handled error
    When I query package "nonexistent-package-xyz"
    Then the response should be None
    And no exception should be raised

  @implemented
  Scenario: Empty package ID should be rejected
    When I query package "<empty>"
    Then a ValueError should be raised
    And error message should be "Package ID cannot be empty"

  # ====================================================================
  # RN-API-002: resource_search (DESABILITADO - Endpoint 409)
  # ====================================================================
  
  @skip @endpoint_disabled
  Scenario: Resource search endpoint returns 409 CONFLICT
    Given the resource_search endpoint is known to be disabled
    When I attempt to search resources with query "RDAC"
    Then the API should return 409 status code
    And response should indicate "Search index not found"

  # ====================================================================
  # RN-API-003: package_list (IMPLEMENTADO)
  # ====================================================================
  
  @implemented
  Scenario: List packages returns nonempty list
    When I list all packages
    Then the response should contain a list
    And list should have at least 50 packages

  # ====================================================================
  # RN-API-004: Formatação (NÃO IMPLEMENTADO - Future)
  # ====================================================================
  
  @wip @future_v0_3_0
  Scenario: Success output should have formatted box header
    Given a successful API response
    When formatting the output
    Then output should contain box drawing characters
    And output should have structured header

  @wip @future_v0_3_0
  Scenario: Output should not contain colored emojis
    Given any API response
    When formatting the output
    Then output should not contain Unicode emojis (U+1F300-U+1F9FF)
    And only ASCII/Unicode symbols should be used

  # ====================================================================
  # RN-API-005: Headers (IMPLEMENTADO)
  # ====================================================================
  
  @implemented
  Scenario: Required headers should be present
    When inspector makes any request
    Then headers should include User-Agent
    And headers should include Accept
    And headers should include Accept-Encoding
