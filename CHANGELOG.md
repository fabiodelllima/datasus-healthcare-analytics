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

## [0.2.0] - 2024-12-11

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

## [0.1.0] - 2024-12-05

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
