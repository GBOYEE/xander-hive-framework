import pytest
from xander.schemas import AgentAnnouncement, TaskAssignment, TaskResult, Heartbeat, validate_message
from datetime import datetime

def test_agent_announcement_valid():
    data = {
        "version": "1.0",
        "type": "agent_online",
        "timestamp": datetime.utcnow().isoformat(),
        "agent_id": "hunter",
        "capabilities": ["scan:targets"]
    }
    msg = validate_message(data)
    assert isinstance(msg, AgentAnnouncement)
    assert msg.agent_id == "hunter"

def test_task_assignment_valid():
    data = {
        "version": "1.0",
        "type": "task",
        "timestamp": datetime.utcnow().isoformat(),
        "task_id": "123",
        "action": "scan",
        "parameters": {"target": "0xabc"}
    }
    msg = validate_message(data)
    assert msg.task_id == "123"
    assert msg.action == "scan"

def test_heartbeat_valid():
    data = {
        "version": "1.0",
        "type": "heartbeat",
        "timestamp": datetime.utcnow().isoformat(),
        "agent_id": "prof"
    }
    msg = validate_message(data)
    assert isinstance(msg, Heartbeat)

def test_invalid_type_falls_back():
    data = {"version": "1.0", "type": "unknown", "timestamp": datetime.utcnow().isoformat()}
    msg = validate_message(data)
    assert msg.type == "unknown"
