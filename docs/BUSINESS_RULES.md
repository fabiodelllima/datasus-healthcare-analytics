# REGRAS DE NEGÓCIO

- **Versão:** 1.0.0 POC
- **Última atualização:** 24/12/2025

**Propósito:** Single Source of Truth para **TODAS** as regras de validação, transformação e enriquecimento do pipeline ETL. Este documento é a base para especificações BDD, testes TDD e implementação de código.

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Regras de Conversão de Tipos](#regras-de-conversão-de-tipos)
3. [Regras de Limpeza](#regras-de-limpeza)
4. [Regras de Validação](#regras-de-validação)
5. [Regras de Enriquecimento](#regras-de-enriquecimento)
6. [Métricas de Qualidade](#métricas-de-qualidade)
7. [Casos Edge e Tratamento de Erros](#casos-edge-e-tratamento-de-erros)
8. [Impacto em KPIs](#impacto-em-kpis)
9. [Referências Cruzadas](#referências-cruzadas)

---

## Visão Geral

### Hierarquia de Execução

```
1. CONVERSÃO DE TIPOS
   ↓
2. LIMPEZA DE DADOS
   ↓
3. VALIDAÇÃO DE REGRAS
   ↓
4. ENRIQUECIMENTO
   ↓
5. OUTPUT FINAL
```

**Princípio:** Cada etapa assume que as anteriores foram executadas com sucesso.

### Princípios de Design

**Fail Fast:**

- Erros críticos interrompem pipeline imediatamente
- Logging detalhado de cada falha
- Sem "silent failures"

**Data Quality First:**

- Preferir rejeitar dados duvidosos a aceitar dados ruins
- Taxa de validação alvo: > 90% (POC), > 95% (MVP)
- Documentar todas as rejeições

**Idempotência:**

- Pipeline pode ser executado múltiplas vezes no mesmo dataset
- Resultado sempre consistente
- Sem efeitos colaterais

---

## Regras de Conversão de Tipos

### RN-CONV-001: Conversão de Campos Numéricos

**Objetivo:** Converter campos string contendo números para tipo numérico (float64).

**Campos afetados:**

```python
['IDADE', 'VAL_TOT', 'VAL_UTI', 'VAL_SH', 'VAL_SP', 'VAL_SADT']
```

**Regra:**

```python
df[field] = pd.to_numeric(df[field], errors='coerce')
```

**Comportamento:**

| Input (String) | Output (float64) | Razão                 |
| -------------- | ---------------- | --------------------- |
| `"25"`         | `25.0`           | Conversão válida      |
| `"30.5"`       | `30.5`           | Float válido          |
| `"abc"`        | `NaN`            | Não é número - coerce |
| `""`           | `NaN`            | String vazia - coerce |
| `None`         | `NaN`            | Null original         |
| `"1.5e3"`      | `1500.0`         | Notação científica OK |

**Justificativa de Negócio:**

- Permite operações matemáticas (soma, média, comparações)
- NaN preserva informação de "dado ausente" vs "zero"
- Evita erros de tipo em análises downstream

**Impacto em KPIs:**

- Receita Total: Requer VAL_TOT numérico
- TMP (Tempo Médio Permanência): Requer IDADE numérico
- Demografia: Requer IDADE numérico

**Casos Edge:**

1. **Valores negativos:** Aceitos na conversão, rejeitados na validação
2. **Valores muito grandes:** Aceitos se dentro de float64 range
3. **Múltiplos pontos decimais:** `"1.5.3"` → NaN (coerce)

**Testes BDD:**

```gherkin
Scenario: Converter campo numérico válido
  Given um DataFrame com campo "IDADE" = ["25", "30"]
  When executo convert_types()
  Then "IDADE" deve ser tipo float64
  And valores devem ser [25.0, 30.0]

Scenario: Converter valor inválido para NaN
  Given um DataFrame com campo "IDADE" = ["25", "abc", "30"]
  When executo convert_types()
  Then "IDADE"[1] deve ser NaN
  And "IDADE"[0] e "IDADE"[2] devem ser numéricos
```

---

### RN-CONV-002: Conversão de Campos de Data

**Objetivo:** Converter campos string formato YYYYMMDD para datetime64.

**Campos afetados:**

```python
['DT_INTER', 'DT_SAIDA']
```

**Regra:**

```python
df[field] = pd.to_datetime(df[field], format='%Y%m%d', errors='coerce')
```

**Comportamento:**

| Input (String) | Output (datetime64) | Razão                              |
| -------------- | ------------------- | ---------------------------------- |
| `"20240101"`   | `2024-01-01`        | Data válida                        |
| `"20240229"`   | `2024-02-29`        | Ano bissexto OK                    |
| `"20230229"`   | `NaT`               | 2023 não bissexto - inválido       |
| `"20241301"`   | `NaT`               | Mês 13 inválido                    |
| `"20240132"`   | `NaT`               | Dia 32 inválido                    |
| `"abc"`        | `NaT`               | Não é data - coerce                |
| `"2024-01-01"` | `NaT`               | Formato errado (esperado YYYYMMDD) |

**Justificativa de Negócio:**

- Permite operações temporais (diferença de dias, comparações)
- NaT preserva informação de "data ausente"
- Validação de datas lógicas (internação ≤ saída)

**Impacto em KPIs:**

- TMP: Requer DT_INTER e DT_SAIDA para calcular stay_days
- Volume temporal: Agrupamento por mês/ano
- Taxa ocupação: Cálculo de pacientes-dia

**Casos Edge:**

1. **Anos futuros:** Aceitos (ex: 2030), rejeitados na validação de negócio se necessário
2. **Anos muito antigos:** Aceitos (ex: 1900), podem indicar erro de digitação
3. **Formato incorreto:** Qualquer formato ≠ YYYYMMDD → NaT

**Testes BDD:**

```gherkin
Scenario: Converter data válida
  Given um DataFrame com "DT_INTER" = ["20240101", "20240115"]
  When executo convert_types()
  Then "DT_INTER" deve ser tipo datetime64
  And valores devem ser datas válidas

Scenario: Rejeitar data inválida
  Given um DataFrame com "DT_INTER" = ["20240132", "20241301"]
  When executo convert_types()
  Then todos valores "DT_INTER" devem ser NaT

Scenario: Rejeitar formato incorreto
  Given um DataFrame com "DT_INTER" = ["2024-01-01", "01/01/2024"]
  When executo convert_types()
  Then todos valores "DT_INTER" devem ser NaT
```

---

## Regras de Limpeza

### RN-LIMP-001: Remoção de Duplicatas

**Objetivo:** Remover registros completamente idênticos (todas colunas iguais).

**Regra:**

```python
df = df.drop_duplicates()
```

**Comportamento:**

| Cenário                         | Ação                          | Resultado              |
| ------------------------------- | ----------------------------- | ---------------------- |
| 2 registros 100% idênticos      | Remove segundo                | Mantém 1 registro      |
| 3 registros idênticos           | Remove 2º e 3º                | Mantém 1 registro      |
| Registros com 1 campo diferente | Mantém ambos                  | Não são duplicatas     |
| Todos campos None               | Se todos None, são duplicatas | Remove exceto primeiro |

**Justificativa de Negócio:**

- Evita contagem duplicada de internações
- Previne distorção de receita total
- Indica problema de qualidade na fonte

**Impacto em KPIs:**

- Volume Atendimentos: Inflação artificial se duplicatas mantidas
- Receita Total: Duplicação de valores
- TMP: Média distorcida

**Casos Edge:**

1. **N_AIH duplicado com outros campos diferentes:**

   - **NÃO** é duplicata completa
   - Pode indicar múltiplas internações mesmo paciente
   - Mantido

2. **Todos campos None:**

   - São duplicatas se critério for "100% iguais"
   - Primeiro registro mantido

3. **Float NaN vs None:**
   - `pd.isna()` considera ambos como "faltando"
   - Registros com NaN em mesmos campos são duplicatas

**Logging:**

```python
logger.info(f"[CLEAN] Duplicatas removidas: {initial_count - len(df)}")
```

**Testes BDD:**

```gherkin
Scenario: Remover duplicatas completas
  Given um DataFrame com 3 registros
  And registro 1 e 2 são 100% idênticos
  And registro 3 é diferente
  When executo clean_data()
  Then resultado deve ter 2 registros
  And registros devem ser 1 e 3

Scenario: Manter registros com 1 campo diferente
  Given um DataFrame com 2 registros
  And todos campos idênticos exceto "IDADE"
  When executo clean_data()
  Then resultado deve ter 2 registros
```

---

### RN-LIMP-002: Remoção de Nulos em Campos Críticos

**Objetivo:** Remover registros com valores ausentes em campos essenciais.

**Campos críticos:**

```python
['N_AIH', 'DT_INTER', 'DT_SAIDA']
```

**Regra:**

```python
df = df.dropna(subset=critical_fields)
```

**Comportamento:**

| Campo Nulo       | Outros Campos | Ação   | Razão                   |
| ---------------- | ------------- | ------ | ----------------------- |
| `N_AIH` = None   | Completos     | Remove | Sem identificador único |
| `DT_INTER` = NaT | Completos     | Remove | Impossível calcular TMP |
| `DT_SAIDA` = NaT | Completos     | Remove | Impossível calcular TMP |
| `IDADE` = NaN    | Críticos OK   | Mantém | IDADE não é crítico     |

**Justificativa de Negócio:**

**N_AIH:**

- Identificador único da internação
- Sem ele, impossível rastreabilidade
- Requerido para auditoria e compliance

**DT_INTER / DT_SAIDA:**

- Essenciais para TMP (KPI principal)
- Requeridos para timeline da internação
- Sem eles, registro é inútil para análises temporais

**Impacto em KPIs:**

- **TODOS KPIs:** Registros sem campos críticos são inutilizáveis
- Volume correto: Apenas internações rastreáveis contam
- TMP: Impossível calcular sem datas

**Casos Edge:**

1. **N_AIH vazio ("") vs None:**

   - String vazia `""` **NÃO** é None
   - Passa por dropna() mas pode ser inválido
   - Considerar validação adicional se necessário

2. **DT_INTER = DT_SAIDA (mesmo dia):**

   - Não é nulo, é válido
   - Stay_days = 0 (internação dia único)

3. **Todos 3 campos nulos:**
   - Registro removido
   - Caso extremo que indica problema na fonte

**Logging:**

```python
logger.info(f"[CLEAN] Registros válidos: {len(df):,}")
```

**Testes BDD:**

```gherkin
Scenario: Remover registro com N_AIH nulo
  Given um DataFrame com 3 registros
  And registro 2 tem "N_AIH" = None
  When executo clean_data()
  Then resultado deve ter 2 registros
  And N_AIH de todos registros deve estar presente

Scenario: Manter registro com campo não-crítico nulo
  Given um DataFrame com 1 registro
  And "IDADE" = NaN mas campos críticos preenchidos
  When executo clean_data()
  Then resultado deve ter 1 registro
```

---

## Regras de Validação

### RN-VAL-001: Validação de Datas Lógicas

**Objetivo:** Garantir que data de saída ≥ data de internação.

**Regra:**

```python
df = df[df['DT_INTER'] <= df['DT_SAIDA']]
```

**Comportamento:**

| DT_INTER   | DT_SAIDA   | Válido? | Ação        | Razão                           |
| ---------- | ---------- | ------- | ----------- | ------------------------------- |
| 2024-01-10 | 2024-01-15 | ✓       | Mantém      | Lógica correta                  |
| 2024-01-10 | 2024-01-10 | ✓       | Mantém      | Mesmo dia OK                    |
| 2024-01-15 | 2024-01-10 | ✗       | Remove      | Impossível sair antes de entrar |
| 2024-01-10 | NaT        | ?       | Já removido | clean_data() removeu antes      |

**Justificativa de Negócio:**

**Impossibilidade física:**

- Paciente não pode receber alta antes de ser internado
- Indica erro de digitação ou inversão de campos

**Impacto em cálculos:**

- stay_days seria negativo
- TMP ficaria distorcido
- Análises temporais inválidas

**Qualidade de dados:**

- Rejeitar dados logicamente impossíveis
- Sinalizar problema na fonte DataSUS

**Impacto em KPIs:**

- TMP: Stay_days negativo distorce média
- Volume temporal: Internações impossíveis inflam contagem
- Custo diário: Divisão por negativo gera valores absurdos

**Casos Edge:**

1. **DT_INTER = DT_SAIDA (mesmo dia):**

   - **VÁLIDO** (internação de 1 dia)
   - stay_days = 0
   - Exemplo: cirurgias ambulatoriais, observação breve

2. **Diferença > 365 dias:**

   - Tecnicamente válido se DT_INTER ≤ DT_SAIDA
   - Pode indicar erro mas não viola lógica
   - Considerar validação adicional MVP se necessário

3. **Anos diferentes mas lógica correta:**
   - Ex: DT_INTER = 2023-12-28, DT_SAIDA = 2024-01-05
   - Válido (internação virada de ano)

**Logging:**

```python
removed = initial_count - len(df)
logger.info(f"[VALIDATE] Registros inválidos removidos: {removed}")
```

**Testes BDD:**

```gherkin
Scenario: Aceitar datas lógicas corretas
  Given um DataFrame com DT_INTER = 2024-01-10
  And DT_SAIDA = 2024-01-15
  When executo validate_data()
  Then registro deve ser mantido

Scenario: Rejeitar DT_SAIDA anterior a DT_INTER
  Given um DataFrame com DT_INTER = 2024-01-15
  And DT_SAIDA = 2024-01-10
  When executo validate_data()
  Then registro deve ser removido

Scenario: Aceitar internação mesmo dia
  Given um DataFrame com DT_INTER = 2024-01-10
  And DT_SAIDA = 2024-01-10
  When executo validate_data()
  Then registro deve ser mantido
  And stay_days deve ser 0
```

---

### RN-VAL-002: Validação de Idade

**Objetivo:** Garantir idade dentro do range humano plausível (0-120 anos).

**Regra:**

```python
df = df[(df['IDADE'] >= 0) & (df['IDADE'] <= 120)]
```

**Comportamento:**

| IDADE | Válido? | Ação                   | Razão                     |
| ----- | ------- | ---------------------- | ------------------------- |
| 0     | ✓       | Mantém                 | Recém-nascido válido      |
| 25    | ✓       | Mantém                 | Range normal              |
| 120   | ✓       | Mantém                 | Limite superior           |
| 121   | ✗       | Remove                 | Acima do limite           |
| -5    | ✗       | Remove                 | Idade negativa impossível |
| 150   | ✗       | Remove                 | Acima do recorde mundial  |
| NaN   | ?       | Já removido ou mantido | Não é campo crítico       |

**Justificativa de Negócio:**

**Range realista:**

- 0 anos: Recém-nascidos/neonatos válidos
- 120 anos: Recorde mundial ~122 anos (Jeanne Calment)
- Limite generoso mas realista

**Qualidade de dados:**

- Idade negativa: Erro de digitação óbvio
- Idade > 120: Provável erro (troca de campos, século errado)

**Demografia precisa:**

- KPIs demográficos requerem idades válidas
- Análises de mortalidade por faixa etária

**Impacto em KPIs:**

- Demografia: Idades inválidas distorcem distribuição
- Mortalidade: Taxa por faixa etária incorreta
- Especialidade: Pediatria vs geriatria mal classificados

**Casos Edge:**

1. **IDADE = 0 (recém-nascido):**

   - **VÁLIDO** - comum em obstetrícia/neonatologia
   - Não confundir com "idade ausente"

2. **IDADE decimal (ex: 25.5):**

   - Válido se campo aceita float
   - DataSUS pode usar decimais para <2 anos

3. **IDADE = 120 (exatamente):**

   - Válido (no limite)
   - Extremamente raro mas possível

4. **COD_IDADE ≠ anos:**
   - Campo `COD_IDADE` indica unidade (2=anos, 3=meses, 4=dias)
   - Esta validação assume `IDADE` já convertido para anos
   - Conversão deve ocorrer antes se necessário

**Logging:**

```python
logger.info(f"[VALIDATE] Registros com idade inválida removidos: {count}")
```

**Testes BDD:**

```gherkin
Scenario: Aceitar idades válidas
  Given um DataFrame com IDADE = [0, 25, 120]
  When executo validate_data()
  Then todos registros devem ser mantidos

Scenario: Rejeitar idade negativa
  Given um DataFrame com IDADE = [-5, 25, 30]
  When executo validate_data()
  Then resultado deve ter 2 registros
  And IDADE -5 deve ser removida

Scenario: Rejeitar idade acima de 120
  Given um DataFrame com IDADE = [25, 150, 30]
  When executo validate_data()
  Then resultado deve ter 2 registros
  And IDADE 150 deve ser removida

Scenario: Aceitar recém-nascido
  Given um DataFrame com IDADE = 0
  When executo validate_data()
  Then registro deve ser mantido
```

---

### RN-VAL-003: Validação de Valores Monetários

**Objetivo:** Garantir que todos valores financeiros sejam não-negativos.

**Campos afetados:**

```python
['VAL_TOT', 'VAL_UTI', 'VAL_SH', 'VAL_SP', 'VAL_SADT']
```

**Regra:**

```python
for col in value_cols:
    df = df[df[col] >= 0]
```

**Comportamento:**

| Campo   | Valor   | Válido? | Ação   | Razão                   |
| ------- | ------- | ------- | ------ | ----------------------- |
| VAL_TOT | 1500.00 | ✓       | Mantém | Valor positivo normal   |
| VAL_TOT | 0.00    | ✓       | Mantém | Zero válido (sem custo) |
| VAL_TOT | -500.00 | ✗       | Remove | Negativo impossível     |
| VAL_UTI | 0.00    | ✓       | Mantém | Sem uso de UTI          |
| VAL_SH  | -100.00 | ✗       | Remove | Negativo impossível     |

**Justificativa de Negócio:**

**Valores negativos impossíveis:**

- Repasses SUS são sempre ≥ 0
- Negativo indicaria estorno/devolução (não presente em SIH)
- Erro de digitação ou problema na fonte

**Integridade financeira:**

- Receita total seria distorcida
- KPIs financeiros incorretos
- Relatórios para gestão inválidos

**Zero é válido:**

- Alguns serviços podem ter custo zero
- UTI não utilizada → VAL_UTI = 0
- Procedimentos cobertos por outros mecanismos

**Impacto em KPIs:**

- Receita Total: Soma seria incorreta
- Custo Médio: Média distorcida por negativos
- Custo Diário: Valor negativo absurdo

**Casos Edge:**

1. **Todos valores = 0:**

   - **VÁLIDO** tecnicamente
   - Pode indicar internação sem repasse SUS
   - Investigar mas não rejeitar automaticamente

2. **VAL_TOT < soma de componentes:**

   - Possível por arredondamentos
   - Não é esta validação (seria RN-VAL-004 se implementada)

3. **Valores muito altos (outliers):**
   - Tecnicamente válidos se ≥ 0
   - Podem ser legítimos (UTI prolongada, procedimentos complexos)
   - Considerar validação de outliers estatísticos no MVP

**Logging:**

```python
logger.info(f"[VALIDATE] Registros com valores negativos removidos: {count}")
```

**Testes BDD:**

```gherkin
Scenario: Aceitar valores positivos
  Given um DataFrame com VAL_TOT = [100.0, 200.0, 1500.0]
  When executo validate_data()
  Then todos registros devem ser mantidos

Scenario: Aceitar valor zero
  Given um DataFrame com VAL_UTI = [0.0, 500.0]
  When executo validate_data()
  Then todos registros devem ser mantidos

Scenario: Rejeitar valores negativos
  Given um DataFrame com VAL_TOT = [100.0, -50.0, 200.0]
  When executo validate_data()
  Then resultado deve ter 2 registros
  And VAL_TOT -50.0 deve ser removido

Scenario: Validar múltiplos campos monetários
  Given um DataFrame com:
    | VAL_TOT | VAL_UTI | VAL_SH |
    | 100.0   | 50.0    | 30.0   |
    | 200.0   | -10.0   | 40.0   |
  When executo validate_data()
  Then resultado deve ter 1 registro
  And registro com VAL_UTI negativo deve ser removido
```

---

## Regras de Enriquecimento

### RN-ENR-001: Cálculo de Tempo de Permanência

**Objetivo:** Calcular dias de internação (DT_SAIDA - DT_INTER).

**Campo gerado:** `stay_days` (int64)

**Regra:**

```python
df['stay_days'] = (df['DT_SAIDA'] - df['DT_INTER']).dt.days
```

**Comportamento:**

| DT_INTER   | DT_SAIDA   | stay_days | Cenário           |
| ---------- | ---------- | --------- | ----------------- |
| 2024-01-10 | 2024-01-15 | 5         | Internação 5 dias |
| 2024-01-10 | 2024-01-11 | 1         | Internação 1 dia  |
| 2024-01-10 | 2024-01-10 | 0         | Mesmo dia         |
| 2024-12-28 | 2025-01-05 | 8         | Virada de ano     |

**Justificativa de Negócio:**

**KPI essencial:**

- TMP (Tempo Médio Permanência) é métrica core
- Benchmark hospitalar internacional
- Indicador de eficiência operacional

**Base para outros cálculos:**

- daily_cost = VAL_TOT / stay_days
- Taxa ocupação = pacientes-dia / leitos-dia
- Giro de leito = 365 / TMP

**Uso clínico:**

- Identificar internações prolongadas (outliers)
- Comparar especialidades
- Analisar complicações (stay_days acima da média)

**Impacto em KPIs:**

- TMP: Diretamente este campo
- Taxa Ocupação: Soma de stay_days / leitos
- Custo Diário: VAL_TOT / stay_days

**Casos Edge:**

1. **stay_days = 0 (mesmo dia):**

   - **VÁLIDO** - cirurgias ambulatoriais, observação breve
   - Não é erro
   - daily_cost terá tratamento especial (divisão por 1)

2. **stay_days > 365:**

   - Possível (internações longas em UTI, pacientes crônicos)
   - Não rejeitar automaticamente
   - Investigar outliers no MVP

3. **Diferença exata vs inclusão de dias parciais:**
   - `.dt.days` retorna diferença exata em dias completos
   - Não conta horas/minutos (DT_INTER 14h → DT_SAIDA 10h = 0 dias se mesmo dia)
   - DataSUS usa datas (YYYYMMDD), não timestamps

**Dependências:**

- Requer `DT_INTER` e `DT_SAIDA` em datetime64
- Requer validação RN-VAL-001 (DT_INTER ≤ DT_SAIDA)

**Logging:**

```python
logger.info("[ENRICH] Campo stay_days calculado")
```

**Testes BDD:**

```gherkin
Scenario: Calcular stay_days normal
  Given um DataFrame com DT_INTER = 2024-01-10
  And DT_SAIDA = 2024-01-15
  When executo enrich_data()
  Then stay_days deve ser 5

Scenario: stay_days zero para mesmo dia
  Given um DataFrame com DT_INTER = 2024-01-10
  And DT_SAIDA = 2024-01-10
  When executo enrich_data()
  Then stay_days deve ser 0

Scenario: stay_days em virada de ano
  Given um DataFrame com DT_INTER = 2024-12-28
  And DT_SAIDA = 2025-01-05
  When executo enrich_data()
  Then stay_days deve ser 8
```

---

### RN-ENR-002: Cálculo de Custo Diário

**Objetivo:** Calcular custo por dia de internação, protegendo contra divisão por zero.

**Campo gerado:** `daily_cost` (float64)

**Regra:**

```python
df['daily_cost'] = df['VAL_TOT'] / df['stay_days'].replace(0, 1)
```

**Comportamento:**

| VAL_TOT | stay_days | daily_cost | Lógica              |
| ------- | --------- | ---------- | ------------------- |
| 1500.0  | 5         | 300.0      | 1500 / 5            |
| 1000.0  | 0         | 1000.0     | 1000 / 1 (proteção) |
| 0.0     | 5         | 0.0        | 0 / 5 (sem custo)   |
| 2400.0  | 8         | 300.0      | 2400 / 8            |

**Justificativa de Negócio:**

**KPI de eficiência:**

- Custo por dia indica eficiência clínica
- Comparação entre especialidades
- Identificação de procedimentos caros

**Benchmark:**

- Comparar com média mercado
- Analisar outliers (muito alto/baixo)
- Negociação com operadoras

**Proteção divisão por zero:**

- stay_days = 0 → usa 1 como denominador
- Evita erro matemático
- daily_cost = VAL_TOT (custo "completo" do dia único)

**Impacto em KPIs:**

- Custo Médio Diário: Média deste campo
- Custo por Especialidade: Agrupamento + média
- Outliers Financeiros: Identificação de custos anormais

**Casos Edge:**

1. **stay_days = 0:**

   - `.replace(0, 1)` transforma 0 em 1
   - daily_cost = VAL_TOT / 1 = VAL_TOT
   - Interpretação: Custo total do dia único

2. **VAL_TOT = 0:**

   - daily_cost = 0 / stay_days = 0.0
   - Válido (internação sem custo SUS)

3. **Ambos zero:**

   - VAL_TOT = 0, stay_days = 0
   - daily_cost = 0 / 1 = 0.0
   - Válido (internação sem custo, dia único)

4. **stay_days muito alto:**
   - daily_cost será muito baixo
   - Não é erro, pode indicar internação longa com custo baixo/dia

**Dependências:**

- Requer `VAL_TOT` numérico (RN-CONV-001)
- Requer `stay_days` calculado (RN-ENR-001)

**Logging:**

```python
logger.info("[ENRICH] Campo daily_cost calculado")
```

**Testes BDD:**

```gherkin
Scenario: Calcular daily_cost normal
  Given um DataFrame com VAL_TOT = 1500.0
  And stay_days = 5
  When executo enrich_data()
  Then daily_cost deve ser 300.0

Scenario: Evitar divisão por zero
  Given um DataFrame com VAL_TOT = 1000.0
  And stay_days = 0
  When executo enrich_data()
  Then daily_cost deve ser 1000.0
  And não deve gerar erro

Scenario: Custo zero válido
  Given um DataFrame com VAL_TOT = 0.0
  And stay_days = 5
  When executo enrich_data()
  Then daily_cost deve ser 0.0
```

---

### RN-ENR-003: Categorização de Faixas Etárias

**Objetivo:** Agrupar idades em faixas demográficas para análises.

**Campo gerado:** `age_group` (categorical)

**Regra:**

```python
df['age_group'] = pd.cut(
    df['IDADE'],
    bins=[0, 18, 30, 45, 60, 120],
    labels=['0-17', '18-29', '30-44', '45-59', '60+']
)
```

**Comportamento (pd.cut com right=True):**

| IDADE | Intervalo | age_group | Explicação                     |
| ----- | --------- | --------- | ------------------------------ |
| 0     | (0, 18]   | "0-17"    | Bebê/criança                   |
| 17    | (0, 18]   | "0-17"    | Adolescente                    |
| 18    | (0, 18]   | "0-17"    | **Limite incluído à esquerda** |
| 19    | (18, 30]  | "18-29"   | Jovem adulto                   |
| 30    | (18, 30]  | "18-29"   | **Limite incluído à esquerda** |
| 31    | (30, 45]  | "30-44"   | Adulto                         |
| 45    | (30, 45]  | "30-44"   | **Limite incluído à esquerda** |
| 60    | (45, 60]  | "45-59"   | **Limite incluído à esquerda** |
| 61    | (60, 120] | "60+"     | Idoso                          |
| 120   | (60, 120] | "60+"     | Limite superior                |

**pd.cut() com right=True (padrão):**

```
Intervalos: (a, b]  ← inclui b, exclui a
Exemplo: (18, 30]   ← inclui 30, exclui 18
         30 está em (18, 30]
         18 está em (0, 18]
```

**Justificativa de Negócio:**

**Análises demográficas:**

- Distribuição por faixa etária
- Comparação com pirâmide populacional
- Planejamento de serviços (pediatria, geriatria)

**Perfil de risco:**

- Mortalidade por faixa
- Complicações por idade
- Tempo de internação por grupo

**Comparação clínica:**

- Pediatria: 0-17
- Adulto jovem: 18-29
- Adulto: 30-44
- Meia-idade: 45-59
- Idoso: 60+

**Impacto em KPIs:**

- Demografia: Contagem por age_group
- Mortalidade: Taxa por faixa etária
- TMP: Média por age_group (idosos tendem a TMP maior)

**Casos Edge:**

1. **Limites exatos (18, 30, 45, 60):**

   - **COMPORTAMENTO pd.cut():** Incluídos no intervalo **ANTERIOR**
   - Idade 18 → (0, 18] → "0-17"
   - Idade 30 → (18, 30] → "18-29"
   - Idade 45 → (30, 45] → "30-44"
   - Idade 60 → (45, 60] → "45-59"

2. **IDADE = NaN:**

   - `pd.cut(NaN)` → NaN (categoria)
   - Não é removido, fica como "missing category"
   - Pode ser filtrado em análises se necessário

3. **IDADE fora dos bins:**

   - Idade 121 → NaN (acima do limite superior)
   - Não deveria ocorrer (validação RN-VAL-002 remove)

4. **Labels customizadas:**
   - Podem ser alteradas conforme necessidade clínica
   - OMS usa: 0-14, 15-49, 50-64, 65+
   - Nossa escolha: 0-17, 18-29, 30-44, 45-59, 60+ (mais granular)

**Dependências:**

- Requer `IDADE` numérica (RN-CONV-001)
- Requer validação RN-VAL-002 (0 ≤ IDADE ≤ 120)

**Logging:**

```python
logger.info("[ENRICH] Campo age_group categorizado")
```

**Testes BDD:**

```gherkin
Scenario: Categorizar idades limites
  Given um DataFrame com IDADE = [10, 18, 25, 30, 45, 60, 85]
  When executo enrich_data()
  Then age_group deve ser:
    | IDADE | age_group |
    | 10    | "0-17"    |
    | 18    | "0-17"    |
    | 25    | "18-29"   |
    | 30    | "18-29"   |
    | 45    | "30-44"   |
    | 60    | "45-59"   |
    | 85    | "60+"     |

Scenario: pd.cut right=True comportamento
  Given um DataFrame com IDADE = [18, 30, 45, 60]
  When executo enrich_data()
  Then todos devem estar no intervalo ANTERIOR ao limite
  And IDADE 18 deve ser "0-17"
  And IDADE 30 deve ser "18-29"
  And IDADE 45 deve ser "30-44"
  And IDADE 60 deve ser "45-59"
```

---

### RN-ENR-004: Flag de Óbito

**Objetivo:** Criar flag booleano indicando se houve óbito.

**Campo gerado:** `death` (bool)

**Regra:**

```python
df['death'] = df['MORTE'] == 1
```

**Comportamento:**

| MORTE | death | Significado                |
| ----- | ----- | -------------------------- |
| 1     | True  | Óbito durante internação   |
| 0     | False | Alta hospitalar (vivo)     |
| NaN   | False | Tratado como "sem óbito"   |
| 2     | False | Qualquer valor ≠ 1 é False |

**Justificativa de Negócio:**

**Taxa de mortalidade:**

- KPI crítico hospitalar
- Indicador de qualidade clínica
- Comparação com benchmarks

**Análises de risco:**

- Mortalidade por especialidade
- Mortalidade por faixa etária
- Mortalidade por procedimento

**Tipo booleano mais claro:**

- `death = True` mais legível que `MORTE = 1`
- Facilita filtros: `df[df['death']]` vs `df[df['MORTE'] == 1]`
- Consistência com convenções Python

**Impacto em KPIs:**

- Taxa Mortalidade: `df['death'].sum() / len(df) * 100`
- Mortalidade por Especialidade: `groupby('ESPEC')['death'].mean()`
- Análises de Risco: Filtro `df[df['death']]`

**Casos Edge:**

1. **MORTE = NaN:**

   - `NaN == 1` → False
   - Tratado como "sem óbito"
   - Pode ser questionável (dado ausente ≠ sem óbito)
   - Considerar `.fillna(0)` antes se necessário no MVP

2. **MORTE = 0:**

   - Explicitamente "sem óbito"
   - `0 == 1` → False

3. **MORTE = 2 ou outro valor:**

   - Qualquer valor ≠ 1 → False
   - Pode indicar erro na fonte
   - Considerar validação adicional no MVP

4. **Tipo retornado:**
   - `==` retorna `np.bool_` (NumPy boolean)
   - Equivalente a `bool` para fins práticos
   - Testes devem usar `== True` não `is True`

**Dependências:**

- Requer campo `MORTE` presente
- Não requer validação prévia (tratamento de NaN automático)

**Logging:**

```python
logger.info("[ENRICH] Flag death criado")
```

**Testes BDD:**

```gherkin
Scenario: Marcar óbito
  Given um DataFrame com MORTE = [1, 0, 1]
  When executo enrich_data()
  Then death deve ser [True, False, True]

Scenario: Tratar NaN como sem óbito
  Given um DataFrame com MORTE = [1, NaN, 0]
  When executo enrich_data()
  Then death deve ser [True, False, False]

Scenario: Usar comparação de valor não identidade
  Given um DataFrame com MORTE = 1
  When executo enrich_data()
  Then death[0] == True deve ser True
  And death[0] is True pode ser False (np.bool_)
```

---

### RN-ENR-005: Nome da Especialidade

**Objetivo:** Converter código especialidade para string (placeholder para MVP).

**Campo gerado:** `specialty_name` (string)

**Regra:**

```python
df['specialty_name'] = df['ESPEC'].astype(str)
```

**Comportamento:**

| ESPEC | specialty_name | Status                          |
| ----- | -------------- | ------------------------------- |
| 01    | "1"            | Placeholder (sem tabela SIGTAP) |
| 03    | "3"            | Placeholder                     |
| NaN   | "nan"          | String "nan"                    |

**Justificativa de Negócio:**

**Placeholder POC:**

- Preparar estrutura para MVP
- specialty_name já existe no schema
- Integração SIGTAP no MVP adicionará descrições

**MVP: Integração SIGTAP:**

```python
# Futuro (MVP)
specialty_map = {
    '01': 'Cirurgia',
    '02': 'Obstetrícia',
    '03': 'Clínica Médica',
    '04': 'Cuidados Prolongados',
    '05': 'Psiquiatria',
    '07': 'Tisiologia',
    '08': 'Pediatria Clínica'
}
df['specialty_name'] = df['ESPEC'].map(specialty_map)
```

**Uso clínico:**

- Análises por especialidade mais legíveis
- Relatórios para gestão
- Comparação entre especialidades

**Impacto em KPIs:**

- Volume por Especialidade: `groupby('specialty_name').size()`
- TMP por Especialidade: `groupby('specialty_name')['stay_days'].mean()`
- Receita por Especialidade: `groupby('specialty_name')['VAL_TOT'].sum()`

**Limitações POC:**

- Nomes não descritivos ("1", "3" vs "Cirurgia", "Clínica Médica")
- Requer lookup manual em tabela SIGTAP
- MVP resolverá com integração automática

**Dependências:**

- Requer campo `ESPEC` presente
- Não requer validação prévia

**Logging:**

```python
logger.info("[ENRICH] Campo specialty_name criado (placeholder)")
```

**Testes BDD:**

```gherkin
Scenario: Converter ESPEC para string
  Given um DataFrame com ESPEC = [1, 3, 8]
  When executo enrich_data()
  Then specialty_name deve ser ["1", "3", "8"]

Scenario: Tratar NaN em ESPEC
  Given um DataFrame com ESPEC = [1, NaN, 3]
  When executo enrich_data()
  Then specialty_name deve ser ["1", "nan", "3"]
```

---

## Métricas de Qualidade

### MQ-001: Taxa de Validação

**Definição:** Percentual de registros que passam por todas as validações.

**Fórmula:**

```python
taxa_validacao = (registros_finais / registros_iniciais) * 100
```

**Metas:**

| Fase     | Meta Mínima | Meta Ideal | Ação se Abaixo   |
| -------- | ----------- | ---------- | ---------------- |
| POC      | 85%         | 95%        | Investigar fonte |
| MVP      | 90%         | 97%        | Revisar regras   |
| Produção | 95%         | 99%        | Alertar equipe   |

**Implementação:**

```python
initial_count = len(df_raw)
final_count = len(df_clean)
rate = (final_count / initial_count) * 100

logger.info(f"[VALIDATE] Taxa validação: {rate:.2f}%")

if rate < 85:
    logger.warning(f"Taxa validação abaixo do limite: {rate:.2f}%")
```

**Interpretação:**

- **> 95%:** Qualidade excelente
- **90-95%:** Qualidade boa
- **85-90%:** Qualidade aceitável, investigar
- **< 85%:** Problema sério, alertar

**AC Janeiro 2024:**

- Registros iniciais: 4.315
- Registros finais: 4.315
- Taxa: **100%** (excelente)

---

### MQ-002: Taxa de Perda de Dados

**Definição:** Percentual de registros removidos pelas validações.

**Fórmula:**

```python
taxa_perda = ((registros_iniciais - registros_finais) / registros_iniciais) * 100
```

**Limites Aceitáveis:**

| Fase     | Limite | Ação se Acima   |
| -------- | ------ | --------------- |
| POC      | 15%    | Investigar      |
| MVP      | 10%    | Revisar regras  |
| Produção | 5%     | Alertar urgente |

**Causas comuns:**

- Datas inválidas (DT_INTER > DT_SAIDA)
- Idades fora do range (< 0 ou > 120)
- Valores negativos
- Campos críticos nulos

**Ação corretiva:**

1. Analisar logs detalhados
2. Identificar regra com mais rejeições
3. Verificar se regra está correta
4. Considerar ajuste de limites se justificado

---

## Casos Edge e Tratamento de Erros

### CE-001: DataFrame Vazio

**Cenário:** `extract()` retorna DataFrame sem registros.

**Comportamento esperado:**

- Pipeline não deve crashar
- Log warning
- Retornar DataFrame vazio (schema preservado)

**Implementação:**

```python
if df.empty:
    logger.warning("[TRANSFORM] DataFrame vazio recebido")
    return df  # Retorna vazio, não None
```

---

### CE-002: Campos Ausentes

**Cenário:** DataFrame não contém campo esperado (ex: `IDADE` ausente).

**Comportamento esperado:**

- Detectar campo ausente
- Log error
- Skip etapa específica
- Continuar pipeline (fail gracefully)

**Implementação:**

```python
if 'IDADE' not in df.columns:
    logger.error("[VALIDATE] Campo IDADE ausente, skip validação idade")
    # Continua sem validar IDADE
```

---

### CE-003: Todos Registros Inválidos

**Cenário:** Validações removem 100% dos registros.

**Comportamento esperado:**

- Log critical error
- Interromper pipeline
- Alertar equipe

**Implementação:**

```python
if len(df) == 0:
    logger.critical("[VALIDATE] Todos registros removidos!")
    raise ValueError("Pipeline resultou em zero registros")
```

---

## Impacto em KPIs

### KPI: Taxa de Ocupação

**Dependências:**

- `stay_days` (RN-ENR-001)
- Validações de data (RN-VAL-001)

**Cálculo:**

```python
pacientes_dia = df['stay_days'].sum()
ocupacao = (pacientes_dia / (leitos * dias_mes)) * 100
```

**Impacto de regras:**

- Datas inválidas removidas → ocupação mais precisa
- stay_days correto → cálculo correto

---

### KPI: Tempo Médio de Permanência (TMP)

**Dependências:**

- `stay_days` (RN-ENR-001)

**Cálculo:**

```python
tmp = df['stay_days'].mean()
```

**Impacto de regras:**

- Datas lógicas validadas → TMP não distorcido por negativos
- Idade validada → TMP por faixa etária correto

---

### KPI: Receita Total

**Dependências:**

- `VAL_TOT` validado (RN-VAL-003)

**Cálculo:**

```python
receita = df['VAL_TOT'].sum()
```

**Impacto de regras:**

- Valores negativos removidos → receita correta
- Duplicatas removidas → sem contagem dupla

---

## Referências Cruzadas

### Código Fonte

- **Implementação:** `src/transform/transformer.py`
- **Testes:** `tests/test_transformer.py`
- **Specs BDD:** `tests/features/hospitalization_validation.feature`

### Documentação

- [DATA_GUIDE.md](DATA_GUIDE.md) - Dicionário de campos
- [ARCHITECTURE.md](ARCHITECTURE.md) - Pipeline ETL
- [ROADMAP.md](ROADMAP.md) - Planejamento

### Externo

- DataSUS: <http://sihd.datasus.gov.br/>
- Pandas cut(): <https://pandas.pydata.org/docs/reference/api/pandas.cut.html>
- OMS benchmarks: <https://www.who.int/>
