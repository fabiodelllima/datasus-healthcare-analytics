# ROADMAP

- **Sistema:** DataSUS Healthcare Analytics
- **Versão:** 0.2.2 POC

**Propósito:** Single Source of Truth para planejamento do projeto, incluindo
visão macro, fases detalhadas, cronograma, milestones e riscos.

---

## Índice

1. [Visão Geral do Projeto](#visão-geral-do-projeto)
2. [Fases do Projeto](#fases-do-projeto)
3. [POC - Detalhamento](#poc---detalhamento)
4. [MVP - Planejamento](#mvp---planejamento)
5. [Produção - Planejamento](#produção---planejamento)
6. [Cronograma Consolidado](#cronograma-consolidado)
7. [Critérios de Sucesso](#critérios-de-sucesso)
8. [Riscos e Mitigações](#riscos-e-mitigações)

---

## Convenções do Documento

**Símbolos de Status:**

- [x] Completo
- [~] Em andamento
- [ ] Planejado

**Categorização de Riscos:**

- Probabilidade: BAIXA | MÉDIA | ALTA
- Impacto: BAIXO | MÉDIO | ALTO

**Prioridades:**

- [OBRIGATÓRIO]: Critérios GO/NO-GO
- [DESEJÁVEL]: Melhorias não bloqueantes

---

## Visão Geral do Projeto

### Objetivo

Sistema de analytics para gestão hospitalar processando dados públicos do
Sistema de Informações Hospitalares (SIH/DataSUS) do Ministério da Saúde brasileiro.

**Escopo:**

- Processamento ETL
- Análise de KPIs operacionais
- Visualização de métricas hospitalares utilizando dados reais de internações do SUS

**Diferenciais técnicos:**

- Processamento de formato proprietário DBC (compressão específica DataSUS)
- Dados governamentais reais (~2k-500k+ registros dependendo da fase)
- Evolução arquitetural progressiva (POC → MVP → Produção)
- Stack completo: ETL, database, dashboard, orquestração, API

### Stakeholders e Use Cases

```
┌─────────────────────────────────────────────────────────────────────────┐
│ STAKEHOLDER          │ USE CASE                   │ REQUISITOS          │
├──────────────────────┼────────────────────────────┼─────────────────────┤
│ Gestores             │ Análise ocupação leitos    │ KPIs tempo real     │
│ Hospitalares         │ Otimização recursos        │ Dashboards          │
│                      │                            │                     │
│ Analistas            │ Estudos epidemiológicos    │ Dados históricos    │
│ Saúde Pública        │ Análise regional           │ Multi-UF            │
│                      │                            │                     │
│ DataSUS/Ministério   │ Fonte dados públicos       │ Uso ético           │
│ da Saúde             │ Transparência SUS          │ Conformidade LGPD   │
│                      │                            │                     │
│ Desenvolvedores      │ Integração sistemas        │ API REST            │
│                      │ Extensibilidade            │ Documentação        │
└──────────────────────┴────────────────────────────┴─────────────────────┘
```

### Diferenciais Técnicos

**Dados:**

- Fonte governamental oficial (DataSUS/Ministério da Saúde)
- Volume real: 2k (POC) → 30k (MVP) → 500k+ (Produção)
- Formato proprietário DBC (descompressão via pyreaddbc)

**Arquitetura:**

- Evolução progressiva validada: POC → MVP → Produção
- Dual-format storage (CSV analytics + Parquet data lakes)
- Star schema dimensional modeling (MVP+)

**Domínio:**

- Sistema de saúde brasileiro (SUS)
- Tabelas SIGTAP, CID-10, especialidades médicas
- Conformidade LGPD (dados públicos anonimizados)

**Classificação do Projeto:**

- Data Engineering: ~65% (ETL, infra, orquestração)
- Data Analytics: ~30% (KPIs, dashboards, BI)
- Data Science: ~5% (EDA, estatística descritiva)

---

## Fases do Projeto

### Visão Macro

```
POC (Em Andamento)        MVP (3-4 semanas)        Produção (4-6 semanas)
┌────────────────┐       ┌──────────────────┐     ┌────────────────────┐
│ Validar        │       │ Produto          │     │ Sistema            │
│ Viabilidade    │──────>│ Funcional        │────>│ Production-Ready   │
│                │       │ Demonstrável     │     │ Robusto            │
│ - 1 estado     │       │                  │     │                    │
│ - 1 mês        │       │ - 2 estados      │     │ - Multi-fonte      │
│ - CSV/Parquet  │       │ - 12 meses       │     │ - Orquestração     │
│ - KPIs básicos │       │ - Oracle DB      │     │ - API REST         │
│ - Jupyter      │       │ - Dashboard      │     │ - Monitoramento    │
│ - Testes 61%+  │       │ - Testes 90%+    │     │ - Multi-estado     │
└────────────────┘       └──────────────────┘     └────────────────────┘

Decisão GO/NO-GO       Decisão DEPLOY         Decisão SCALE
```

### Comparativo entre Fases

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ASPECTO          │ POC           │ MVP               │ PRODUÇÃO         │
├──────────────────┼───────────────┼───────────────────┼──────────────────┤
│ Duração          │ 2-3 semanas   │ 3-4 semanas       │ 4-6 semanas      │
│                  │               │                   │                  │
│ Dataset          │ AC Jan/2024   │ AC/ES 2024        │ Multi-UF         │
│                  │ 1 mês         │ 12 meses          │ Múltiplos anos   │
│                  │               │                   │                  │
│ Registros        │ ~4k           │ ~20-30k           │ 500k+            │
│                  │               │                   │                  │
│ Database         │ Arquivos      │ Oracle XE 21c     │ Oracle/          │
│                  │ CSV/Parquet   │                   │ PostgreSQL       │
│                  │               │                   │                  │
│ Visualização     │ Jupyter       │ Power BI ou       │ Dashboard        │
│                  │ matplotlib    │ Streamlit         │ production       │
│                  │               │                   │                  │
│ KPIs             │ 5 básicos     │ 10+ completos     │ 15+ avançados    │
│                  │               │                   │                  │
│ Testes           │ pytest 61%+   │ pytest 90%+       │ pytest 95%+      │
│                  │               │                   │                  │
│ CI/CD            │ GitHub Actions│ GitHub Actions    │ Full pipeline    │
│                  │               │                   │                  │
│ Orquestração     │ Manual        │ cron              │ Airflow          │
│                  │               │                   │                  │
│ API              │ Inspector     │ Não               │ FastAPI + JWT    │
│                  │               │                   │                  │
│ Monitoramento    │ Logs básicos  │ Logs estruturados │ Prometheus +     │
│                  │               │                   │ Grafana + ELK    │
│                  │               │                   │                  │
│ Multi-fonte      │ Apenas SIH    │ Apenas SIH        │ SIH+CNES+SIM     │
└──────────────────┴───────────────┴───────────────────┴──────────────────┘
```

---

## POC - Detalhamento

**Status:** [~] EM ANDAMENTO

- **Início:** 01/12/2025
- **Previsão conclusão:** 31/12/2025

### Objetivo

Validar viabilidade técnica de processar DataSUS e gerar analytics úteis
**ANTES** de investir tempo no MVP.

**Pergunta central:** É viável processar dados reais do DataSUS e gerar
KPIs úteis para gestão hospitalar?

### Dataset POC

```
Estado:     Acre (AC)
Período:    Janeiro/2024
Tipo:       RD (Dados Reduzidos)
Registros:  ~4.300
Arquivo:    RDAC2401.dbc (~500 KB comprimido, ~2.7 MB CSV)
```

### Entregas POC

```
[1] Pipeline ETL Funcional
    [x] Extract: pysus + FTP DataSUS
    [x] Transform: limpeza + validação + enriquecimento
    [x] Load: CSV + Parquet dual-format

[2] Code Quality & CI/CD
    [x] Ruff (linter + formatter)
    [x] Mypy (type checking)
    [x] Pre-commit hooks
    [x] GitHub Actions CI/CD
    [x] Codecov integration
    [x] VCR.py (HTTP mocking)

[3] Testes Automatizados
    [x] pytest configurado
    [x] pytest-bdd (BDD scenarios)
    [x] Coverage 68% (76 passed, 1 skipped)
    [x] Testes unitários Transform
    [x] Testes BDD API Inspector

[4] API Inspector (OpenDataSUS)
    [x] RN-API-001: package_show
    [x] RN-API-003: package_list
    [x] RN-API-005: Headers HTTP
    [~] RN-API-004: Formatação output (parcial)

[5] KPIs Básicos (5) - CONCLUÍDO
    [x] Taxa de ocupação
    [x] Tempo médio de permanência (TMP)
    [x] Volume de internações
    [x] Receita total e ticket médio
    [x] Distribuição demográfica

[6] Análise Exploratória
    [ ] Jupyter Notebook documentado
    [ ] Insights sobre os dados
    [ ] Qualidade e limitações

[7] Visualizações Estáticas
    [ ] 4-6 gráficos PNG (300 DPI)
    [ ] matplotlib + seaborn
    [ ] Prontos para apresentação

[8] Documentação
    [x] README.md (entry point)
    [x] ARCHITECTURE.md (stack + ADRs)
    [x] DATA_GUIDE.md (dicionário + ETL)
    [x] BUSINESS_RULES.md (regras negócio)
    [x] API.md (integrações)
    [x] METHODOLOGY.md (workflow dev)
    [x] TOOLING.md (ferramentas CI/CD)
    [x] ROADMAP.md (este arquivo)
    [x] CHANGELOG.md (histórico)
```

### Progresso Atual

```
Infraestrutura:     [##########] 100%  (Pipeline, CI/CD, Testes)
Documentação:       [##########] 100%  (Todos docs criados)
Code Quality:       [##########] 100%  (Ruff, Mypy, Pre-commit)
Testes:             [######----]  61%  (53 passed, meta 90%)
API Inspector:      [########--]  80%  (3/4 RNs implementadas)
KPIs:               [----------]   0%  (Pendente)
EDA:                [----------]   0%  (Pendente)
Visualizações:      [----------]   0%  (Pendente)

TOTAL POC:          [######----]  60%
```

### Critérios Sucesso POC

```
[OBRIGATÓRIO - GO para MVP]
[x] Pipeline ETL sem erros críticos
[x] Validações passam (>90% registros válidos) → 100%
[x] CI/CD configurado e funcionando
[x] Testes automatizados >50% coverage → 61%
[ ] KPIs calculados corretamente
[ ] Documentação permite reprodução completa

[DESEJÁVEL - Nice to have]
[x] Taxa de perda dados <10% → 0%
[x] Código organizado e comentado
[ ] Insights interessantes sobre dados
[x] Zero warnings Ruff/Mypy
[ ] Visualizações com qualidade profissional
```

---

## MVP - Planejamento

**Status:** [ ] PLANEJADO

- **Início previsto:** Janeiro 2026
- **Duração:** 3-4 semanas

### Objetivo

Sistema funcional completo e demonstrável com database, dashboard e testes
automatizados 90%+.

### Dataset MVP

```
Estados:    Acre (AC) + Espírito Santo (ES)
Período:    Janeiro-Dezembro 2024 (12 meses)
Registros:  ~20.000-30.000
Database:   Oracle XE 21c
```

### Entregas MVP

```
[1] Oracle Database
    [ ] Oracle XE 21c instalado
    [ ] Schema star schema
    [ ] Views materializadas para KPIs

[2] Pipeline ETL Adaptado
    [ ] Extract multi-mês
    [ ] Load Oracle (cx_Oracle)
    [ ] Agendamento cron

[3] Dashboard Interativo
    [ ] Power BI ou Streamlit
    [ ] 3-5 páginas
    [ ] 10+ KPIs

[4] Testes 90%+
    [ ] Coverage 90%+
    [ ] Testes integração DB

[5] Segurança
    [ ] Bandit (security scan)
    [ ] Safety (dependency check)
```

---

## Produção - Planejamento

**Status:** [ ] FUTURO

- **Início previsto:** Q2 2026
- **Duração:** 4-6 semanas

### Entregas Produção

```
[1] Multi-Fonte
    [ ] SIH + CNES + SIM integrados
    [ ] Data Warehouse unificado

[2] Orquestração
    [ ] Apache Airflow DAGs
    [ ] Alertas automáticos

[3] API REST
    [ ] FastAPI + JWT
    [ ] Rate limiting
    [ ] Documentação OpenAPI

[4] Monitoramento
    [ ] Prometheus + Grafana
    [ ] ELK Stack (logs)
    [ ] Alertas 24/7
```

---

## Cronograma Consolidado

### Milestones

```
M1: [x] Setup Completo           05/12/2025
    - Ambiente Python 3.11 ✓
    - pysus instalado ✓
    - Pipeline ETL funcional ✓
    - Documentação inicial ✓

M2: [x] CI/CD & Testes           27/12/2025
    - GitHub Actions ✓
    - Codecov integration ✓
    - VCR.py HTTP mocking ✓
    - Coverage 61% ✓
    - Documentação completa ✓

M3: [ ] POC Finalizada           31/12/2025  <- PRÓXIMO
    - KPIs calculados
    - EDA notebook
    - Visualizações
    - Decisão GO/NO-GO

M4: [ ] Oracle Configurado       15/01/2026
    - Database instalado
    - Schema criado
    - Pipeline migrado

M5: [ ] MVP Release              31/03/2026
    - Dashboard funcional
    - Testes 90%+
    - Sistema demonstrável
```

### Próximas Tarefas POC

```
1. [ ] Implementar cálculo dos 5 KPIs básicos
2. [ ] Criar Jupyter Notebook EDA
3. [ ] Gerar visualizações matplotlib
4. [ ] Aumentar coverage para 90%
5. [ ] Implementar RN-API-004 (fancy output)
6. [ ] Decisão GO/NO-GO para MVP
```

---

## Critérios de Sucesso

### Técnicos - POC

```
[PIPELINE]
[x] Extract: pysus baixa DBC sem erros
[x] Transform: 90%+ registros válidos → 100%
[x] Load: CSV + Parquet salvos corretamente
[x] Performance: <10 min total

[QUALIDADE]
[x] Validações implementadas e passando
[x] Taxa perda <10% → 0%
[ ] KPIs corretos (validação manual)

[TESTES]
[x] pytest configurado
[x] Coverage >50% → 61%
[ ] Coverage 90% (meta final)
```

### Técnicos - MVP

```
[DATABASE]
[ ] Oracle XE instalado
[ ] Schema normalizado
[ ] Performance queries <3s

[DASHBOARD]
[ ] Interativo
[ ] 10+ KPIs
[ ] Design profissional

[TESTES]
[ ] 90%+ coverage
[ ] Zero testes falhando
```

---

## Riscos e Mitigações

### RISCO-01: FTP DataSUS Instável

```
Probabilidade: MÉDIA
Impacto:       ALTO
Status:        MITIGADO

Mitigação implementada:
[x] VCR.py para testes (evita dependência FTP em CI)
[x] Cache local arquivos baixados
[ ] Retry logic com tenacity (MVP)
```

### RISCO-02: Python 3.12+ Incompatível com pysus

```
Probabilidade: ALTA
Impacto:       MÉDIO
Status:        RESOLVIDO

Solução:
[x] Usar Python 3.11.x
[x] Documentar versão obrigatória
```

### RISCO-03: API OpenDataSUS Limitações

```
Probabilidade: ALTA (confirmado)
Impacto:       BAIXO
Status:        DOCUMENTADO

Descobertas:
[x] resource_search desabilitado (409)
[x] SIH tradicional não disponível via API
[x] Apenas metadados via CKAN API
[x] Dados reais apenas via FTP/pysus
```

### RISCO-04: Tempo Insuficiente POC

```
Probabilidade: MÉDIA
Impacto:       MÉDIO
Status:        MONITORANDO

Mitigação:
[x] Priorizar entregas core (pipeline, testes, docs)
[x] CI/CD implementado (acelera desenvolvimento)
[ ] KPIs e EDA pendentes
```

---

## Referências

- [README.md](../README.md) - Entry point
- [ARCHITECTURE.md](ARCHITECTURE.md) - Stack técnico
- [DATA_GUIDE.md](DATA_GUIDE.md) - Dicionário dados
- [BUSINESS_RULES.md](BUSINESS_RULES.md) - Regras negócio
- [API.md](API.md) - Integrações API
- [METHODOLOGY.md](METHODOLOGY.md) - Workflow dev
- [TOOLING.md](TOOLING.md) - Ferramentas CI/CD

---

**Última atualização:** 27/12/2025
