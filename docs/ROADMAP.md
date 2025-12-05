# ROADMAP

- **Sistema:** DataSUS Healthcare Analytics
- **Versão:** 1.0.0 POC

**Propósito:** Single Source of Truth para planejamento do projeto, incluindo
visão macro, fases detalhadas, cronograma, milestones e riscos.

---

## Índice

1. [Visão Geral do Projeto](#visão-geral-do-projeto)
2. [Fases do Projeto](#fases-do-projeto)
3. [POC - Detalhamento Dia-a-Dia](#poc---detalhamento-dia-a-dia)
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
POC (1 semana)            MVP (3-4 semanas)        Produção (4-6 semanas)
┌────────────────┐       ┌──────────────────┐     ┌────────────────────┐
│ Validar        │       │ Produto          │     │ Sistema            │
│ Viabilidade    │──────>│ Funcional        │────>│ Production-Ready   │
│                │       │ Demonstrável     │     │ Robusto            │
│ - 1 estado     │       │                  │     │                    │
│ - 1 mês        │       │ - 1 estado       │     │ - Multi-fonte      │
│ - CSV/Parquet  │       │ - 12 meses       │     │ - Orquestração     │
│ - KPIs básicos │       │ - Oracle DB      │     │ - API REST         │
│ - Jupyter      │       │ - Dashboard      │     │ - Monitoramento    │
│                │       │ - Testes 87%+    │     │ - Multi-estado     │
└────────────────┘       └──────────────────┘     └────────────────────┘

Decisão GO/NO-GO       Decisão DEPLOY         Decisão SCALE
```

### Comparativo entre Fases

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ASPECTO          │ POC           │ MVP               │ PRODUÇÃO         │
├──────────────────┼───────────────┼───────────────────┼──────────────────┤
│ Duração          │ 1 semana      │ 3-4 semanas       │ 4-6 semanas      │
│                  │               │                   │                  │
│ Dataset          │ AC Jan/2024   │ AC/ES 2024        │ Multi-UF         │
│                  │ 1 mês         │ 12 meses          │ Múltiplos anos   │
│                  │               │                   │                  │
│ Registros        │ ~2k           │ ~20-30k           │ 500k+            │
│                  │               │                   │                  │
│ Database         │ Arquivos      │ Oracle XE 21c     │ Oracle/          │
│                  │ CSV/Parquet   │                   │ PostgreSQL       │
│                  │               │                   │                  │
│ Visualização     │ Jupyter       │ Power BI ou       │ Dashboard        │
│                  │ matplotlib    │ Streamlit         │ production       │
│                  │               │                   │                  │
│ KPIs             │ 5 básicos     │ 10+ completos     │ 15+ avançados    │
│                  │               │                   │                  │
│ Testes           │ Manual        │ pytest 87%+       │ pytest 95%+      │
│                  │               │                   │                  │
│ CI/CD            │ Não           │ GitHub Actions    │ Full pipeline    │
│                  │               │                   │                  │
│ Orquestração     │ Manual        │ cron              │ Airflow          │
│                  │               │                   │                  │
│ API              │ Não           │ Não               │ FastAPI + JWT    │
│                  │               │                   │                  │
│ Monitoramento    │ Logs básicos  │ Logs estruturados │ Prometheus +     │
│                  │               │                   │ Grafana + ELK    │
│                  │               │                   │                  │
│ Multi-fonte      │ Apenas SIH    │ Apenas SIH        │ SIH+CNES+SIM     │
└──────────────────┴───────────────┴───────────────────┴──────────────────┘
```

### Technology Stack Evolution

**POC Phase - Foundation:**

- ETL: Python 3.11 + pysus library
- Storage: Dual-format (CSV + Parquet)
- Analysis: Jupyter Notebooks + pandas
- Visualization: matplotlib + seaborn

**MVP Phase - Scale:**

- Database: Oracle XE 21c (12GB capacity)
- BI: Power BI Desktop
- Testing: pytest + coverage >87%
- CI/CD: GitHub Actions

**Production Phase - Enterprise:**

- Orchestration: Apache Airflow
- API: FastAPI + JWT authentication
- Monitoring: Prometheus + Grafana + ELK
- Multi-source: SIH + CNES + SIM integration

---

## Estratégia de Dataset por Fase

### Critérios de Seleção de Estados

**Fatores considerados:**

- Volume de registros (progressão controlada)
- Qualidade dos dados (completude, consistência)
- Diversidade geográfica (diferentes regiões)
- Complexidade hospitalar (hospitais secundários vs terciários)
- Limites técnicos (Oracle XE 12GB, tempo processamento)

---

### POC - Acre (AC)

**Volume:** ~2.000 registros/mês

**Justificativa técnica:**

```
- [+] Menor estado em volume absoluto (processamento em segundos)
- [+] Permite iteração rápida durante desenvolvimento inicial
- [+] Validação de viabilidade técnica sem overhead computacional
- [+] Teste de conectividade FTP DataSUS e descompressão DBC
```

**Justificativa estratégica:**

```
- [+] Foco em validar pipeline ETL, não análise estatística
- [+] Baseline de complexidade mínima
- [+] Permite identificar problemas arquiteturais cedo
```

**Limitações conhecidas:**

```
- [-] Amostra pequena não permite análises estatísticas robustas
- [-] Pode não representar complexidade de estados maiores
- [-] Taxa de dados faltantes pode ser maior (~10-15%)
```

---

### MVP - Acre + Espírito Santo (AC + ES)

**Volume:** ~20-30k registros totais (12 meses cada estado)

**Justificativa técnica:**

```
- [+] Dentro dos limites Oracle XE (12GB user data)
- [+] Tempo de processamento gerenciável (~5-10 minutos)
- [+] ES tem melhor qualidade de dados que AC (taxa completude ~85-90%)
- [+] Progressão controlada: 2k → 30k (crescimento 15x)
- [+] Demonstra capacidade multi-UF sem overhead excessivo
- [+] Volume suficiente para KPIs estatisticamente significativos (n > 20k)
```

**Justificativa estratégica:**

```
- [+] Diversidade geográfica: Norte (AC) + Sudeste (ES)
- [+] Complexidade hospitalar variada:
  - AC: Hospitais menores, atendimento básico predominante
  - ES: Mix de hospitais secundários e terciários
- [+] Demonstra flexibilidade do pipeline para diferentes perfis estaduais
- [+] Permite comparações regionais (Norte vs Sudeste)
```

**Justificativa operacional:**

```
- [+] Portfolio demonstra capacidade com dados reais em escala realista
- [+] Volume comparável a um hospital de médio porte (~30k internações/ano)
- [+] Suficiente para demonstrar todos os KPIs principais
```

**Por que NÃO escolhemos estados maiores (SP, PR, RS, SC):**

```
- [-] SP (~200k/mês): Oracle XE não suporta volume
- [-] PR (~100k/mês): Tempo processamento excessivo (>30 min)
- [-] RS (~120k/mês): Risco saturar recursos no MVP
- [-] SC (~80k/mês): Próximo dos limites, pouco headroom
```

**Alternativas consideradas:**

```
- AC + SC: Volume maior (~80k), mas próximo do limite Oracle XE
- AC + PR: Volume muito grande para MVP, deixado para Produção
- Apenas AC (12 meses): Volume muito pequeno (~24k), baixa diversidade
```

---

### Produção - Multi-UF (SP, RJ, MG, PR, RS)

**Volume:** 500k+ registros (múltiplos estados, 12 meses)

**Justificativa técnica:**

```
- [+] Demonstra capacidade de escalar para volumes hospitalares reais
- [+] Requer infraestrutura robusta (Airflow, FastAPI, monitoramento)
- [+] Múltiplas fontes de dados (SIH + CNES + SIM)
```

**Justificativa estratégica:**

```
- [+] Estados com maior complexidade hospitalar (SP, RJ, MG)
- [+] Representa ~40% das internações brasileiras
- [+] Sistema production-ready para uso real em ambiente hospitalar
```

**Progressão lógica:**

```
POC:      2k registros      (1 estado, 1 mês)       → Viabilidade
MVP:      30k registros     (2 estados, 12 meses)   → Demonstração
Produção: 500k+ registros   (5+ estados, 12 meses)  → Sistema real
          ↓                  ↓                        ↓
        Crescimento 15x    Crescimento 15x         Escala produção
```

---

## POC - Detalhamento Dia-a-Dia

**Status:**

- [x] EM ANDAMENTO
- **Início:** 01/12/2024
- **Prazo:** 07/12/2024 (7 dias)

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
Registros:  ~2.000
Arquivo:    RDAC2401.dbc (~500 KB comprimido, ~1.5 MB CSV)
```

**Justificativa da Escolha:**

- Estado pequeno: dataset gerenciável
- Processamento rápido: 2-5 minutos total
- Menos complexidade: foco em pipeline não escala

### Entregas POC

```
[1] Pipeline ETL Funcional
    [x] Extract: pysus + FTP DataSUS
    [x] Transform: limpeza + validação + enriquecimento
    [ ] Load: CSV + Parquet dual-format

[2] KPIs Básicos (5)
    [ ] Taxa de ocupação
    [ ] Tempo médio de permanência (TMP)
    [ ] Volume de internações
    [ ] Receita total e ticket médio
    [ ] Distribuição demográfica (idade, sexo)

[3] Visualizações Estáticas
    [ ] 4-6 gráficos PNG (300 DPI)
    [ ] matplotlib + seaborn
    [ ] Prontos para apresentação

[4] Análise Exploratória
    [ ] Jupyter Notebook documentado
    [ ] Insights sobre os dados
    [ ] Qualidade e limitações

[5] Documentação Completa
    [x] README.md (entry point)
    [x] ARCHITECTURE.md (stack + ADRs)
    [x] DATA_GUIDE.md (dicionário + regras + ETL)
    [x] ROADMAP.md (este arquivo)
```

### Timeline POC (Dia-a-Dia)

```
┌────────────────────────────────────────────────────────────────────────┐
│ DIA │ DATA       │ ATIVIDADES                        │ STATUS          │
├─────┼────────────┼───────────────────────────────────┼─────────────────┤
│ 1   │ 01/12/2024 │ Setup ambiente + Pesquisa         │ [x] COMPLETO    │
│ Dom │            │ - Python 3.11 + venv              │                 │
│     │            │ - Pesquisa DataSUS/pysus          │                 │
│     │            │ - Estrutura diretórios            │                 │
│     │            │                                   │                 │
│ 2   │ 02/12/2024 │ Extract + Documentação Inicial    │ [x] COMPLETO    │
│ Seg │            │ - pysus download AC Jan/2024      │                 │
│     │            │ - Decode DBC -> DataFrame         │                 │
│     │            │ - README.md, ARCHITECTURE.md      │                 │
│     │            │                                   │                 │
│ 3   │ 03/12/2024 │ Transform + Docs Consolidação     │ [x] COMPLETO    │
│ Ter │            │ - Limpeza dados                   │                 │
│     │            │ - Validações                      │                 │
│     │            │ - Enriquecimento                  │                 │
│     │            │ - DATA_GUIDE.md, ROADMAP.md       │                 │
│     │            │                                   │                 │
│ 4   │ 04/12/2024 │ Load + Testes                     │ [ ] PLANEJADO   │
│ Qua │            │ - Salvar CSV + Parquet            │                 │
│     │            │ - Testar leitura                  │                 │
│     │            │ - Validar metadata                │                 │
│     │            │                                   │                 │
│ 5   │ 05/12/2024 │ Analytics + KPIs                  │ [ ] PLANEJADO   │
│ Qui │            │ - Calcular 5 KPIs                 │                 │
│     │            │ - Jupyter Notebook                │                 │
│     │            │ - Análise exploratória            │                 │
│     │            │                                   │                 │
│ 6   │ 06/12/2024 │ Visualizações                     │ [ ] PLANEJADO   │
│ Sex │            │ - 4-6 gráficos matplotlib         │                 │
│     │            │ - Exportar PNG 300 DPI            │                 │
│     │            │ - Formatação apresentação         │                 │
│     │            │                                   │                 │
│ 7   │ 07/12/2024 │ Revisão + Decisão GO/NO-GO        │ [ ] PLANEJADO   │
│ Sáb │            │ - Review documentação             │                 │
│     │            │ - Validar entregas                │                 │
│     │            │ - Decisão: avançar MVP ou revisar │                 │
└─────┴────────────┴───────────────────────────────────┴─────────────────┘
```

### Critérios Sucesso POC

```
[OBRIGATÓRIO - GO para MVP]
[x] Pipeline ETL sem erros críticos
[x] Validações passam (>90% registros válidos)
[ ] KPIs calculados corretamente
[ ] Visualizações com qualidade profissional
[ ] Documentação permite reprodução
[ ] Tempo processamento <10 minutos

[DESEJÁVEL - Nice to have]
[ ] Taxa de perda dados <10%
[ ] Código organizado e comentado
[ ] Insights interessantes sobre dados
[ ] Zero warnings Python
```

### Decisão GO/NO-GO

**Se GO (critérios obrigatórios OK):**

- Avançar para MVP (Janeiro 2025)
- Começar setup Oracle Database
- Expandir para 12 meses dados

**Se NO-GO (critérios não atendidos):**

- Revisar arquitetura pipeline
- Considerar dados sintéticos
- Reavaliar viabilidade projeto

### Limitações POC

```
[-] Apenas 1 estado (AC) - não representa Brasil
[-] Apenas 1 mês - não captura sazonalidade
[-] Apenas SUS - não inclui privado
[-] Sem database - apenas arquivos
[-] Gráficos estáticos - sem interatividade
[-] Sem testes - validação manual
[-] Sem CI/CD - deploy manual
```

---

## MVP - Planejamento

**Status:**

- [ ] PLANEJADO
- **Início previsto:** 08/12/2024
- **Prazo:** 31/12/2024 (3-4 semanas)

### Objetivo

Sistema funcional completo e demonstrável com database, dashboard e testes
automatizados.

**Pergunta central:** Sistema funciona em escala maior e gera valor real?

### Dataset MVP

```
Estado:     Acre (AC) ou Espírito Santo (ES)
Período:    Janeiro-Dezembro 2024 (12 meses)
Registros:  ~20.000-30.000
Database:   Oracle XE 21c
```

**Justificativa ES alternativa:**

- Maior que AC mas menor que SP
- ~20k registros/mês (balanceado)
- Testa escala sem overhead

### Entregas MVP

```
[1] Oracle Database
    [ ] Oracle XE 21c instalado e configurado
    [ ] Schema star schema (fatos + dimensões)
    [ ] Tabelas criadas com constraints
    [ ] Views materializadas para KPIs
    [ ] Índices otimizados

[2] Pipeline ETL Adaptado
    [ ] Extract multi-mês (loop 12 meses)
    [ ] Transform otimizado (performance)
    [ ] Load Oracle (cx_Oracle)
    [ ] Agendamento cron
    [ ] Logs estruturados

[3] Dashboard Interativo
    [ ] Power BI Desktop ou Streamlit
    [ ] 3-5 páginas navegáveis
    [ ] Filtros interativos (período, especialidade)
    [ ] 10+ KPIs
    [ ] Drill-down capacidade

[4] Testes Automatizados
    [ ] pytest configurado
    [ ] Testes unitários ETL
    [ ] Testes integração database
    [ ] Coverage 87%+ (pytest-cov)

[5] CI/CD
    [ ] GitHub Actions configurado
    [ ] Lint (flake8) automático
    [ ] Tests em cada commit
    [ ] Build artifacts

[6] Data Dictionary Completo
    [ ] Todos campos documentados
    [ ] Relacionamentos explicados
    [ ] Exemplos de queries
```

### Timeline MVP (Semanal)

```
┌────────────────────────────────────────────────────────────────────────┐
│ SEMANA │ DATAS          │ FOCO                        │ ENTREGAS       │
├────────┼────────────────┼─────────────────────────────┼────────────────┤
│ 1      │ 08-14/12/2024  │ Database + Infraestrutura   │ Oracle setup   │
│        │                │ - Instalar Oracle XE        │ Schema criado  │
│        │                │ - Criar schema, tabelas     │ Pipeline migra │
│        │                │ - Migrar pipeline para DB   │                │
│        │                │                             │                │
│ 2      │ 15-21/12/2024  │ Expansão Dados + KPIs       │ 12 meses load  │
│        │                │ - Processar 12 meses        │ 10 KPIs impl.  │
│        │                │ - Implementar 5 KPIs novos  │ Queries SQL    │
│        │                │ - Queries SQL complexas     │                │
│        │                │                             │                │
│ 3      │ 22-28/12/2024  │ Dashboard + Visualização    │ Dashboard func │
│        │                │ - Configurar Power BI       │ 3-5 páginas    │
│        │                │ - Criar 3-5 páginas         │ Filtros OK     │
│        │                │ - Implementar filtros       │                │
│        │                │                             │                │
│ 4      │ 29-31/12/2024  │ Qualidade + Documentação    │ Testes 87%+    │
│        │                │ - Testes unitários pytest   │ CI/CD config   │
│        │                │ - CI/CD GitHub Actions      │ Docs completa  │
│        │                │ - Documentação técnica      │                │
└────────┴────────────────┴─────────────────────────────┴────────────────┘
```

### Critérios Sucesso MVP

```
[OBRIGATÓRIO]
[ ] Database Oracle operacional
[ ] Pipeline processa 12 meses sem erros
[ ] Dashboard funcional e apresentável
[ ] Testes 87%+ coverage
[ ] CI/CD automático funcionando
[ ] Documentação técnica completa
[ ] Tempo processamento <30 min (12 meses)

[DESEJÁVEL]
[ ] Dashboard Power BI (não Streamlit)
[ ] Performance queries <3s
[ ] Zero critical bugs
[ ] Documentação de deployment completa
```

---

## Produção - Planejamento

**Status:**

- [ ] FUTURO
- **Início previsto:** Q1 2025
- **Prazo:** 4-6 semanas

### Objetivo

Sistema robusto production-ready com multi-fonte, orquestração, API e
monitoramento completo.

**Pergunta central:** Sistema está pronto para uso real em hospital?

### Dataset Produção

```
Estados:    Múltiplos (até 27 UFs)
Fontes:     SIH + CNES + SIM
Período:    Múltiplos anos
Registros:  500.000+
```

### Entregas Produção

```
[1] Multi-Fonte Integrada
    [ ] SIH: Internações hospitalares
    [ ] CNES: Cadastro estabelecimentos
    [ ] SIM: Sistema informações mortalidade
    [ ] Data Warehouse star schema unificado

[2] Orquestração Airflow
    [ ] DAGs para cada fonte
    [ ] Agendamento automático
    [ ] Retry + error handling
    [ ] Alertas (Slack/email)

[3] API REST
    [ ] FastAPI implementado
    [ ] Autenticação JWT
    [ ] Rate limiting
    [ ] Documentação OpenAPI (Swagger)

[4] Monitoramento Completo
    [ ] Prometheus + Grafana
    [ ] ELK Stack (logs)
    [ ] Alertas automáticos (PagerDuty/Slack)
    [ ] Dashboards operacionais
```

### Timeline Produção (Semanal)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ SEMANAS │ FOCO                              │ ENTREGAS                  │
├─────────┼───────────────────────────────────┼───────────────────────────┤
│ 1-2     │ Multi-Fonte                       │ CNES + SIM integrados     │
│         │ - Integrar CNES, SIM              │ DW unificado              │
│         │ - Data Warehouse unificado        │                           │
│         │                                   │                           │
│ 3-4     │ Escalabilidade                    │ Airflow funcionando       │
│         │ - Múltiplos estados               │ Multi-estado OK           │
│         │ - Airflow orquestração            │ Performance otimizada     │
│         │ - Otimizações performance         │                           │
│         │                                   │                           │
│ 5-6     │ API + Monitoramento               │ API REST deployment       │
│         │ - API REST FastAPI                │ Monitoramento 24/7        │
│         │ - Prometheus + Grafana            │ Documentação final        │
│         │ - Documentação completa           │                           │
└─────────┴───────────────────────────────────┴───────────────────────────┘
```

---

## Cronograma Consolidado

### Visão Trimestral

```
Q4 2024 - Dezembro
┌──────────────────────────────────────────────────────────────────┐
│ SEMANA  │ 02-08 │ 09-15 │ 16-22 │ 23-29 │ 30-31 │                │
│ FASE    │ POC   │ MVP   │ MVP   │ MVP   │ MVP   │                │
│ FOCO    │ Setup │ DB    │ Dados │ Dash  │ Test  │                │
│         │ ETL   │ Infra │ KPIs  │ board │ CI/CD │                │
└──────────────────────────────────────────────────────────────────┘

Q1 2025 - Janeiro-Março
┌──────────────────────────────────────────────────────────────────┐
│ MÊS     │ Janeiro       │ Fevereiro     │ Março         │        │
│ FASE    │ Produção      │ Produção      │ Produção      │        │
│ FOCO    │ Multi-fonte   │ Escalabilidade│ API + Monitor │        │
│         │ CNES + SIM    │ Airflow       │ FastAPI       │        │
└──────────────────────────────────────────────────────────────────┘

Q2 2025 - Abril-Junho
┌──────────────────────────────────────────────────────────────────┐
│ MÊS     │ Abril         │ Maio          │ Junho         │        │
│ FASE    │ Produção Beta │ Ajustes       │ Release       │        │
│ FOCO    │ Testes real   │ Bug fixes     │ Documentation │        │
│         │ Feedback      │ Performance   │ Deploy final  │        │
└──────────────────────────────────────────────────────────────────┘
```

### Milestones

```
M1: [x] Setup Completo           02/12/2024
    - Ambiente Python 3.11
    - pysus instalado
    - Estrutura docs/

M2: [ ] POC Finalizada           07/12/2024  <- PRÓXIMO
    - Pipeline ETL funcional
    - 5 KPIs calculados
    - Documentação completa
    - Decisão GO/NO-GO

M3: [ ] Oracle Configurado       15/12/2024
    - Database instalado
    - Schema criado
    - Pipeline migrado

M4: [ ] Dashboard Funcional      28/12/2024
    - Power BI 3-5 páginas
    - 10+ KPIs interativos
    - Apresentável

M5: [ ] MVP Release              31/12/2024
    - Todos critérios MVP atendidos
    - Sistema funcional e demonstrável
    - Documentação técnica completa

M6: [ ] Produção Beta            28/02/2025
    - Multi-fonte integrada
    - Airflow operacional
    - API funcionando

M7: [ ] Produção Release         31/03/2025
    - Sistema completo
    - Monitoramento 24/7
    - Documentação final
```

---

## Critérios de Sucesso

### Técnicos - POC

```
[PIPELINE]
[x] Extract: pysus baixa DBC sem erros
[ ] Transform: 90%+ registros válidos após limpeza
[ ] Load: CSV + Parquet salvos corretamente
[ ] Performance: <10 min total AC 2k registros

[QUALIDADE]
[ ] Validações implementadas e passando
[ ] Taxa perda <10%
[ ] KPIs corretos (validação manual)

[VISUALIZAÇÕES]
[ ] 4-6 gráficos profissionais
[ ] PNG 300 DPI
[ ] Títulos, labels, legendas OK
```

### Técnicos - MVP

```
[DATABASE]
[ ] Oracle XE instalado e configurado
[ ] Schema normalizado (3NF mínimo)
[ ] Constraints, índices, views OK
[ ] Performance queries <3s

[DASHBOARD]
[ ] Interativo (filtros funcionando)
[ ] 3-5 páginas navegáveis
[ ] 10+ KPIs implementados
[ ] Design profissional

[TESTES]
[ ] pytest configurado
[ ] 87%+ coverage
[ ] Zero testes falhando
[ ] CI/CD automático
```

### Técnicos - Produção

```
[ESCALABILIDADE]
[ ] Multi-fonte integrada (SIH+CNES+SIM)
[ ] Processa múltiplos estados
[ ] Performance mantida (<1h para 500k registros)

[AUTOMAÇÃO]
[ ] Airflow DAGs funcionando
[ ] Retry automático em falhas
[ ] Alertas configurados

[API]
[ ] FastAPI endpoints documentados
[ ] Autenticação JWT funcionando
[ ] Rate limiting configurado

[MONITORAMENTO]
[ ] Prometheus + Grafana operacional
[ ] Logs centralizados (ELK)
[ ] Dashboards operacionais
[ ] Alertas 24/7
```

---

## Riscos e Mitigações

### RISCO-01: FTP DataSUS Instável

```
Probabilidade: MÉDIA
Impacto:       ALTO (bloqueia extract)
Categoria:     Infraestrutura Externa

Descrição:
Servidor FTP DataSUS pode ficar indisponível ou lento, impedindo
download dos arquivos DBC.

Mitigação:
[x] Implementar retry automático (3 tentativas, backoff exponencial)
[x] Cache local dos arquivos baixados
[ ] Fallback: download manual quando FTP falha
[ ] Documentar URLs alternativas se existirem

Status: MITIGADO PARCIALMENTE
```

### RISCO-02: Python 3.14 Incompatível com pysus

```
Probabilidade: ALTA (já identificado)
Impacto:       MÉDIO
Categoria:     Dependências

Descrição:
pysus 0.11.0 requer numpy 1.26.2 e cffi 1.15.1 que não compilam
em Python 3.14.

Mitigação:
[x] RESOLVIDO: Usar Python 3.11.x (ADR-002)
[x] Documentar versão obrigatória
[x] requirements.txt com versões fixas
[ ] Monitorar releases pysus para migração futura

Status: RESOLVIDO
```

### RISCO-03: Volume Dados > RAM Disponível

```
Probabilidade: BAIXA (POC/MVP), MÉDIA (Produção)
Impacto:       ALTO
Categoria:     Performance

Descrição:
Estados grandes (SP ~200k registros) podem exceder RAM disponível
causando swap ou crash.

Mitigação:
[ ] Processar dados em chunks (pandas chunksize)
[ ] Considerar Dask para processamento paralelo
[ ] Monitorar uso memória durante testes
[ ] Upgrade RAM se necessário (MVP: 12GB+)

Status: MONITORANDO
```

### RISCO-04: Oracle XE Limitações (MVP)

```
Probabilidade: MÉDIA
Impacto:       MÉDIO
Categoria:     Tecnologia

Descrição:
Oracle XE 21c tem limitações: 2GB RAM, 12GB dados, 2 CPUs.
Pode não suportar volume planejado.

Mitigação:
[ ] Otimizar queries (índices, views materializadas)
[ ] Considerar PostgreSQL como alternativa gratuita
[ ] Particionar tabelas se necessário
[ ] Monitorar uso recursos Oracle

Status: A MONITORAR (MVP)
```

### RISCO-05: Tempo Insuficiente

```
Probabilidade: MÉDIA
Impacto:       ALTO
Categoria:     Planejamento

Descrição:
POC 1 semana, MVP 4 semanas pode ser insuficiente se surgirem
blockers técnicos.

Mitigação:
[x] Priorizar entregas core (pipeline, KPIs, docs)
[ ] Cortar features não essenciais se necessário
[ ] Buffer 1 semana no cronograma MVP
[ ] Decisão GO/NO-GO após POC permite replanejar

Status: MITIGADO PARCIALMENTE
```

### RISCO-06: Qualidade Dados DataSUS

```
Probabilidade: ALTA
Impacto:       MÉDIO
Categoria:     Dados

Descrição:
Dados públicos podem ter qualidade variável: duplicatas, nulos,
inconsistências, códigos inválidos.

Mitigação:
[x] MITIGADO: Validações rigorosas no Transform
[x] Documentar limitações conhecidas
[x] Taxa perda 5-15% esperada e aceitável
[ ] Comunicar limitações em apresentações

Status: MITIGADO
```

### RISCO-07: Complexidade Subestimada

```
Probabilidade: MÉDIA
Impacto:       ALTO
Categoria:     Estimativa

Descrição:
Projeto pode ser mais complexo que o estimado, especialmente
integração multi-fonte (Produção).

Mitigação:
[x] Abordagem iterativa POC->MVP->Prod valida cada etapa
[ ] POC valida viabilidade antes de investir no MVP
[ ] MVP valida escala antes de investir em Produção
[ ] Possibilidade de abortar/replanejar em cada milestone

Status: MITIGADO POR DESIGN
```

---

**Última atualização:** 04/12/2024

**Veja Também:**

- [README.md](../README.md) - Entry point do projeto
- [ARCHITECTURE.md](ARCHITECTURE.md) - Stack técnico e ADRs
- [DATA_GUIDE.md](DATA_GUIDE.md) - Dicionário de dados e regras
