from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Dict, Any, List
from datetime import datetime

class Message(BaseModel):
    """Base message with versioning."""
    version: str = Field("1.0", description="Message schema version")
    type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any]

class AgentAnnouncement(Message):
    """Agent announces presence and capabilities."""
    type: str = "agent_online"
    agent_id: str
    capabilities: List[str]

class TaskAssignment(Message):
    """Task assigned to an agent."""
    type: str = "task"
    task_id: str
    action: str
    parameters: Dict[str, Any]

class TaskResult(Message):
    """Result from an agent."""
    type: str = "result"
    task_id: str
    status: str  # "done" or "error"
    result: Optional[Any] = None
    error: Optional[str] = None

class Heartbeat(Message):
    """Agent heartbeat."""
    type: str = "heartbeat"
    agent_id: str

def validate_message(data: dict) -> Message:
    """Dispatch to appropriate model based on type."""
    msg_type = data.get("type")
    if msg_type == "agent_online":
        return AgentAnnouncement(**data)
    elif msg_type == "task":
        return TaskAssignment(**data)
    elif msg_type == "result":
        return TaskResult(**data)
    elif msg_type == "heartbeat":
        return Heartbeat(**data)
    else:
        return Message(**data)
