# DataSUS Healthcare Analytics — Contexto de Sessão

**Última auditoria:** 2026-09-24, verificada por execução
**Versão:** 0.2.7

## Regra deste documento

Nenhum número de cobertura, contagem de testes ou percentual de progresso
entra aqui. Métrica em markdown envelhece em silêncio, e foi isso que a
auditoria de setembro de 2026 encontrou. Estado de execução vem do CI;
estado de escopo vem de `ROADMAP.md`.

## Ambiente

Python >= 3.11 e < 3.14, restrição herdada do `pysus` 2.x. Sem venv o
`conftest.py` falha ao importar `vcr` e a suíte inteira não executa.

```bash
python3.11 -m venv venv && source venv/bin/activate
python -m pip install -r requirements.txt
```

Use sempre `python -m pip` e `python -m mypy`: invocar os executáveis
diretamente pode resolver pacotes de fora do venv.

## O que está implementado

**Pipeline ETL.** `extract` baixa via `pysus.ftp.sih` (API namespaced; a
chamada direta `pysus.sih()` está obsoleta), `transform` converte tipos,
limpa, valida e enriquece, `load` grava CSV e Parquet. Orquestrado por
`src/main.py` via `main(state, year, month)`.

**Campos enriquecidos:** `stay_days`, `daily_cost`, `age_group`, `death`,
`specialty_name`. Campos de origem consumidos: `N_AIH`, `DT_INTER`,
`DT_SAIDA`, `IDADE`, `MORTE`, `ESPEC`, `VAL_TOT`, `VAL_SH`, `VAL_SP`,
`VAL_SADT`, `VAL_UTI`.

**KPIs (`src/analytics/kpis.py`, `KPICalculator`).** `occupancy_rate`,
`average_length_of_stay`, `volume`, `revenue`, `average_ticket`,
`demographics` e `summary`, que consolida todos.

A taxa de ocupação é calculável: a capacidade de leitos não vem do SIH e
entra como parâmetro externo `beds`. Qualquer consumidor precisa informar a
origem desse número.

**Visualizações (`src/visualizations/charts.py`, `ChartGenerator`).** Seis
gráficos: faixa etária, receita por especialidade, permanência por
especialidade, principais diagnósticos, volume diário e distribuição por
sexo.

**EDA.** `notebooks/01_exploratory_analysis.ipynb`, 25 células, seis seções.

**API Inspector.** `src/api/datasus_inspector.py` sobre OpenDataSUS.

## O que não está implementado

`KPICalculator` e `ChartGenerator` não são chamados por `src/main.py` —
apenas por testes e pelo notebook. Não existe caminho de pipeline que produza
saída de KPI serializada. É por aí que o módulo de publicação do frontend deve
entrar, estendendo o `main`.

Mortalidade hospitalar não existe como KPI, embora a flag `death` exista.

O frontend não existe. Decisões tomadas: Vue 3 com TypeScript e Vite,
Tailwind v4, submódulos do D3 para cálculo com SVG próprio, TanStack Query,
interface em pt-BR, hospedagem em S3 privado com CloudFront e OAC via
Terraform, repositório único com o frontend em `frontend/`. Direção visual e
contrato de dados em aberto.

## Armadilhas conhecidas

`data/processed/` é ignorado pelo git (`.gitignore`, linhas 51-55). Os PNGs e
o notebook versionados derivam de um Parquet ausente do repositório. Quem
clona precisa rodar o pipeline antes de reproduzir qualquer análise.

O Pylance acusa que `sih` não é atributo conhecido de `pysus.ftp`. É falso
positivo: os namespaces por origem são construídos em tempo de execução. O
`mypy` passa limpo e os testes cobrem o contrato.

`kpis.feature` e `api_inspection.feature` estão em inglês;
`hospitalization_validation.feature` está em português. Os arquivos Gherkin
devem ser todos em inglês — conversão pendente, exige reescrever também os
step definitions.

A branch `develop` não existe, apesar de a convenção declarar GitFlow.

## Pendências anotadas

Usar o parâmetro `columns` do `pysus` para pedir os doze campos que o
transform consome, em vez das 113 do grupo RD. Implementar mortalidade
hospitalar como KPI. Avaliar o módulo `pysus.cnes` como origem real do
parâmetro `beds`. Remover a seção morta `[mypy-pytest_bdd.*]` do `mypy.ini`.

## Metodologia

RE > BDD > TDD > CODE. Consultar antes de implementar: `ROADMAP.md` para
escopo, `BUSINESS_RULES.md` para regras, `DATA_GUIDE.md` para dicionário e
fórmulas, `METHODOLOGY.md` para processo, `ARCHITECTURE.md` para desenho,
`DECISION_LOG.md` para decisões anteriores.

Commits: `tipo(escopo): Descrição em português`. Merges com `--no-ff`. Código
e nomes de arquivo em inglês, comentários e docstrings em português. Arquivos
Gherkin em inglês. Sem emojis em nenhum artefato.
