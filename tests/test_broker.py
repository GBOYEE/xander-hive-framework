import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from unittest.mock import MagicMock, patch
from xander.broker import HiveBroker

def test_broker_publish_and_subscribe():
    with patch("xander.broker.redis.from_url") as mock_redis_cls:
        mock_redis = MagicMock()
        mock_redis_cls.return_value = mock_redis
        broker = HiveBroker("redis://localhost:6379")
        broker.connect()

        # Register a handler for a channel
        handler = MagicMock()
        broker.subscribe("test", handler)

        # Simulate a message arriving in the subscriber thread
        # We'll directly invoke the handler via the broker's internal dispatch
        # Since _dispatch_loop runs in its own thread, we manually trigger
        msg = {"type": "message", "channel": "test", "data": json.dumps({"hello": "world"})}
        broker._handlers["test"](json.loads(msg["data"]))
        handler.assert_called_once_with({"hello": "world"})

        broker.stop()

def test_broker_send_task():
    with patch("xander.broker.redis.from_url") as mock_redis_cls:
        mock_redis = MagicMock()
        mock_redis_cls.return_value = mock_redis
        broker = HiveBroker()
        broker.connect()
        broker.send_task("agent42", {"task_id": "123", "action": "scan"})
        # Should publish to agent:42:inbox
        mock_redis.publish.assert_called_with("agent:agent42:inbox", MagicMock())
        broker.stop()
