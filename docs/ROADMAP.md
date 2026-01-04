# ROADMAP

- **Sistema:** DataSUS Healthcare Analytics
- **Versão:** 0.2.6

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

- Processamento ETL de arquivos .dbc (formato proprietário DataSUS)
- Análise de KPIs operacionais hospitalares
- Visualização de métricas utilizando dados reais de internações do SUS

**Diferenciais técnicos:**

- Dados governamentais reais (~4k registros POC → 500k+ Produção)
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
│ Desenvolvedores      │ Integração sistemas        │ API REST            │
│                      │ Extensibilidade            │ Documentação        │
└──────────────────────┴────────────────────────────┴─────────────────────┘
```

### Diferenciais Técnicos

**Dados:**

- Fonte: SIH/DataSUS (Ministério da Saúde)
- Acesso: FTP via biblioteca pysus (Fiocruz/AlertaDengue)
- Volume: 4k (POC) → 30k (MVP) → 500k+ (Produção)
- Formato: .dbc (DBF comprimido, proprietário DataSUS)

**Arquitetura:**

- Evolução progressiva validada: POC → MVP → Produção
- Dual-format storage (CSV analytics + Parquet data lakes)
- Star schema dimensional modeling (MVP+)

**Domínio:**

- Sistema de saúde brasileiro (SUS)
- Tabelas SIGTAP, CID-10, especialidades médicas
- Dados públicos anonimizados

**Classificação do Projeto:**

- Data Engineering: ~65% (ETL, infra, orquestração)
- Data Analytics: ~30% (KPIs, dashboards, BI)
- Data Science: ~5% (EDA, estatística descritiva)

---

## Fases do Projeto

### Visão Macro

```
POC (Concluída)           MVP (3-4 semanas)        Produção (4-6 semanas)
┌────────────────┐       ┌──────────────────┐     ┌────────────────────┐
│ Validar        │       │ Produto          │     │ Sistema            │
│ Viabilidade    │──────>│ Funcional        │────>│ Production-Ready   │
│                │       │ Demonstrável     │     │ Robusto            │
│ - 1 estado     │       │                  │     │                    │
│ - 1 mês        │       │ - Multi-estado   │     │ - Multi-fonte      │
│ - CSV/Parquet  │       │ - 12 meses       │     │ - Orquestração     │
│ - KPIs básicos │       │ - Oracle DB      │     │ - API REST         │
│ - Jupyter      │       │ - Dashboard      │     │ - Monitoramento    │
│ - Testes 97%   │       │ - Testes 90%+    │     │ - Escala           │
└────────────────┘       └──────────────────┘     └────────────────────┘
      ✓
   GO para MVP         Decisão DEPLOY         Decisão SCALE
```

### Comparativo entre Fases

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ASPECTO          │ POC           │ MVP               │ PRODUÇÃO         │
├──────────────────┼───────────────┼───────────────────┼──────────────────┤
│ Duração          │ 4 semanas     │ 3-4 semanas       │ 4-6 semanas      │
│                  │               │                   │                  │
│ Dataset          │ AC Jan/2024   │ Multi-estado      │ Multi-UF         │
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
│ Testes           │ pytest 97%    │ pytest 90%+       │ pytest 95%+      │
│                  │               │                   │                  │
│ CI/CD            │ GitHub Actions│ GitHub Actions    │ Full pipeline    │
│                  │               │                   │                  │
│ Orquestração     │ Manual        │ cron              │ Airflow          │
│                  │               │                   │                  │
│ API              │ Inspector     │ Não               │ FastAPI + JWT    │
│                  │               │                   │                  │
│ Monitoramento    │ Logs básicos  │ Logs estruturados │ Prometheus +     │
│                  │               │                   │ Grafana          │
│                  │               │                   │                  │
│ Multi-fonte      │ Apenas SIH    │ Apenas SIH        │ SIH+CNES+SIM     │
└──────────────────┴───────────────┴───────────────────┴──────────────────┘
```

---

## POC - Detalhamento

**Status:** [x] CONCLUÍDA

- **Início:** 05/12/2025
- **Conclusão:** 30/12/2025
- **Decisão:** GO para MVP

### Objetivo

Validar viabilidade técnica de processar dados do DataSUS e gerar analytics úteis
**ANTES** de investir tempo no MVP.

**Pergunta central:** É viável processar dados reais do DataSUS e gerar
KPIs úteis para gestão hospitalar?

**Resposta:** SIM - Pipeline funcional, 4.315 registros processados, 5 KPIs implementados.

### Dataset POC

```
Estado:     Acre (AC)
Período:    Janeiro/2024
Tipo:       RD (Dados Reduzidos)
Registros:  4.315
Arquivo:    RDAC2401.dbc (~500 KB comprimido)
Output:     SIH_AC_202401.csv (~2.7 MB) + .parquet (~320 KB)
```

### Entregas POC

