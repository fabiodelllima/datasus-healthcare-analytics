# DataSUS Healthcare Analytics

![Status](https://img.shields.io/badge/POC-Conclu%C3%ADda-brightgreen)
![Slides](https://img.shields.io/badge/Slides-Em%20Progresso-yellow)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Coverage](https://img.shields.io/badge/Coverage-97%25-brightgreen)
![Tests](https://img.shields.io/badge/Tests-128%20passed-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)

> Sistema que transforma dados brutos de internações hospitalares do SUS em análises úteis para gestão hospitalar. O projeto processa arquivos do Ministério da Saúde (formato proprietário .dbc), limpa e valida os dados, e gera indicadores de desempenho hospitalar.

Hospitais e gestores de saúde precisam de dados confiáveis para tomar decisões. Os dados públicos do SUS estão disponíveis, mas em formato difícil de usar. Este projeto resolve esse problema, entregando dados limpos e KPIs prontos para análise.

**Resultados concretos:**

| Métrica                 | Valor                          |
| ----------------------- | ------------------------------ |
| Internações processadas | 4.315 registros                |
| Taxa de validação       | 100% dos dados                 |
| KPIs calculados         | 5 indicadores hospitalares     |
| Cobertura de testes     | 97% (128 testes automatizados) |
| Visualizações           | 6 gráficos profissionais       |

---

## Índice

- [Arquitetura](#arquitetura)
- [KPIs Implementados](#kpis-implementados)
- [Visualizações](#visualizações)
- [Stack Tecnológico](#stack-tecnológico)
- [Dados](#dados)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Status e Roadmap](#status-e-roadmap)
- [Quick Start](#quick-start)
- [Documentação](#documentação)

---

## Arquitetura

O sistema segue uma arquitetura ETL (Extract, Transform, Load) clássica, processando dados em etapas bem definidas:

```
DataSUS FTP ──> EXTRACT ──> TRANSFORM ──> LOAD ──> Analytics
                  |            |           |           |
                pysus        pandas    CSV/Parquet  Jupyter
              (Fiocruz)      numpy                  matplotlib
```

**Como funciona:**

1. **Extract:** Baixa arquivos .dbc do servidor FTP do Ministério da Saúde
2. **Transform:** Converte tipos, remove duplicatas, valida regras de negócio, enriquece com campos calculados
3. **Load:** Salva em dois formatos (CSV para análise manual, Parquet para performance)
4. **Analytics:** Calcula KPIs e gera visualizações

**Detalhes técnicos:** [ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## KPIs Implementados

Os indicadores foram escolhidos por sua relevância na gestão hospitalar real:

| KPI                        | O que mede                    | Relevância              |
| -------------------------- | ----------------------------- | ----------------------- |
| Taxa de Ocupação           | Utilização de leitos          | Otimização de recursos  |
| Tempo Médio de Permanência | Dias de internação            | Eficiência operacional  |
| Volume de Internações      | Total por período             | Planejamento de demanda |
| Receita Total              | Valores reembolsados pelo SUS | Saúde financeira        |
| Distribuição Demográfica   | Perfil etário dos pacientes   | Adequação de serviços   |

**Detalhes e fórmulas:** [DATA_GUIDE.md](docs/DATA_GUIDE.md)

---

## Visualizações

O sistema gera automaticamente 6 gráficos em alta resolução (300 DPI), prontos para apresentações:

1. Distribuição por faixa etária
2. Receita por especialidade médica
3. Tempo médio de permanência por especialidade
4. Top 10 diagnósticos (CID-10)
5. Volume diário de internações
6. Distribuição por sexo

**Localização:** `outputs/charts/`

---

## Stack Tecnológico

### Core

Cada ferramenta foi escolhida com propósito específico:

| Tecnologia       | Função                 | Justificativa                                         |
| ---------------- | ---------------------- | ----------------------------------------------------- |
| **Python 3.11**  | Linguagem principal    | Compatibilidade com biblioteca de acesso ao DataSUS   |
| **pandas/numpy** | Processamento de dados | Padrão da indústria para data wrangling               |
| **pysus**        | Acesso ao DataSUS      | Biblioteca da Fiocruz que abstrai complexidade do FTP |
| **pyarrow**      | Storage eficiente      | Parquet oferece compressão 8x menor que CSV           |
| **pytest**       | Testes automatizados   | Framework robusto com suporte a BDD                   |
| **ruff**         | Qualidade de código    | 10-100x mais rápido que alternativas                  |

### Ferramentas de Qualidade

| Ferramenta          | Função                                       |
| ------------------- | -------------------------------------------- |
| ruff                | Linter + formatter (substitui 4 ferramentas) |
| mypy                | Verificação de tipos estáticos               |
| pytest + pytest-bdd | Testes unitários e comportamentais           |
| pre-commit          | Validação automática antes de commits        |
| VCR.py              | Mock de requisições HTTP para testes         |
| GitHub Actions      | CI/CD automatizado                           |

---

## Dados

### Fonte

Os dados vêm do **Sistema de Informações Hospitalares (SIH)** do DataSUS/Ministério da Saúde. São dados públicos que registram todas as internações realizadas em hospitais do SUS no Brasil.

O acesso é feito via FTP utilizando a biblioteca pysus, desenvolvida pela Fiocruz (projeto AlertaDengue).

### Dataset Atual

| Estado    | Período      | Registros | Tamanho       |
| --------- | ------------ | --------- | ------------- |
| Acre (AC) | Janeiro/2024 | 4.315     | ~2.7 MB (CSV) |

### Principais Campos

| Categoria     | Campos               | Descrição                                |
| ------------- | -------------------- | ---------------------------------------- |
| Identificação | N_AIH, CNES          | Número da internação, código do hospital |
| Temporal      | DT_INTER, DT_SAIDA   | Datas de entrada e saída                 |
| Financeiro    | VAL_TOT, VAL_UTI     | Valores reembolsados pelo SUS            |
| Clínico       | DIAG_PRINC, PROC_REA | Diagnóstico (CID-10), procedimento       |
| Demográfico   | IDADE, SEXO          | Perfil do paciente                       |

**Dicionário completo:** [DATA_GUIDE.md](docs/DATA_GUIDE.md)

---

## Estrutura do Projeto

Organização modular seguindo boas práticas de engenharia de software:

```
datasus-healthcare-analytics/
├── src/
│   ├── extract/           # Download via FTP
│   ├── transform/         # Limpeza e validação
│   ├── load/              # Persistência
│   ├── analytics/         # Cálculo de KPIs
│   ├── visualizations/    # Gráficos
│   ├── api/               # Integração OpenDataSUS
│   └── main.py            # Orquestração
├── tests/                 # 128 testes automatizados
├── notebooks/             # Análise exploratória
├── data/                  # Dados brutos e processados
├── outputs/               # Visualizações geradas
└── docs/                  # 8 documentos técnicos
```

---

## Status e Roadmap

### POC Concluída

| Entrega                 | Status |
| ----------------------- | ------ |
| Pipeline ETL funcional  | ✓      |
| 5 KPIs implementados    | ✓      |
| 6 visualizações         | ✓      |
| 97% cobertura de testes | ✓      |
| Documentação completa   | ✓      |
| CI/CD configurado       | ✓      |

### Próximas Fases

| Fase         | Entregas Planejadas                                      |
| ------------ | -------------------------------------------------------- |
| **MVP**      | Oracle Database, Dashboard interativo, múltiplos estados |
| **Produção** | Apache Airflow, API REST, monitoramento em tempo real    |

**Planejamento detalhado:** [ROADMAP.md](docs/ROADMAP.md)

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

# 6. Verificar resultados
ls data/processed/  # SIH_AC_202401.csv e .parquet
```

### Executar Testes

```bash
# Todos os testes
pytest tests/ -v

# Com relatório de cobertura
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Documentação

| Documento                                   | Conteúdo                                |
| ------------------------------------------- | --------------------------------------- |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md)     | Stack técnico, decisões arquiteturais   |
| [DATA_GUIDE.md](docs/DATA_GUIDE.md)         | Dicionário de dados, KPIs, pipeline ETL |
| [BUSINESS_RULES.md](docs/BUSINESS_RULES.md) | Regras de validação e transformação     |
| [ROADMAP.md](docs/ROADMAP.md)               | Planejamento e cronograma               |
| [METHODOLOGY.md](docs/METHODOLOGY.md)       | Workflow de desenvolvimento             |
| [TOOLING.md](docs/TOOLING.md)               | Ferramentas de qualidade e CI/CD        |
| [API.md](docs/API.md)                       | Integração com OpenDataSUS              |
| [CHANGELOG.md](CHANGELOG.md)                | Histórico de versões                    |

---

## Licença

Projeto de código aberto para fins educacionais e de portfólio.

---

## Disclaimer

Projeto independente para aprendizado e demonstração de habilidades em Data Analytics/Engineering. Não há vínculo oficial com o Ministério da Saúde ou DATASUS.

A biblioteca pysus utilizada é desenvolvida pelo projeto AlertaDengue da Fiocruz.

Dados de domínio público: <https://datasus.saude.gov.br>
