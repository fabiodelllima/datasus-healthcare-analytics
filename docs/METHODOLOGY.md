# Metodologia de Desenvolvimento - DataSUS Analytics

**Última atualização:** 03/01/2026

## Índice

1. [Hierarquia de Desenvolvimento](#hierarquia-de-desenvolvimento)
2. [Ciclo TDD](#ciclo-tdd)
3. [Git Workflow](#git-workflow)
4. [Convenções](#convenções)
5. [Testes](#testes)
6. [Code Review](#code-review)

---

## Hierarquia de Desenvolvimento

### DOCS → BDD → TDD → CODE

```
1. DOCS:  Escrever regras de negócio (RN-XXX-NNN)
          ↓
2. BDD:   Especificar cenários Gherkin (Given/When/Then)
          ↓
3. TDD:   Implementar testes unitários
          ↓
4. CODE:  Implementar código mínimo (RED → GREEN → REFACTOR)
```

**Ordem OBRIGATÓRIA:** Nunca pular etapas.

**Exemplo prático:**

```
Feature: Calcular dias de internação

DOCS:  RN-ETL-008 documentada em docs/BUSINESS_RULES.md
  ↓
BDD:   Scenario em tests/features/hospitalization.feature
  ↓
TDD:   test_calculate_stay_days() em tests/test_transformer.py
  ↓
CODE:  calculate_stay_days() em src/transform/transformer.py
```

---

## Ciclo TDD

### RED → GREEN → REFACTOR (Incremental)

```python
# CORRETO: TDD incremental por funcionalidade
def develop_feature():
    for each_requirement:
        # RED: Escrever teste que falha
        write_one_test()           # 1 teste → FAIL

        # GREEN: Implementar mínimo para passar
        implement_minimum()        # código mínimo → PASS

        # REFACTOR: Melhorar mantendo verde
        improve_code()             # melhora → PASS

        commit()                   # Checkpoint
```

**NUNCA fazer:**

```python
# INCORRETO: Testes antecipados (violado em v0.2.0)
def develop_feature_wrong():
    write_all_tests()              # 45 testes
    implement_partial_code()       # 60% implementado
    result: 45 tests RED           # [FAIL] NÃO É TDD
```

**Lição aprendida:** Ver docs/DECISION_LOG.md entrada 2025-12-17.

---

## Git Workflow

### GitFlow Completo

```
main/           Production-ready code
  ↑
release/*       Pre-production staging (v0.3.0-rc1)
  ↑
develop         Integration branch
  ↑
feature/*       New features
fix/*           Bug fixes
hotfix/*        Emergency production fixes
test/*          Test coverage
docs/*          Documentation only
```

### Fluxos

**Feature normal:**

```bash
git checkout develop
git checkout -b feature/api-retry-logic
# ... desenvolvimento
git checkout develop
git merge feature/api-retry-logic --no-ff
git branch -d feature/api-retry-logic
```

**Release:**

```bash
git checkout develop
git checkout -b release/v0.3.0
# Bump version, update CHANGELOG
git checkout main
git merge release/v0.3.0 --no-ff
git tag -a v0.3.0 -m "Release v0.3.0"
git checkout develop
git merge release/v0.3.0 --no-ff
git branch -d release/v0.3.0
```

**Hotfix emergencial:**

```bash
git checkout main
git checkout -b hotfix/critical-bug
# Fix urgente
git checkout main
git merge hotfix/critical-bug --no-ff
git tag -a v0.2.1 -m "Hotfix: Critical bug"
git checkout develop
git merge hotfix/critical-bug --no-ff
git branch -d hotfix/critical-bug
```

---

## Convenções

### Commits

**Formato:** `type(scope): Descrição em português`

**Types:**

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `refactor`: Refatoração sem mudança funcional
- `test`: Adiciona/modifica testes
- `docs`: Documentação apenas
- `chore`: Manutenção (deps, config)
- `perf`: Melhoria de performance

**Exemplo:**

```bash
feat(api): Adiciona retry logic para OpenDataSUS

- Implementa HTTPAdapter com backoff exponencial
- Aumenta timeout padrão para 60s
- Adiciona 3 tentativas automáticas
- Coverage: 97% (128 testes)

Refs: docs/API.md RN-API-001
```

### Linguagem

**Código:**

- Variáveis, funções, classes: Inglês
- Docstrings: Português
- Comentários inline: Português
- Type hints: Inglês (padrão Python)

**Documentação:**

- README, docs/: Português
- BDD Gherkin: Inglês (padrão internacional)
- Commit messages: Português

**Gramática:**

- ✓ "em vez de" (substituição)
- ✗ "ao invés de" (arcaico, evitar)

### Símbolos

**NUNCA usar emojis. Usar ASCII/Unicode:**

```python
# Correto
status = "[OK] Teste passou"
status = "[FAIL] Teste falhou"
status = "[WARN] Aviso"

# Incorreto (NUNCA)
status = "✓ Teste passou"      # emoji
status = "✗ Falhou"            # emoji
```

---

## Testes

### Pirâmide de Testes

```
┌─────────────────────────────────┐
│      E2E Tests                  │  Poucos, lentos, caros
│      (End-to-End)               │  Sistema completo
└─────────────────────────────────┘
         ▲
         │
┌─────────────────────────────────┐
│      Integration Tests          │  Moderados
│      (2-3 módulos)              │  Mocks parciais
└─────────────────────────────────┘
         ▲
         │
┌─────────────────────────────────┐
│         Unit Tests              │  Muitos, rápidos, baratos
│      (Função isolada)           │  Mocks completos
└─────────────────────────────────┘
```

### Tipos

| Tipo            | Escopo           | Velocidade | Exemplo                        |
| --------------- | ---------------- | ---------- | ------------------------------ |
| **Unit**        | Função isolada   | <10ms      | `test_calculate_stay_days()`   |
| **Integration** | 2-3 módulos      | <100ms     | `test_extractor_transformer()` |
| **E2E**         | Sistema completo | >1s        | `test_full_pipeline()`         |

**Diferença Integration vs E2E:**

```python
# Integration: Testa interação componentes (mocks parciais)
def test_integration():
    extractor = Extractor()
    transformer = Transformer()
    data = extractor.extract()
    result = transformer.transform(data)
    assert result.valid

# E2E: Testa sistema completo (sem mocks)
def test_e2e_full_pipeline():
    exit_code = subprocess.run(["python", "src/main.py", "--state=AC"])
    assert exit_code == 0
    assert Path("data/processed/AC_2024_01.csv").exists()
```

### Coverage Mínimo

- **POC:** >50% (atual: 97%)
- **MVP:** >90%
- **Produção:** >95%

### Ferramentas

- `pytest`: Framework principal
- `pytest-cov`: Coverage reports
- `pytest-bdd`: BDD scenarios
- `pytest-mock`: Mocking

**Configuração:**

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["--cov=src", "--cov-report=term-missing"]
```

---

## Code Review

### Checklist

**Antes do PR:**

- [ ] Testes passando (100%)
- [ ] Coverage mantido/aumentado
- [ ] Ruff sem warnings
- [ ] Mypy sem erros
- [ ] Docstrings em português
- [ ] Type hints presentes
- [ ] Pre-commit passou

**No PR:**

- [ ] Descrição clara
- [ ] Refs para issues/docs
- [ ] Screenshots (se UI)
- [ ] CHANGELOG.md atualizado

**Aprovação:**

- [ ] CI passou
- [ ] 1+ aprovação
- [ ] Sem conflitos
- [ ] Squash ou merge (depende do caso)

### Automação

**Pre-commit (local):**

```bash
pre-commit install
pre-commit run --all-files
```

**CI/CD (GitHub Actions):**

- Ruff lint/format
- Mypy type check
- Pytest + coverage
- Codecov upload

**Ferramentas futuras:**

- MVP: Bandit, Safety
- Produção: SonarQube, Radon

Ver detalhes em: docs/TOOLING.md

---

## Referências

- Kent Beck: "Test-Driven Development by Example"
- Martin Fowler: "Refactoring"
- Vaughn Vernon: "Implementing Domain-Driven Design"
- PEP 8: Python Style Guide
- Conventional Commits: <https://www.conventionalcommits.org/>

---

**Última atualização:** 03/01/2026
