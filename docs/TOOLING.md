# Ferramentas de Qualidade e CI/CD

**Última atualização:** 03/01/2026

## Índice

1. [Ferramentas Ativas](#ferramentas-ativas)
2. [Ferramentas Futuras](#ferramentas-futuras)
3. [Configuração](#configuração)

---

## Ferramentas Ativas

### Ruff (Linter + Formatter)

**O que é:** Linter e formatter Python ultrarrápido (Rust-based).

**Substitui:**

- black (formatter)
- flake8 (linter)
- isort (import sorting)
- pyupgrade (syntax upgrades)

**Por que usar:**

- 10-100x mais rápido que alternativas
- Configuração unificada (pyproject.toml)
- Auto-fix nativo
- Zero dependencies

**Configuração:**

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP"]
ignore = ["E501"]  # Line too long (delegado ao formatter)
```

**CI/CD:**

```yaml
- name: Ruff
  run: |
    ruff check .
    ruff format --check .
```

**Referências:**

- Docs: <https://docs.astral.sh/ruff/\>
- GitHub: <https://github.com/astral-sh/ruff\>

---

### Mypy (Type Checker)

**O que é:** Type checker estático para Python.

**Por que usar:**

- Detecta bugs antes de runtime
- Melhora IDE autocomplete
- Documenta tipos esperados
- Padrão indústria para Python tipado

**Configuração:**

```ini
# mypy.ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False  # Gradual adoption

[mypy-requests.*]
ignore_missing_imports = True

[mypy-pytest_bdd.*]
ignore_missing_imports = True
```

**CI/CD:**

```yaml
- name: Mypy
  run: mypy src/ --show-error-codes
```

**Referências:**

- Docs: <https://mypy.readthedocs.io/\>
- PEP 484: Type Hints

---

### Pytest (Test Framework)

**O que é:** Framework de testes Python padrão indústria.

**Plugins usados:**

- pytest-cov: Coverage reports
- pytest-bdd: Behavior-Driven Development
- pytest-mock: Mocking utilities

**Configuração:**

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = [
    "--strict-markers",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=xml",
    "-m", "not wip"
]
markers = [
    "wip: Work in progress (not run by default)",
    "implemented: Fully implemented scenarios",
    "skip: Skipped tests",
    "endpoint_disabled: API endpoint is disabled",
    "future_v0_3_0: Planned for v0.3.0"
]
```

**CI/CD:**

```yaml
- name: Pytest
  run: pytest --cov=src --cov-report=xml
```

**Coverage mínimo:**

- POC: >50% (atual: 97%)
- MVP: >90%
- Produção: >95%

---

### Pre-commit (Git Hooks)

**O que é:** Framework para git hooks automáticos.

**Por que usar:**

- Bloqueia commits ruins ANTES do push
- Automação zero-config
- Padronização time

**Configuração:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.8
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.19.0
    hooks:
      - id: mypy
        additional_dependencies: [pandas-stubs]
```

**Setup:**

```bash
pip install pre-commit
pre-commit install
```

**CI/CD:**

```yaml
- name: Pre-commit
  run: pre-commit run --all-files
```

---

### VCR.py (HTTP Mocking)

**O que é:** Biblioteca para gravar e reproduzir interações HTTP.

**Por que usar:**

- Evita timeouts em testes CI (API externa indisponível)
- Testes determinísticos e rápidos
- Grava cassettes YAML com requests/responses reais
- Replay automático nas execuções seguintes

**Configuração:**

```python
# tests/conftest.py
import vcr

vcr_config = vcr.VCR(
    cassette_library_dir="tests/fixtures/cassettes",
    record_mode="none",  # Apenas replay
    match_on=["uri", "method"],
    filter_headers=["User-Agent"],
    decode_compressed_response=True,
)
```

**Uso em testes:**

```python
@pytest.fixture
def api_vcr():
    def _api_vcr(cassette_name):
        return vcr_config.use_cassette(f"{cassette_name}.yaml")
    return _api_vcr

def test_api_call(api_vcr):
    with api_vcr("package_list"):
        response = inspector.list_packages()
        assert len(response) > 0
```

**Cassettes criadas:**

- `package_list.yaml`: Lista de packages OpenDataSUS
- `package_show_covid_hospital_occupancy.yaml`: Metadados package válido
- `package_show_nonexistent.yaml`: Resposta 404 para package inexistente

**Referências:**

- Docs: <https://vcrpy.readthedocs.io/\>
- GitHub: <https://github.com/kevin1024/vcrpy\>

---

### Codecov (Coverage Tracking)

**O que é:** Plataforma de tracking de code coverage.

**Por que usar:**

- Badges no README (demonstra qualidade)
- Tracking temporal (coverage trends)
- PR comments automáticos
- GRÁTIS para repos públicos

**Configuração:**

```yaml
# .codecov.yml
coverage:
  status:
    project:
      default:
        target: 90%
        threshold: 2%
    patch:
      default:
        target: 80%
```

**CI/CD:**

```yaml
- name: Upload to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
    fail_ci_if_error: true
```

**Badge README:**

```markdown
[![codecov](https://codecov.io/gh/USER/REPO/branch/main/graph/badge.svg)](https://codecov.io/gh/USER/REPO)
```

---

## Ferramentas Futuras

### Tenacity (Retry Logic) - MVP

**O que é:** Biblioteca para retry com backoff exponencial.

**Quando usar:** MVP (já instalada, não implementada).

**Por que usar:**

- Retry automático em falhas de rede
- Backoff exponencial configurável
- Decorators simples

**Exemplo:**

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
def call_api():
    return requests.get(url, timeout=30)
```

**Referências:**

- Docs: <https://tenacity.readthedocs.io/\>

---

### Bandit (Security Scanner) - MVP

**O que é:** Scanner de vulnerabilidades de segurança Python.

**Quando usar:** MVP e Produção.

**O que detecta:**

- SQL injection
- Hardcoded passwords
- Insecure functions (eval, exec)
- Weak cryptography
- Path traversal

**Configuração:**

```yaml
# .bandit
exclude_dirs:
  - /tests/
  - /venv/

tests:
  - B201 # Flask debug mode
  - B301 # Pickle usage
  - B501 # Request without verify SSL
```

**CI/CD:**

```yaml
- name: Bandit Security Scan
  run: |
    pip install bandit
    bandit -r src/ -f json -o bandit-report.json
```

**Referências:**

- Docs: <https://bandit.readthedocs.io/\>
- PyCQA: <https://github.com/PyCQA/bandit\>

---

### Safety (Dependency Vulnerabilities) - MVP

**O que é:** Scanner de vulnerabilidades em dependências.

**Quando usar:** MVP e Produção.

**O que faz:**

- Verifica requirements.txt contra CVE database
- Detecta packages com vulnerabilidades conhecidas
- Recomenda versões seguras

**CI/CD:**

```yaml
- name: Safety Check
  run: |
    pip install safety
    safety check --json
```

**Integração GitHub:**

```yaml
- name: Safety Check
  uses: pyupio/safety@2.3.5
```

**Referências:**

- Docs: <https://pyup.io/safety/\>
- Database: <https://github.com/pyupio/safety-db\>

---

### Radon (Complexity Metrics) - Produção

**O que é:** Ferramenta para calcular complexidade ciclomática.

**Quando usar:** Produção (opcional para MVP).

**Métricas:**

- Cyclomatic Complexity (CC)
- Maintainability Index (MI)
- Halstead metrics
- Lines of Code

**Limites recomendados:**

- CC < 10: Boa (simples)
- CC 11-20: Média (moderada)
- CC > 20: Alta (refatorar)

**CI/CD:**

```yaml
- name: Radon Complexity
  run: |
    pip install radon
    radon cc src/ -n C  # Bloqueia se CC > 10
    radon mi src/ -n B  # Bloqueia se MI < 20
```

**Referências:**

- Docs: <https://radon.readthedocs.io/\>
- McCabe: <https://en.wikipedia.org/wiki/Cyclomatic_complexity\>

---

### SonarQube (Code Quality Platform) - Produção

**O que é:** Plataforma completa de análise de código.

**Quando usar:** Produção (overkill para POC/MVP).

**O que analisa:**

- Bugs
- Code smells
- Security vulnerabilities
- Technical debt
- Duplicação de código
- Coverage

**Configuração:**

```yaml
# sonar-project.properties
sonar.projectKey=datasus-analytics
sonar.sources=src
sonar.tests=tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.version=3.11
```

**CI/CD:**

```yaml
- name: SonarQube Scan
  uses: SonarSource/sonarqube-scan-action@master
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
```

**Alternativas gratuitas:**

- SonarCloud (GitHub integration, free para OSS)
- CodeClimate (similar)

**Referências:**

- Docs: <https://docs.sonarqube.org/\>
- SonarCloud: <https://sonarcloud.io/\>

---

### Docker Build - Produção

**O que é:** Containerização da aplicação.

**Quando usar:** Produção (opcional para MVP).

**Dockerfile exemplo:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY docs/ ./docs/

CMD ["python", "-m", "src.main"]
```

**CI/CD:**

```yaml
- name: Build Docker Image
  run: |
    docker build -t datasus-analytics:${{ github.sha }} .
    docker tag datasus-analytics:${{ github.sha }} datasus-analytics:latest

- name: Push to Registry
  run: |
    echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
    docker push datasus-analytics:latest
```

**Referências:**

- Best practices: <https://docs.docker.com/develop/dev-best-practices/\>
- Multi-stage: <https://docs.docker.com/build/building/multi-stage/\>

---

## Configuração

### Ordem de Implementação

**POC (Concluída - v0.2.6):**

- [x] Ruff
- [x] Mypy
- [x] Pytest
- [x] Pre-commit
- [x] VCR.py
- [x] Codecov

**MVP (Planejado):**

- [ ] Tenacity (retry logic)
- [ ] Bandit
- [ ] Safety

**Produção (v2.0.0):**

- [ ] Radon
- [ ] SonarQube/SonarCloud
- [ ] Docker Build

---

## CI/CD Pipeline Completo

### POC (Atual)

```yaml
jobs:
  test:
    - Ruff check/format
    - Mypy
    - Pytest + coverage (VCR.py cassettes)
    - Codecov upload
```

### MVP

```yaml
jobs:
  test:
    - Pre-commit
    - Ruff
    - Mypy
    - Pytest + coverage
    - Bandit security
    - Safety dependencies
    - Codecov upload
```

### Produção

```yaml
jobs:
  quality:
    - Pre-commit
    - Ruff
    - Mypy
    - Radon complexity

  security:
    - Bandit
    - Safety

  test:
    - Pytest + coverage
    - Codecov

  analysis:
    - SonarQube scan

  build:
    - Docker build/push
```

---

## Referências

- Python Packaging Authority: <https://www.pypa.io/\>
- PEP 8 Style Guide: <https://peps.python.org/pep-0008/\>
- GitHub Actions: <https://docs.github.com/en/actions\>
- Docker Best Practices: <https://docs.docker.com/develop/dev-best-practices/\>

---
