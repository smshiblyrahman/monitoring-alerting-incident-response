# Runbook: High Error Rate (5xx)

## 1. Alert Name
`HighErrorRate`

## 2. Impact
Users experience HTTP 500 internal server errors on order operations. Checkout and API transactions may fail.

## 3. Symptoms
- HTTP 5xx error rate exceeds 5% of total requests over a 30s evaluation window.
- Error alerts firing in Alertmanager and Slack #incident-alerts.

## 4. Initial Checks
1. Inspect the Grafana Application Performance Dashboard: `http://localhost:3000/d/app-perf-dash`
2. Check the recent error logs on target pod or service:
   ```bash
   kubectl logs -l app=order-service --tail=100
   # or docker compose
   docker compose logs --tail=50 order-app
   ```
3. Check database connectivity and connection pool metrics.

## 5. Diagnostic Commands
```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/metrics | grep http_requests_total
```

## 6. Dashboards
- [Grafana Application Performance](http://localhost:3000/d/app-perf-dash)
- [Grafana Database Dashboard](http://localhost:3000/d/db-health-dash)

## 7. Likely Causes
- Database connection pool exhaustion.
- Downstream microservice outage or network partition.
- Faulty application release deployment.

## 8. Mitigation
- If automated remediation is active, the webhook service attempts a bounded service reset (max 3 retries, 300s cooldown).
- If manual intervention is required:
  ```bash
  # Reset faulty state
  curl -X POST http://localhost:8000/chaos/reset
  # Restart deployment
  kubectl rollout restart deployment/order-service
  ```

## 9. Rollback
If caused by a recent deployment:
```bash
kubectl rollout undo deployment/order-service
```

## 10. Escalation
- Escalate to Primary On-Call Backend Engineer if unresolved after 5 minutes.
- Slack: `@backend-ops-oncall`
- PagerDuty: `PD-TIER-1-SYSENG`

## 11. Post-Incident Action
- Collect incident timeline from `/api/incidents`.
- Fill postmortem template in `docs/runbooks/RCA_TEMPLATE.md`.
