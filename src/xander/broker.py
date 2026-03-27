import redis
import json
import threading
import time
from typing import Callable, Dict, Any, Optional
from .schemas import validate_message, Heartbeat, Message

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
        self._reconnect_delay = 1  # seconds, exponential backoff
        self._max_reconnect_delay = 60

    def connect(self):
        self.redis = redis.from_url(self.redis_url, decode_responses=True)
        self.pubsub = self.redis.pubsub()

    def start(self):
        self.connect()
        self._running = True
        # Start dispatch thread
        t = threading.Thread(target=self._dispatch_loop, daemon=True)
        t.start()
        self._threads.append(t)
        # Start heartbeat emitter (for brokers that also act as agents; optional)

    def stop(self):
        self._running = False
        for t in self._threads:
            t.join(timeout=1)
        if self.pubsub:
            self.pubsub.close()
        if self.redis:
            self.redis.close()

    def _dispatch_loop(self):
        """Listen to all subscribed channels, validate messages, and dispatch."""
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
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error on {channel}: {e}")
                        except Exception as e:
                            print(f"Handler error on {channel}: {e}")
                # Reset backoff on successful read
                self._reconnect_delay = 1
            except redis.ConnectionError:
                print(f"Redis connection lost. Reconnecting in {self._reconnect_delay}s...")
                time.sleep(self._reconnect_delay)
                try:
                    self.connect()
                    # Resubscribe to all channels
                    for ch in self._handlers:
                        self.pubsub.subscribe(ch)
                    self._reconnect_delay = 1
                except Exception as e:
                    print(f"Reconnection failed: {e}")
                    self._reconnect_delay = min(self._reconnect_delay * 2, self._max_reconnect_delay)

    def publish(self, channel: str, message: Dict[str, Any]):
        """Publish a validated message dict (will be validated on receive)."""
        if not self.redis:
            self.connect()
        try:
            # Ensure message has version and timestamp? Sender should set.
            self.redis.publish(channel, json.dumps(message))
        except redis.ConnectionError:
            # Could buffer for later; for now just print
            print(f"Publish failed (disconnected): {channel}")

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
