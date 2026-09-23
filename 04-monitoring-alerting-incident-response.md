# Project 4 — Automated Monitoring, Alerting & Incident Response System

## SELISE-Oriented Technical Implementation Plan

## 1. Project Purpose

This project should demonstrate that the engineer can **operate** infrastructure after deployment.

The supplied project combines Azure Monitor, Application Insights, Log Analytics, Prometheus, Grafana, Alertmanager, Slack, email, PagerDuty, webhooks, and Python automation. turn0file0

The current SELISE SysOps role explicitly emphasizes monitoring systems and incident response, infrastructure availability, troubleshooting, and automation. turn0search0

## 2. Observability Goals

The system must answer:

1. Is the service available?
2. Is it slow?
3. Is it producing errors?
4. Which dependency is failing?
5. Which environment is affected?
6. When did the problem start?
7. Who should be notified?
8. Can the issue be remediated automatically?
9. If not, what is the runbook?

## 3. Architecture

```text
Applications
   |
   +---- Application Insights
   |
AKS
   |
   +---- Prometheus ----+
   |                    |
   +---- Logs           |
                        v
                     Grafana
                        |
                     Alerts
                        |
                  Alertmanager
              /        |        \
          Slack       Email    PagerDuty
                                |
                             Webhook
                                |
                         Python Automation
```

## 4. Three Observability Signals

### Metrics

Examples:

- Request rate.
- Error rate.
- Latency.
- CPU.
- Memory.
- Pod restarts.

### Logs

Examples:

- Application errors.
- Authentication failures.
- Deployment events.
- Infrastructure events.

### APM/Tracing

Use Application Insights for application performance and dependency visibility where applicable.

## 5. Dashboard Strategy

The supplied project defines five major dashboard categories. turn0file0

### Infrastructure

- CPU.
- Memory.
- Disk.
- Network.

### Application

- Throughput.
- P50/P95/P99 latency.
- Error rate.
- Dependency failures.

### Kubernetes

- Node status.
- Pod status.
- Restarts.
- Pending pods.
- Resource pressure.

### Database

- Connections.
- Query performance.
- Slow operations.

### Security

- Failed logins.
- Unauthorized access.
- Vulnerability findings.

## 6. Alert Philosophy

Alerts must be actionable.

### Critical

- Service unavailable.
- Database failure.
- Critical pod crash.

### Warning

- High CPU.
- High memory.
- Elevated latency.

### Informational

- Deployment.
- Scaling event.

The severity model follows the supplied project. turn0file0

## 7. Prometheus Alert Example

```yaml
groups:
  - name: application_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status="500"}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
```

The metric name, label model, and threshold must be validated against the real application.

## 8. Alert Routing

```text
Critical
  -> PagerDuty
  -> Slack
  -> Email

Warning
  -> Slack
  -> Team channel

Info
  -> Slack
```

Routing should be ownership-aware.

## 9. Incident Response Workflow

```text
Alert
 |
Validate
 |
Classify
 |
Acknowledge
 |
Investigate
 |
Mitigate
 |
Recover
 |
Verify
 |
Document
 |
RCA
```

## 10. Automated Remediation

The supplied project includes Python automation for:

- Pod restart.
- Custom-metric scaling triggers.
- Log collection.
- Health checks. turn0file0

Use safety controls:

```text
Alert
 ↓
Check condition still true
 ↓
Check cooldown
 ↓
Check retry count
 ↓
Execute remediation
 ↓
Verify result
 ↓
Escalate if unsuccessful
```

Never allow unlimited automated restart loops.

## 11. Runbook Standard

Every critical alert should have:

```text
Alert name
Impact
Symptoms
Initial checks
Commands
Dashboard
Likely causes
Mitigation
Rollback
Escalation
Post-incident action
```

Example:

```text
HIGH_ERROR_RATE

1. Check Grafana.
2. Check latest deployment.
3. Check pod logs.
4. Check dependency health.
5. Check database.
6. Roll back if deployment-related.
7. Escalate if unresolved.
```

## 12. Incident Metrics

Measure:

- MTTD.
- MTTA.
- MTTR.
- Incident frequency.
- Repeat incidents.
- Alert noise.
- Automated remediation success rate.

The supplied project reports MTTD improvement from 25 minutes to 2 minutes. Treat this as a project-specific reported result and validate it with incident timestamps before presenting it as measured evidence. turn0file0

## 13. Root Cause Analysis

For important incidents:

```text
What happened?
Why did it happen?
Why wasn't it detected earlier?
What reduced the impact?
What should change?
What monitoring should be added?
What automation should be improved?
```

Avoid blaming individuals; focus on system/process improvement.

## 14. Implementation Plan

### Phase 1 — Instrumentation

- Application metrics.
- APM.
- Structured logs.

### Phase 2 — Collection

- Prometheus.
- Azure Monitor.
- Log Analytics.
- Log aggregation.

### Phase 3 — Dashboards

- Infrastructure.
- Application.
- Kubernetes.
- Database.
- Security.

### Phase 4 — Alerts

- Severity.
- Ownership.
- Routing.
- Noise control.

### Phase 5 — Automation

- Health checks.
- Safe remediation.
- Escalation.

### Phase 6 — Incident Testing

Simulate:

- Pod failure.
- High error rate.
- CPU saturation.
- Memory pressure.
- Database failure.
- Bad deployment.

## 15. SELISE Alignment

This project demonstrates:

```text
Monitoring
Incident response
Troubleshooting
Availability
Operational automation
Cloud operations
Kubernetes operations
Security visibility
Documentation
Continuous improvement
```

These map closely to the current SELISE SysOps responsibilities around monitoring, availability, troubleshooting, incident response and operational automation. turn0search0

## 16. Acceptance Criteria

```text
[ ] Application metrics available
[ ] Infrastructure metrics available
[ ] Centralized logs available
[ ] Grafana dashboards exist
[ ] Critical alerts route correctly
[ ] Alerts have runbooks
[ ] Automated remediation is bounded
[ ] Incidents are timestamped
[ ] RCA template exists
[ ] Failure simulations have been performed
```

## 17. Interview Questions

1. What is the difference between monitoring and observability?
2. How do you reduce alert noise?
3. How do you define a critical alert?
4. How would you troubleshoot high latency?
5. How would you identify whether an issue came from a deployment?
6. What is MTTD vs MTTR?
7. When should remediation be automated?
8. How do you prevent automation from making an incident worse?
9. What information belongs in an incident runbook?
10. How do you perform RCA?
