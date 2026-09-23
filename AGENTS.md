# Project Context: Automated Monitoring, Alerting & Incident Response System

## Stack & Architecture
- Runtime: Python 3.11+ (FastAPI for Automated Remediation Webhook, pytest for tests)
- Metrics & Monitoring: Prometheus, Node Exporter, kube-state-metrics, Alertmanager
- Visualization: Grafana (Provisioned dashboards & datasources)
- Orchestration & Deployments: Docker Compose (local dev/test) + Kubernetes / AKS manifests
- Alerting & Automation: Webhook receiver with idempotency, cooldowns, and loop guard

## Conventions
- Code style: PEP 8, typed Python with Pydantic v2
- Testing: pytest for unit/integration tests
- Infrastructure as Code: declarative Kubernetes YAML manifests and Docker Compose configs
- Plain language in docs, no punctuation dashes

## Agent skills
- `architect`: `docs/specs/` decision specs
- `develop`: implementation builder
- `caveman`: token efficient communication
