# CHANGELOG

Todas as mudanças notáveis do projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [Unreleased]

### Planejado

- Processamento estado ES (validação multi-estado)
- Análise exploratória completa (AC + ES)
- Dashboard Power BI inicial
- Integração Oracle Database (MVP)

---

## [0.2.2] - 2025-12-27

### Corrigido

- **Testes CI**: Implementado VCR.py para resolver 3 timeouts API
- **BDD**: Cenários @wip pulados automaticamente via pytest config
- **Markers**: Corrigido future_v0.3.0 -> future_v0_3_0

### Adicionado

- **VCR.py**: HTTP mocking para testes API (cassettes gravadas)
- **Tenacity**: Biblioteca para retry logic (preparação futura)
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
- Necessário retry logic com exponential backoff

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
- Integração pysus para download dados DataSUS
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

**Commits principais:**

- `b976ea0`: Renomear projeto para Healthcare Analytics
- `1d032ee`: Implementar ruff + mypy + pre-commit
- `3cc9826`: Remover black e flake8

**Métricas:**

- Cobertura testes: 5% (1/1 teste passando)
- Pipeline: 4.315 registros AC processados com sucesso
- Pre-commit: 3 hooks configurados (ruff, ruff-format, mypy)
