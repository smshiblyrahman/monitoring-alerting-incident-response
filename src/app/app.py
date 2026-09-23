from fastapi import FastAPI, HTTPException, Response, status
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
import random
import os

app = FastAPI(title="Sample Microservice with Observability", version="1.0.0")

# Prometheus Metrics
REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "status"]
)
REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP Request Latency in seconds",
    ["endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)
ACTIVE_CONNECTIONS = Gauge(
    "app_active_connections",
    "Current active database or client connections"
)
MEMORY_LEAK_BYTES = Gauge(
    "app_simulated_memory_usage_bytes",
    "Simulated memory footprint"
)

# State for chaos testing
chaos_state = {
    "error_mode": False,
    "latency_seconds": 0.0,
    "memory_leak_mb": 50.0,
    "is_healthy": True
}

ACTIVE_CONNECTIONS.set(12)
MEMORY_LEAK_BYTES.set(chaos_state["memory_leak_mb"] * 1024 * 1024)

@app.middleware("http")
async def record_metrics_middleware(request, call_next):
    start_time = time.time()
    endpoint = request.url.path
    response = None
    try:
        response = await call_next(request)
        status_code = str(response.status_code)
    except Exception as exc:
        status_code = "500"
        REQUESTS_TOTAL.labels(method=request.method, endpoint=endpoint, status=status_code).inc()
        raise exc
    duration = time.time() - start_time
    REQUESTS_TOTAL.labels(method=request.method, endpoint=endpoint, status=status_code).inc()
    REQUEST_DURATION_SECONDS.labels(endpoint=endpoint).observe(duration)
    return response

@app.get("/health")
def health():
    if not chaos_state["is_healthy"]:
        raise HTTPException(status_code=503, detail="Unhealthy: service is in degraded state")
    return {"status": "healthy", "service": "order-service", "version": "1.0.0"}

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/orders")
def get_orders():
    if chaos_state["latency_seconds"] > 0:
        time.sleep(chaos_state["latency_seconds"])
    if chaos_state["error_mode"]:
        raise HTTPException(status_code=500, detail="Internal Database Connection Pool Exhausted")
    return {
        "orders": [
            {"id": "ORD-101", "item": "Cloud Compute Node", "price": 120.00, "status": "COMPLETED"},
            {"id": "ORD-102", "item": "Database Storage Volume", "price": 45.00, "status": "PENDING"}
        ],
        "latency_added": chaos_state["latency_seconds"]
    }

# Fault injection endpoints for chaos testing
@app.post("/chaos/inject-errors")
def inject_errors(enabled: bool = True):
    chaos_state["error_mode"] = enabled
    return {"message": f"Error mode set to {enabled}"}

@app.post("/chaos/inject-latency")
def inject_latency(seconds: float = 2.0):
    chaos_state["latency_seconds"] = seconds
    return {"message": f"Latency set to {seconds}s"}

@app.post("/chaos/leak-memory")
def leak_memory(add_mb: float = 100.0):
    chaos_state["memory_leak_mb"] += add_mb
    MEMORY_LEAK_BYTES.set(chaos_state["memory_leak_mb"] * 1024 * 1024)
    return {"simulated_memory_mb": chaos_state["memory_leak_mb"]}

@app.post("/chaos/toggle-health")
def toggle_health(healthy: bool = False):
    chaos_state["is_healthy"] = healthy
    return {"is_healthy": chaos_state["is_healthy"]}

@app.post("/chaos/reset")
def reset_chaos():
    chaos_state["error_mode"] = False
    chaos_state["latency_seconds"] = 0.0
    chaos_state["memory_leak_mb"] = 50.0
    chaos_state["is_healthy"] = True
    MEMORY_LEAK_BYTES.set(50.0 * 1024 * 1024)
    return {"message": "Chaos state reset to normal"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
