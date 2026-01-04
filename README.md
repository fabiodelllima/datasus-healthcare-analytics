# DataSUS Healthcare Analytics

- **Versão:** 0.2.6
- **Fase:** POC Concluída
- **Última atualização:** 03/01/2026

Sistema de analytics para gestão hospitalar utilizando dados públicos do Sistema de Informações Hospitalares (SIH/DataSUS) do Ministério da Saúde brasileiro.

---

## Documentação

A documentação está organizada em módulos específicos para facilitar navegação e manutenção.

### Documentos Principais

| Documento                                   | Descrição                            | Quando Consultar                  |
| ------------------------------------------- | ------------------------------------ | --------------------------------- |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md)     | Stack técnico, ADRs, diagramas       | Setup inicial, decisões técnicas  |
| [DATA_GUIDE.md](docs/DATA_GUIDE.md)         | Dicionário de dados, pipeline ETL    | Análise de dados, desenvolvimento |
| [BUSINESS_RULES.md](docs/BUSINESS_RULES.md) | Regras de validação e enriquecimento | Implementação, testes             |
| [ROADMAP.md](docs/ROADMAP.md)               | Planejamento, cronograma, milestones | Acompanhamento do projeto         |
| [CHANGELOG.md](CHANGELOG.md)                | Histórico de versões                 | Release notes                     |

### Documentos Complementares

| Documento                             | Descrição                                     |
| ------------------------------------- | --------------------------------------------- |
| [API.md](docs/API.md)                 | Integração OpenDataSUS, regras de negócio API |
| [METHODOLOGY.md](docs/METHODOLOGY.md) | Workflow de desenvolvimento, TDD, Git         |
| [TOOLING.md](docs/TOOLING.md)         | Ferramentas de qualidade e CI/CD              |

---

## Quick Start

### Pré-requisitos

- Python 3.11.x (obrigatório - pysus não suporta 3.12+)
- pip >= 23.0
- Git

### Instalação

```bash
# 1. Clonar repositório
git clone https://github.com/fabiodelllima/datasus-healthcare-analytics.git
cd datasus-healthcare-analytics

# 2. Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar pre-commit hooks
pre-commit install

# 5. Rodar pipeline ETL
python -m src.main --state AC --year 2024 --month 1

# 6. Verificar outputs
ls data/processed/
# SIH_AC_202401.csv e SIH_AC_202401.parquet
```

---

## Desenvolvimento

### Executar Testes

```bash
# Todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=src --cov-report=term-missing

# Cobertura HTML
pytest tests/ --cov=src --cov-report=html
# Abrir: htmlcov/index.html
```

### Qualidade de Código

```bash
# Lint + format
ruff check src/ tests/ --fix
ruff format src/ tests/

# Type checking
mypy src/

# Todas verificações (pre-commit)
pre-commit run --all-files
```

---

## Arquitetura

```
DataSUS FTP ──→ EXTRACT ──→ TRANSFORM ──→ LOAD ──→ Analytics
                  │            │           │          │
                pysus        pandas   CSV/Parquet  Jupyter
              (Fiocruz)      numpy                matplotlib
```

O pipeline ETL processa arquivos .dbc (formato proprietário DataSUS) e gera datasets limpos para análise.

