import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

class AgentStateDB:
    """SQLite-backed state store for an agent."""
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS kv_store (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS heartbeats (
                    agent_id TEXT PRIMARY KEY,
                    last_seen TIMESTAMP,
                    metadata TEXT
                )
            """)
            conn.commit()

    def set(self, key: str, value: Any):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO kv_store (key, value, updated) VALUES (?, ?, ?)",
                (key, json.dumps(value), datetime.utcnow().isoformat())
            )
            conn.commit()

    def get(self, key: str, default=None) -> Any:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT value FROM kv_store WHERE key=?", (key,))
            row = cur.fetchone()
            if row:
                return json.loads(row[0])
            return default

    def update_heartbeat(self, agent_id: str, metadata: Optional[Dict] = None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO heartbeats (agent_id, last_seen, metadata) VALUES (?, ?, ?)",
                (agent_id, datetime.utcnow().isoformat(), json.dumps(metadata or {}))
            )
            conn.commit()

    def get_heartbeat(self, agent_id: str) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT last_seen, metadata FROM heartbeats WHERE agent_id=?", (agent_id,))
            row = cur.fetchone()
            if row:
                return {"last_seen": row[0], "metadata": json.loads(row[1])}
            return None
