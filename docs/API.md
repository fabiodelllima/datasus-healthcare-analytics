# INTEGRAÇÕES API

- **Versão:** 1.0.0 POC
- **Última atualização:** 24/12/2025

**Propósito:** Single Source of Truth para integrações com APIs externas do ecossistema DataSUS/Ministério da Saúde.

**IMPORTANTE:** A API OpenDataSUS disponibiliza apenas datasets publicados no portal. Dados SIH tradicionais (internações) estão disponíveis exclusivamente via FTP através da biblioteca pysus.

---

## Índice

1. [Visão Geral](#visão-geral)
2. [API OpenDataSUS (CKAN)](#api-opendatasus-ckan)
   - [RN-API-001: Requisição GET para Package Info](#rn-api-001-requisição-get-para-informações-de-package)
   - [RN-API-002: Requisição GET para Busca de Recursos (DESABILITADO)](#rn-api-002-requisição-get-para-busca-de-recursos-desabilitado)
   - [RN-API-003: Requisição GET para Lista de Packages](#rn-api-003-requisição-get-para-lista-de-packages)
   - [RN-API-004: Formatação de Output Terminal](#rn-api-004-formatação-de-output-terminal)
   - [RN-API-005: Configuração de Headers HTTP](#rn-api-005-configuração-de-headers-http)
3. [Limitações da API](#limitações-da-api)
4. [Casos Edge e Tratamento de Erros](#casos-edge-e-tratamento-de-erros)
5. [Impacto em Sistema](#impacto-em-sistema)
6. [Referências Cruzadas](#referências-cruzadas)

---

## Visão Geral

### Contexto: API vs FTP

```
API OpenDataSUS (CKAN):
├── Retorna: METADADOS de datasets publicados no portal
├── Formato: JSON via HTTP
├── Exemplo: "Dataset COVID-19 tem 10 recursos"
└── Uso: Descoberta de novos datasets

FTP DataSUS (via pysus):
├── Retorna: DADOS BRUTOS (arquivos .dbc)
├── Formato: DBC (DBF comprimido)
├── Exemplo: 4.315 registros de internações AC Jan/2024
└── Uso: Pipeline ETL principal (SIH)
```

**Importante:** SIH tradicional NÃO está disponível via API.

---

## API OpenDataSUS (CKAN)

### Informações Gerais

**Base URL:** `https://opendatasus.saude.gov.br/api/3/action/`

**Endpoints Status:**

```
✓ package_list          → FUNCIONAL (83 packages)
✓ package_show          → FUNCIONAL
✗ resource_search       → DESABILITADO (409 CONFLICT)
```

---

### RN-API-001: Requisição GET para Informações de Package

**Status:** [✓] IMPLEMENTADO E FUNCIONAL

**Endpoint:**

```
GET https://opendatasus.saude.gov.br/api/3/action/package_show?id={package_id}
```

**Parâmetros:**

- `package_id` (str): Identificador do dataset

**Validações:**

- Package ID não-vazio (min 2 caracteres)
- Timeout: 30s

**Exemplo Real:**

```python
inspector = OpenDataSUSInspector()
info = inspector.get_package_info('registro-de-ocupacao-hospitalar-covid-19')
# Retorna: {'name': '...', 'title': 'Registro de Ocupação Hospitalar COVID-19', ...}
```

**Tratamento de Erros:**

| Cenário             | Status        | Ação               |
| ------------------- | ------------- | ------------------ |
| Package válido      | 200 OK        | Retornar metadados |
| Package inexistente | 404 NOT FOUND | Retornar None      |
| Package ID vazio    | -             | ValueError         |
| Timeout             | -             | requests.Timeout   |

---

### RN-API-002: Requisição GET para Busca de Recursos (DESABILITADO)

**Status:** [✗] NÃO IMPLEMENTADO (Endpoint retorna 409 CONFLICT)

**Endpoint:**

```
GET https://opendatasus.saude.gov.br/api/3/action/resource_search
```

**Motivo da Desabilitação:**

```
Status Code: 409 CONFLICT
Mensagem: "Search index not found"
Testado: 17/12/2025
Resultado: Todas queries retornam 409
```

**Impacto:**

- Não é possível buscar recursos específicos via API
- Workaround: Usar FTP direto via pysus para dados SIH

**Decisão de Implementação:**

- ✗ NÃO implementar método `search_resources()`
- ✓ Documentar limitação
- ✓ Manter numeração RN-API-002 para rastreabilidade

**Alternativa:**

```python
# Ao invés de buscar via API
# results = inspector.search_resources('RDAC')

# Usar pysus diretamente
from pysus.online_data import SIH
sih = SIH().load()
# Listar arquivos disponíveis via FTP
```

---

### RN-API-003: Requisição GET para Lista de Packages

**Status:** [✓] IMPLEMENTADO E FUNCIONAL

**Endpoint:**

```
GET https://opendatasus.saude.gov.br/api/3/action/package_list
```

**Resultado Real (17/12/2025):**

```python
inspector = OpenDataSUSInspector()
packages = inspector.list_packages()
# Retorna: 83 packages

# Exemplos:
['acompanhamento-gestacional-siasi',
 'alimentar-nutricional-van-siasi',
 'arboviroses-dengue',
 'arboviroses-febre-de-chikungunya',
 'registro-de-ocupacao-hospitalar-covid-19',
 ...]
```

**Observação Importante:**

- ✗ `sihsus` NÃO existe na lista
- ✓ Apenas datasets publicados no portal
- ✓ SIH tradicional disponível apenas via FTP

---

### RN-API-004: Formatação de Output Terminal

**Status:** [✓] IMPLEMENTADO - TerminalFormatter com cores ANSI e box drawing

**Símbolos Permitidos:**

```
Status: ✓ ✗
Box Drawing: ┌ ┐ └ ┘ ─ │
Tags: [OK] [ERROR] [WARNING]
ANSI Colors: \033[92m \033[91m
```

**Símbolos Proibidos:**

```
Emojis: U+1F300-U+1F9FF
Exemplos proibidos: checkmark colorido, rocket, package, warning triangle
```

**Justificativa:**

- Renderização consistente
- Acessibilidade
- Compatibilidade com terminais limitados

---

### RN-API-005: Configuração de Headers HTTP

**Status:** [✓] IMPLEMENTADO

**Headers Obrigatórios:**

```python
headers = {
    'User-Agent': 'DataSUS-Healthcare-Analytics/0.2.0 (Educational Project; Python/3.11)',
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip, deflate',
}
```

**Conformidade:** RFC 7231

---

## Limitações da API

### Endpoints Desabilitados

**1. resource_search (RN-API-002)**

```
Status: 409 CONFLICT
Mensagem: "Search index not found"
Testado: 17/12/2025
Impacto: Busca de recursos indisponível
```

### Datasets Não Disponíveis

**2. SIH Tradicional**

```
Package ID esperado: sihsus
Status: NÃO EXISTE
Disponibilidade: Apenas FTP
Acesso: Via pysus
```

**3. Datasets Históricos**

- CNES (estabelecimentos): Apenas FTP
- SIM (mortalidade): Apenas FTP
- SINAN (agravos): Apenas FTP

**Datasets Disponíveis na API:**

- COVID-19 (ocupação hospitalar)
- Dengue, Chikungunya, Zika
- SIASI (saúde indígena)
- Arboviroses

---

## Casos Edge e Tratamento de Erros

### EDGE-API-001: HTML ao invés de JSON

```python
content_type = response.headers.get('Content-Type', '')
if 'text/html' in content_type:
    raise ValueError("API returned HTML")
```

### EDGE-API-002: Package Não Encontrado (404)

```python
if response.status_code == 404:
    return None
```

### EDGE-API-003: Timeout

```python
try:
    response = requests.get(url, timeout=30)
except requests.Timeout:
    logger.warning("Timeout")
    raise
```

### EDGE-API-004: Endpoint Desabilitado (409)

```
Cenário: resource_search retorna 409 CONFLICT
Ação: Não implementar método
Documentar: Limitação conhecida
```

---

## Impacto em Sistema

### Pipeline ETL

**Impacto:** NENHUM (zero)

- API independente do pipeline
- Pipeline usa FTP via pysus
- Falha de API não afeta ETL

### Descoberta de Datasets

**Impacto:** MÉDIO

- Identifica novos datasets (COVID-19, dengue)
- Planejamento de expansão futura

---

## Referências Cruzadas

### Documentação

- [BUSINESS_RULES.md](BUSINESS_RULES.md) - Pipeline ETL via FTP
- [ARCHITECTURE.md](ARCHITECTURE.md) - Stack técnica

### Código Fonte

```
src/api/
├── __init__.py
└── datasus_inspector.py    # 2 métodos implementados
```

### Testes

```
tests/
├── test_api_inspector.py
└── manual/
    └── test_api_final.py
```

### Status de Implementação

| RN-API     | Endpoint        | Status              | Método               |
| ---------- | --------------- | ------------------- | -------------------- |
| RN-API-001 | package_show    | [OK] IMPLEMENTADO   | `get_package_info()` |
| RN-API-002 | resource_search | [SKIP] DESABILITADO | -                    |
| RN-API-003 | package_list    | [OK] IMPLEMENTADO   | `list_packages()`    |
| RN-API-004 | Formatação      | [OK] IMPLEMENTADO   | `TerminalFormatter`  |
| RN-API-005 | Headers         | [OK] IMPLEMENTADO   | (no **init**)        |

---
