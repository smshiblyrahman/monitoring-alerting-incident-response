# Runbook: Service Down

## 1. Alert Name
`ServiceDown`

## 2. Impact
Complete outage of `order-service`. Incoming customer traffic receives connection refused or 502/503 Bad Gateway.

## 3. Symptoms
- Prometheus metric `up{job="order-service"} == 0` for more than 5 seconds.
- Alertmanager routes critical paging alert to PagerDuty and Webhook.

## 4. Initial Checks
1. Verify if pod or container crashed:
   ```bash
   kubectl get pods -l app=order-service
   # or docker compose
   docker compose ps order-app
   ```
2. Check container exit code and termination reason (OOMKilled, Panic):
   ```bash
   kubectl describe pod -l app=order-service
   ```

## 5. Diagnostic Commands
```bash
curl -i http://localhost:8000/health
```

## 6. Dashboards
- [Grafana Kubernetes Cluster Health](http://localhost:3000/d/k8s-health-dash)
- [Grafana Infrastructure Metrics](http://localhost:3000/d/infra-metrics-dash)

## 7. Likely Causes
- Node out of memory (OOMKilled).
- Unhandled application runtime exception causing fatal process exit.
- Liveness probe failure resulting in kubelet kill loop.

## 8. Mitigation
- Automated webhook attempts self healing restart (capped at 3 attempts).
- Manual mitigation:
  ```bash
  kubectl rollout restart deployment/order-service
  ```

## 9. Rollback
```bash
kubectl rollout undo deployment/order-service
```

## 10. Escalation
- Escalate to SysOps Lead if not restored within 2 minutes.
- Bridge link: `https://meet.company.com/incident-war-room`

## 11. Post-Incident Action
- Document crash stack trace and root cause in RCA postmortem.
