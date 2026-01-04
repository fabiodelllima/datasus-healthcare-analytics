# Decision Log - DataSUS Analytics

Registro cronológico de decisões arquiteturais e técnicas importantes.

**Formato:** Cada decisão documenta contexto, alternativas consideradas, razionale e consequências.

---

## 2025-12-22: Não Usar Microsserviços

**Contexto:**
Considerando arquitetura para processar dados de todos os 27 estados brasileiros.
Volume projetado: 10-50M registros, 5-20 GB processados.

**Decisão:** Modular Monolith em vez de Microsserviços.

**Alternativas consideradas:**

1. **Microsserviços** (rejeitado)

   - Prós: Escala independente, isolamento falhas
   - Contras: Overhead operacional (Kubernetes, service mesh), complexidade desnecessária
   - Por que não: Volume < 100M registros, time pequeno (1-5 devs), domínio coeso

2. **Serverless (AWS Lambda)** (rejeitado)

   - Prós: Zero infra, escala automática
   - Contras: Cold start, timeout 15min, vendor lock-in
   - Por que não: ETL pode levar >15min para UFs grandes

3. **Modular Monolith** (escolhido)
   - Prós: Simples operar, deploy único, transações ACID, menor custo
   - Contras: Escala vertical limitada, acoplamento moderado
   - Por que sim: Adequado para <1M registros/dia, fácil manter

**Consequências:**

- [+] Menor complexidade operacional
- [+] Deploy e rollback simples
- [+] Transações ACID mantidas
- [-] Escala limitada a vertical scaling
- [-] Acoplamento entre módulos

**Revisão:** Q1 2026 se volume exceder 50M registros ou 100k requests/dia.

**Referências:**

- Martin Fowler: "MonolithFirst" - <https://martinfowler.com/bliki/MonolithFirst.html>
- Sam Newman: "Monolith to Microservices"

---

## 2025-12-22: Stack Observabilidade - Loki + Prometheus + Grafana

**Contexto:**
Definir stack de monitoramento para Produção.

**Decisão:** Loki + Prometheus + Grafana (stack coesa).

**Alternativas consideradas:**

1. **ELK Stack (Elasticsearch + Logstash + Kibana)** (rejeitado)

   - Prós: Mature, poderoso, rico em features
   - Contras: Pesado (>4GB RAM), complexo configurar, custo alto
   - Por que não: Overkill para volume inicial

2. **Loki + Prometheus + Grafana** (escolhido)

   - Prós: Integração nativa, leve (<1GB RAM), mesmo vendor (Grafana Labs)
   - Contras: Menos features que ELK
   - Por que sim: Adequado para analytics, não transacional

3. **Prometheus sozinho** (rejeitado)
   - Prós: Simples, foco em métricas
   - Contras: Sem logs centralizados
   - Por que não: Precisa de logs para debugging

**Componentes:**

- **Loki:** Logs (eventos, debugging)
- **Prometheus:** Métricas (quantitativas - latency, errors, throughput)
- **Grafana:** Dashboards unified

**Consequências:**

- [+] Stack leve e integrada
- [+] Menor curva de aprendizado
- [+] Cost-effective
- [-] Menos poderoso que ELK para search complexo

**Revisão:** Se precisar full-text search avançado em logs, considerar ELK.

**Referências:**

- Grafana Loki: <https://grafana.com/oss/loki>
- Prometheus: <https://prometheus.io>

---

## 2025-12-17: Metodologia DOCS > BDD > TDD > CODE

**Contexto:**
Definir metodologia de desenvolvimento para features futuras após identificação de anti-pattern em v0.2.0.

**Decisão:** Hierarquia obrigatória DOCS → BDD → TDD → CODE com TDD incremental.

**Problema identificado:**
Em v0.2.0, escrevemos todos os testes (40 BDD + 45 unitários) ANTES de implementar o código, resultando em 45 testes RED permanentes. Isso viola o princípio TDD de progresso incremental.

**Solução adotada:**
TDD incremental por regra de negócio:

1. Documentar 1 RN em docs/
2. Escrever 1 cenário BDD
3. Escrever 1 teste unitário (RED)
4. Implementar mínimo necessário (GREEN)
5. Refatorar mantendo testes verdes (REFACTOR)
6. Commit e repetir

**Consequências:**

- [+] TDD real (RED → GREEN → REFACTOR por feature)
- [+] Progresso incremental visível
- [+] Testes sempre verdes (exceto durante RED phase)
- [-] Specs menos antecipadas (tradeoff aceitável)

**Revisão:** Avaliar efetividade em v0.3.0.

**Referências:**

- Kent Beck: "Test-Driven Development by Example"
- docs/METHODOLOGY.md para detalhes de implementação

---

## 2025-12-05: Python 3.11 (não 3.12+)

**Contexto:**
Escolher versão Python para o projeto.

**Decisão:** Python 3.11.x (não 3.12 ou 3.13).

**Razionale:**

- pysus (biblioteca da Fiocruz/AlertaDengue) não suporta Python 3.12+
- Python 3.11 é estável e tem bom suporte de bibliotecas
- Type hints modernos disponíveis (PEP 604: `dict[str, Any]` nativo)

**Alternativas:**

- Python 3.12: Não compatível com pysus
- Python 3.10: Funciona, mas syntax menos moderna

**Consequências:**

- [+] Compatibilidade total com pysus
- [+] Type hints modernos
- [-] Não usa features Python 3.12+ (PEP 695 generic syntax)

**Revisão:** Quando pysus suportar 3.12+ ou quando implementarmos extração FTP própria.

---

## 2025-12-30: VCR.py para HTTP Mocking

**Contexto:**
Testes de API falhavam por timeout/instabilidade do servidor OpenDataSUS.

**Decisão:** Usar VCR.py para gravar e reproduzir respostas HTTP.

**Alternativas consideradas:**

1. **Mock manual (unittest.mock)** (rejeitado)

   - Prós: Sem dependências extras
   - Contras: Muito trabalho manual, não captura requests reais
   - Por que não: Propenso a erros, respostas fake

2. **responses** (rejeitado)

   - Prós: Simples para casos básicos
   - Contras: Não grava automaticamente
   - Por que não: Preferimos capturar respostas reais

3. **VCR.py** (escolhido)
   - Prós: Grava requests reais em cassettes YAML, reproduz deterministicamente
   - Contras: Cassettes precisam ser atualizadas se API mudar
   - Por que sim: Testes determinísticos, rápidos, não dependem de rede

**Consequências:**

- [+] Testes determinísticos (não falham por rede)
- [+] CI/CD não depende de serviços externos
- [+] Execução rápida (sem I/O de rede)
- [-] Cassettes precisam ser regravadas se API mudar

**Revisão:** Se API mudar frequentemente, considerar mock manual para endpoints críticos.

---

## Template para Novas Decisões

```markdown
## YYYY-MM-DD: Título da Decisão

**Contexto:**
[Situação que motivou a decisão]

**Decisão:** [O que foi decidido]

**Alternativas consideradas:**

1. **Opção A** (escolhida/rejeitada)
   - Prós:
   - Contras:
   - Por que sim/não:

**Consequências:**

- [+] Vantagem 1
- [-] Desvantagem 1

**Revisão:** [Quando reavaliar]

**Referências:**

- [Links relevantes]
```

---

**Última atualização:** 03/01/2026
