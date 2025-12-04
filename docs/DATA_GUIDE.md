# DATA GUIDE

- **Sistema:** DataSUS Healthcare Analytics
- **Versão:** 1.0.0 POC
- **Última Atualização:** 03/12/2024

**Propósito:** Single Source of Truth para tudo relacionado a dados: fonte,
dicionário de campos, códigos, regras de negócio, validações e workflows ETL.

---

## Índice

1. [Fonte de Dados](#fonte-de-dados)
2. [Dicionário de Campos](#dicionário-de-campos)
3. [Tabelas Auxiliares e Códigos](#tabelas-auxiliares-e-códigos)
4. [Regras de Negócio](#regras-de-negócio)
5. [Workflows ETL](#workflows-etl)
6. [Qualidade de Dados](#qualidade-de-dados)
7. [Exemplos de Queries](#exemplos-de-queries)

---

## Fonte de Dados

### DataSUS - Sistema de Informações Hospitalares (SIH)

- **Origem:** Ministério da Saúde / DATASUS
- **Sistema:** SIH/SUS (Sistema de Informações Hospitalares)
- **Formato:** DBC (DataBase Compressed - proprietário DBF comprimido)
- **Frequência:** Mensal
- **Cobertura:** Nacional (27 UFs)
- **Período Disponível:** 2008-presente

### Localização FTP

```
Servidor: ftp.datasus.gov.br
Porta:    21
Usuário:  anonymous
Senha:    qualquer email válido

Caminho:  /dissemin/publicos/SIHSUS/200801_/Dados/

Nomenclatura: RDSSAAMM.dbc
  RD = Tipo (Dados Reduzidos)
  SS = Estado (AC, SP, RJ, etc)
  AA = Ano (24 = 2024)
  MM = Mês (01-12)

Exemplo: RDAC2401.dbc = Acre, Janeiro/2024
```

### Tipos de Arquivos SIH

```
┌────────────────────────────────────────────────────────────────────────┐
│ TIPO │ NOME COMPLETO          │ CONTEÚDO              │ TAMANHO        │
├──────┼────────────────────────┼───────────────────────┼────────────────┤
│ RD   │ Dados Reduzidos        │ ~90% dos campos       │ Menor          │
│      │ [USADO NO PROJETO]     │ Dados essenciais      │ (~500 KB AC)   │
│      │                        │                       │                │
│ RJ   │ Dados Rejeitados       │ AIHs rejeitadas       │ Pequeno        │
│      │                        │                       │                │
│ ER   │ Dados de Erro          │ Motivos rejeição      │ Muito pequeno  │
│      │                        │                       │                │
│ SP   │ Serviços Profissionais │ Detalhamento serviços │ Grande         │
│      │                        │ Procedimentos         │ (~2-5 MB)      │
└──────┴────────────────────────┴───────────────────────┴────────────────┘
```

---

## Dicionário de Campos

### Campos de Identificação

```
┌────────────────────────────────────────────────────────────────────────┐
│ CAMPO      │ TIPO    │ TAMANHO │ DESCRIÇÃO                             │
├────────────┼─────────┼─────────┼───────────────────────────────────────┤
│ N_AIH      │ String  │ 13      │ Número da AIH                         │
│            │         │         │ Chave primária única                  │
│            │         │         │ Exemplo: 1234567890123                │
│            │         │         │                                       │
│ CNES       │ String  │ 7       │ Código estabelecimento                │
│            │         │         │ Cadastro Nacional                     │
│            │         │         │ Exemplo: 2000105                      │
│            │         │         │                                       │
│ CGC_HOSP   │ String  │ 14      │ CNPJ do hospital                      │
│            │         │         │ Exemplo: 12345678000190               │
│            │         │         │                                       │
│ UF_ZI      │ String  │ 2       │ UF residência paciente                │
│            │         │         │ Exemplo: AC, SP, RJ                   │
│            │         │         │                                       │
│ MUNIC_RES  │ String  │ 6       │ Município residência (IBGE)           │
│            │         │         │ Exemplo: 120001                       │
│            │         │         │                                       │
│ MUNIC_MOV  │ String  │ 6       │ Município hospital (IBGE)             │
│            │         │         │ Exemplo: 120001                       │
└────────────┴─────────┴─────────┴───────────────────────────────────────┘
```

### Campos de Datas e Tempo

```
┌────────────────────────────────────────────────────────────────────────┐
│ CAMPO      │ TIPO    │ FORMATO  │ DESCRIÇÃO                            │
├────────────┼─────────┼──────────┼──────────────────────────────────────┤
│ DT_INTER   │ Date    │ YYYYMMDD │ Data de internação                   │
│            │         │          │ Exemplo: 20240115                    │
│            │         │          │ Conversão: pd.to_datetime()          │
│            │         │          │                                      │
│ DT_SAIDA   │ Date    │ YYYYMMDD │ Data de alta/saída                   │
│            │         │          │ Exemplo: 20240122                    │
│            │         │          │ Conversão: pd.to_datetime()          │
│            │         │          │                                      │
│ DIAS_PERM  │ Integer │ -        │ Dias de permanência                  │
│            │         │          │ Calculado: DT_SAIDA - DT_INTER       │
│            │         │          │ Exemplo: 7                           │
│            │         │          │ Range válido: 0-365                  │
│            │         │          │                                      │
│ ANO_CMPT   │ Integer │ YYYY     │ Ano de competência                   │
│            │         │          │ Exemplo: 2024                        │
│            │         │          │                                      │
│ MES_CMPT   │ Integer │ MM       │ Mês de competência                   │
│            │         │          │ Exemplo: 1 (Janeiro)                 │
└────────────┴─────────┴──────────┴──────────────────────────────────────┘
```

### Campos Clínicos

```
┌────────────────────────────────────────────────────────────────────────┐
│ CAMPO        │ TIPO    │ TAMANHO │ DESCRIÇÃO                           │
├──────────────┼─────────┼─────────┼─────────────────────────────────────┤
│ ESPEC        │ String  │ 2       │ Especialidade                       │
│              │         │         │ 01-12 (ver tabela auxiliar)         │
│              │         │         │ Exemplo: 01 = Cirurgia              │
│              │         │         │                                     │
│ DIAG_PRINC   │ String  │ 4       │ Diagnóstico principal (CID-10)      │
│              │         │         │ Exemplo: A001, I210                 │
│              │         │         │                                     │
│ DIAG_SECUN   │ String  │ 4       │ Diagnóstico secundário (CID-10)     │
│              │         │         │ Opcional, ~50% nulo                 │
│              │         │         │                                     │
│ PROC_REA     │ String  │ 10      │ Procedimento realizado (SIGTAP)     │
│              │         │         │ Exemplo: 0201010135                 │
│              │         │         │                                     │
│ PROC_SOLIC   │ String  │ 10      │ Procedimento solicitado             │
│              │         │         │ Pode diferir do realizado           │
│              │         │         │                                     │
│ CAR_INT      │ String  │ 2       │ Caráter da internação               │
│              │         │         │ 1=Eletivo, 2=Urgência               │
│              │         │         │                                     │
│ MORTE        │ Integer │ 1       │ Indicador de óbito                  │
│              │         │         │ 0=Não, 1=Sim                        │
│              │         │         │                                     │
│ COBRANCA     │ String  │ 2       │ Tipo de alta                        │
│              │         │         │ 11-24 (ver tabela auxiliar)         │
└──────────────┴─────────┴─────────┴─────────────────────────────────────┘
```

### Campos Demográficos

```
┌────────────────────────────────────────────────────────────────────────┐
│ CAMPO      │ TIPO    │ VALORES     │ DESCRIÇÃO                         │
├────────────┼─────────┼─────────────┼───────────────────────────────────┤
│ IDADE      │ Integer │ 0-999       │ Idade do paciente                 │
│            │         │             │ Range válido: 0-120               │
│            │         │             │                                   │
│ SEXO       │ String  │ 1, 3        │ Sexo                              │
│            │         │             │ 1=Masculino, 3=Feminino           │
│            │         │             │ ATENÇÃO: 3 não é typo             │
│            │         │             │                                   │
│ RACA_COR   │ String  │ 01-05, 99   │ Raça/Cor (IBGE)                   │
│            │         │             │ 01=Branca, 02=Preta, 03=Parda     │
│            │         │             │ 04=Amarela, 05=Indígena           │
│            │         │             │ 99=Não informado                  │
│            │         │             │ NOTA: 30-40% nulo/99              │
│            │         │             │                                   │
│ NASC       │ Date    │ YYYYMMDD    │ Data de nascimento                │
│            │         │             │ Opcional, nem sempre preenchido   │
│            │         │             │ Redundante com IDADE              │
└────────────┴─────────┴─────────────┴───────────────────────────────────┘
```

### Campos Financeiros

```
┌──────────────────────────────────────────────────────────────────────┐
│ CAMPO         │ TIPO          │ DESCRIÇÃO                            │
├───────────────┼───────────────┼──────────────────────────────────────┤
│ VAL_SH        │ Decimal(10,2) │ Valor serviços hospitalares          │
│               │               │ Exemplo: 1234.56                     │
│               │               │                                      │
│ VAL_SP        │ Decimal(10,2) │ Valor serviços profissionais         │
│               │               │ Exemplo: 234.50                      │
│               │               │                                      │
│ VAL_SADT      │ Decimal(10,2) │ Valor SADT (exames)                  │
│               │               │ Exemplo: 456.78                      │
│               │               │                                      │
│ VAL_RN        │ Decimal(10,2) │ Valor recém-nascido                  │
│               │               │                                      │
│ VAL_ACOMP     │ Decimal(10,2) │ Valor acompanhante                   │
│               │               │                                      │
│ VAL_ORTP      │ Decimal(10,2) │ Valor órteses/próteses               │
│               │               │                                      │
│ VAL_SANGUE    │ Decimal(10,2) │ Valor hemoterapia                    │
│               │               │                                      │
│ VAL_SADTSR    │ Decimal(10,2) │ Valor SADT serviço                   │
│               │               │                                      │
│ VAL_TRANSP    │ Decimal(10,2) │ Valor transporte                     │
│               │               │                                      │
│ VAL_TOT       │ Decimal(10,2) │ VALOR TOTAL AIH                      │
│               │               │ Soma de todos acima                  │
│               │               │ Exemplo: 1975.84                     │
└───────────────┴───────────────┴──────────────────────────────────────┘

REGRA CRÍTICA:
VAL_TOT = VAL_SH + VAL_SP + VAL_SADT + VAL_RN + VAL_ACOMP +
          VAL_ORTP + VAL_SANGUE + VAL_SADTSR + VAL_TRANSP

Tolerância: ±R$ 1,00 (arredondamentos aceitáveis)
Validação obrigatória no Transform
```

### Campos Calculados (Enriquecimento)

```
┌────────────────────────────────────────────────────────────────────────┐
│ CAMPO              │ TIPO       │ ORIGEM            │ DESCRIÇÃO        │
├────────────────────┼────────────┼───────────────────┼──────────────────┤
│ faixa_etaria       │ String     │ IDADE             │ Categorização    │
│                    │            │                   │ etária           │
│                    │            │                   │                  │
│ especialidade_nome │ String     │ ESPEC             │ Nome legível     │
│                    │            │                   │                  │
│ custo_dia          │ Float      │ VAL_TOT /         │ Custo médio      │
│                    │            │ DIAS_PERM         │ diário           │
│                    │            │                   │                  │
│ mes_ano            │ Period[M]  │ DT_INTER          │ Agregação        │
│                    │            │                   │ temporal         │
│                    │            │                   │                  │
│ obito              │ Boolean    │ MORTE             │ Flag boolean     │
│                    │            │                   │                  │
│ carater_nome       │ String     │ CAR_INT           │ Nome legível     │
│                    │            │                   │                  │
│ sexo_nome          │ String     │ SEXO              │ Nome legível     │
└────────────────────┴────────────┴───────────────────┴──────────────────┘
```

---

## Tabelas Auxiliares e Códigos

### Especialidades (ESPEC)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ CÓDIGO │ DESCRIÇÃO                    │ OBSERVAÇÕES                      │
├────────┼──────────────────────────────┼──────────────────────────────────┤
│ 01     │ Cirurgia                     │ Mais comum                       │
│ 02     │ Obstetrícia                  │ Partos e gestação                │
│ 03     │ Clínica Médica               │ Mais comum                       │
│ 04     │ Crônico                      │ Longa permanência                │
│ 05     │ Psiquiatria                  │                                  │
│ 06     │ Pneumologia                  │ Tisiologia                       │
│ 07     │ Pediatria                    │ < 18 anos                        │
│ 08     │ Reabilitação                 │                                  │
│ 09     │ Psiquiatria (Hospital-Dia)   │                                  │
│ 10     │ Geriatria                    │ > 60 anos                        │
│ 11     │ Desintoxicação               │ Dependência química              │
│ 12     │ AIDS                         │ HIV/AIDS                         │
└────────┴──────────────────────────────┴──────────────────────────────────┘
```

### Caráter de Atendimento (CAR_INT)

```
┌────────────────────────────────────────────────────────────────────────┐
│ CÓDIGO │ DESCRIÇÃO               │ % TÍPICO │ TEMPO PERMANÊNCIA MÉDIO  │
├────────┼─────────────────────────┼──────────┼──────────────────────────┤
│ 1      │ Eletivo                 │ ~40%     │ Mais longo (~8-10 dias)  │
│        │ (programado, agendado)  │          │                          │
│        │                         │          │                          │
│ 2      │ Urgência/Emergência     │ ~60%     │ Mais curto (~4-6 dias)   │
│        │ (não programado)        │          │                          │
└────────┴─────────────────────────┴──────────┴──────────────────────────┘
```

### Tipo de Alta (COBRANCA)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ CÓDIGO │ DESCRIÇÃO                          │ OBSERVAÇÕES               │
├────────┼────────────────────────────────────┼───────────────────────────┤
│ 11     │ Alta curado                        │ Mais comum                │
│ 12     │ Alta melhorado                     │ Comum                     │
│ 14     │ Alta a pedido                      │ Contra indicação médica   │
│ 15     │ Alta com previsão de retorno       │ Continua tratamento       │
│ 16     │ Alta por óbito                     │ MORTE=1 obrigatório       │
│ 18     │ Alta por evasão                    │ Abandono                  │
│ 19     │ Alta por outros motivos            │                           │
│ 21     │ Permanência                        │ Ainda internado           │
│ 22     │ Alta paciente agudo (psiq)         │                           │
│ 23     │ Alta paciente crônico (psiq)       │                           │
│ 24     │ Alta melhorado (psiq)              │                           │
└────────┴────────────────────────────────────┴───────────────────────────┘
```

### CID-10 (Diagnósticos)

**Estrutura:** Letra + 3 dígitos (ex: A001, I210, J180)

**Capítulos principais:**

```
A00-B99   Doenças infecciosas e parasitárias
C00-D48   Neoplasias
E00-E90   Doenças endócrinas, nutricionais e metabólicas
I00-I99   Doenças do aparelho circulatório
J00-J99   Doenças do aparelho respiratório
K00-K93   Doenças do aparelho digestivo
O00-O99   Gravidez, parto e puerpério
S00-T98   Lesões, envenenamento
```

**Referência:** <https://cid10.com.br>

### SIGTAP (Procedimentos)

**Estrutura:** 10 dígitos  
**Formato:** 02 01 01 01 35

```
││ ││ ││ ││ └└─ Sub-procedimento
││ ││ ││ └└──── Procedimento
││ ││ └└──────── Sub-grupo
││ └└────────── Grupo
└└──────────── Forma de organização
```

**Exemplos:**

- 0201010135: Apendicectomia
- 0310010039: Parto normal
- 0211060011: Revascularização miocárdica

**Referência:** <http://sigtap.datasus.gov.br>

---

## Regras de Negócio

### Validações Críticas (Transform)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ VALIDAÇÃO                  │ REGRA                │ AÇÃO SE FALHAR      │
├────────────────────────────┼──────────────────────┼─────────────────────┤
│ Chave primária             │ N_AIH não nulo       │ REMOVER registro    │
│                            │ N_AIH único          │ REMOVER duplicata   │
│                            │                      │                     │
│ Datas válidas              │ DT_INTER <= DT_SAIDA │ REMOVER registro    │
│                            │ DT_INTER >= 2008     │ REMOVER registro    │
│                            │ DT_SAIDA <= hoje     │ REMOVER registro    │
│                            │                      │                     │
│ Permanência                │ DIAS_PERM >= 0       │ REMOVER registro    │
│                            │ DIAS_PERM <= 365     │ FLAG outlier        │
│                            │                      │                     │
│ Valores financeiros        │ VAL_TOT > 0          │ REMOVER registro    │
│                            │ VAL_TOT < 1000000    │ FLAG outlier        │
│                            │ Soma componentes OK  │ FLAG inconsistência │
│                            │                      │                     │
│ Idade                      │ IDADE >= 0           │ REMOVER registro    │
│                            │ IDADE <= 120         │ FLAG outlier        │
│                            │                      │                     │
│ Consistência óbito         │ Se MORTE=1 então     │ FLAG inconsistência │
│                            │ COBRANCA=16          │                     │
└────────────────────────────┴──────────────────────┴─────────────────────┘
```

### Regras de Enriquecimento

**Faixa Etária:**

```python
def categorizar_idade(idade):
    if pd.isna(idade):
        return 'Não informado'
    elif idade < 1:
        return 'Recém-nascido'
    elif idade < 12:
        return 'Criança (1-11 anos)'
    elif idade < 18:
        return 'Adolescente (12-17 anos)'
    elif idade < 60:
        return 'Adulto (18-59 anos)'
    else:
        return 'Idoso (60+ anos)'
```

**Custo Diário:**

```python
df['custo_dia'] = df['VAL_TOT'] / df['DIAS_PERM'].replace(0, 1)
# Evita divisão por zero substituindo 0 por 1
```

**Indicador Óbito:**

```python
df['obito'] = df['MORTE'].isin([1, '1'])
# Boolean: True se óbito, False caso contrário
```

### Critérios de Qualidade

```
┌─────────────────────────────────────────────────────────────────────────┐
│ MÉTRICA                    │ MÍNIMO ACEITÁVEL     │ IDEAL               │
├────────────────────────────┼──────────────────────┼─────────────────────┤
│ Taxa de registros válidos  │ >= 85%               │ >= 95%              │
│                            │                      │                     │
│ Campos críticos preenchidos│ >= 90%               │ >= 98%              │
│ (N_AIH, datas, valores)    │                      │                     │
│                            │                      │                     │
│ Consistência financeira    │ >= 95%               │ >= 99%              │
│ (soma componentes)         │                      │                     │
│                            │                      │                     │
│ Duplicatas                 │ < 1%                 │ < 0.1%              │
└────────────────────────────┴──────────────────────┴─────────────────────┘
```

---

## Workflows ETL

### Extract (pysus + FTP)

```python
# Workflow Extract
from pysus.online_data import SIH

# 1. Download automático via pysus
sih = SIH()
df_raw = sih.download(state='AC', year=2024, month=1, group='RD')

# Tempo esperado: 30-90 segundos
# Tamanho: ~500KB comprimido, ~1-2MB descomprimido
# Saída: DataFrame pandas com ~80 colunas

# 2. Backup local (cache)
import shutil
shutil.copy('RDAC2401.dbc', 'data/raw/RDAC2401.dbc')

# 3. Log
print(f"[EXTRACT] Registros extraídos: {len(df_raw)}")
print(f"[EXTRACT] Colunas: {len(df_raw.columns)}")
```

**Tratamento de Erros Extract:**

```python
# FTP instável: retry com backoff
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def extract_datasus(state, year, month):
    sih = SIH()
    return sih.download(state=state, year=year, month=month, group='RD')

# Fallback: usar arquivo local cache se FTP falhar
try:
    df = extract_datasus('AC', 2024, 1)
except Exception as e:
    print(f"[EXTRACT ERROR] FTP failed: {e}")
    print("[EXTRACT] Loading from cache...")
    df = pd.read_parquet('data/raw/cache/RDAC2401.parquet')
```

### Transform (Limpeza + Validação + Enriquecimento)

```python
# Workflow Transform (4 etapas)
import pandas as pd
import numpy as np

# ============================================================================
# ETAPA 1: Conversão de Tipos
# ============================================================================
def etapa1_conversao_tipos(df):
    """Converte tipos de dados brutos para corretos"""

    # Datas
    df['DT_INTER'] = pd.to_datetime(df['DT_INTER'], format='%Y%m%d', errors='coerce')
    df['DT_SAIDA'] = pd.to_datetime(df['DT_SAIDA'], format='%Y%m%d', errors='coerce')

    # Numéricos
    numeric_cols = ['IDADE', 'DIAS_PERM', 'VAL_TOT', 'VAL_SH', 'VAL_SP',
                    'VAL_SADT', 'MORTE']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Categóricos
    categorical_cols = ['SEXO', 'ESPEC', 'CAR_INT', 'UF_ZI']
    for col in categorical_cols:
        df[col] = df[col].astype(str)

    return df

# ============================================================================
# ETAPA 2: Limpeza
# ============================================================================
def etapa2_limpeza(df):
    """Remove registros inválidos"""

    initial_count = len(df)

    # 1. Remover duplicatas
    df = df.drop_duplicates(subset=['N_AIH'], keep='first')
    duplicates_removed = initial_count - len(df)

    # 2. Remover nulos críticos
    df = df.dropna(subset=['N_AIH', 'DT_INTER', 'DT_SAIDA', 'VAL_TOT'])
    nulls_removed = initial_count - duplicates_removed - len(df)

    print(f"[LIMPEZA] Duplicatas removidas: {duplicates_removed}")
    print(f"[LIMPEZA] Nulos críticos removidos: {nulls_removed}")

    return df

# ============================================================================
# ETAPA 3: Validação
# ============================================================================
def etapa3_validacao(df):
    """Valida regras de negócio"""

    initial_count = len(df)

    # Datas válidas
    df = df[df['DT_INTER'] <= df['DT_SAIDA']]
    df = df[df['DT_INTER'] >= pd.Timestamp('2008-01-01')]
    df = df[df['DT_SAIDA'] <= pd.Timestamp.now()]

    # Permanência válida
    df = df[df['DIAS_PERM'] >= 0]

    # Valores válidos
    df = df[df['VAL_TOT'] > 0]
    df = df[df['VAL_TOT'] < 1000000]

    # Idade válida
    df = df[(df['IDADE'] >= 0) & (df['IDADE'] <= 120)]

    invalid_removed = initial_count - len(df)
    print(f"[VALIDAÇÃO] Registros inválidos removidos: {invalid_removed}")

    return df

# ============================================================================
# ETAPA 4: Enriquecimento
# ============================================================================
def etapa4_enriquecimento(df):
    """Adiciona campos calculados"""

    # Faixa etária
    df['faixa_etaria'] = df['IDADE'].apply(categorizar_idade)

    # Especialidade nome
    especialidades_map = {
        '01': 'Cirurgia', '02': 'Obstetrícia', '03': 'Clínica Médica',
        '04': 'Crônico', '05': 'Psiquiatria', '06': 'Pneumologia',
        '07': 'Pediatria', '08': 'Reabilitação', '09': 'Psiquiatria (HD)',
        '10': 'Geriatria', '11': 'Desintoxicação', '12': 'AIDS'
    }
    df['especialidade_nome'] = df['ESPEC'].map(especialidades_map)

    # Custo diário
    df['custo_dia'] = df['VAL_TOT'] / df['DIAS_PERM'].replace(0, 1)

    # Mês/ano
    df['mes_ano'] = df['DT_INTER'].dt.to_period('M')

    # Óbito
    df['obito'] = df['MORTE'].isin([1, '1'])

    # Caráter e sexo nomes
    df['carater_nome'] = df['CAR_INT'].map({'1': 'Eletivo', '2': 'Urgência/Emergência'})
    df['sexo_nome'] = df['SEXO'].map({'1': 'Masculino', '3': 'Feminino'})

    print(f"[ENRIQUECIMENTO] {len(df.columns)} colunas totais (incluindo calculadas)")

    return df

# ============================================================================
# Pipeline Transform Completo
# ============================================================================
def transform_pipeline(df_raw):
    """Executa pipeline transform completo"""

    print("[TRANSFORM] Iniciando pipeline...")
    print(f"[TRANSFORM] Registros iniciais: {len(df_raw)}")

    df = etapa1_conversao_tipos(df_raw)
    df = etapa2_limpeza(df)
    df = etapa3_validacao(df)
    df = etapa4_enriquecimento(df)

    print(f"[TRANSFORM] Registros finais: {len(df)}")
    perda = ((len(df_raw) - len(df)) / len(df_raw)) * 100
    print(f"[TRANSFORM] Taxa de perda: {perda:.2f}%")

    return df
```

### Load (CSV + Parquet)

```python
# Workflow Load (formato dual)
import os
from datetime import datetime

def load_dual_format(df, state, year, month):
    """Salva em CSV e Parquet simultaneamente"""

    # Criar diretórios
    os.makedirs('data/processed', exist_ok=True)

    # Nomenclatura padronizada
    filename_base = f"sih_{state}_{year}{month:02d}"
    csv_path = f"data/processed/{filename_base}.csv"
    parquet_path = f"data/processed/{filename_base}.parquet"

    # Salvar CSV
    print(f"[LOAD] Salvando CSV: {csv_path}")
    df.to_csv(csv_path, index=False, encoding='utf-8')
    csv_size = os.path.getsize(csv_path) / 1024 / 1024
    print(f"[LOAD] CSV size: {csv_size:.2f} MB")

    # Salvar Parquet
    print(f"[LOAD] Salvando Parquet: {parquet_path}")
    df.to_parquet(parquet_path, index=False, compression='snappy')
    parquet_size = os.path.getsize(parquet_path) / 1024 / 1024
    print(f"[LOAD] Parquet size: {parquet_size:.2f} MB")

    # Comparação
    reducao = ((csv_size - parquet_size) / csv_size) * 100
    print(f"[LOAD] Redução Parquet: {reducao:.1f}%")

    # Metadata
    metadata = {
        'state': state,
        'year': year,
        'month': month,
        'records': len(df),
        'columns': len(df.columns),
        'csv_size_mb': round(csv_size, 2),
        'parquet_size_mb': round(parquet_size, 2),
        'processed_at': datetime.now().isoformat()
    }

    import json
    metadata_path = f"data/processed/metadata_{state}_{year}{month:02d}.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"[LOAD] Metadata: {metadata_path}")

    return csv_path, parquet_path

# Exemplo de uso
csv_file, parquet_file = load_dual_format(df_clean, 'AC', 2024, 1)
```

---

## Qualidade de Dados

### Taxa de Perda Esperada

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ESTADO         │ REGISTROS │ PERDA ESPERADA │ MOTIVOS PRINCIPAIS        │
├────────────────┼───────────┼────────────────┼───────────────────────────┤
│ Pequeno (AC)   │ ~2k       │ 5-10%          │ - Duplicatas ~1%          │
│                │           │                │ - Datas inválidas ~2-3%   │
│                │           │                │ - Valores negativos ~1%   │
│                │           │                │ - Outliers ~2-3%          │
│                │           │                │                           │
│ Médio (ES)     │ ~20k      │ 8-12%          │ - Duplicatas ~1-2%        │
│                │           │                │ - Datas inválidas ~3-4%   │
│                │           │                │ - Valores negativos ~1-2% │
│                │           │                │ - Outliers ~3-4%          │
│                │           │                │                           │
│ Grande (SP)    │ ~200k     │ 10-15%         │ - Duplicatas ~2-3%        │
│                │           │                │ - Datas inválidas ~4-5%   │
│                │           │                │ - Valores negativos ~2%   │
│                │           │                │ - Outliers ~4-5%          │
└────────────────┴───────────┴────────────────┴───────────────────────────┘
```

### Qualidade por Campo

```
┌────────────────────────────────────────────────────────────────────────┐
│ CAMPO        │ QUALIDADE │ COMPLETUDE │ CONFIABILIDADE                 │
├──────────────┼───────────┼────────────┼────────────────────────────────┤
│ N_AIH        │ Excelente │ 99.9%      │ Chave primária confiável       │
│ DT_INTER     │ Ótima     │ 99%        │ Poucos erros                   │
│ DT_SAIDA     │ Ótima     │ 99%        │ Poucos erros                   │
│ DIAS_PERM    │ Boa       │ 98%        │ Requer validação               │
│ VAL_TOT      │ Boa       │ 97%        │ Verificar consistência         │
│ ESPEC        │ Excelente │ 99.5%      │ Bem preenchido                 │
│ DIAG_PRINC   │ Boa       │ 95%        │ Alguns códigos inválidos       │
│ PROC_REA     │ Boa       │ 94%        │ Alguns códigos inválidos       │
│ SEXO         │ Excelente │ 99.8%      │ Bem preenchido                 │
│ IDADE        │ Ótima     │ 98%        │ Poucos outliers                │
│ RACA_COR     │ Ruim      │ 60-70%     │ 30-40% não preenchido          │
│ DIAG_SECUN   │ Média     │ 50-60%     │ Frequentemente vazio           │
│ NASC         │ Média     │ 80%        │ Redundante com IDADE           │
│ CEP          │ Média     │ 75-80%     │ Muitos nulos/inválidos         │
└──────────────┴───────────┴────────────┴────────────────────────────────┘
```

---

## Exemplos de Queries

### Queries Básicas (POC - CSV/Parquet)

```python
# Carregar dados
df = pd.read_parquet('data/processed/sih_AC_202401.parquet')

# KPI 1: Volume de internações
total_internacoes = len(df)

# KPI 2: Tempo médio de permanência (TMP)
tmp = df['DIAS_PERM'].mean()

# KPI 3: Taxa de mortalidade
taxa_mortalidade = (df['obito'].sum() / len(df)) * 100

# KPI 4: Receita total
receita_total = df['VAL_TOT'].sum()

# KPI 5: Ticket médio
ticket_medio = df['VAL_TOT'].mean()

# Distribuição por especialidade
dist_espec = df.groupby('especialidade_nome').size().sort_values(ascending=False)

# Distribuição por faixa etária
dist_idade = df.groupby('faixa_etaria').size().sort_values(ascending=False)

# Top 10 diagnósticos
top_diag = df['DIAG_PRINC'].value_counts().head(10)
```

### Queries Agregadas

```python
# Análise por especialidade
analise_espec = df.groupby('especialidade_nome').agg({
    'N_AIH': 'count',
    'DIAS_PERM': 'mean',
    'VAL_TOT': ['sum', 'mean'],
    'obito': 'sum'
}).round(2)

# Análise temporal
analise_tempo = df.groupby('mes_ano').agg({
    'N_AIH': 'count',
    'VAL_TOT': 'sum',
    'DIAS_PERM': 'mean'
}).round(2)

# Análise comparativa Eletivo vs Urgência
analise_carater = df.groupby('carater_nome').agg({
    'N_AIH': 'count',
    'DIAS_PERM': 'mean',
    'VAL_TOT': 'mean',
    'obito': lambda x: (x.sum() / len(x)) * 100
}).round(2)
```

### Queries SQL (MVP - Oracle)

```sql
-- KPI: Taxa de Ocupação Mensal
SELECT
    TRUNC(dt_internacao, 'MM') AS mes_ref,
    COUNT(*) AS total_internacoes,
    SUM(dias_permanencia) AS total_dias_perm,
    ROUND(AVG(dias_permanencia), 2) AS tmp_medio
FROM sih_internacoes
GROUP BY TRUNC(dt_internacao, 'MM')
ORDER BY mes_ref DESC;

-- KPI: Receita por Especialidade
SELECT
    e.nome_espec,
    COUNT(i.n_aih) AS total_internacoes,
    SUM(i.val_tot) AS receita_total,
    ROUND(AVG(i.val_tot), 2) AS ticket_medio
FROM sih_internacoes i
JOIN dim_especialidades e ON i.espec = e.cod_espec
GROUP BY e.nome_espec
ORDER BY receita_total DESC;

-- Análise Mortalidade por Faixa Etária
SELECT
    CASE
        WHEN idade < 1 THEN 'Recém-nascido'
        WHEN idade < 12 THEN 'Criança (1-11)'
        WHEN idade < 18 THEN 'Adolescente (12-17)'
        WHEN idade < 60 THEN 'Adulto (18-59)'
        ELSE 'Idoso (60+)'
    END AS faixa_etaria,
    COUNT(*) AS total_internacoes,
    SUM(CASE WHEN morte = '1' THEN 1 ELSE 0 END) AS total_obitos,
    ROUND(
        (SUM(CASE WHEN morte = '1' THEN 1 ELSE 0 END) / COUNT(*)) * 100,
        2
    ) AS taxa_mortalidade
FROM sih_internacoes
GROUP BY
    CASE
        WHEN idade < 1 THEN 'Recém-nascido'
        WHEN idade < 12 THEN 'Criança (1-11)'
        WHEN idade < 18 THEN 'Adolescente (12-17)'
        WHEN idade < 60 THEN 'Adulto (18-59)'
        ELSE 'Idoso (60+)'
    END
ORDER BY taxa_mortalidade DESC;
```

---

- **Última Atualização:** 03/12/2024
- **Próxima Revisão:** Após conclusão POC (07/12/2024)

**Veja Também:**

- [README.md](../README.md) - Entry point do projeto
- [ARCHITECTURE.md](ARCHITECTURE.md) - Stack técnico e ADRs
- [ROADMAP.md](ROADMAP.md) - Planejamento e cronograma
