import pytest
from unittest.mock import MagicMock, patch
from xander.broker import HiveBroker
from xander.schemas import AgentAnnouncement

def test_broker_publish_and_subscribe_with_fakeredis():
    import fakeredis
    broker = HiveBroker(redis_url="fakeredis://")
    broker.connect()
    received = []

    def handler(msg):
        received.append(msg)

    broker.subscribe("test_channel", handler)
    ann = AgentAnnouncement(agent_id="test", capabilities=["cap"]).dict()
    broker.publish("test_channel", ann)
    # The dispatch happens in a separate thread; wait briefly
    time.sleep(0.2)
    assert len(received) == 1
    assert isinstance(received[0], AgentAnnouncement)
    assert received[0].agent_id == "test"
    broker.stop()

def test_broker_send_task():
    import fakeredis
    broker = HiveBroker(redis_url="fakeredis://")
    broker.connect()
    # Subscribe to the agent inbox to catch the message
    received = []
    def handler(msg):
        received.append(msg)
    agent_id = "agent42"
    inbox = f"agent:{agent_id}:inbox"
    broker.subscribe(inbox, handler)
    task = {"task_id": "123", "action": "scan"}
    broker.send_task(agent_id, task)
    time.sleep(0.2)
    assert any(isinstance(m, dict) and m.get("task_id") == "123" for m in received)
    broker.stop()

def test_broker_heartbeat():
    import fakeredis
    broker = HiveBroker(redis_url="fakeredis://")
    broker.connect()
    received = []
    def handler(msg):
        received.append(msg)
    broker.subscribe("hive:heartbeats", handler)
    broker.heartbeat("myagent")
    time.sleep(0.2)
    assert any(isinstance(m, dict) and m.get("type") == "heartbeat" and m.get("agent_id") == "myagent" for m in received)
    broker.stop()

import time
