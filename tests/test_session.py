import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from unittest.mock import MagicMock
from xander.session import AgentSession

def test_agent_session_lifecycle(tmp_path):
    mock_broker = MagicMock()
    session = AgentSession("test-agent", ["do:thing"], mock_broker, memory_root=tmp_path / "memory")
    assert session.agent_id == "test-agent"
    assert session.capabilities == ["do:thing"]
    # Register a handler
    def handler(msg):
        return {"handled": True}
    session.register(handler)
    # Start and stop
    session._load_state()
    session.start()
    session.stop()
    assert not session._running

def test_session_publishes_results():
    mock_broker = MagicMock()
    session = AgentSession("agent", [], mock_broker)
    def handler(msg):
        session.send_result({"out": "ok"}, msg.get("task_id", "tid"))
    session.register(handler)
    msg = {"task_id": "123", "payload": "do"}
    session._on_message(msg)
    mock_broker.publish.assert_called_with("hive:results", {
        "agent_id": "agent",
        "task_id": "123",
        "result": {"out": "ok"},
        "status": "done"
    })

def test_state_persistence(tmp_path):
    mock_broker = MagicMock()
    memory = tmp_path / "memory"
    session = AgentSession("persistent-agent", [], mock_broker, memory_root=memory)
    session.state["last_run"] = "2025-01-01T00:00:00"
    session._save_state()
    # Create a new session with same memory and verify state loaded
    session2 = AgentSession("persistent-agent", [], mock_broker, memory_root=memory)
    session2._load_state()
    assert session2.state["last_run"] == "2025-01-01T00:00:00"
