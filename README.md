# Xander Hive Framework

> Orchestration engine for autonomous multi‑agent systems — persistent sessions, shared vector memory, and a Redis event bus.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/GBOYEE/xander-hive-framework/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
[![Docker Compose](https://img.shields.io/badge/docker-compose-ready-blue.svg)](docker-compose.yml)

## Problem

Single‑agent systems don’t scale. Multi‑agent systems are hard to coordinate: agents lose context between runs, there’s no shared memory, and you end up reinventing messaging plumbing.

## Solution

Hive Framework gives you:

- **Persistent sessions** — agents keep conversation history across restarts
- **Shared vector memory** — semantic recall across all agents (RAG‑ready)
- **Redis‑backed pub/sub bus** — reliable, real‑time command and event routing
- **Self‑repair** — auto‑restart crashed agents and health monitoring
- **Extensible** — drop in any agent (LLM‑based, rule‑based, custom)

Built for the HiveSec suite but generic enough for research, automation, trading bots, and more.

## Features

- `HiveBroker` — publish/subscribe and direct inbox queues
- `AgentSession` — long‑lived agent identity, state persistence, result reporting
- Vector memory integration (Chroma/FAISS) via `memory/`
- CLI utilities: `xander.client` to send tasks, `xander.broker` standalone
- Example agents included (`agents/hunter`, `agents/prof`, etc.)

## Quickstart

```bash
# 1. Clone and install
git clone https://github.com/GBOYEE/xander-hive-framework.git
cd xander-hive-framework
pip install -r requirements.txt

# 2. Start Redis broker (Docker)
docker run -p 6379:6379 redis:7-alpine

# 3. Launch a sample agent (Hunter)
python -m agents.hunter

# 4. In another terminal, send a task
python -m xander.client --agent hunter --task "Find latest DeFi exploits"

# 5. Check agent logs and shared memory
```

## Architecture

```mermaid
flowchart TD
    A[Client CLI] --> B[Broker (Redis)]
    B --> C[Agent Session 1]
    B --> D[Agent Session 2]
    B --> E[Agent Session N]
    C --> F[Vector Memory]
    D --> F
    E --> F
    C --> G[Local Logger]
    D --> G
    E --> G
```

## Core API

### HiveBroker

```python
from xander import HiveBroker

broker = HiveBroker(redis_url="redis://localhost:6379")
broker.start()

# Publish an event to all agents listening on "hive:events"
broker.publish("hive:events", {"type": "market_volatility", "level": "high"})

# Send a direct command to a specific agent
broker.direct_send("hunter", {"task": "scan", "target": "0x123..."})

# Agent side: fetch next pending command (blocking)
msg = broker.fetch_next("hunter", timeout=5)
```

### AgentSession

```python
from xander import AgentSession, HiveBroker

broker = HiveBroker()
session = AgentSession(
    agent_id="hunter",
    capabilities=["scan:contracts"],
    broker=broker,
    memory_root=Path("memory")
)

def handle_task(task):
    # do work
    return {"found": 3}

session.register(handle_task)
session.start()  # blocks, runs in foreground; spawn thread for inbox
```

## Project Structure

```
xander-hive-framework/
├── xander/                 # Core package
│   ├── __init__.py
│   ├── broker.py           # Redis pub/sub + direct inbox
│   └── session.py          # AgentSession class
├── agents/                 # Example agents
│   ├── hunter/README.md
│   └── hunter/main.py
├── memory/                 # Shared vector store & agent states
├── scripts/                # Utilities (backup, resource_check)
├── skills/                 # Optional OpenClaw skills
├── docs/                   # Detailed architecture (ARCHITECTURE.md)
├── requirements.txt
├── LICENSE
└── README.md
```

## Testing

```bash
pytest -q
```

CI installs deps, lints with ruff, and runs tests on every push.

## Production Notes

- Use a managed Redis (Encrypted in transit, AUTH)
- Set `REDIS_URL` env var for remote
- Enable TLS and use strong AUTH
- Agents should store state to `memory/<agent_id>/` regularly
- Consider Docker Compose to spin up broker + multiple agents

## Roadmap

- [ ] Role‑based access control for commands
- [ ] Rate limiting per agent
- [ ] Prometheus metrics endpoint
- [ ] Web dashboard (see HiveSec‑Ecosystem‑Hub)

## License

MIT. See [LICENSE](LICENSE).
