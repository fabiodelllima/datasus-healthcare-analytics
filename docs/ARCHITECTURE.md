# ARCHITECTURE

- **Sistema:** DataSUS Healthcare Analytics
- **Versão:** 0.2.6
- **Última Atualização:** 03/01/2026

**Propósito:** Single Source of Truth para decisões arquiteturais, stack técnico, requisitos de sistema e workflows de infraestrutura.

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Arquitetura do Sistema](#arquitetura-do-sistema)
4. [Pipeline ETL](#pipeline-etl)
5. [Qualidade de Código](#qualidade-de-código)
6. [Testes e Coverage](#testes-e-coverage)
7. [Estrutura do Projeto](#estrutura-do-projeto)
8. [Decisões Arquiteturais (ADRs)](#decisões-arquiteturais-adrs)
9. [Workflows](#workflows)
10. [Requisitos de Sistema](#requisitos-de-sistema)

---

## Visão Geral

Sistema de analytics para gestão hospitalar baseado em dados públicos do SIH/DataSUS, estruturado em três fases progressivas: POC, MVP e Produção.

### Princípios Arquiteturais

1. **Simplicidade primeiro:** POC usa ferramentas simples, escala progressivamente
2. **Dados reais:** Sem dados sintéticos, apenas datasets governamentais públicos
3. **Code quality:** Type safety, linting automático, pre-commit hooks
4. **Documentação:** Single Source of Truth por domínio
5. **Testabilidade:** Coverage tracking, testes automatizados

---

## Stack Tecnológico

### Core Pipeline (POC)

| Componente    | Tecnologia | Versão   | Justificativa                             |
| ------------- | ---------- | -------- | ----------------------------------------- |
| **Runtime**   | Python     | 3.11.x   | Compatibilidade pysus (não suporta 3.12+) |
| **Extract**   | pysus      | >=0.11.0 | Biblioteca Fiocruz para FTP DataSUS       |
| **Transform** | pandas     | >=2.1.4  | Padrão indústria para data wrangling      |
| **Transform** | numpy      | >=1.26.2 | Operações numéricas otimizadas            |
| **Load**      | pyarrow    | >=14.0.1 | Parquet format, compressão eficiente      |

**Nota sobre pysus:** Biblioteca desenvolvida pela Fiocruz (projeto AlertaDengue), não é oficial do DataSUS. Abstrai acesso ao FTP e decode de arquivos .dbc.

### Qualidade de Código

| Ferramenta       | Versão   | Função                | Substitui                          |
| ---------------- | -------- | --------------------- | ---------------------------------- |
| **ruff**         | >=0.14.8 | Linter + formatter    | black + flake8 + isort + pyupgrade |
| **mypy**         | >=1.19.0 | Type checker          | -                                  |
| **pre-commit**   | >=4.5.0  | Git hooks automáticos | -                                  |
| **pandas-stubs** | >=2.3.3  | Type stubs pandas     | -                                  |

**Por que Ruff?**

- 10-100x mais rápido que flake8/black
- Consolidação: 1 ferramenta substitui 4
- Configuração unificada (pyproject.toml)
- Auto-fix nativo

### Testes

| Ferramenta      | Versão   | Função           |
| --------------- | -------- | ---------------- |
| **pytest**      | >=8.0.0  | Framework testes |
| **pytest-cov**  | >=6.0.0  | Cobertura código |
| **pytest-bdd**  | >=7.0.0  | BDD scenarios    |
| **pytest-mock** | >=3.14.0 | Mocking          |
| **VCR.py**      | >=6.0.0  | HTTP mocking     |

### Visualização e Análise

| Componente    | Tecnologia | Versão   | Uso                     |
| ------------- | ---------- | -------- | ----------------------- |
| **Gráficos**  | matplotlib | >=3.8.2  | Visualizações estáticas |
| **Notebooks** | jupyter    | >=1.0.0  | Análise exploratória    |
| **Kernel**    | ipykernel  | >=6.27.1 | Runtime notebooks       |

### Utilities

| Ferramenta        | Versão   | Função             |
| ----------------- | -------- | ------------------ |
| **python-dotenv** | >=1.0.0  | Variáveis ambiente |
| **requests**      | >=2.31.0 | HTTP client        |

### Stack MVP (Planejado)

- **Database:** Oracle XE 21c
- **BI:** Power BI Desktop ou Streamlit
- **Data Lake:** Parquet files

### Stack Produção (Planejado)

- **Orquestração:** Apache Airflow
- **API:** FastAPI + Uvicorn
- **Auth:** JWT (pyjwt)
- **Monitoring:** Prometheus + Grafana
- **CI/CD:** GitHub Actions

---

## Arquitetura do Sistema

### Diagrama High-Level

```
┌─────────────────────────────────────────────────────────────────┐
│                         DataSUS FTP Server                      │
│                    ftp.datasus.gov.br/dissemin/                 │
└─────────────────┬───────────────────────────────────────────────┘
                  │ .dbc files (compressed DBF)
                  │
                  ▼
┌────────────────────────────────────────────────────────────────┐
│                   EXTRACT (pysus - Fiocruz)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ DataSUSExtractor                                         │  │
│  │ - download(state, year, month, groups='RD')              │  │
│  │ - ParquetSet.to_dataframe()                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────┬──────────────────────────────────────────────┘
                  │ pd.DataFrame (raw)
                  │
                  ▼
┌────────────────────────────────────────────────────────────────┐
│                    TRANSFORM (pandas/numpy)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ DataTransformer                                          │  │
│  │ 1. _convert_types()    → tipos corretos                  │  │
│  │ 2. _clean_data()       → remove duplicatas/nulos         │  │
│  │ 3. _validate_data()    → valida ranges                   │  │
│  │ 4. _enrich_data()      → campos calculados               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────┬──────────────────────────────────────────────┘
                  │ pd.DataFrame (clean)
                  │
                  ▼
┌────────────────────────────────────────────────────────────────┐
│                      LOAD (pyarrow)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ DataLoader                                               │  │
│  │ - to_csv()      → CSV UTF-8                              │  │
│  │ - to_parquet()  → Parquet compressed                     │  │
│  │ - metadata      → Dict com estatísticas                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────┬──────────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│   CSV Files   │   │ Parquet Files │
│  (~2.7 MB)    │   │  (~320 KB)    │
│  Human-read   │   │  Compressed   │
└───────┬───────┘   └───────┬───────┘
        │                   │
        └─────────┬─────────┘
                  │
                  ▼
        ┌─────────────────┐
        │   Analytics     │
        │   (Jupyter)     │
        └─────────────────┘
```

---

## Pipeline ETL

### 1. Extract

**Responsabilidade:** Download e decode arquivos DBC do DataSUS.

**Implementação:**

```python
from pysus.online_data.SIH import download

parquet_set = download(
    states='AC',
    years=2024,
    months=1,
    groups='RD'  # AIH Reduzida
)
df = parquet_set.to_dataframe()
```

**Características:**

- pysus (Fiocruz) abstrai FTP + decode DBC
- Retorna ParquetSet (não lista de arquivos)
- Método `.to_dataframe()` converte para pandas
- Cache automático em `~/pysus/`

**Performance:**

- Download: ~313 KB comprimido
- Tempo: <1s (AC janeiro 2024)
- Registros: 4.315

### 2. Transform

**Responsabilidade:** Limpeza, validação e enriquecimento.

**Pipeline em 4 etapas:**

#### 2.1. Convert Types

```python
def _convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
    # Numéricos: IDADE, VAL_TOT, VAL_UTI, etc
    df[field] = pd.to_numeric(df[field], errors='coerce')

    # Datas: DT_INTER, DT_SAIDA
    df[field] = pd.to_datetime(df[field], format='%Y%m%d', errors='coerce')
```

#### 2.2. Clean Data

```python
def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
    # Remove duplicatas
    df = df.drop_duplicates()

    # Remove nulos em campos críticos
    df = df.dropna(subset=['N_AIH', 'DT_INTER', 'DT_SAIDA'])
```

#### 2.3. Validate Data

```python
def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
    # Datas: DT_INTER <= DT_SAIDA
    df = cast(pd.DataFrame, df[df['DT_INTER'] <= df['DT_SAIDA']])

    # Idade: 0-120 anos
    df = cast(pd.DataFrame, df[(df['IDADE'] >= 0) & (df['IDADE'] <= 120)])

    # Valores: >= 0
    df = cast(pd.DataFrame, df[df[col] >= 0])
```

#### 2.4. Enrich Data

```python
def _enrich_data(self, df: pd.DataFrame) -> pd.DataFrame:
    # Tempo permanência
    df['stay_days'] = (df['DT_SAIDA'] - df['DT_INTER']).dt.days

    # Custo diário
    df['daily_cost'] = df['VAL_TOT'] / df['stay_days'].replace(0, 1)

    # Faixa etária
    df['age_group'] = pd.cut(df['IDADE'], bins=[0,18,30,45,60,120])

    # Flag óbito
    df['death'] = df['MORTE'] == 1
```

**Taxa validação:** 100% (AC jan/2024: 4.315/4.315)

### 3. Load

**Responsabilidade:** Salvamento dual-format com metadata.

**Implementação:**

```python
# CSV - Human-readable
df.to_csv(csv_path, index=False, encoding='utf-8')

# Parquet - Compressed
df.to_parquet(parquet_path, index=False, engine='pyarrow')

# Metadata
metadata = {
    'state': 'AC',
    'records': 4315,
    'csv_size_mb': 2.7,
    'parquet_size_mb': 0.32,
    'timestamp': '2025-12-05T12:16:49'
}
```

**Compressão:** Parquet é ~8.5x menor que CSV

---

## Qualidade de Código

### Pre-commit Hooks

**Configuração:** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.8
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.19.0
    hooks:
      - id: mypy
        additional_dependencies: [pandas-stubs]
        args: [--ignore-missing-imports]
```

**Workflow:**

```bash
git commit -m "feat: nova feature"

# Pre-commit executa automaticamente:
# 1. ruff check --fix     → lint + auto-fix
# 2. ruff format          → formatting
# 3. mypy                 → type checking

# Se falhar → commit bloqueado
# Se passar → commit realizado
```

### Ruff Configuration

**Arquivo:** `pyproject.toml`

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
```

### Mypy Configuration

**Arquivo:** `mypy.ini`

```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
check_untyped_defs = True
ignore_missing_imports = True

[mypy-pysus.*]
ignore_missing_imports = True

[mypy-pyarrow.*]
ignore_missing_imports = True
```

### Type Hints Coverage

**Status atual:** 100% em funções públicas

```python
# Correto
def extract(self, state: str, year: int, month: int) -> pd.DataFrame:
    ...

def load(self, df: pd.DataFrame, state: str, year: int, month: int) -> dict[str, Any]:
    ...

# Type casting para satisfazer mypy
df = cast(pd.DataFrame, df[df['IDADE'] > 0])
```

---

## Testes e Coverage

### Framework

**pytest** com plugins:

- `pytest-cov`: relatórios cobertura
- `pytest-bdd`: BDD scenarios (Gherkin)
- `pytest-mock`: mocking/patching
- `VCR.py`: HTTP request mocking (cassettes)

### Executar Testes

```bash
# Rodar todos testes
pytest tests/ -v

# Com coverage
pytest tests/ --cov=src --cov-report=term-missing

# HTML report
pytest tests/ --cov=src --cov-report=html
# Ver: htmlcov/index.html
```

### Métricas Atuais (POC Concluída)

```
Cobertura: 97% (546 stmts, 18 miss)
Testes: 128 passed, 1 skipped

Módulos:
├── src/extract/extractor.py      100%
├── src/transform/transformer.py   94%
├── src/load/loader.py            100%
├── src/analytics/kpis.py         100%
├── src/visualizations/charts.py   84%
├── src/api/datasus_inspector.py   97%
├── src/main.py                    84%
└── src/utils/logger.py            84%
```

**Meta POC:** >50% coverage → Atingido: 97%
**Meta MVP:** >90% coverage

### Estrutura Testes

```
tests/
├── features/                    # BDD Gherkin
│   ├── hospitalization_validation.feature
│   ├── api_inspection.feature
│   └── kpis.feature
├── steps/                       # Step definitions
│   └── test_api_steps.py
├── fixtures/
│   └── cassettes/               # VCR.py HTTP mocks
├── test_extractor.py
├── test_transformer.py
├── test_loader.py
├── test_kpis.py
├── test_visualizations.py
├── test_terminal_formatter.py
├── test_api_inspector.py
├── test_main.py
├── test_coverage_gaps.py
└── conftest.py                  # Fixtures compartilhadas
```

---

## Estrutura do Projeto

```
datasus-healthcare-analytics/
├── src/                        # Código fonte
│   ├── __init__.py
│   ├── config.py               # Configurações globais
│   ├── main.py                 # Pipeline principal
│   │
│   ├── extract/                # Módulo Extract
│   │   ├── __init__.py
│   │   └── extractor.py        # DataSUSExtractor
│   │
│   ├── transform/              # Módulo Transform
│   │   ├── __init__.py
│   │   └── transformer.py      # DataTransformer
│   │
│   ├── load/                   # Módulo Load
│   │   ├── __init__.py
│   │   └── loader.py           # DataLoader
│   │
│   ├── analytics/              # Módulo Analytics
│   │   ├── __init__.py
│   │   └── kpis.py             # KPICalculator
│   │
│   ├── visualizations/         # Módulo Visualizações
│   │   ├── __init__.py
│   │   └── charts.py           # ChartGenerator
│   │
│   ├── api/                    # Módulo API
│   │   ├── __init__.py
│   │   └── datasus_inspector.py # OpenDataSUSInspector
│   │
│   └── utils/                  # Utilitários
│       ├── __init__.py
│       └── logger.py           # Setup logging
│
├── tests/                      # Testes pytest + BDD
│   ├── features/               # Gherkin scenarios
│   ├── steps/                  # Step definitions
│   ├── fixtures/cassettes/     # VCR.py mocks
│   └── test_*.py               # Testes unitários
│
├── data/                       # Dados (git-ignored parcialmente)
│   ├── raw/                    # Dados brutos
│   └── processed/              # Dados processados
│       ├── SIH_AC_202401.csv
│       └── SIH_AC_202401.parquet
│
├── outputs/                    # Outputs gerados
│   └── charts/                 # Visualizações PNG
│
├── logs/                       # Logs (git-ignored)
│
├── notebooks/                  # Jupyter notebooks
│   └── 01_exploratory_analysis.ipynb
│
├── docs/                       # Documentação
│   ├── ARCHITECTURE.md         # Este arquivo
│   ├── DATA_GUIDE.md           # Dicionário dados
│   ├── BUSINESS_RULES.md       # Regras de negócio
│   ├── API.md                  # Integrações API
│   ├── METHODOLOGY.md          # Workflow dev
│   ├── TOOLING.md              # Ferramentas CI/CD
│   └── ROADMAP.md              # Planejamento
│
├── .github/workflows/          # CI/CD
│   └── ci.yml
│
├── .gitignore
├── .pre-commit-config.yaml
├── mypy.ini
├── pyproject.toml
├── requirements.txt
├── CHANGELOG.md
└── README.md
```

---

## Decisões Arquiteturais (ADRs)

### ADR-001: Python 3.11 (não 3.12+)

**Status:** Aceito

**Contexto:** pysus (biblioteca Fiocruz) não suporta Python 3.12+

**Decisão:** Usar Python 3.11.x

**Consequências:**

- ✓ Compatibilidade garantida com pysus
- ✓ Suporte pandas/numpy maduro
- ✗ Sem features Python 3.12+

**Mitigação planejada (MVP):** Implementar extração FTP própria para eliminar dependência.

---

### ADR-002: Ruff vs Black + Flake8

**Status:** Aceito

**Contexto:** Black + flake8 + isort são ferramentas separadas, lentas

**Decisão:** Migrar para Ruff

**Alternativas consideradas:**

- Black + flake8 + isort (status quo)
- Pylint (mais lento que Ruff)

**Consequências:**

- ✓ 10-100x mais rápido
- ✓ 1 ferramenta substitui 4
- ✓ Configuração unificada (pyproject.toml)
- ✓ Auto-fix nativo
- ✗ Ferramenta relativamente nova (risco adoção)

---

### ADR-003: Dual-Format Storage (CSV + Parquet)

**Status:** Aceito

**Contexto:** CSV legível vs Parquet comprimido

**Decisão:** Salvar ambos formatos

**Consequências:**

- ✓ CSV: inspeção manual, Excel, debugging
- ✓ Parquet: compressão (~8.5x), queries rápidas
- ✗ 2x espaço disco (mitigado: Parquet pequeno)

---

### ADR-004: Type Hints com cast()

**Status:** Aceito

**Contexto:** Mypy não infere tipos em operações DataFrame

**Decisão:** Usar `cast(pd.DataFrame, df[...])` quando necessário

**Alternativas:**

- `# type: ignore` (menos explícito)
- Desabilitar mypy (perde type safety)

**Consequências:**

- ✓ Type safety mantido
- ✓ Mypy passa sem erros
- ✗ Verbosidade ligeiramente maior

---

### ADR-005: Pre-commit Hooks Obrigatórios

**Status:** Aceito

**Contexto:** Code quality deve ser automática, não manual

**Decisão:** Instalar pre-commit hooks para todos desenvolvedores

**Consequências:**

- ✓ Impossível commitar código sem lint/type check
- ✓ Consistência garantida
- ✓ CI/CD mais rápido (já validado localmente)
- ✗ Primeiro commit mais lento (setup hooks)

---

### ADR-006: VCR.py para HTTP Mocking

**Status:** Aceito

**Contexto:** Testes de API falhavam por timeout/instabilidade FTP

**Decisão:** Usar VCR.py para gravar e reproduzir respostas HTTP

**Consequências:**

- ✓ Testes determinísticos
- ✓ CI/CD não depende de serviços externos
- ✓ Execução rápida
- ✗ Cassettes precisam ser atualizadas se API mudar

---

## Workflows

### Desenvolvimento Local

```bash
# 1. Setup inicial
git clone https://github.com/fabiodelllima/datasus-healthcare-analytics.git
cd datasus-healthcare-analytics
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pre-commit install

# 2. Criar feature branch
git checkout develop
git checkout -b feat/nome-feature

# 3. Desenvolver
# Editar código...

# 4. Testar localmente
pytest tests/ -v
ruff check src/ --fix
mypy src/

# 5. Commit (pre-commit roda automaticamente)
git add .
git commit -m "feat(scope): Descrição em português"

# Se pre-commit falhar:
# - Corrige automaticamente
# - Adicionar correções: git add .
# - Commitar novamente

# 6. Push
git push origin feat/nome-feature

# 7. Merge para develop (--no-ff)
git checkout develop
git merge feat/nome-feature --no-ff
```

### CI/CD (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: ruff check .
      - run: mypy src/
      - run: pytest tests/ --cov=src
```

---

## Requisitos de Sistema

### Hardware Mínimo (POC)

- **CPU:** 2 cores
- **RAM:** 4 GB
- **Disco:** 10 GB livre
- **Rede:** Conexão internet (download DataSUS)

### Hardware Recomendado (MVP)

- **CPU:** 4+ cores
- **RAM:** 8+ GB
- **Disco:** 50+ GB (múltiplos estados)
- **Rede:** Banda larga (downloads grandes)

### Software

**Obrigatório:**

- Python 3.11.x
- pip >= 23.0
- Git >= 2.30

**Recomendado:**

- VS Code + extensões:
  - Python (Microsoft)
  - Pylance (Microsoft)
  - Ruff (Astral)
  - Jupyter
- Oracle SQL Developer (MVP)
- Power BI Desktop (MVP)

### Plataformas Suportadas

- ✓ Linux (testado: Ubuntu, Fedora)
- ✓ macOS (não testado, deve funcionar)
- ✓ Windows (não testado, deve funcionar)

---

## Evolução Arquitetural

### Decisão: Modular Monolith (Não Microsserviços)

**Contexto:** Processamento de dados de 27 estados brasileiros, volume 10-50M registros.

**Escolha:** Modular Monolith com separação clara de módulos.

**Razionale:**

- Volume < 100M registros (microsserviços são overkill)
- Time pequeno (1-5 devs)
- Domínio coeso (healthcare analytics)
- Overhead operacional de microsserviços não justificado
- Transações ACID necessárias

**Ver:** docs/DECISION_LOG.md para detalhes completos.

---

### Fase 1: POC (Concluída - v0.2.6)

**Arquitetura:** Script-based ETL pipeline

```
DataSUS FTP → Extract → Transform → Load → CSV/Parquet
     ↓          ↓          ↓          ↓         ↓
   .dbc       pysus     pandas     pathlib   storage
```

**Características:**

- Execução manual/script
- Sem orquestração
- Storage: Filesystem (CSV + Parquet)
- Análise: Jupyter notebooks + matplotlib

**Adequado para:**

- <10k registros/dia
- 1 desenvolvedor
- Prototipação rápida

---

### Fase 2: MVP (Planejado - Q1 2026)

**Arquitetura:** Modular Monolith + Scheduled Jobs

```
┌─────────────────────────────────────────────┐
│              Application                    │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │   ETL    │  │   API    │  │ Analytics │  │
│  │  Module  │  │  Module  │  │   Module  │  │
│  └──────────┘  └──────────┘  └───────────┘  │
│        │             │             │        │
│        └─────────────┴─────────────┘        │
│                      │                      │
│               Shared Services               │
│             (config, logging, db)           │
└─────────────────────────────────────────────┘
        │
   ┌────▼─────┐
   │ Oracle   │
   │ Database │
   └──────────┘
```

**Stack adicional:**

- Oracle XE 21c: RDBMS
- Power BI ou Streamlit: Dashboards
- cron: Agendamento

**Adequado para:**

- <100k registros/dia
- 2-5 desenvolvedores
- SLA moderados (latência <5s)

---

### Fase 3: Produção (Planejado - Q2 2026)

**Arquitetura:** Event-Driven Batch + API

```
┌───────────┐     ┌───────────┐     ┌──────────┐
│ Airflow   │────▶│ Message   │────▶│ Workers  │
│ Scheduler │     │  Queue    │     │          │
└───────────┘     └───────────┘     └──────────┘
                       │                 │
                       ▼                 ▼
                 ┌──────────┐      ┌───────────┐
                 │ FastAPI  │◀─────│  Oracle   │
                 │ Workers  │      │  Database │
                 └──────────┘      └───────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   Prometheus    │
              │   + Grafana     │
              └─────────────────┘
```

**Stack adicional:**

- Airflow: Orquestração DAGs
- Prometheus + Grafana: Observabilidade
- Docker: Containerização

**Adequado para:**

- <1M registros/dia
- 5-10 desenvolvedores
- SLA rigorosos (latência <1s p99)

---

### Quando Considerar Microsserviços

**Reavaliar arquitetura se:**

- Volume > 100M registros/dia
- Requisições > 100k/dia
- SLA < 100ms p99
- Times múltiplos independentes (>10 devs)
- Múltiplas fontes heterogêneas

**Até lá:** Modular Monolith é suficiente e mais simples.

---

## Referências

- [pysus Documentation](https://github.com/AlertaDengue/PySUS) (Fiocruz)
- [DataSUS FTP](ftp://ftp.datasus.gov.br)
- [Ruff](https://docs.astral.sh/ruff/)
- [Mypy](https://mypy.readthedocs.io/)
- [pytest](https://docs.pytest.org/)
- [Pre-commit](https://pre-commit.com/)
- [VCR.py](https://vcrpy.readthedocs.io/)
