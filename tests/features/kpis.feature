Feature: Hospital KPIs Calculation
  As a data analyst
  I want to calculate basic hospitalization KPIs
  To support hospital management decisions

  Background:
    Given a DataFrame with SIH/DataSUS hospitalization data

  # KPI 1: Taxa de Ocupação
  @kpi @occupancy
  Scenario: Calculate occupancy rate
    Given a DataFrame with stay_days = [5, 3, 2]
    And a total of 10 available beds
    And a period of 30 days
    When I calculate the occupancy rate
    Then the result should be 3.33%

  # KPI 2: Tempo Médio de Permanência (TMP)
  @kpi @alos
  Scenario: Calculate overall ALOS
    Given a DataFrame with stay_days = [5, 3, 7, 2, 3]
    When I calculate the ALOS
    Then the result should be 4.0 days

  @kpi @alos
  Scenario: Calculate ALOS by specialty
    Given a DataFrame with hospitalizations from multiple specialties
    When I calculate the ALOS grouped by specialty
    Then I should receive a dictionary with ALOS per specialty

  # KPI 3: Volume de Atendimentos
  @kpi @volume
  Scenario: Calculate total volume
    Given a DataFrame with 100 records
    When I calculate the total volume
    Then the result should be 100

  @kpi @volume
  Scenario: Calculate volume by period
    Given a DataFrame with hospitalizations across multiple months
    When I calculate the volume grouped by month
    Then I should receive a dictionary with volume per month

  # KPI 4: Receita Total
  @kpi @revenue
  Scenario: Calculate total revenue
    Given a DataFrame with VAL_TOT = [1000.0, 1500.0, 2000.0]
    When I calculate the total revenue
    Then the result should be 4500.0

  @kpi @revenue
  Scenario: Calculate revenue by specialty
    Given a DataFrame with hospitalizations from multiple specialties
    When I calculate the revenue grouped by specialty
    Then I should receive a dictionary with revenue per specialty

  @kpi @revenue
  Scenario: Calculate average ticket
    Given a DataFrame with VAL_TOT = [1000.0, 1500.0, 2000.0]
    When I calculate the average ticket
    Then the result should be 1500.0

  # KPI 5: Distribuição Demográfica
  @kpi @demographics
  Scenario: Calculate age group distribution
    Given a DataFrame with categorized age_group
    When I calculate the demographic distribution
    Then I should receive counts per age group
