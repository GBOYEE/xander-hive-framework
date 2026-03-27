import pytest
from pathlib import Path
from xander.state import AgentStateDB

def test_state_set_get(tmp_path):
    db = AgentStateDB(tmp_path / "test.db")
    db.set("key1", {"a": 1, "b": 2})
    val = db.get("key1")
    assert val == {"a": 1, "b": 2}
    assert db.get("missing") is None

def test_heartbeat_update_and_get(tmp_path):
    db = AgentStateDB(tmp_path / "hb.db")
    db.update_heartbeat("agent1", {"ip": "1.2.3.4"})
    hb = db.get_heartbeat("agent1")
    assert hb is not None
    assert hb["metadata"]["ip"] == "1.2.3.4"
    assert "last_seen" in hb
