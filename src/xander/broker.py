import redis
import json
import threading
import time
import logging
from typing import Callable, Dict, Any, Optional
from .schemas import validate_message, Heartbeat, Message

logger = logging.getLogger("xander.broker")

class HiveBroker:
    """
    Redis-backed message broker with schema validation, reconnection, and heartbeats.
    """
    def __init__(self, redis_url: str = "redis://localhost:6379", heartbeat_interval: int = 30):
        self.redis_url = redis_url
        self.heartbeat_interval = heartbeat_interval
        self.redis = None
        self.pubsub = None
        self._running = False
        self._threads = []
        self._handlers = {}  # channel -> handler
        self._reconnect_delay = 1
        self._max_reconnect_delay = 60
        self.metrics = {
            "messages_published": 0,
            "messages_delivered": 0,
            "dispatch_errors": 0,
        }

    def connect(self):
        self.redis = redis.from_url(self.redis_url, decode_responses=True)
        self.pubsub = self.redis.pubsub()

    def start(self):
        self.connect()
        self._running = True
        t = threading.Thread(target=self._dispatch_loop, daemon=True)
        t.start()
        self._threads.append(t)

    def stop(self):
        self._running = False
        for t in self._threads:
            t.join(timeout=1)
        if self.pubsub:
            self.pubsub.close()
        if self.redis:
            self.redis.close()

    def _dispatch_loop(self):
        while self._running:
            try:
                for msg in self.pubsub.listen():
                    if not self._running:
                        break
                    if msg["type"] == "message":
                        channel = msg["channel"]
                        try:
                            data = json.loads(msg["data"])
                            validated = validate_message(data)
                            handler = self._handlers.get(channel)
                            if handler:
                                handler(validated)
                                self.metrics["messages_delivered"] += 1
                        except json.JSONDecodeError as e:
                            logger.error("JSON decode error on %s: %s", channel, e)
                            self.metrics["dispatch_errors"] += 1
                        except Exception as e:
                            logger.error("Handler error on %s: %s", channel, e, exc_info=True)
                            self.metrics["dispatch_errors"] += 1
                self._reconnect_delay = 1
            except redis.ConnectionError:
                logger.warning("Redis connection lost. Reconnecting in %ds...", self._reconnect_delay)
                time.sleep(self._reconnect_delay)
                try:
                    self.connect()
                    for ch in self._handlers:
                        self.pubsub.subscribe(ch)
                    self._reconnect_delay = 1
                except Exception as e:
                    logger.error("Reconnection failed: %s", e)
                    self._reconnect_delay = min(self._reconnect_delay * 2, self._max_reconnect_delay)

    def publish(self, channel: str, message: Dict[str, Any]):
        """Publish a validated message dict."""
        if not self.redis:
            self.connect()
        try:
            self.redis.publish(channel, json.dumps(message))
            self.metrics["messages_published"] += 1
        except redis.ConnectionError as e:
            logger.error("Publish failed (disconnected): %s", e)

    def send_task(self, agent_id: str, task: Dict[str, Any]):
        """Send a task to an agent's inbox."""
        channel = f"agent:{agent_id}:inbox"
        self.publish(channel, task)

    def subscribe(self, channel: str, handler: Callable[[Message], None]):
        """Subscribe to a channel; handler receives validated Message."""
        if not self.pubsub:
            self.connect()
        self._handlers[channel] = handler
        self.pubsub.subscribe(channel)

    def unsubscribe(self, channel: str):
        if channel in self._handlers:
            del self._handlers[channel]
        if self.pubsub:
            self.pubsub.unsubscribe(channel)

    def heartbeat(self, agent_id: str):
        """Send a heartbeat for this agent (if broker also acts as agent)."""
        hb = Heartbeat(agent_id=agent_id).dict()
        self.publish("hive:heartbeats", hb)
