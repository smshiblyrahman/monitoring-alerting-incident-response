# Root Cause Analysis (RCA) Postmortem Template

## 1. Incident Overview
- **Incident ID**: INC-YYYYMMDD-01
- **Severity**: Critical (P1) / Warning (P2)
- **Impacted Services**: `order-service`
- **Incident Commander / Lead**: <Name>
- **Date & Time (UTC)**:
- **Mean Time to Detect (MTTD)**: <Minutes>
- **Mean Time to Acknowledge (MTTA)**: <Minutes>
- **Mean Time to Recover (MTTR)**: <Minutes>

## 2. Executive Summary
Brief non-technical description of the incident and impact to business/users.

## 3. Timeline
| Timestamp (UTC) | Event Description | Detected By |
|---|---|---|
| 00:00 | Issue introduced (e.g. faulty deployment or memory leak) | System |
| 00:02 | Alert triggered (`HighErrorRate` or `ServiceDown`) | Prometheus |
| 00:03 | Webhook automated remediation triggered | Alertmanager |
| 00:04 | Service restored to healthy state | Health Check |

## 4. Root Cause (5 Whys)
1. Why did the service fail? (e.g., Connection pool exhausted)
2. Why was the pool exhausted? (e.g., Leaked connections on timeout)
3. Why did queries timeout? (e.g., Missing index on orders table)
4. Why was the index missing? (e.g., Migration script skipped in release)
5. Why was migration skipped? (e.g., CI/CD pipeline step had non-blocking error flag)

## 5. What Went Well
- Automated alert fired within 10 seconds.
- Runbook clearly identified first step diagnostic commands.
- Safety guard prevented infinite restart loops.

## 6. Where We Got Lucky
- Failover database absorbed read traffic.

## 7. Action Items & Preventive Improvements
- [ ] Add database connection leak detection alert (Owner: Ops, Due: YYYY-MM-DD)
- [ ] Enforce schema migration gate in CD pipeline (Owner: DevOps, Due: YYYY-MM-DD)
- [ ] Update runbook with new query optimization guide (Owner: SRE, Due: YYYY-MM-DD)
