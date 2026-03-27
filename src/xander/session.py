import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from .broker import HiveBroker, Message
from .state import AgentStateDB

class AgentSession:
    """
    Persistent session for an agent. Connects to broker, subscribes to its inbox,
    maintains state, sends heartbeats, and reports results.
    """
    def __init__(self, agent_id: str, capabilities: list, broker: HiveBroker,
                 memory_root: Optional[Path] = None, heartbeat_interval: int = 30):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.broker = broker
        self.heartbeat_interval = heartbeat_interval
        self.memory_root = (memory_root or Path("memory")).expanduser()
        self.memory_root.mkdir(parents=True, exist_ok=True)
        self.state_db_path = self.memory_root / f"{agent_id}.db"
        self.state = AgentStateDB(self.state_db_path)
        self._running = False
        self._task_handler = None
        self._heartbeat_thread = None
        self._lock = threading.RLock()

    def register(self, task_handler: Callable[[Message], Any]):
        """Set the function that handles incoming tasks."""
        self._task_handler = task_handler
        # Announce presence
        ann = {
            "version": "1.0",
            "type": "agent_online",
            "timestamp": time.time(),
            "agent_id": self.agent_id,
            "capabilities": self.capabilities
        }
        self.broker.publish("hive:agents", ann)

    def start(self):
        """Begin listening for tasks on the inbox channel."""
        self._running = True
        inbox_channel = f"agent:{self.agent_id}:inbox"
        self.broker.subscribe(inbox_channel, self._on_message)
        # Start heartbeat loop
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
        # Keep main thread alive; actual work in callbacks
        while self._running:
            time.sleep(1)

    def stop(self):
        self._running = False
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=1)

    def _heartbeat_loop(self):
        """Periodically send heartbeats."""
        while self._running:
            try:
                hb = {
                    "version": "1.0",
                    "type": "heartbeat",
                    "timestamp": time.time(),
                    "agent_id": self.agent_id
                }
                self.broker.publish("hive:heartbeats", hb)
                self.state.update_heartbeat(self.agent_id)
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                print(f"Heartbeat error: {e}")

    def _on_message(self, message: Message):
        if not self._task_handler:
            return
        try:
            result = self._task_handler(message)
            # Report result
            res_msg = {
                "version": "1.0",
                "type": "result",
                "timestamp": time.time(),
                "task_id": message.payload.get("task_id", "unknown"),
                "status": "done",
                "result": result
            }
            self.broker.publish("hive:results", res_msg)
        except Exception as e:
            err_msg = {
                "version": "1.0",
                "type": "result",
                "timestamp": time.time(),
                "task_id": message.payload.get("task_id", "unknown"),
                "status": "error",
                "error": str(e)
            }
            self.broker.publish("hive:results", err_msg)

    def send_result(self, result: Any, task_id: str):
        res_msg = {
            "version": "1.0",
            "type": "result",
            "timestamp": time.time(),
            "task_id": task_id,
            "status": "done",
            "result": result
        }
        self.broker.publish("hive:results", res_msg)
