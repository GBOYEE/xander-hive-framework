import redis
import json
import threading
import time
from typing import Callable, Dict, Any

class HiveBroker:
    """
    Redis-backed message broker for agent coordination.
    Provides pub/sub for events and per-agent inbox channels for commands.
    """
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.pubsub = None
        self._running = False
        self._threads = []
        self._handlers = {}  # channel -> handler

    def connect(self):
        self.redis = redis.from_url(self.redis_url, decode_responses=True)
        self.pubsub = self.redis.pubsub()

    def start(self):
        self.connect()
        self._running = True
        # Start a background thread to distribute pub/sub messages to handlers
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
        """Listen to all subscribed channels and call the appropriate handler."""
        while self._running:
            try:
                for msg in self.pubsub.listen():
                    if not self._running:
                        break
                    if msg["type"] == "message":
                        channel = msg["channel"]
                        try:
                            data = json.loads(msg["data"])
                            handler = self._handlers.get(channel)
                            if handler:
                                handler(data)
                        except Exception as e:
                            print(f"Broker handler error on {channel}: {e}")
            except redis.ConnectionError:
                # Attempt reconnection
                time.sleep(2)
                try:
                    self.connect()
                    # Resubscribe to all channels
                    for ch in self._handlers:
                        self.pubsub.subscribe(ch)
                except Exception as e:
                    print(f"Reconnection failed: {e}")

    def publish(self, channel: str, message: Dict[str, Any]):
        """Send a message to a channel (push model)."""
        if not self.redis:
            self.connect()
        self.redis.publish(channel, json.dumps(message))

    def send_task(self, agent_id: str, task: Dict[str, Any]):
        """Send a command/task to a specific agent via its inbox pub/sub channel."""
        channel = f"agent:{agent_id}:inbox"
        self.publish(channel, task)

    def subscribe(self, channel: str, handler: Callable[[Dict[str, Any]], None]):
        """Subscribe to a channel for push notifications."""
        if not self.pubsub:
            self.connect()
        self._handlers[channel] = handler
        self.pubsub.subscribe(channel)

    def unsubscribe(self, channel: str):
        if channel in self._handlers:
            del self._handlers[channel]
        if self.pubsub:
            self.pubsub.unsubscribe(channel)
