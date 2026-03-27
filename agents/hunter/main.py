#!/usr/bin/env python3
"""Hunter agent — scans for data from APIs and feeds."""
import logging
from pathlib import Path
from xander import AgentSession, HiveBroker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def handle_task(message):
    """
    Expected message payload:
    {
        "task_id": "...",
        "action": "scan",
        "target": "something"
    }
    """
    payload = message.payload
    action = payload.get("action")
    target = payload.get("target")
    if action == "scan" and target:
        logging.info(f"Hunter scanning target: {target}")
        return {"found": 3, "target": target, "sample": "0x123...abc"}
    else:
        logging.warning(f"Unknown task: {payload}")
        return {"error": "unknown action"}

def main():
    broker = HiveBroker()
    session = AgentSession(
        agent_id="hunter",
        capabilities=["scan:targets"],
        broker=broker,
        memory_root=Path("./memory")
    )
    session.register(handle_task)
    logging.info("Hunter agent starting...")
    session.start()

if __name__ == "__main__":
    main()
