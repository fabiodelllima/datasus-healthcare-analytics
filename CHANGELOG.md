# CHANGELOG

Todas as mudanças notáveis do projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [Unreleased]

### Planejado

- Dashboard Power BI ou Streamlit
- Integração Oracle Database (MVP)
- Processamento multi-estado
- Independência do pysus (extração FTP própria)

---

## [0.2.6] - 2025-12-30

### Adicionado

- **RN-API-004 Formatação Terminal**: TerminalFormatter com output formatado

  - Cores ANSI (verde, vermelho, amarelo, azul, cyan)
  - Box drawing (┌ ┐ └ ┘ ─ │ ├ ┤)
  - Status tags ([OK], [ERROR], [WARNING], [INFO])
  - Métodos display\_\*: package_info, packages_list, status
  - Cálculo de largura visual (ignora códigos ANSI no padding)

- **Testes Coverage 97%**: 52 novos testes
  - test_terminal_formatter.py: 25 testes (TerminalFormatter + display methods)
  - test_visualizations.py: 12 testes (ChartGenerator)
  - test_main.py: 3 testes (pipeline ETL)
  - test_coverage_gaps.py: 12 testes (edge cases)

### Técnico

- Coverage: 48% → 97% (superou meta de 90%)
- Total: 128 passed, 1 skipped
- API Inspector: 59% → 97% coverage
- KPICalculator, DataSUSExtractor: 100% coverage

---

## [0.2.5] - 2025-12-30

### Adicionado

- **Visualizações Estáticas**: Módulo ChartGenerator com 6 gráficos
  - Distribuição por faixa etária
  - Receita por especialidade
  - Tempo médio permanência por especialidade
  - Top 10 diagnósticos (CID-10)
  - Volume diário de internações
  - Distribuição por sexo
- **Gráficos PNG**: 300 DPI prontos para apresentação

### Técnico

- src/visualizations/charts.py: ChartGenerator reutilizável
- Type hints completos com cast para matplotlib
- Ruff + mypy passing

---

## [0.2.4] - 2025-12-29

### Adicionado

- **Análise Exploratória (EDA)**: Jupyter Notebook completo
  - Setup e carregamento de dados
  - Visão geral do dataset (118 colunas, 4.315 registros)
  - Estatísticas descritivas
  - Análise de qualidade de dados
  - Distribuições (idade, valores, permanência)
  - Insights e conclusões

### Técnico

- Exclui notebooks do ruff pre-commit (types_or: [python, pyi])
- Notebook executado com outputs reais de AC Jan/2024

---

## [0.2.3] - 2025-12-28

### Adicionado

- **KPIs Básicos**: Módulo analytics com 5 indicadores hospitalares
  - Taxa de ocupação (occupancy_rate)
  - Tempo médio de permanência (average_length_of_stay)
  - Volume de atendimentos (volume)
  - Receita total e ticket médio (revenue, average_ticket)
  - Distribuição demográfica (demographics)
- **Testes KPIs**: 23 testes unitários com 95% coverage no módulo
- **BDD KPIs**: Feature com 10 cenários Gherkin
- **Type Overloads**: Retornos precisos para métodos com group_by

### Técnico

- Resultado: 76 passed, 1 skipped, coverage 68%
- pyproject.toml: Configuração pyright para pandas .dt accessor
- src/analytics/kpis.py: KPICalculator com typing.overload

---

## [0.2.2] - 2025-12-27

### Corrigido

- **Testes CI**: Implementado VCR.py para resolver 3 timeouts API
- **BDD**: Cenários @wip pulados automaticamente via pytest config
- **Markers**: Corrigido future_v0.3.0 -> future_v0_3_0

### Adicionado

- **VCR.py**: HTTP mocking para testes API (cassettes gravadas)
- **Cassettes**: package_list, package_show_covid_hospital_occupancy, package_show_nonexistent

### Técnico

- Resultado: 53 passed, 1 skipped, coverage 61%
- pyproject.toml: Configuração pytest com markers customizados
- conftest.py: Configuração VCR.py global
- .gitignore: Adicionado coverage.xml

---

## [0.2.1] - 2025-12-27

### Corrigido

- **CI/CD**: GitHub Actions configurado e testado
- **Métricas**: Coverage real 56% (51/57 testes, 5 falhas, 1 skip)
- **README**: Atualizado com resultados reais do CI/CD

### Descoberto

- Testes API: 3 timeouts opendatasus.saude.gov.br (timeout 30s insuficiente)
- Testes BDD: 2 step definitions faltando em api_inspection.feature
- API Inspector coverage: 49% (timeouts reduzem métrica)
- Necessário VCR.py para fixtures de testes API

### Técnico

- GitHub Actions rodando pytest + coverage automaticamente
- Coverage XML gerado e enviado para Codecov
- Badges Codecov funcionais no README
- Ruff + Mypy passing em CI

---

## [0.2.0] - 2025-12-22

### Adicionado

- Conjunto abrangente de testes (18 testes, 54% coverage)
- Especificações BDD em formato Gherkin (hospitalization_validation.feature)
- Documentação de regras de negócio (BUSINESS_RULES.md)
- Validações de qualidade de dados (datas, idade, valores monetários)
- Enriquecimento de dados (stay_days, daily_cost, age_group, flag óbito)
- Documentação completa de todas regras ETL (12 regras: CONV, LIMP, VAL, ENR)

### Modificado

- Métodos Transformer agora públicos (clean_data, validate_data, enrich_data)
- Melhoria cobertura testes: 5% → 54%
- Coverage transformer: 0% → 94%
- DATA_GUIDE.md: removidas regras negócio duplicadas (movidas para BUSINESS_RULES.md)

### Técnico

- Adoção Google Python Style Guide para testabilidade
- Conformidade PEP 8
- Ruff + mypy configurados
- Pre-commit hooks habilitados
- Hierarquia DOCS > BDD > TDD > CODE implementada

### Corrigido

- Expectativas pd.cut() para intervalos (comportamento right=True)
- Comparações booleanas (== ao invés de is)
- Correções type hints
- Consistência nomenclatura testes (hospitalization_validation.feature)

---

## [0.1.0] - 2025-12-05

### Adicionado

- Pipeline ETL completo (Extract, Transform, Load)
- Integração com FTP DataSUS via biblioteca pysus (Fiocruz/AlertaDengue)
- Transformações: limpeza, validação, enriquecimento
- Salvamento dual-format (CSV + Parquet)
- Sistema logging estruturado
- Ferramentas code quality: ruff, mypy, pre-commit
- Framework testes: pytest com coverage
- Documentação completa (README, ARCHITECTURE, DATA_GUIDE, ROADMAP)
- Configuração type hints (mypy.ini)
- Configuração ruff (pyproject.toml)
- Pre-commit hooks automáticos

### Modificado

- Renomeação projeto: "DataSUS Analytics" → "DataSUS Healthcare Analytics"
- Substituição black + flake8 → ruff (10-100x mais rápido)
- Dependências: versões fixadas (==) → flexíveis (>=)
- Config paths: pathlib → os.path (compatibilidade)

### Corrigido

- Test extractor: removido assert self.sih obsoleto
- Type hints: adicionado cast() para operações DataFrame
- Imports: removidos imports não utilizados
- Formatação: aplicado ruff em toda codebase

### Técnico

- Cobertura testes: 5% (1/1 teste passando)
- Pipeline: 4.315 registros AC processados com sucesso
- Pre-commit: 3 hooks configurados (ruff, ruff-format, mypy)
