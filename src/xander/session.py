import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from .broker import HiveBroker

class AgentSession:
    """
    Persistent session for an agent. Connects to broker, subscribes to its inbox,
    maintains local state, and reports results.
    """
    def __init__(self, agent_id: str, capabilities: list, broker: HiveBroker, memory_root: Optional[Path] = None):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.broker = broker
        self.memory_root = (memory_root or Path("memory")).expanduser()
        self.memory_root.mkdir(parents=True, exist_ok=True)
        self.state_file = self.memory_root / agent_id / "state.json"
        self._load_state()
        self._running = False
        self._task_handler = None

    def _load_state(self):
        if self.state_file.exists():
            try:
                self.state = json.loads(self.state_file.read_text())
            except Exception:
                self.state = {"last_run": None, "stats": {}}
        else:
            self.state = {"last_run": None, "stats": {}}

    def _save_state(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.state, indent=2))

    def register(self, task_handler: Callable[[Dict[str, Any]], Any]):
        """Set the function that handles incoming tasks."""
        self._task_handler = task_handler
        # Announce presence on the agents channel
        self.broker.publish("hive:agents", {
            "type": "agent_online",
            "agent_id": self.agent_id,
            "capabilities": self.capabilities
        })

    def start(self):
        """Begin listening for tasks on the inbox channel."""
        self._running = True
        inbox_channel = f"agent:{self.agent_id}:inbox"
        self.broker.subscribe(inbox_channel, self._on_message)
        # Keep main thread alive; actual work happens in the broker's dispatch thread
        while self._running:
            time.sleep(1)

    def stop(self):
        self._running = False

    def _on_message(self, message: Dict[str, Any]):
        if not self._task_handler:
            return
        try:
            result = self._task_handler(message)
            # Report result
            self.broker.publish("hive:results", {
                "agent_id": self.agent_id,
                "task_id": message.get("task_id"),
                "result": result,
                "status": "done"
            })
        except Exception as e:
            self.broker.publish("hive:results", {
                "agent_id": self.agent_id,
                "task_id": message.get("task_id"),
                "error": str(e),
                "status": "error"
            })

    def send_result(self, result: Any, task_id: str):
        self.broker.publish("hive:results", {
            "agent_id": self.agent_id,
            "task_id": task_id,
            "result": result,
            "status": "done"
        })
