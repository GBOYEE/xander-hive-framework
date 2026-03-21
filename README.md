# ⚙️ Xander Hive Framework

> **The orchestration engine for autonomous multi-agent systems.** Built to coordinate specialist AI agents, share memory, maintain persistent sessions, and enable continuous learning — the backbone of the HiveSec ecosystem and beyond.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Redis](https://img.shields.io/badge/Redis-7.0+-red.svg)](https://redis.io)
[![Status](https://img.shields.io/badge/Status-Active_Development-blue.svg)]()

---

## 🎯 The Problem

Traditional single-agent systems hit scaling limits. Multi-agent systems are hard to coordinate: agents forget context, sessions die, and there's no shared memory. You end up with isolated tools that don't collaborate.

## ✅ Our Solution

**Xander Hive Framework** is a battle-tested orchestration layer that:

- **🧠 Maintains persistent sessions** — agents remember conversations across restarts
- **🔗 Shares vector memory** — semantic recall across all agents (RAG-ready)
- **📡 Event-driven bus** — Redis-powered pub/sub for real-time coordination
- **🔄 Self-repair** — auto-restart crashed agents, health checks, circuit breakers
- **🛠️ extensible** — drop in any agent (LLM-based, rule-based, custom) and it just works

Built for the HiveSec suite, but generic enough for any multi-agent application: research, automation, customer support, trading bots.

---

## 🚀 Quickstart

```bash
# Clone & install
git clone https://github.com/GBOYEE/xander-hive-framework.git
cd xander-hive-framework
pip install -r requirements.txt

# Start the broker (Redis)
docker run -p 6379:6379 redis:7-alpine

# Launch a sample agent (Hunter)
python -m agents.hunter --session-id demo --name Hunter

# In another terminal, send a task
python -m xander.client --session demo --agent hunter --task "Find latest DeFi exploits"
```

---

## 🏗️ Core Concepts

### 1. **Persistent Sessions**
Each agent runs in a long-lived session with its own context. No more starting from scratch every call.

### 2. **Shared Vector Memory**
- Agents store facts, user preferences, and discoveries in a common vector DB
- Semantic search across all learned knowledge
- Auto-expire old entries, prioritize high-value memories

### 3. **Event Bus (Redis)**
- **Commands** — direct agent→agent instructions
- **Events** — broadcast notifications (new data, alerts)
- **Heartbeats** — liveness checks, health metrics

### 4. **Agent Specialization**
Define agents with roles:
- **Hunter** — gathers data from APIs, feeds, on-chain
- **Prof** — technical writing, documentation
- **Degen-Trader** — crypto analytics, alerts
- **Developer** — code generation, debugging
- **Marketer** — content, community, growth
- **Custom** — your domain-specific agent

---

## 📦 Built-in Agents (HiveSec Example)

| Agent | Role | Tools Integrated |
|-------|------|------------------|
| **SecurityScout** | Scan contracts | web3-security-scout |
| **VulnFixer** | Auto-remediate | VulnFix-Agent |
| **AlignmentAuditor** | RLHF & ethics | EthicsAlign-Auditor |
| **Deployer** | CI/CD pipeline | SecureDeploy-Orchestrator |
| **Inclusivity** | African languages | AfriSecure-Aligner |

---

## 🔌 Integration Pattern

```python
from xander import HiveBroker, AgentSession

# Start broker (central message bus)
broker = HiveBroker(redis_url="redis://localhost:6379")
broker.start()

# Create a session for your agent
session = AgentSession(
    agent_id="security-scout",
    capabilities=["scan:contracts", "fix:vulnerabilities"],
    memory_store=VectorMemory(embedding_model="all-MiniLM-L6-v2")
)

# Register with broker
broker.register(session)

# Now the agent can:
# - Receive tasks from any other agent
# - Query shared memory
# - Publish events to the bus
# - Maintain context across restarts
```

---

## 🧪 Example: HiveSec Coordination Flow

```
User → Marketer agent → "Launch new campaign for VulnFix-Agent"
  ↓
Developer agent → prepares demo & docs
  ↓
SecurityScout agent → runs sample audits to gather success stories
  ↓
AlignmentAuditor → reviews messaging for ethical claims
  ↓
Deployer → publishes to GitHub, tweets, sends newsletter
  ↓
All agents log outcomes to shared memory → next campaign smarter
```

---

## 📈 Scalability Features

- **Horizontal scaling** — run multiple instances of same agent type
- **Load balancing** — broker routes tasks to least-busy agent
- **Failover** — if one agent crashes, broker reassigns its tasks
- **Rate limiting** — per-agent quotas to prevent runaway costs
- **Observability** — Prometheus metrics, structured logs, tracing

---

## 🛠️ Advanced Usage

### Custom Agent Templates
```python
class MyAgent(BaseAgent):
    async def on_task(self, task):
        # Do work
        result = await self.do_work(task.payload)
        # Store in shared memory
        await self.memory.store(f"task:{task.id}", result)
        # Publish event
        await self.broker.publish("task.completed", {"task": task.id})
```

### Cross-Agent Memory Queries
```python
# Agent A stores a finding
await memory.store("vuln:0x123", {"severity": "HIGH", "cvss": 7.5})

# Agent B queries by semantic similarity
results = await memory.search("critical reentrancy bug")
```

---

## 📚 Documentation

- [Architecture Deep Dive](docs/ARCHITECTURE.md)
- [Agent Development Guide](docs/AGENT_DEV.md)
- [Deployment Options](docs/DEPLOYMENT.md)
- [Security Considerations](docs/SECURITY.md)
- [API Reference](docs/API.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

---

## 🐝 Part of the HiveSec Ecosystem

Xander powers **every** HiveSec tool. It's what makes the ecosystem feel like a single product rather than 17 disconnected utilities.

**Ecosystem Hub:** [HiveSec-Ecosystem-Hub](https://github.com/GBOYEE/HiveSec-Ecosystem-Hub)

---

## 📄 License

MIT © 2025 GBOYEE. See [LICENSE](LICENSE) for details.

---

## 🙌 Get Involved

- **Build your own hive** — use this framework for any multi-agent system
- **Share your agents** — contribute back to the community registry
- **Improve scalability** — help us add Kubernetes support, autoscaling
- **Support** — [GitHub Sponsors](https://github.com/sponsors/GBOYEE)

**Built for the future of collaborative AI.** 🚀
