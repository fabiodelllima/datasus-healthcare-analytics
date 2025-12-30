# DataSUS Healthcare Analytics

- **Versão:** 0.2.6
- **Fase:** POC (Proof of Concept)
- **Data:** 30/12/2025

Sistema de analytics para gestão hospitalar utilizando dados públicos reais do Sistema de Informações Hospitalares (SIH/DataSUS) do Ministério da Saúde brasileiro.

---

## Documentação

Esta documentação está organizada em módulos específicos para facilitar navegação e manutenção.

### Quick Links

| Documento                                       | Descrição                                   | Uso                               |
| ----------------------------------------------- | ------------------------------------------- | --------------------------------- |
| **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**     | Decisões arquiteturais, stack técnico, ADRs | Setup inicial, entender o sistema |
| **[DATA_GUIDE.md](docs/DATA_GUIDE.md)**         | Dicionário de dados, regras de negócio, ETL | Desenvolvimento, análise de dados |
| **[BUSINESS_RULES.md](docs/BUSINESS_RULES.md)** | Regras de validação e enriquecimento        | Implementação, testes             |
| **[ROADMAP.md](docs/ROADMAP.md)**               | Planejamento, cronograma, milestones        | Acompanhamento do projeto         |
| **[CHANGELOG.md](CHANGELOG.md)**                | Histórico de versões e mudanças             | Release notes                     |

---

## Quick Start

### Pré-requisitos

- Python 3.11.x (OBRIGATÓRIO - pysus não suporta 3.12+)
- pip >= 23.0
- Git

### Instalação

```bash
# 1. Clonar repositório
git clone <repo-url>
cd datasus-test

# 2. Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Criar diretórios
mkdir -p data/{raw,processed} logs outputs

# 5. Rodar pipeline
python -m src.main --state AC --year 2024 --month 1

# 6. Verificar outputs
ls data/processed/
# Deve conter: SIH_AC_202401.csv e SIH_AC_202401.parquet
```

---

## Desenvolvimento

### Setup Ferramentas Quality

```bash
# Instalar ferramentas de desenvolvimento
pip install -r requirements.txt

# Configurar pre-commit hooks
pre-commit install

# Agora todo commit rodará automaticamente:
# - Ruff (linter + formatter)
# - Mypy (type checker)
```

### Executar Testes

```bash
# Rodar todos testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=src --cov-report=term-missing

# Cobertura HTML
pytest tests/ --cov=src --cov-report=html
# Ver em: htmlcov/index.html
```

### Qualidade de Código

```bash
# Lint + format
ruff check src/ tests/ --fix
ruff format src/ tests/

# Type checking
mypy src/ tests/

# Rodar todas verificações (pre-commit)
pre-commit run --all-files
```

### Workflow Git

```bash
# Criar branch feature
git checkout -b feat/nome-feature

# Desenvolver...
# Pre-commit roda automaticamente ao commitar
git add .
git commit -m "feat: descrição"

# Se pre-commit falhar, corrige automaticamente
# Adicionar correções e commitar novamente
git add .
git commit -m "feat: descrição"

# Merge para develop
git checkout develop
git merge feat/nome-feature --no-ff
```

---

## Arquitetura

Resumo da arquitetura:

```
DataSUS FTP → EXTRACT → TRANSFORM → LOAD → CSV/Parquet → Analytics
    ↓           ↓           ↓         ↓           ↓          ↓
  .dbc        pysus   pandas/numpy  pathlib    storage    jupyter
```