**Detalhes:** [ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Estrutura do Projeto

```
datasus-healthcare-analytics/
├── src/
│   ├── extract/           # Download via FTP (pysus)
│   ├── transform/         # Limpeza, validação, enriquecimento
│   ├── load/              # Salvamento CSV/Parquet
│   ├── analytics/         # Cálculo de KPIs
│   ├── visualizations/    # Geração de gráficos
│   ├── api/               # API Inspector OpenDataSUS
│   ├── utils/             # Logger e helpers
│   ├── config.py          # Configurações
│   └── main.py            # Pipeline principal
├── tests/                 # Testes pytest + BDD
├── notebooks/             # Jupyter notebooks EDA
├── data/
│   ├── raw/               # Dados brutos (.dbc)
│   └── processed/         # Dados processados (CSV/Parquet)
├── outputs/
│   └── charts/            # Visualizações PNG
├── docs/                  # Documentação
└── logs/                  # Logs de execução
```

---

## Stack Tecnológico

### Core

| Componente | Tecnologia    | Descrição                                        |
| ---------- | ------------- | ------------------------------------------------ |
| Runtime    | Python 3.11   | Compatibilidade com pysus                        |
| Extract    | pysus         | Biblioteca da Fiocruz para acesso ao FTP DataSUS |
| Transform  | pandas, numpy | Manipulação e validação de dados                 |
| Load       | pyarrow       | Storage Parquet comprimido                       |

### Qualidade

| Ferramenta | Função                   |
| ---------- | ------------------------ |
| ruff       | Linter + formatter       |
| mypy       | Type checking            |
| pytest     | Testes + cobertura       |
| pre-commit | Git hooks automáticos    |
| VCR.py     | HTTP mocking para testes |

### Visualização

| Ferramenta | Função                         |
| ---------- | ------------------------------ |
| matplotlib | Gráficos estáticos             |
| jupyter    | Notebooks análise exploratória |

---

## Dados

### Fonte

**Sistema de Informações Hospitalares (SIH)** do DataSUS/Ministério da Saúde.

Acesso via FTP utilizando a biblioteca pysus (desenvolvida pela Fiocruz/AlertaDengue).

### Dataset POC

| Estado | Período      | Registros | Arquivo       |
| ------ | ------------ | --------- | ------------- |
| AC     | Janeiro/2024 | 4.315     | SIH_AC_202401 |

### Campos Principais

| Categoria     | Campos                            |
| ------------- | --------------------------------- |
| Identificação | N_AIH, CGC_HOSP, CNES, MUNIC_RES  |
| Datas         | DT_INTER, DT_SAIDA                |
| Valores       | VAL_TOT, VAL_UTI, VAL_SH, VAL_SP  |
| Clínica       | DIAG_PRINC, PROC_REA, IDADE, SEXO |

**Dicionário completo:** [DATA_GUIDE.md](docs/DATA_GUIDE.md)

---

## KPIs Implementados

| KPI                     | Descrição            | Método                             |
| ----------------------- | -------------------- | ---------------------------------- |
| Taxa de Ocupação        | Utilização de leitos | pacientes_dia / leitos_disponíveis |
| Tempo Médio Permanência | Dias de internação   | stay_days.mean()                   |
| Volume                  | Total de internações | count por período                  |
| Receita                 | Valores SUS          | VAL_TOT.sum()                      |
| Demografia              | Distribuição etária  | age_group.value_counts()           |

**Detalhes:** [DATA_GUIDE.md](docs/DATA_GUIDE.md)

---

## Visualizações

O módulo `ChartGenerator` produz 6 gráficos em PNG (300 DPI):

1. Distribuição por faixa etária
2. Receita por especialidade
3. Tempo médio de permanência por especialidade
4. Top 10 diagnósticos (CID-10)
5. Volume diário de internações
6. Distribuição por sexo

**Localização:** `outputs/charts/`

---

## Status do Projeto

### POC Concluída

| Métrica             | Valor                          |
| ------------------- | ------------------------------ |
| Cobertura de testes | 97% (128 testes)               |
| Type hints          | 100% funções públicas          |
| Pipeline            | 4.315 registros AC processados |
| Visualizações       | 6 gráficos PNG                 |
| Documentação        | 8 documentos SSOT              |

### Roadmap

| Fase     | Status    | Entregas                                      |
| -------- | --------- | --------------------------------------------- |
| POC      | Concluída | Pipeline ETL, KPIs, visualizações, testes 97% |
| MVP      | Planejado | Oracle Database, Dashboard, multi-estado      |
| Produção | Futuro    | Airflow, API REST, monitoramento              |

**Planejamento detalhado:** [ROADMAP.md](docs/ROADMAP.md)

---

## Licença

Projeto de código aberto para fins educacionais e de portfólio.

---

## Disclaimer

Este é um projeto independente para aprendizado e demonstração de habilidades em Data Analytics/Engineering. Não há vínculo oficial com o Ministério da Saúde ou DATASUS.

A biblioteca pysus utilizada para acesso aos dados é desenvolvida pelo projeto AlertaDengue da Fiocruz.

Os dados são de domínio público e acessíveis através do portal oficial: https://datasus.saude.gov.br
