# Project 4: Automated Monitoring, Alerting & Incident Response System

Comprehensive implementation of Project 4 aligned with SELISE SysOps requirements.

## Architecture

```
                    +--------------------+
                    | Simulated Traffic  |
                    +---------+----------+
                              |
                              v
                   +---------------------+
                   |   order-service     | (FastAPI + Prometheus metrics)
                   +----------+----------+
                              |
                     /metrics | scrape
                              v
                   +---------------------+
                   |     Prometheus      | (Scrapes, evaluates alert rules)
                   +----------+----------+
                              |
                      firing  | alerts
                              v
                   +---------------------+
                   |    Alertmanager     | (Routes by severity)
                   +----------+----------+
                              |
                     webhook  | POST (with shared secret)
                              v
            +---------------------------------+
            |   remediation-webhook           |
            |   - SafetyLoopGuard (cooldown)  |
            |   - Retry caps (max 3)          |
            |   - Escalation to on-call       |
            +-----------------+---------------+
                              |
                              v
                     Automated Recovery
                     (POST /chaos/reset)
```

## Directory Structure

- `04-monitoring-alerting-incident-response.md`: Foundation document (citations cleaned).
- [AGENTS.md](file:///Users/smshiblyrahman/Documents/monitoring-alerting-incident-response/AGENTS.md): Repository context and technical conventions.
- [docs/specs/0001-monitoring-alerting-incident-response.md](file:///Users/smshiblyrahman/Documents/monitoring-alerting-incident-response/docs/specs/0001-monitoring-alerting-incident-response.md): Architecture build specification.
- [docs/runbooks/](file:///Users/smshiblyrahman/Documents/monitoring-alerting-incident-response/docs/runbooks/):
  - [RUNBOOK_HIGH_ERROR_RATE.md](file:///Users/smshiblyrahman/Documents/monitoring-alerting-incident-response/docs/runbooks/RUNBOOK_HIGH_ERROR_RATE.md): Standardized 11-step incident response playbook.
  - [RUNBOOK_SERVICE_DOWN.md](file:///Users/smshiblyrahman/Documents/monitoring-alerting-incident-response/docs/runbooks/RUNBOOK_SERVICE_DOWN.md): Outage response playbook.
  - [RCA_TEMPLATE.md](file:///Users/smshiblyrahman/Documents/monitoring-alerting-incident-response/docs/runbooks/RCA_TEMPLATE.md): Blameless postmortem template with 5-whys & MTTD/MTTR.
- `src/`:
  - `app/app.py`: Instrumented microservice with metrics (`/metrics`) and chaos simulation endpoints.
  - `remediation/`:
    - `safety_guard.py`: Bounded self healing loop guard with cooldowns and retry caps.
    - `webhook_server.py`: FastAPI Alertmanager webhook processor.
- `config/`:
  - `prometheus/`: Scrape configurations and alert rules (`HighErrorRate`, `ServiceDown`, `HighLatency`, `HighMemoryUsage`).
  - `alertmanager/`: Alert routing by severity (`critical`, `warning`).
  - `grafana/`: Datasource provisioning and 5 JSON dashboards:
    1. Infrastructure Metrics
    2. Application Performance
    3. Kubernetes Cluster Health
    4. Database Health
    5. Security & Access Audit
- `docker-compose.yml`: Full local stack.
- `k8s/`: Production Kubernetes/AKS manifests with RBAC ServiceAccount for self healing.
- `scripts/simulate_chaos.py`: Automated end to end failure injection and recovery verification script.

## Running Locally with Docker Compose

```bash
docker compose up -d --build
```

Access services:
- **Application**: http://localhost:8000
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093
- **Grafana**: http://localhost:3000 (user: `admin`, pass: `admin`)
- **Remediation Webhook**: http://localhost:5001

## Running Chaos Simulation & Automated Recovery

```bash
python3 scripts/simulate_chaos.py
```