```
[1] Pipeline ETL Funcional
    [x] Extract: FTP DataSUS via pysus (Fiocruz)
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
    [x] Coverage 97% (128 passed, 1 skipped)
    [x] Testes unitários completos
    [x] Testes BDD API Inspector

[4] API Inspector (OpenDataSUS)
    [x] RN-API-001: package_show
    [x] RN-API-003: package_list
    [x] RN-API-004: Formatação terminal (TerminalFormatter)
    [x] RN-API-005: Headers HTTP

[5] KPIs Básicos (5)
    [x] Taxa de ocupação
    [x] Tempo médio de permanência (TMP)
    [x] Volume de internações
    [x] Receita total e ticket médio
    [x] Distribuição demográfica

[6] Análise Exploratória
    [x] Jupyter Notebook documentado
    [x] Insights sobre os dados
    [x] Qualidade e limitações

[7] Visualizações Estáticas
    [x] 6 gráficos PNG (300 DPI)
    [x] matplotlib
    [x] Prontos para apresentação

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

### Progresso Final POC

```
Infraestrutura:     [##########] 100%  (Pipeline, CI/CD, Testes)
Documentação:       [##########] 100%  (8 documentos SSOT)
Code Quality:       [##########] 100%  (Ruff, Mypy, Pre-commit)
Testes:             [##########]  97%  (128 passed, 1 skipped)
API Inspector:      [##########] 100%  (4/4 RNs implementadas)
KPIs:               [##########] 100%  (5 KPIs implementados)
EDA:                [##########] 100%  (Notebook executado)
Visualizações:      [##########] 100%  (6 gráficos)

TOTAL POC:          [##########] 100%
```

### Critérios Sucesso POC

```
[OBRIGATÓRIO - GO para MVP]
[x] Pipeline ETL sem erros críticos
[x] Validações passam (>90% registros válidos) → 100%
[x] CI/CD configurado e funcionando
[x] Testes automatizados >50% coverage → 97%
[x] KPIs calculados corretamente
[x] Documentação permite reprodução completa

[DESEJÁVEL - Nice to have]
[x] Taxa de perda dados <10% → 0%
[x] Código organizado e comentado
[x] Insights interessantes sobre dados
[x] Zero warnings Ruff/Mypy
[x] Visualizações com qualidade profissional
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
Estados:    Multi-estado (a definir)
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
    [ ] Manter coverage >90%
    [ ] Testes integração DB

[5] Segurança
    [ ] Bandit (security scan)
    [ ] Safety (dependency check)

[6] Independência pysus (opcional)
    [ ] Extração FTP própria
    [ ] Decode DBC próprio
    [ ] Compatibilidade Python 3.12+
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
    [ ] Logs estruturados
    [ ] Alertas 24/7
```

---

## Cronograma Consolidado

### Milestones

```
M1: [x] Setup Completo           05/12/2025
    - Ambiente Python 3.11
    - pysus instalado
    - Pipeline ETL funcional
    - Documentação inicial

M2: [x] CI/CD & Testes           27/12/2025
    - GitHub Actions
    - Codecov integration
    - VCR.py HTTP mocking
    - Coverage 61%
    - Documentação completa

M3: [x] POC Finalizada           30/12/2025
    - KPIs calculados
    - EDA notebook
    - Visualizações
    - Coverage 97%
    - Decisão GO para MVP

M4: [ ] Oracle Configurado       15/01/2026
    - Database instalado
    - Schema criado
    - Pipeline migrado

M5: [ ] MVP Release              31/03/2026
    - Dashboard funcional
    - Testes 90%+
    - Sistema demonstrável
```

---

## Critérios de Sucesso

### Técnicos - POC (Concluído)

```
[PIPELINE]
[x] Extract: pysus baixa DBC sem erros
[x] Transform: 100% registros válidos
[x] Load: CSV + Parquet salvos corretamente
[x] Performance: <1 min total

[QUALIDADE]
[x] Validações implementadas e passando
[x] Taxa perda: 0%
[x] KPIs corretos (validação manual)

[TESTES]
[x] pytest configurado
[x] Coverage 97% (128 testes)
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
[ ] Retry logic com backoff exponencial (MVP)
```

### RISCO-02: Dependência pysus / Python 3.11

```
Probabilidade: ALTA
Impacto:       MÉDIO
Status:        MONITORANDO

Situação:
- pysus não suporta Python 3.12+
- Biblioteca mantida pela Fiocruz (AlertaDengue)
- Sem previsão de atualização

Mitigação planejada (MVP):
[ ] Implementar extração FTP própria
[ ] Implementar decode DBC próprio (blast-dbf ou similar)
[ ] Eliminar dependência do pysus
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
[x] Dados reais apenas via FTP
```

### RISCO-04: Tempo Insuficiente POC

```
Probabilidade: MÉDIA
Impacto:       MÉDIO
Status:        RESOLVIDO

Resultado:
[x] POC concluída em 4 semanas
[x] Todos critérios obrigatórios atendidos
[x] Coverage superou meta (97% vs 50%)
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

**Última atualização:** 03/01/2026
