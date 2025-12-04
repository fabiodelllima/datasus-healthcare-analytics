# ARCHITECTURE

- **Sistema:** DataSUS Healthcare Analytics
- **Versão:** 1.0.0 POC
- **Última Atualização:** 03/12/2024

**Propósito:** Single Source of Truth para decisões arquiteturais, stack
técnico, requisitos de sistema e workflows de infraestrutura.

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Stack Técnico](#stack-técnico)
3. [Arquitetura do Pipeline](#arquitetura-do-pipeline)
4. [Decisões Arquiteturais (ADRs)](#decisões-arquiteturais-adrs)
5. [Requisitos de Sistema](#requisitos-de-sistema)
6. [Workflows de Infraestrutura](#workflows-de-infraestrutura)

---

## Visão Geral

### Contexto

Sistema de analytics para gestão hospitalar baseado em **dados REAIS** do
Sistema de Informações Hospitalares (SIH) do DataSUS/Ministério da Saúde.

**Diferencial competitivo:**

- Integração com fontes públicas brasileiras (DataSUS)
- Processamento de formato proprietário DBC (DBF comprimido)
- Demonstração de competências completas de engenharia de dados
- Pipeline end-to-end: Extract → Transform → Load → Analytics

### Objetivos por Fase

**POC (atual):**

- Validar viabilidade técnica de processar DataSUS
- Pipeline ETL funcional com dados reais
- KPIs básicos para demonstração
- Documentação reproduzível

**MVP:**

- Produto funcional demonstrável
- Database Oracle com schema relacional
- Dashboard interativo (Power BI ou Streamlit)
- Testes automatizados (87%+ coverage)
- CI/CD básico

**Produção:**

- Sistema robusto production-ready
- Multi-fonte (SIH + CNES + SIM)
- Orquestração Airflow
- API REST + autenticação
- Monitoramento completo

---

## Stack Técnico

### POC - Stack Atual

```
┌──────────────────────────────────────────────────────────────────────────┐
│ CAMADA           │ TECNOLOGIA              │ VERSÃO      │ JUSTIFICATIVA │
├──────────────────┼─────────────────────────┼─────────────┼───────────────┤
│ Linguagem        │ Python                  │ 3.11.x      │ [ADR-002]     │
│                  │                         │ OBRIGATÓRIO │ Compatível    │
│                  │                         │             │ pysus         │
│                  │                         │             │               │
│ Extract          │ pysus                   │ 0.11.0      │ Lib oficial   │
│                  │                         │             │ DataSUS       │
│                  │                         │             │               │
│ Transform        │ pandas                  │ 2.1.4       │ Manipulação   │
│                  │ numpy                   │ 1.26.2      │ dados         │
│                  │                         │             │               │
│ Visualização     │ matplotlib              │ 3.8.2       │ Gráficos      │
│                  │ seaborn                 │ 0.13.0      │ estáticos     │
│                  │                         │             │               │
│ Storage          │ CSV                     │ nativo      │ [ADR-003]     │
│                  │ Parquet (pyarrow)       │ 14.0.1      │ Formato dual  │
│                  │                         │             │               │
│ Notebooks        │ Jupyter                 │ 1.0.0       │ Análise       │
│                  │                         │             │ exploratória  │
│                  │                         │             │               │
│ Ambiente Virtual │ venv                    │ nativo      │ Isolamento    │
└──────────────────┴─────────────────────────┴─────────────┴───────────────┘

Tempo processamento esperado (POC):
  AC 2k registros:  2-5 minutos total
  ES 20k registros: 5-10 minutos total
```

### MVP - Stack Planejado

```
┌──────────────────────────────────────────────────────────────────────────┐
│ CAMADA           │ TECNOLOGIA              │ VERSÃO      │ STATUS        │
├──────────────────┼─────────────────────────┼─────────────┼───────────────┤
│ Database         │ Oracle Database XE      │ 21c         │ [ ] Planejado │
│                  │ cx_Oracle               │ 8.3+        │               │
│                  │                         │             │               │
│ BI/Dashboard     │ Power BI Desktop        │ Latest      │ [ ] Planejado │
│                  │ ou Streamlit            │ 1.30+       │ Alternativa   │
│                  │                         │             │               │
│ Testes           │ pytest                  │ 7.4+        │ [ ] Planejado │
│                  │ pytest-cov              │ 4.1+        │               │
│                  │                         │             │               │
│ CI/CD            │ GitHub Actions          │ -           │ [ ] Planejado │
│                  │ flake8 (linting)        │ 6.1+        │               │
│                  │                         │             │               │
│ Agendamento      │ cron                    │ nativo      │ [ ] Planejado │
└──────────────────┴─────────────────────────┴─────────────┴───────────────┘
```

### Produção - Stack Futuro

```
┌─────────────────────────────────────────────────────────────────────────┐
│ CAMADA           │ TECNOLOGIA              │ VERSÃO      │ STATUS       │
├──────────────────┼─────────────────────────┼─────────────┼──────────────┤
│ Orquestração     │ Apache Airflow          │ 2.8+        │ [ ] Futuro   │
│                  │                         │             │              │
│ API              │ FastAPI                 │ 0.109+      │ [ ] Futuro   │
│                  │ JWT Authentication      │ -           │              │
│                  │                         │             │              │
│ Monitoramento    │ Prometheus              │ 2.48+       │ [ ] Futuro   │
│                  │ Grafana                 │ 10.2+       │              │
│                  │                         │             │              │
│ Logging          │ ELK Stack               │ 8.11+       │ [ ] Futuro   │
│                  │ (Elasticsearch, Kibana) │             │              │
│                  │                         │             │              │
│ Containerização  │ Docker                  │ 24+         │ [ ] Futuro   │
│                  │ Docker Compose          │ 2.23+       │              │
└──────────────────┴─────────────────────────┴─────────────┴──────────────┘
```

---

## Arquitetura do Pipeline

### Diagrama de Fluxo (POC)

```
 DataSUS FTP                EXTRACT             TRANSFORM
┌─────────────┐           ┌──────────┐         ┌───────────────────────┐
│ ftp.datasus │           │          │         │ 1. Conversão Tipos    │
│ .gov.br     │──────────→│  pysus   │────────→│    - datetime         │
│             │  Download │          │  DBC→   │    - numeric          │
│ RDAC2401    │  ~500KB   │  Decode  │  DBF    │    - categorical      │
│ .dbc        │  30-90s   │          │         │                       │
└─────────────┘           └──────────┘         │ 2. Limpeza            │
                                               │    - duplicatas       │
                                               │    - nulos críticos   │
                                               │    - outliers         │
                                               │                       │
                                               │ 3. Validação          │
                                               │    - datas            │
                                               │    - valores          │
                                               │    - consistência     │
                                               │                       │
                                               │ 4. Enriquecimento     │
                                               │    - faixa_etaria     │
                                               │    - especialidade    │
                                               │    - custo_dia        │
                                               │                       │
                                               │ pandas/numpy          │
                                               │ 15-45s                │
                                               │ Perda: 5-10%          │
                                               └───────────────────────┘
                                                         │
                                                         ▼
 LOAD                             ANALYTICS
┌──────────────────────┐        ┌────────────────────────────┐
│ Storage Dual-Format  │        │ Jupyter Notebook           │
│                      │        │                            │
│ /data/processed/     │        │ KPIs:                      │
│ ├─ sih_AC_202401.csv │───────→│ - Taxa ocupação            │
│ │  (~1.5MB)          │        │ - Tempo médio permanência  │
│ │  Universal         │        │ - Volume internações       │
│ │                    │        │ - Receita total            │
│ └─ sih_AC_202401     │        │ - Distribuição demográfica │
│    .parquet          │        │                            │
│    (~450KB, 70%)     │        │ Visualizações:             │
│    Performance       │        │ - 4-6 gráficos PNG 300 DPI │
│                      │        │ - matplotlib/seaborn       │
│ 5-15s                │        │                            │
└──────────────────────┘        └────────────────────────────┘

Total: ~80 colunas raw → validado/enriquecido → 2 formatos storage
```

### Fluxo de Dados Detalhado

```
ENTRADA                  PROCESSAMENTO                     SAÍDA
┌────────────┐          ┌──────────────────┐          ┌──────────────┐
│ DBC        │          │ Validações:      │          │ CSV          │
│ Comprimido │ ────────→│ - NOT NULL       │─────────→│ + Parquet    │
│ ~500KB     │  Decode  │ - Ranges válidos │ Storage  │ ~1.5MB / 450 │
│            │          │ - Consistência   │          │              │
│ Colunas:   │          │ - Duplicatas     │          │ Campos:      │
│ ~80 campos │          │                  │          │ ~85 campos   │
│            │          │ Enriquecimento:  │          │ (+ calc.)    │
│            │          │ - Campos calc.   │          │              │
└────────────┘          └──────────────────┘          └──────────────┘
```

---

## Decisões Arquiteturais (ADRs)

### ADR-001: Dados Reais vs Dados Sintéticos

- **Status:** [x] APROVADO
- **Data:** 01/12/2024
- **Decisores:** F. (desenvolvedor)

**Contexto:**

- Projeto visa portfolio para vaga de Analista de Informações Gerenciais Pleno
  em hospital. Escolha entre usar dados sintéticos (mais rápido) ou dados reais
  do DataSUS (mais complexo).

**Decisão:**

- Usar **dados REAIS do DataSUS** (Sistema de Informações Hospitalares).

**Justificativa:**

- [+] Portfolio diferenciado: poucos candidatos usam dados reais governamentais
- [+] Conhecimento prático: familiaridade com formato DBC proprietário
- [+] Credibilidade: demonstra capacidade de trabalhar com dados complexos
- [+] Problema real: validações e limpeza necessárias (não dados perfeitos)
- [+] Contexto brasileiro: conhecimento do sistema de saúde nacional

- [-] Setup mais lento: ~3 horas vs ~30 minutos dados sintéticos
- [-] Dependência externa: FTP DataSUS pode estar instável
- [-] Qualidade variável: requer validações rigorosas
- [-] Documentação limitada: menos docs que datasets acadêmicos

**Consequências:**

- Pipeline ETL mais robusto (validações reais)
- Conhecimento transferível para ambiente hospitalar
- Possível instabilidade FTP (mitigado: cache local)
- Necessidade de documentação detalhada dos campos

**Alternativas Consideradas:**

- Kaggle healthcare datasets (rejeitado: dados limpos demais)
- MIMIC-III (rejeitado: foco EUA, não Brasil)
- Dados sintéticos faker (rejeitado: pouco realista)

### ADR-002: Python 3.11 vs Python 3.14

- **Status:** [x] APROVADO
- **Data:** 01/12/2024
- **Decisores:** F. (desenvolvedor)

**Contexto:**

- Biblioteca pysus (essencial para ler DBC) tem dependências antigas. Python 3.14
  é versão mais recente mas pode ter problemas de compatibilidade.

**Decisão:**

- Usar **Python 3.11.x** (não Python 3.14).

**Justificativa:**

- [+] Compatibilidade pysus: biblioteca testada e funcional em 3.11
- [+] Dependências estáveis: numpy 1.26.2, cffi 1.15.1 compilam sem erros
- [+] Ambiente produção: hospitais tipicamente usam versões LTS
- [+] Suporte garantido: Python 3.11 suportado até outubro/2027

- [-] Não é latest: Python 3.14 tem features novas (não essenciais)
- [-] Migração futura: eventual upgrade necessário

**Consequências:**

- Ambiente isolado venv obrigatório para evitar conflitos
- Documentação deve especificar versão exata
- Setup reproduzível garantido

**Evidências Técnicas:**

```bash
# Python 3.14: FALHOU
numpy 1.26.2: C extensions não compilam
cffi 1.15.1: Build errors

# Python 3.11: SUCESSO
Todas dependências instaladas corretamente
pysus funcional
```

### ADR-003: CSV + Parquet vs Apenas um Formato

- **Status:** [x] APROVADO
- **Data:** 02/12/2024
- **Decisores:** F. (desenvolvedor)

**Contexto:**

- Necessidade de storage para dados processados. Escolha entre formato único ou
  múltiplos formatos.

**Decisão:**

- Usar **formato dual: CSV + Parquet simultaneamente**.

**Justificativa:**

CSV:

- [+] Universal: abre em Excel, LibreOffice, qualquer ferramenta
- [+] Debug fácil: inspeção visual direta
- [+] Compatibilidade: importação garantida em qualquer sistema
- [+] Human-readable: facilita troubleshooting

- [-] Tamanho: ~1.5MB (maior)
- [-] Performance: leitura mais lenta

Parquet:

- [+] Compacto: ~450KB (70% menor que CSV)
- [+] Performance: 3x mais rápido leitura (columnar)
- [+] Tipos: preserva datetime, int, float nativamente
- [+] Ecosistema: padrão Data Lake (Spark, Athena, BigQuery)

- [-] Binário: não human-readable
- [-] Ferramentas: requer libs específicas (pyarrow, pandas)

**Decisão: AMBOS**

- [+] Máxima flexibilidade: escolher formato por contexto
- [+] Demo portfolio: mostra conhecimento Data Lake ecosystem
- [+] MVP-ready: Parquet preparado para escala
- [+] POC-friendly: CSV para validação rápida

- [-] Duplicação storage: ~2MB total vs ~1.5MB
- [-] Duplicação processamento: write 2x (overhead mínimo ~2s)

**Consequências:**

- Storage dual aumenta confiabilidade (backup implícito)
- MVP pode usar apenas Parquet se storage for crítico
- Entrevistas: demonstra conhecimento de trade-offs

### ADR-004: Documentação Modular vs Monolítica

- **Status:** [x] APROVADO
- **Data:** 03/12/2024
- **Decisores:** F. (desenvolvedor)

**Contexto:**

- Arquivo DOCS.md monolítico (1800+ linhas) difícil de manter. Corrupção de
  arquivo (6GB por loop sed) evidenciou fragilidade.

**Decisão:**

- Quebrar documentação em **4 arquivos SSOT modulares e consolidados**:

- README.md (entry point)
- ARCHITECTURE.md (técnico)
- DATA_GUIDE.md (dados)
- ROADMAP.md (planejamento)

**Justificativa:**

- [+] Arquivos menores: <500 linhas cada, mais fácil editar
- [+] Separação concerns: técnico vs dados vs planejamento
- [+] Versionamento: menos conflitos merge em Git
- [+] Propósito claro: cada arquivo tem responsabilidade única
- [+] Navegação: índice no README.md facilita descoberta

- [-] Navegação: precisa manter links entre arquivos
- [-] Índice centralizado: README.md como "table of contents"

**Consequências:**

- Manutenção mais fácil: editar apenas arquivo relevante
- Onboarding: novos podem focar em arquivo específico
- Risco reduzido: corrupção afeta apenas 1 arquivo não tudo
- Trade-off aceitável: múltiplos arquivos vs gerenciabilidade

---

## Requisitos de Sistema

### Requisitos Mínimos (Funcional mas Lento)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ COMPONENTE       │ MÍNIMO              │ DESEMPENHO ESPERADO            │
├──────────────────┼─────────────────────┼────────────────────────────────┤
│ CPU              │ 2 cores             │ AC 2k registros: 5-8 min       │
│                  │                     │ ES 20k registros: 15-20 min    │
│                  │                     │                                │
│ RAM              │ 4GB                 │ Pandas pode usar swap          │
│                  │                     │ Processamento mais lento       │
│                  │                     │                                │
│ Disco            │ 10GB livres         │ Dados + ambiente virtual       │
│                  │                     │                                │
│ Conexão Internet │ 5 Mbps              │ Download DBC ~2-3 minutos      │
│                  │                     │                                │
│ Sistema          │ Linux Ubuntu 20.04+ │ Ou Windows 10+ com WSL2        │
│ Operacional      │ macOS 11+           │                                │
└──────────────────┴─────────────────────┴────────────────────────────────┘
```

### Requisitos Recomendados (POC)

```
┌────────────────────────────────────────────────────────────────────────┐
│ COMPONENTE       │ RECOMENDADO         │ DESEMPENHO ESPERADO           │
├──────────────────┼─────────────────────┼───────────────────────────────┤
│ CPU              │ 4 cores             │ AC 2k registros: 2-5 min      │
│                  │ Intel i5/Ryzen 5+   │ ES 20k registros: 5-10 min    │
│                  │                     │ SP 200k registros: 25-50 min  │
│                  │                     │                               │
│ RAM              │ 8GB                 │ Processamento confortável     │
│                  │                     │ Múltiplos notebooks abertos   │
│                  │                     │                               │
│ Disco            │ 50GB SSD            │ I/O rápido                    │
│                  │                     │ Espaço para múltiplos estados │
│                  │                     │                               │
│ Conexão Internet │ 10+ Mbps            │ Download DBC ~30-60 segundos  │
│                  │                     │                               │
│ Sistema          │ Linux Ubuntu 22.04  │ Ambiente nativo Python        │
│ Operacional      │ macOS 12+           │ Performance otimizada         │
└──────────────────┴─────────────────────┴───────────────────────────────┘
```

### Requisitos MVP (Oracle Database)

```
┌────────────────────────────────────────────────────────────────────────┐
│ COMPONENTE       │ MVP                 │ OBSERVAÇÕES                   │
├──────────────────┼─────────────────────┼───────────────────────────────┤
│ CPU              │ 4 cores             │ Oracle XE consome recurso     │
│                  │                     │                               │
│ RAM              │ 12GB+               │ Oracle XE: até 2GB RAM        │
│                  │                     │ Sistema: 4GB                  │
│                  │                     │ Python: 2GB                   │
│                  │                     │ Overhead: 4GB                 │
│                  │                     │                               │
│ Disco            │ 100GB SSD           │ Oracle XE: até 12GB dados     │
│                  │                     │ Dados processados: 20-30GB    │
│                  │                     │                               │
│ Database         │ Oracle XE 21c       │ Gratuito, limitações:         │
│                  │                     │ - 2GB RAM                     │
│                  │                     │ - 12GB dados                  │
│                  │                     │ - 2 CPUs                      │
└──────────────────┴─────────────────────┴───────────────────────────────┘
```

### Dependências Python (POC)

```bash
# requirements.txt
python==3.11.*          # OBRIGATÓRIO: compatibilidade pysus

# ETL
pysus==0.11.0          # Extract DataSUS
pandas==2.1.4          # Transform
numpy==1.26.2          # Cálculos
pyarrow==14.0.1        # Parquet

# Visualização
matplotlib==3.8.2
seaborn==0.13.0

# Notebooks
jupyter==1.0.0
ipykernel==6.27.1

# Desenvolvimento
black==23.12.1         # Code formatter
flake8==6.1.0          # Linter
```

---

## Workflows de Infraestrutura

### Setup Ambiente (POC)

```bash
# 1. Verificar versão Python
python3 --version  # Deve ser 3.11.x

# 2. Criar ambiente virtual
python3.11 -m venv venv

# 3. Ativar ambiente
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 4. Atualizar pip
pip install --upgrade pip

# 5. Instalar dependências
pip install --break-system-packages -r requirements.txt

# 6. Verificar instalação
python -c "import pysus; print(pysus.__version__)"
```

### Deploy Pipeline (POC)

```bash
# 1. Estrutura de diretórios
mkdir -p data/{raw,processed}
mkdir -p logs
mkdir -p outputs

# 2. Executar pipeline
python src/main.py --state AC --year 2024 --month 01

# 3. Verificar saídas
ls -lh data/processed/
ls -lh outputs/

# 4. Logs
tail -f logs/etl_pipeline.log
```

### Troubleshooting Comum

```bash
# Problema: pysus não instala
# Solução: Verificar Python 3.11
python3.11 -m pip install pysus==0.11.0 --break-system-packages

# Problema: FTP DataSUS timeout
# Solução: Retry manual ou usar cache local
wget ftp://ftp.datasus.gov.br/dissemin/publicos/SIHSUS/200801_/Dados/RDAC2401.dbc

# Problema: Memory error pandas
# Solução: Processar em chunks
df = pd.read_csv('file.csv', chunksize=10000)

# Problema: Parquet write error
# Solução: Verificar pyarrow instalado
pip install pyarrow==14.0.1 --break-system-packages
```

### CI/CD (MVP - Planejado)

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: flake8 src/
      - run: pytest tests/ --cov
```

---

- **Última Atualização:** 03/12/2024
- **Próxima Revisão:** Após conclusão POC (07/12/2024)

**Veja Também:**

- [README.md](../README.md) - Entry point do projeto
- [DATA_GUIDE.md](DATA_GUIDE.md) - Dicionário de dados e regras
- [ROADMAP.md](ROADMAP.md) - Planejamento e cronograma
