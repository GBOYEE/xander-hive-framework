#!/usr/bin/env python3
"""
XANDER Coordinator (main agent)

- Receives user intents (via OpenClaw)
- Creates task folders in memory/tasks/
- Spawns specialist subagents as needed
- Monitors progress and assembles final responses
- Maintains global state (todo, heartbeat)
"""

import json
import logging
from pathlib import Path
from datetime import datetime
import uuid

WORKSPACE = Path(__file__).parents[2]  # agents/main/ -> workspace root
MEMORY_ROOT = WORKSPACE / "memory"
TASKS_DIR = MEMORY_ROOT / "tasks"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def create_task_brief(user_request: str) -> dict:
    task_id = str(uuid.uuid4())[:8]
    task_dir = TASKS_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    brief = {
        "id": task_id,
        "request": user_request,
        "created": datetime.utcnow().isoformat(),
        "status": "pending",
        "assignments": []
    }
    (task_dir / "brief.json").write_text(json.dumps(brief, indent=2))
    logging.info(f"Created task {task_id}: {user_request[:50]}...")
    return brief

def assign_agents(brief: dict, needed_agents: list):
    assignments = []
    for agent in needed_agents:
        assignment = {
            "agent": agent,
            "subtask": f"Handle portion of {brief['id']}",
            "status": "assigned",
            "assigned_at": datetime.utcnow().isoformat()
        }
        assignments.append(assignment)
    brief["assignments"] = assignments
    task_dir = TASKS_DIR / brief["id"]
    (task_dir / "assignments.json").write_text(json.dumps(assignments, indent=2))
    logging.info(f"Assigned {len(assignments)} agents to task {brief['id']}")

def synthesize_results(brief: dict) -> str:
    task_dir = TASKS_DIR / brief["id"]
    partials_dir = task_dir / "partials"
    if partials_dir.exists():
        partials = list(partials_dir.glob("*"))
    else:
        partials = []
    parts = []
    for p in partials:
        parts.append(p.read_text())
    final = "\n\n---\n\n".join(parts) if parts else "No partial results yet."
    final_dir = task_dir / "final"
    final_dir.mkdir(exist_ok=True)
    (final_dir / "response.md").write_text(final)
    brief["status"] = "completed"
    brief["completed"] = datetime.utcnow().isoformat()
    (task_dir / "brief.json").write_text(json.dumps(brief, indent=2))
    return final

def handle_user_message(message: str) -> str:
    logging.info(f"Coordinator received: {message[:50]}...")
    # Simple routing: always use prof + hunter for demo
    needed_agents = ["prof", "hunter"]
    brief = create_task_brief(message)
    assign_agents(brief, needed_agents)
    # In a real system we'd wait; here we simulate immediate completion after agents write partials
    # For scaffold, we just create placeholder partials to demonstrate flow
    partials_dir = TASKS_DIR / brief["id"] / "partials"
    partials_dir.mkdir(exist_ok=True)
    (partials_dir / "prof_output.txt").write_text("Prof: Here is the educational content you requested.")
    (partials_dir / "hunter_output.txt").write_text("Hunter: Bounty scan complete; see summary.")
    result = synthesize_results(brief)
    logging.info(f"Task {brief['id']} finished.")
    return result

if __name__ == "__main__":
    # Simulate a sample request
    sample = "Generate a lesson plan on plate tectonics and scan for recent bounty opportunities."
    print(handle_user_message(sample))
