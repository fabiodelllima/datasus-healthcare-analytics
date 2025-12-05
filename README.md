# DataSUS Healthcare Analytics

- **Versão:** 0.1.0
- **Fase:** POC (Proof of Concept)
- **Data:** 01/12/2024

Sistema de analytics para gestão hospitalar utilizando dados públicos reais do Sistema de Informações Hospitalares (SIH/DataSUS) do Ministério da Saúde brasileiro.

---

## Documentação

Esta documentação está organizada em módulos específicos para facilitar navegação e manutenção.

### Quick Links

| Documento                                   | Descrição                                   | Uso                               |
| ------------------------------------------- | ------------------------------------------- | --------------------------------- |
| **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** | Decisões arquiteturais, stack técnico, ADRs | Setup inicial, entender o sistema |
| **[DATA_GUIDE.md](docs/DATA_GUIDE.md)**     | Dicionário de dados, regras de negócio, ETL | Desenvolvimento, análise de dados |
| **[ROADMAP.md](docs/ROADMAP.md)**           | Fases do projeto, timeline, milestones      | Planejamento, tracking progresso  |
| **[CHANGELOG.md](CHANGELOG.md)**            | Histórico de versões                        | Controle de mudanças              |

---

## Quick Start

```bash
# 1. Setup ambiente (Python 3.11 obrigatório)
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Criar estrutura de dados (se necessário)
mkdir -p data/{raw,processed} logs outputs

# 3. Executar pipeline ETL
python src/main.py --state AC --year 2024 --month 1

# 4. Verificar outputs
# Deve conter: AC_2024_01.csv e AC_2024_01.parquet
ls data/processed/

# 5. Análise exploratória
jupyter notebook
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

## Fases do Projeto

```
[ATUAL] POC (1 semana | 01-07/12/2024)
├─ Dataset: AC, Jan/2024, ~2k registros
├─ Stack: Python + pandas + matplotlib
└─ Entregável: Pipeline funcional + 5 KPIs

[FUTURO] MVP (3-4 semanas | 08-31/12/2024)
├─ Dataset: AC/ES, 12 meses, ~30k registros
├─ Stack: + Oracle XE + Power BI
└─ Entregável: Dashboard interativo

[FUTURO] Produção (4-6 semanas | Q1 2025)
├─ Dataset: Multi-UF, multi-fontes
├─ Stack: + Airflow + API REST
└─ Entregável: Sistema production-ready
```

**Timeline detalhado:** [ROADMAP.md](docs/ROADMAP.md)

---

## Stack Técnico

| Camada           | Tecnologia           | Versão | Fase     |
| ---------------- | -------------------- | ------ | -------- |
| **Linguagem**    | Python               | 3.11.x | POC      |
| **ETL**          | pysus, pandas, numpy | -      | POC      |
| **Visualização** | matplotlib, seaborn  | -      | POC      |
| **Storage**      | CSV + Parquet        | -      | POC      |
| **Analysis**     | Jupyter Notebooks    | -      | POC      |
| **Database**     | Oracle XE            | 21c    | MVP      |
| **BI**           | Power BI             | -      | MVP      |
| **Orquestração** | Apache Airflow       | -      | Produção |
| **API**          | FastAPI              | -      | Produção |

**Detalhes completos:** [ARCHITECTURE.md](docs/ARCHITECTURE.md#stack-técnico)

---

## Estrutura do Projeto

```
datasus-analytics/
├── docs/                    # Documentação (SSOT)
│   ├── ARCHITECTURE.md
│   ├── DATA_GUIDE.md
│   └── ROADMAP.md
├── src/                     # Código fonte
│   ├── extract/             # Extração DataSUS
│   ├── transform/           # Transformação dados
│   ├── load/                # Armazenamento dual-format
│   └── utils/               # Utilitários
├── data/                    # Dados (gitignored)
│   ├── raw/                 # Arquivos .dbc originais
│   └── processed/           # CSV + Parquet processados
├── tests/                   # Testes unitários
├── logs/                    # Logs aplicação (gitignored)
├── outputs/                 # Visualizações (gitignored)
├── requirements.txt         # Dependências Python
├── CHANGELOG.md             # Histórico versões
└── README.md                # Este arquivo
```

---

## Status Atual

- **Fase:** POC (Proof of Concept) - Dia 3/7
- **Dataset:** Acre (AC) - Janeiro/2024 (~2.000 registros)
- **Progresso:** Transform stage em andamento

### Milestones

- [x] M1: Setup Completo (02/12/2024)
- [ ] M2: POC Finalizada (07/12/2024) - PRÓXIMO
- [ ] M3: MVP Finalizado (31/12/2024)
- [ ] M4: Produção Finalizada (Q1 2025)

**Tracking detalhado:** [ROADMAP.md](docs/ROADMAP.md#milestones)

---

## Development Standards

- **Git Workflow:** Gitflow (develop → feature branches → main)
- **Code Style:** PEP 8
- **Testing:** pytest com cobertura >90% (fase MVP)

---

## Licença

- **Código:** MIT License
- **Dados:** Domínio público (Governo Brasileiro - DataSUS)
- **Documentação:** CC BY 4.0

---

## Disclaimer

Este é um projeto independente para aprendizado e portfólio profissional.

**Não possui vínculo oficial com:**

- Ministério da Saúde
- DATASUS
- FIOCRUZ
- Qualquer órgão governamental brasileiro

Os dados utilizados são de domínio público e acessíveis através do portal oficial do DataSUS:

> <https://datasus.saude.gov.br/>
