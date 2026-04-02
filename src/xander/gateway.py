"""Hive Framework Gateway — FastAPI front door for observability and control."""
import os
import time
import uuid
import logging
import threading
from typing import Dict, List
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from .broker import HiveBroker

logger = logging.getLogger("xander.gateway")

APP_VERSION = "1.0.0"
ENV = os.getenv("XANDER_ENV", "production")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Shared broker
broker = HiveBroker(redis_url=REDIS_URL)

# In-memory agent registry (could be persisted to SQLite later)
 agents: Dict[str, dict] = {}
agents_lock = threading.Lock()

# Metrics
metrics_store = {
    "requests_total": 0,
    "requests_failed": 0,
    "agents_online": 0,
}

def create_app() -> FastAPI:
    app = FastAPI(title="Xander Hive Gateway", version=APP_VERSION)

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        start = time.time()
        metrics_store["requests_total"] += 1
        try:
            resp = await call_next(request)
            elapsed = time.time() - start
            logger.info("request completed", extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": resp.status_code,
                "ms": int(elapsed*1000)
            })
            resp.headers["X-Request-ID"] = request_id
            return resp
        except Exception as exc:
            metrics_store["requests_failed"] += 1
            logger.error("request failed", extra={
                "request_id": request_id,
                "error": str(exc)
            }, exc_info=True)
            raise

    @app.on_event("startup")
    def startup_event():
        # Start broker and subscribe to agent events
        broker.start()
        broker.subscribe("hive:agents", handle_agent_announcement)
        broker.subscribe("hive:heartbeats", handle_heartbeat)
        logger.info("Gateway started, subscribed to hive events")

    @app.on_event("shutdown")
    def shutdown_event():
        broker.stop()
        logger.info("Gateway shutdown")

    def handle_agent_announcement(msg):
        payload = msg.payload
        agent_id = payload.get("agent_id")
        if not agent_id:
            return
        with agents_lock:
            agents[agent_id] = {
                "agent_id": agent_id,
                "capabilities": payload.get("capabilities", []),
                "last_announcement": datetime.utcnow().isoformat(),
                "online": True,
            }
        logger.info("Agent online: %s", agent_id)

    def handle_heartbeat(msg):
        payload = msg.payload
        agent_id = payload.get("agent_id")
        if not agent_id:
            return
        with agents_lock:
            if agent_id in agents:
                agents[agent_id]["last_heartbeat"] = datetime.utcnow().isoformat()
            else:
                agents[agent_id] = {
                    "agent_id": agent_id,
                    "online": True,
                    "last_heartbeat": datetime.utcnow().isoformat(),
                }

    @app.get("/health")
    async def health():
        try:
            broker.redis.ping()
            with agents_lock:
                online_count = sum(1 for a in agents.values() if a.get("online"))
            return {
                "status": "ok",
                "timestamp": time.time(),
                "version": APP_VERSION,
                "environment": ENV,
                "agents_online": online_count,
                "redis": "connected",
            }
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={"status": "error", "detail": str(e)}
            )

    @app.get("/metrics")
    async def metrics():
        with agents_lock:
            online_count = sum(1 for a in agents.values() if a.get("online"))
        metrics_store["agents_online"] = online_count
        return metrics_store

    @app.get("/agents")
    async def list_agents() -> List[dict]:
        with agents_lock:
            return list(agents.values())

    @app.post("/agents/{agent_id}/cmd")
    async def send_command(agent_id: str, cmd: dict):
        broker.send_task(agent_id, cmd)
        broker.metrics["messages_published"] += 1
        metrics_store["requests_total"] += 1  # or separate command counter
        return {"status": "queued", "agent_id": agent_id}

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "src.xander.gateway:app",
        host="0.0.0.0",
        port=int(os.getenv("XANDER_PORT", 8080)),
        reload=ENV == "development",
    )
