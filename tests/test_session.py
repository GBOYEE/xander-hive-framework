import time
import pytest
from pathlib import Path
from unittest.mock import MagicMock
from xander.session import AgentSession
from xander.broker import HiveBroker
from xander.schemas import TaskAssignment

def test_agent_session_lifecycle(tmp_path):
    # Use fakeredis to avoid real Redis
    import fakeredis
    broker = HiveBroker(redis_url="fakeredis://")
    broker.connect()
    session = AgentSession(
        agent_id="test-agent",
        capabilities=["do:thing"],
        broker=broker,
        memory_root=tmp_path / "memory"
    )
    def handler(msg):
        return {"handled": True}
    session.register(handler)
    session.start()
    # Let it run a moment, then stop
    time.sleep(0.3)
    session.stop()
    assert not session._running

def test_session_publishes_results():
    import fakeredis
    broker = HiveBroker(redis_url="fakeredis://")
    broker.connect()
    results = []
    def result_handler(msg):
        results.append(msg)
    broker.subscribe("hive:results", result_handler)

    session = AgentSession("agent", [], broker)
    def handler(msg):
        session.send_result({"out": "ok"}, msg.payload.get("task_id", "tid"))
    session.register(handler)
    # Simulate a task message
    task_msg = TaskAssignment(
        version="1.0",
        timestamp=time.time(),
        task_id="123",
        action="test",
        parameters={}
    )
    session._on_message(task_msg)
    time.sleep(0.2)
    assert any(r.get("task_id") == "123" and r.get("status") == "done" for r in results)
    broker.stop()

def test_state_persistence(tmp_path):
    import fakeredis
    broker = HiveBroker(redis_url="fakeredis://")
    broker.connect()
    mem = tmp_path / "memory"
    session1 = AgentSession("persistent-agent", [], broker, memory_root=mem)
    session1.state.set("last_run", "2025-01-01T00:00:00")
    session1.state.update_heartbeat("persistent-agent")
    session1.stop()
    # New session
    session2 = AgentSession("persistent-agent", [], broker, memory_root=mem)
    assert session2.state.get("last_run") == "2025-01-01T00:00:00"
    hb = session2.state.get_heartbeat("persistent-agent")
    assert hb is not None
    broker.stop()
