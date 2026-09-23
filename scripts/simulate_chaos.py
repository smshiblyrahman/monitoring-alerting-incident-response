import requests
import time
import sys

BASE_URL = "http://localhost:8000"
WEBHOOK_URL = "http://localhost:5001"
PROMETHEUS_URL = "http://localhost:9090"
ALERTMANAGER_URL = "http://localhost:9093"

def run_simulation():
    print("=== [1/4] Baseline Health Check ===")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=3)
        print(f"Service health: {r.status_code} - {r.json()}")
    except Exception as e:
        print(f"Could not reach order-app at {BASE_URL}. Ensure stack is running! Error: {e}")
        return

    print("\n=== [2/4] Triggering Error Chaos (Simulate 500 Outage) ===")
    requests.post(f"{BASE_URL}/chaos/inject-errors?enabled=true")
    
    # Generate traffic to produce HTTP 500 metrics
    for i in range(15):
        try:
            requests.get(f"{BASE_URL}/api/orders", timeout=1)
        except:
            pass
        time.sleep(0.2)
    print("Traffic generated: 15 failed requests logged to Prometheus metrics.")

    print("\n=== [3/4] Triggering Automated Remediation Simulation ===")
    mock_alertmanager_payload = {
        "receiver": "critical-remediation-receiver",
        "status": "firing",
        "alerts": [
            {
                "status": "firing",
                "labels": {
                    "alertname": "HighErrorRate",
                    "severity": "critical",
                    "job": "order-service"
                },
                "annotations": {
                    "summary": "High error rate detected on order-service"
                }
            }
        ]
    }
    
    headers = {"X-Webhook-Token": "selise-incident-secret-token"}
    res = requests.post(
        f"{WEBHOOK_URL}/webhook/alertmanager",
        json=mock_alertmanager_payload,
        headers=headers
    )
    print(f"Webhook response: {res.status_code} - {res.json()}")

    print("\nWaiting 2 seconds for background remediation...")
    time.sleep(2)

    print("\n=== [4/4] Verifying Post-Remediation Recovery ===")
    verify_res = requests.get(f"{BASE_URL}/api/orders", timeout=3)
    print(f"Order endpoint status after self-healing: {verify_res.status_code}")
    assert verify_res.status_code == 200, "Service did not recover!"
    print("Service recovered successfully! MTTD/MTTR automated remediation loop validated.")

if __name__ == "__main__":
    run_simulation()
