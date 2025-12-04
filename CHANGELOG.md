# CHANGELOG

Todas as mudanças notáveis do projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [Unreleased]

### Em desenvolvimento

- Pipeline ETL POC em andamento

---

## [0.1.0] - 2024-12-03

### Adicionado

- Estrutura inicial do projeto
- Documentação completa (4 arquivos SSOT):
  - README.md (entry point)
  - ARCHITECTURE.md (stack técnico + ADRs)
  - DATA_GUIDE.md (dicionário dados + regras + ETL)
  - ROADMAP.md (planejamento + cronograma + riscos)
- ADR-001: Decisão usar dados reais DataSUS
- ADR-002: Decisão Python 3.11 (não 3.14)
- ADR-003: Decisão formato dual CSV + Parquet
- ADR-004: Decisão documentação modular
- Estrutura código Python:
  - src/extract/ (módulo Extract)
  - src/transform/ (módulo Transform)
  - src/load/ (módulo Load)
  - src/utils/ (utilitários)
  - src/main.py (pipeline principal)
- requirements.txt com dependências POC
- .gitignore configurado para Python/dados
- Estrutura diretórios: data/, logs/, outputs/, tests/

### Configurado

- Python 3.11.x como versão obrigatória
- Ambiente virtual (venv)
- Logging estruturado

---

## Tipos de Mudanças

- **Adicionado** para novas funcionalidades
- **Modificado** para mudanças em funcionalidades existentes
- **Descontinuado** para funcionalidades que serão removidas
- **Removido** para funcionalidades removidas
- **Corrigido** para correções de bugs
- **Segurança** para vulnerabilidades

---

## Versionamento

```
MAJOR.MINOR.PATCH

MAJOR: Mudanças incompatíveis na API
MINOR: Novas funcionalidades compatíveis
PATCH: Correções de bugs compatíveis

Exemplos:
0.1.0 = POC inicial
0.2.0 = MVP features
1.0.0 = Produção release
```

---

**Nota:** Versões 0.x.x são consideradas desenvolvimento inicial.
