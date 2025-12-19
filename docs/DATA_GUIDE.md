# DATA GUIDE

- **Sistema:** DataSUS Healthcare Analytics
- **Versão:** 1.0.0 POC
- **Última Atualização:** 05/12/2024

**Propósito:** Single Source of Truth para tudo relacionado a dados: fonte, dicionário de campos, códigos, regras de negócio, validações e workflows ETL.

---

## Índice

1. [Fonte de Dados](#fonte-de-dados)
2. [Dataset POC](#dataset-poc)
3. [Dicionário de Dados](#dicionário-de-dados)
4. [Códigos e Tabelas](#códigos-e-tabelas)
5. [KPIs Implementados](#kpis-implementados)
6. [Pipeline ETL Detalhado](#pipeline-etl-detalhado)
7. [Qualidade de Dados](#qualidade-de-dados)
8. [Limitações Conhecidas](#limitações-conhecidas)

---

## Fonte de Dados

### Sistema de Informações Hospitalares (SIH/DataSUS)

**Origem:** Ministério da Saúde - DATASUS

**URL:** <https://datasus.saude.gov.br/\>

**FTP:** ftp://ftp.datasus.gov.br/dissemin/publicos/SIHSUS/200801\_/Dados/

### Descrição

O SIH/SUS registra todas as internações realizadas em hospitais públicos e conveniados ao SUS no Brasil. Contém informações sobre:

- Identificação da internação (AIH)
- Dados demográficos do paciente
- Diagnóstico principal (CID-10)
- Procedimentos realizados
- Valores financeiros (repasse SUS)
- Datas de entrada/saída

### Formato Original

**Extensão:** `.dbc` (DBF comprimido)  
**Encoding:** CP850 (DOS Latin 1)  
**Estrutura:** DBF (dBase III+)  
**Compressão:** Proprietária Microsoft

**Nomenclatura arquivos:**

```
RDUF AAMM.dbc
│  │  │ │
│  │  │ └─ Mês (01-12)
│  │  └─── Ano (24 = 2024)
│  └────── UF (AC, SP, etc)
└───────── Tipo AIH (RD = Reduzida)

Exemplo: RDAC2401.dbc
→ AIH Reduzida, Acre, Janeiro 2024
```

### Grupos de Arquivos SIH

| Grupo  | Descrição              | Conteúdo                 | Uso POC |
| ------ | ---------------------- | ------------------------ | ------- |
| **RD** | AIH Reduzida           | Dados básicos internação | ✓ SIM   |
| **ER** | AIH Rejeitadas         | Internações rejeitadas   | ✗ Não   |
| **SP** | Serviços Profissionais | Detalhamento equipe      | ✗ Não   |

---

## Dataset POC

### Estados Selecionados

**Justificativa Técnica:**

| Estado | Volume Jan/2024   | Razão Escolha                       |
| ------ | ----------------- | ----------------------------------- |
| **AC** | ~4.300 registros  | Dataset pequeno para testes rápidos |
| **ES** | ~15.000 registros | Validação pipeline com volume médio |

**Exclusões:**

- SP (~200k/mês): Volume excessivo para POC
- Estados grandes: Tempo processamento incompatível com POC

### Volume de Dados

```
POC (AC + ES, Jan 2024):
├── Registros: ~19.300
├── CSV total: ~8 MB
├── Parquet total: ~1 MB
└── Tempo proc: <10s

Comparação Nacional (Jan 2024):
└── Total Brasil: ~1.2M registros/mês
```

### Período Temporal

**POC:** Janeiro 2024 (mês completo)

**Razão:**

- Dados recentes (freshness)
- Mês completo (sazonalidade)
- Sem feriados prolongados

---

## Dicionário de Dados

### Campos Principais SIH/DataSUS

#### Identificação

| Campo      | Tipo       | Descrição                            | Exemplo        | Obrigatório |
| ---------- | ---------- | ------------------------------------ | -------------- | ----------- |
| `N_AIH`    | String(13) | Número AIH (Autorização Internação)  | 1224100061118  | ✓           |
| `IDENT`    | Int        | Identificação atendimento (1=normal) | 1              | ✓           |
| `CGC_HOSP` | String(14) | CNPJ hospital                        | 04034526003240 | ✓           |
| `CNES`     | String(7)  | Código estabelecimento saúde         | 2000121        | ✓           |

#### Datas

| Campo      | Tipo Original | Tipo Convertido | Descrição       | Formato  |
| ---------- | ------------- | --------------- | --------------- | -------- |
| `DT_INTER` | String(8)     | datetime64      | Data internação | YYYYMMDD |
| `DT_SAIDA` | String(8)     | datetime64      | Data saída      | YYYYMMDD |

**Validação:** `DT_INTER <= DT_SAIDA`

#### Demografia

| Campo       | Tipo             | Descrição                   | Valores                  | Validação    |
| ----------- | ---------------- | --------------------------- | ------------------------ | ------------ |
| `IDADE`     | String → float64 | Idade paciente              | 0-120                    | >= 0, <= 120 |
| `COD_IDADE` | Int              | Tipo unidade idade          | 2=anos, 3=meses, 4=dias  | -            |
| `SEXO`      | Int              | Sexo                        | 1=M, 3=F                 | -            |
| `RACA_COR`  | String(2)        | Raça/cor (IBGE)             | 01=Branca, 02=Preta, etc | -            |
| `MUNIC_RES` | String(6)        | Município residência (IBGE) | 120060                   | -            |

#### Clínica

| Campo        | Tipo       | Descrição               | Formato | Tabela Referência     |
| ------------ | ---------- | ----------------------- | ------- | --------------------- |
| `DIAG_PRINC` | String(4)  | Diagnóstico principal   | CID-10  | Tabela CID            |
| `DIAG_SECUN` | String(4)  | Diagnóstico secundário  | CID-10  | Tabela CID            |
| `PROC_REA`   | String(10) | Procedimento realizado  | SIGTAP  | Tabela Procedimentos  |
| `PROC_SOLIC` | String(10) | Procedimento solicitado | SIGTAP  | Tabela Procedimentos  |
| `ESPEC`      | String(2)  | Especialidade leito     | 01-14   | Tabela Especialidades |

#### Valores Financeiros

| Campo      | Tipo Original    | Tipo Convertido               | Descrição | Validação |
| ---------- | ---------------- | ----------------------------- | --------- | --------- |
| `VAL_TOT`  | String → float64 | Valor total AIH               | >= 0      |
| `VAL_UTI`  | String → float64 | Valor diárias UTI             | >= 0      |
| `VAL_SH`   | String → float64 | Valor serviços hospitalares   | >= 0      |
| `VAL_SP`   | String → float64 | Valor serviços profissionais  | >= 0      |
| `VAL_SADT` | String → float64 | Valor SADT (diagnose/terapia) | >= 0      |

**Fórmula:** `VAL_TOT = VAL_SH + VAL_SP + VAL_SADT + VAL_UTI + outros componentes`

#### Internação

| Campo        | Tipo      | Descrição                  | Valores                      |
| ------------ | --------- | -------------------------- | ---------------------------- |
| `DIAS_PERM`  | Int       | Dias permanência (DataSUS) | 0-999                        |
| `QT_DIARIAS` | Int       | Quantidade diárias         | 0-999                        |
| `CAR_INT`    | String(2) | Caráter internação         | 01=Eletiva, 02=Urgência, etc |
| `MORTE`      | Int       | Flag óbito                 | 0=Não, 1=Sim                 |

#### UTI

| Campo        | Tipo | Descrição                  |
| ------------ | ---- | -------------------------- |
| `UTI_MES_IN` | Int  | Diárias UTI mês internação |
| `UTI_MES_AN` | Int  | Diárias UTI mês anterior   |
| `UTI_MES_AL` | Int  | Diárias UTI mês alta       |
| `UTI_MES_TO` | Int  | Total diárias UTI          |

---

#### 4. Métricas Qualidade

**AC Janeiro 2024:**

```
Registros iniciais:    4,315
Duplicatas removidas:      0
Nulos críticos:            0
Validações falhadas:       0
Registros finais:      4,315
Taxa validação:       100.0%
```

---

## Códigos e Tabelas

### CID-10 (Classificação Doenças)

**Estrutura:** Letra + 2-3 dígitos (ex: I21, Z371)

**Capítulos principais:**

- I00-I99: Doenças aparelho circulatório
- J00-J99: Doenças aparelho respiratório
- K00-K99: Doenças aparelho digestivo
- O00-O99: Gravidez, parto e puerpério
- Z00-Z99: Fatores que influenciam estado saúde

**Exemplos dataset AC:**

```
Q18  → Outras malformações congênitas face/pescoço
Z371 → Gêmeos, ambos nativivos
R10  → Dor abdominal e pélvica
O140 → Pré-eclâmpsia moderada
```

### Tabela Especialidades (ESPEC)

| Código | Descrição            | Exemplo Procedimento   |
| ------ | -------------------- | ---------------------- |
| 01     | Cirurgia             | Apendicectomia         |
| 02     | Obstetrícia          | Parto normal           |
| 03     | Clínica Médica       | Pneumonia              |
| 04     | Cuidados Prolongados | Reabilitação           |
| 05     | Psiquiatria          | Tratamento transtornos |
| 07     | Tisiologia           | Tuberculose            |
| 08     | Pediatria Clínica    | Infecções pediátricas  |

### Tabela Procedimentos (SIGTAP)

**Estrutura:** 10 dígitos

**Exemplos:**

```
0301060010 → Tratamento de intercorrências clínicas na gravidez
0301060088 → Parto normal
0303100036 → Tratamento de eclâmpsia
```

**Referência completa:** Sistema SIGTAP (Tabela Unificada Procedimentos SUS)

---

## KPIs Implementados

### 1. Taxa de Ocupação

**Definição:** Percentual utilização leitos disponíveis

**Cálculo:**

```python
ocupacao = (total_pacientes_dia / leitos_disponiveis) * 100
```

**Meta:** 75-85% (OMS recomenda 80%)

**Uso:** Planejamento capacidade, eficiência operacional

---

### 2. Tempo Médio Permanência (TMP)

**Definição:** Média dias internação por tipo procedimento/especialidade

**Cálculo:**

```python
tmp = df.groupby('PROC_REA')['stay_days'].mean()
```

**Benchmark:**

- Cirurgias eletivas: 3-5 dias
- Clínica médica: 5-7 dias
- UTI: 7-14 dias

**Uso:** Giro leito, benchmarking, identificar outliers

---

### 3. Volume Atendimentos

**Definição:** Total internações por período

**Cálculo:**

```python
volume_mes = df.groupby(df['DT_INTER'].dt.month).size()
volume_especialidade = df.groupby('ESPEC').size()
```

**Uso:** Planejamento demanda, alocação recursos

---

### 4. Receita Total

**Definição:** Soma valores reembolsados SUS

**Cálculo:**

```python
receita_total = df['VAL_TOT'].sum()
receita_por_especialidade = df.groupby('ESPEC')['VAL_TOT'].sum()
```

**AC Jan/2024:** R$ 1.021.234,50 (exemplo)

**Uso:** Planejamento financeiro, análise rentabilidade

---

### 5. Demografia Atendimentos

**Definição:** Distribuição faixa etária

**Cálculo:**

```python
demografia = df['age_group'].value_counts()
```

**Uso:** Planejamento serviços específicos (pediatria, geriatria)

---

## Pipeline ETL Detalhado

### Extract

- **Input:** Parâmetros (state, year, month)
- **Output:** DataFrame raw

```python
from pysus.online_data.SIH import download

parquet_set = download(
    states='AC',
    years=2024,
    months=1,
    groups='RD'
)
df_raw = parquet_set.to_dataframe()
```

**Logs:**

```
[2024-12-05 12:16:47] INFO - [EXTRACT] Baixando: AC 2024/01
[2024-12-05 12:16:47] INFO - [EXTRACT] Download concluído
[2024-12-05 12:16:48] INFO - [EXTRACT] Registros carregados: 4,315
[2024-12-05 12:16:48] INFO - [EXTRACT] Colunas: 115
```

---

### Transform

- **Input:** DataFrame raw
- **Output:** DataFrame clean

**Pipeline 4 etapas:**

```
1. _convert_types()
   ├─ String → float64 (numéricos)
   └─ String → datetime64 (datas)

2. _clean_data()
   ├─ drop_duplicates()
   └─ dropna(subset=critical)

3. _validate_data()
   ├─ DT_INTER <= DT_SAIDA
   ├─ 0 <= IDADE <= 120
   └─ VAL_* >= 0

4. _enrich_data()
   ├─ stay_days
   ├─ daily_cost
   ├─ age_group
   ├─ death
   └─ specialty_name
```

**Logs:**

```
[2024-12-05 12:16:48] INFO - [TRANSFORM] Iniciado: 4,315 registros
[2024-12-05 12:16:48] INFO - [CONVERT] Convertendo tipos...
[2024-12-05 12:16:48] INFO - [CONVERT] Tipos convertidos
[2024-12-05 12:16:48] INFO - [CLEAN] Iniciando limpeza...
[2024-12-05 12:16:48] INFO - [CLEAN] Duplicatas removidas: 0
[2024-12-05 12:16:48] INFO - [CLEAN] Registros válidos: 4,315
[2024-12-05 12:16:48] INFO - [VALIDATE] Iniciando validações...
[2024-12-05 12:16:48] INFO - [VALIDATE] Registros inválidos removidos: 0
[2024-12-05 12:16:48] INFO - [VALIDATE] Taxa validação: 100.00%
[2024-12-05 12:16:48] INFO - [ENRICH] Iniciando enriquecimento...
[2024-12-05 12:16:48] INFO - [ENRICH] Campos adicionados: stay_days, daily_cost, age_group, death, specialty_name
[2024-12-05 12:16:48] INFO - [TRANSFORM] Concluído: 4,315 registros
```

---

### Load

- **Input:** DataFrame clean + metadata
- **Output:** CSV + Parquet files

```python
# CSV
df.to_csv(csv_path, index=False, encoding='utf-8')

# Parquet
df.to_parquet(parquet_path, index=False, engine='pyarrow')

# Metadata
metadata = {
    'state': 'AC',
    'year': 2024,
    'month': 1,
    'records': 4315,
    'columns': 120,  # 115 original + 5 calculados
    'csv_path': '/path/to/SIH_AC_202401.csv',
    'parquet_path': '/path/to/SIH_AC_202401.parquet',
    'csv_size_mb': 2.7,
    'parquet_size_mb': 0.32,
    'timestamp': '2024-12-05T12:16:49'
}
```

**Logs:**

```
[2024-12-05 12:16:48] INFO - [LOAD] Salvando: AC 2024/01
[2024-12-05 12:16:49] INFO - [LOAD] Salvando CSV: /path/SIH_AC_202401.csv
[2024-12-05 12:16:49] INFO - [LOAD] Salvando Parquet: /path/SIH_AC_202401.parquet
[2024-12-05 12:16:49] INFO - [LOAD] CSV: 2.70 MB
[2024-12-05 12:16:49] INFO - [LOAD] Parquet: 0.32 MB
[2024-12-05 12:16:49] INFO - [LOAD] Concluído: 4,315 registros
```

---

## Qualidade de Dados

### Métricas AC Janeiro 2024

```
Completude:
├─ N_AIH:        100% (4,315/4,315)
├─ DT_INTER:     100% (4,315/4,315)
├─ DT_SAIDA:     100% (4,315/4,315)
├─ IDADE:         99% (estimado)
└─ VAL_TOT:      100% (4,315/4,315)

Acurácia:
├─ Datas lógicas:         100% (0 registros DT_INTER > DT_SAIDA)
├─ Idade válida:          100% (0 registros fora 0-120)
└─ Valores positivos:     100% (0 valores negativos)

Consistência:
├─ Duplicatas:            0
└─ Formatos inconsistentes: 0 (após conversão tipos)

Taxa Validação Geral:     100%
```

### Campos com Nulos Esperados

Alguns campos têm nulos por design:

| Campo        | Nulos Esperados | Razão                           |
| ------------ | --------------- | ------------------------------- |
| `DIAG_SECUN` | Sim             | Diagnóstico secundário opcional |
| `UTI_MES_*`  | Sim             | Apenas se usou UTI              |
| `VAL_UTI`    | Sim             | Apenas se usou UTI              |
| `CID_ASSO`   | Sim             | CID associado opcional          |

---

## Limitações Conhecidas

### 1. Especialidade (ESPEC)

**Problema:** Código numérico sem descrição legível

**Solução POC:** Campo `specialty_name` = `ESPEC.astype(str)`

**Solução MVP:** Integrar tabela SIGTAP completa

```python
# Atual (POC)
df['specialty_name'] = df['ESPEC'].astype(str)  # "03"

# Futuro (MVP)
specialty_map = load_sigtap_table('especialidades')
df['specialty_name'] = df['ESPEC'].map(specialty_map)  # "Clínica Médica"
```

---

### 2. Procedimentos (PROC_REA)

**Problema:** Códigos SIGTAP sem descrição

**Impacto:** Análises requerem consulta manual tabela

**Solução MVP:** Carregar tabela procedimentos SIGTAP

---

### 3. CID-10 Secundário

**Problema:** ~60% registros sem diagnóstico secundário

**Impacto:** Análise comorbidades limitada

**Mitigação:** Focar em DIAG_PRINC para análises POC

---

### 4. Encoding Original

**Problema:** Arquivos .dbc em CP850 (DOS Latin 1)

**Solução:** pysus já converte para UTF-8 automaticamente

**Impacto POC:** Zero (abstrado pela biblioteca)

---

### 5. Volume POC Limitado

**Problema:** Apenas AC+ES (~19k registros) vs Brasil completo (~1.2M/mês)

**Impacto:**

- Análises estatísticas menos robustas
- Padrões nacionais não capturados

**Justificativa:** Trade-off consciente POC vs tempo desenvolvimento

---

## Referências

### Oficial DATASUS

- [Portal DataSUS](https://datasus.saude.gov.br/)
- [Dicionário de Dados SIH](http://sihd.datasus.gov.br/principal/index.php)
- [Tabela CID-10](https://datasus.saude.gov.br/cid10/)
- [Sistema SIGTAP](http://sigtap.datasus.gov.br/)

### Técnicas

- [pysus GitHub](https://github.com/AlertaDengue/PySUS)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Parquet Format](https://parquet.apache.org/)

### Regulamentação

- Portaria SAS/MS nº 142/2014 (Tabela procedimentos)
- Resolução CIT nº 4/2012 (Financiamento SUS)
- Lei 8.080/1990 (Lei Orgânica da Saúde)
