# CHANGELOG

Todas as mudanças notáveis do projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.1.0] - 2024-12-05

### Added

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

### Changed

- Renomeação projeto: "DataSUS Analytics" → "DataSUS Healthcare Analytics"
- Substituição black + flake8 → ruff (10-100x mais rápido)
- Dependências: versões fixadas (==) → flexíveis (>=)
- Config paths: pathlib → os.path (compatibilidade)

### Fixed

- Test extractor: removido assert self.sih obsoleto
- Type hints: adicionado cast() para operações DataFrame
- Imports: removidos imports não utilizados
- Formatação: aplicado ruff em toda codebase

### Technical Details

**Commits principais:**

- `b976ea0`: Renomear projeto para Healthcare Analytics
- `1d032ee`: Implementar ruff + mypy + pre-commit
- `3cc9826`: Remover black e flake8

**Métricas:**

- Cobertura testes: 5% (1/1 teste passando)
- Pipeline: 4.315 registros AC processados com sucesso
- Pre-commit: 3 hooks configurados (ruff, ruff-format, mypy)

---

## [Unreleased]

### Planned

- Análise exploratória (EDA) em Jupyter
- Cálculo 5 KPIs básicos
- Visualizações matplotlib (4-6 gráficos)
- Aumento cobertura testes (meta: 80%)
- Processamento estado ES (validação dataset MVP)
