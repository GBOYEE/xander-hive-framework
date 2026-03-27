#!/usr/bin/env python3
"""Prof agent — technical writing and documentation."""
import logging
from pathlib import Path
from xander import AgentSession, HiveBroker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def handle_task(task: dict):
    task_type = task.get("type", "write")
    topic = task.get("topic", "")
    if task_type == "write" and topic:
        # Simulate writing a technical document
        logging.info(f"Prof writing about: {topic}")
        doc = f"# {topic}\n\nThis is a generated document about {topic}.\n\n## Details\n\n..."
        return {"document": doc, "topic": topic}
    else:
        return {"error": "invalid task"}

def main():
    broker = HiveBroker()
    session = AgentSession(
        agent_id="prof",
        capabilities=["write:docs"],
        broker=broker,
        memory_root=Path("./memory")
    )
    session.register(handle_task)
    logging.info("Prof agent starting...")
    session.start()

if __name__ == "__main__":
    main()
