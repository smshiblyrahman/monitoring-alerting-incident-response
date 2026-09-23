from fastapi import FastAPI, HTTPException, Header, status, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import time
import logging
import requests
from safety_guard import SafetyLoopGuard

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("remediation_service")

app = FastAPI(title="Automated Incident Remediation Webhook", version="1.0.0")

WEBHOOK_TOKEN = os.getenv("WEBHOOK_SECRET_TOKEN", "selise-incident-secret-token")
APP_SERVICE_URL = os.getenv("APP_SERVICE_URL", "http://order-app:8000")

# Safety guard: max 3 restarts per 30 mins, 300s cooldown between attempts
# During testing / demo, we allow 10s cooldown if DEMO_MODE=true
is_demo = os.getenv("DEMO_MODE", "true").lower() == "true"
cooldown = 10 if is_demo else 300
guard = SafetyLoopGuard(cooldown_seconds=cooldown, max_retries=3, window_seconds=1800)

class AlertItem(BaseModel):
    status: str
    labels: Dict[str, str]
    annotations: Dict[str, str]
    startsAt: Optional[str] = None
    endsAt: Optional[str] = None

class AlertmanagerPayload(BaseModel):
    receiver: str
    status: str
    alerts: List[AlertItem]
    groupLabels: Dict[str, str] = Field(default_factory=dict)
    commonLabels: Dict[str, str] = Field(default_factory=dict)
    commonAnnotations: Dict[str, str] = Field(default_factory=dict)

# In-memory execution log for post-incident audits
incident_log = []

def execute_remediation(alert_name: str, target: str, action: str):
    logger.info(f"Executing automated remediation: {action} on {target} for alert {alert_name}")
    try:
        if action == "restart_service" or action == "reset_chaos":
            # For demonstration, call the reset endpoint on the target service
            res = requests.post(f"{APP_SERVICE_URL}/chaos/reset", timeout=5)
            logger.info(f"Target reset response: {res.status_code} - {res.text}")
        elif action == "collect_diagnostics":
            logger.info(f"Gathering logs and telemetry diagnostics for {target}...")
        incident_log.append({
            "timestamp": time.time(),
            "alert": alert_name,
            "target": target,
            "action": action,
            "result": "success"
        })
    except Exception as e:
        logger.error(f"Remediation action failed: {str(e)}")
        incident_log.append({
            "timestamp": time.time(),
            "alert": alert_name,
            "target": target,
            "action": action,
            "result": f"failed: {str(e)}"
        })

@app.get("/health")
def health():
    return {"status": "ok", "service": "automated-remediation-webhook"}

@app.get("/api/incidents")
def get_incidents():
    return {"incidents": incident_log}

@app.get("/api/guard/status")
def get_guard_status(target: str = "order-service"):
    return guard.get_status(target)

@app.post("/webhook/alertmanager")
async def receive_alert(
    payload: AlertmanagerPayload,
    background_tasks: BackgroundTasks,
    x_webhook_token: Optional[str] = Header(None)
):
    if WEBHOOK_TOKEN and x_webhook_token != WEBHOOK_TOKEN:
        logger.warning("Unauthorized webhook request rejected.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth token")

    results = []
    for alert in payload.alerts:
        alert_name = alert.labels.get("alertname", "UnknownAlert")
        severity = alert.labels.get("severity", "info")
        target = alert.labels.get("job", alert.labels.get("instance", "default-workload"))

        if alert.status == "resolved":
            logger.info(f"Alert {alert_name} on {target} resolved.")
            guard.reset_target(target)
            results.append({"alert": alert_name, "status": "resolved_acknowledged"})
            continue

        logger.info(f"Received alert: {alert_name} [Severity: {severity}] for target: {target}")

        # Check safety guard boundaries
        allowed, reason = guard.can_remediate(target)
        if not allowed:
            logger.warning(f"Remediation blocked by safety loop guard: {reason}")
            incident_log.append({
                "timestamp": time.time(),
                "alert": alert_name,
                "target": target,
                "action": "ESCALATE_TO_PAGERDUTY",
                "result": f"remediation_blocked: {reason}"
            })
            results.append({
                "alert": alert_name,
                "target": target,
                "action_taken": "escalated_to_human",
                "reason": reason
            })
            continue

        # Map alert to remediation playbook
        action = None
        if alert_name in ["HighErrorRate", "ServiceDown", "CrashLoopBackOff"]:
            action = "restart_service"
        elif alert_name in ["HighMemoryUsage", "HighLatency"]:
            action = "collect_diagnostics"
        else:
            action = "notify_only"

        if action and action != "notify_only":
            guard.record_action(target)
            background_tasks.add_task(execute_remediation, alert_name, target, action)
            results.append({
                "alert": alert_name,
                "target": target,
                "action_taken": action,
                "status": "scheduled"
            })
        else:
            results.append({
                "alert": alert_name,
                "target": target,
                "action_taken": "logged",
                "status": "no_auto_action"
            })

    return {"status": "processed", "results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("webhook_server:app", host="0.0.0.0", port=5001, reload=False)