**Detalhes completos:** [ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Estrutura do Projeto

```
datasus-test/
├── src/
│   ├── extract/             # Download dados DataSUS
│   ├── transform/           # Limpeza e enriquecimento
│   ├── load/                # Salvamento dual-format
│   ├── utils/               # Logger e helpers
│   ├── config.py            # Configurações
│   └── main.py              # Pipeline principal
├── tests/                   # Testes pytest
├── data/
│   ├── raw/                 # Dados brutos (git-ignored)
│   ├── processed/           # Dados processados (git-ignored)
├── logs/                    # Logs pipeline (git-ignored)
├── notebooks/               # Jupyter notebooks análise
├── docs/                    # Documentação detalhada
├── .pre-commit-config.yaml  # Hooks pre-commit
├── mypy.ini                 # Configuração mypy
├── pyproject.toml           # Configuração ruff
└── requirements.txt         # Dependências Python
```

---

## Stack Tecnológico

### Core

- **Python 3.11**: Compatibilidade pysus
- **pysus**: Download/decode arquivos DataSUS
- **pandas**: Manipulação dados
- **pyarrow**: Storage Parquet

### Qualidade de Código

- **ruff**: Linter + formatter (substitui black + flake8)
- **mypy**: Type checking
- **pre-commit**: Git hooks automáticos
- **pytest**: Framework testes + cobertura

### Visualização

- **matplotlib**: Gráficos estáticos
- **seaborn**: Visualizações estatísticas
- **jupyter**: Notebooks análise exploratória

**Stack completo:** [ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Dados

### Fonte

Sistema de Informações Hospitalares (SIH/DataSUS) - dados públicos de internações hospitalares do SUS.

### Período POC

- **Estados:** AC, ES (dataset reduzido para validação)
- **Período:** Janeiro 2024
- **Volume:** ~4.300 registros AC, ~15.000 registros ES

### Campos Principais

- Identificação: N_AIH, CGC_HOSP, MUNIC_RES
- Datas: DT_INTER, DT_SAIDA
- Valores: VAL_TOT, VAL_UTI, VAL_SH, VAL_SP
- Clínica: DIAG_PRINC, PROC_REA, IDADE, SEXO

**Dicionário completo:** [DATA_GUIDE.md](docs/DATA_GUIDE.md)

---

## KPIs Implementados

POC implementa 5 KPIs básicos:

1. **Taxa de Ocupação**: Utilização leitos disponíveis
2. **Tempo Médio Permanência (TMP)**: Dias internação por procedimento
3. **Volume Atendimentos**: Total internações por período
4. **Receita Total**: Valores reembolsados SUS
5. **Demografia**: Distribuição faixa etária atendimentos

**Detalhes cálculo:** [DATA_GUIDE.md](docs/DATA_GUIDE.md)

---

## Roadmap

### POC (Atual - 1 semana)

- [x] Pipeline ETL funcional
- [x] Code quality (ruff + mypy + pre-commit)
- [x] Testes CI/CD (VCR.py para API mocking)
- [x] Análise exploratória (EDA)
- [x] Visualizações matplotlib (6 gráficos)
- [x] Documentação completa

### MVP (3-4 semanas)

- [ ] Integração Oracle Database
- [ ] Dashboard Power BI
- [ ] Processamento múltiplos estados
- [ ] Testes integração

### Produção (Futuro)

- [ ] Orquestração Airflow
- [ ] API REST
- [ ] Monitoramento
- [ ] CI/CD completo

**Planejamento detalhado:** [ROADMAP.md](docs/ROADMAP.md)

---

## Status do Projeto

### Métricas Atuais (CI/CD Real)

- **Cobertura Testes:** 97% (128 testes passing, 1 skip)
- **Type Hints:** 100% funções públicas
- **Code Quality:** Ruff + Mypy passing
- **Pipeline:** Funcional (4.315 registros AC processados)
- **API Inspector:** 97% coverage (VCR.py cassettes)
- **CI/CD:** GitHub Actions configurado

### Status POC

- [x] **CONCLUÍDA**
- Testes CI: Corrigidos com VCR.py (HTTP mocking)
- POC concluída com sucesso
- POC 100% - Pronto para MVP

---

## Licença

Este projeto é de código aberto para fins educacionais e de portfólio.

---

## Disclaimer

Este é um projeto independente para aprendizado e portfólio profissional. Não há qualquer vínculo com:

- Ministério da Saúde
- DATASUS
- FIOCRUZ
- Qualquer órgão governamental brasileiro

Os dados utilizados são de domínio público e acessíveis através do portal oficial do DataSUS:

> <https://datasus.saude.gov.br\>
