# XANDER Hive Framework

**Coordinator:** Gboyee (XANDER 3.0)  
**Status:** Ongoing — active development  
**License:** MIT  

---

## Overview

XANDER is a multi‑agent orchestration framework built from scratch to enable autonomous, collaborative AI systems. It coordinates specialist subagents (Hunter, Prof, Degen‑Trader, Developer, Marketer) that operate in persistent sessions, share vector memory, and execute tasks via a central broker. The hive mind pattern allows for continuous evolution, self‑monitoring, and cross‑agent learning.

---

## Purpose & Vision

- **Automate complex workflows** across Web3 monitoring, educational content creation, and AI‑augmented development.
- **Demonstrate coordinated intelligence** — agents plan, execute, verify, and improve without human micro‑management.
- **Serve as a testbed** for RLHF‑like concepts: human‑in‑the‑loop feedback, iterative refinement, and skill evolution.
- **Scale problem‑solving** by decomposing tasks and recombining results.

---

## Core Architecture

```mermaid
graph TB
  GW[Gateway<br/>OpenClaw] --> Main[main agent<br/>(coordinator)]
  Main -->|spawns| Sub[Specialist subagents]
  Sub -->|shared memory| VM[Vector Memory<br/>(Ollama nomic‑embed‑text)]
  Sub -->|state files| State[State JSON<br/>(per agent)]
  GW -->|bindings| Discord[Discord channels]
  GW -->|bindings| Telegram[Telegram chats]
  
  subgraph Specialists
    Prof[prof<br/>TPT/Education]
    Hunter[hunter<br/>Bounties & DeFi]
    Degen[degen‑trader<br/>Solana memecoin]
    Dev[developer<br/>(future)]
    Mkt[marketer<br/>(future)]
  end
  
  Main -.->|orchestration| Specialists
  Sub -.->|can spawn further| SubSub[sub‑subagents]
```

### Components

- **Gateway** – central message router (OpenClaw) binding Telegram/Discord to agents.
- **Coordinator (main)** – receives user intents, spawns specialists, aggregates results, maintains global todo and heartbeat.
- **Specialist Agents** – each owns a domain, runs in persistent `session` mode, writes daily notes and state files.
- **Vector Memory** – shared semantic store (`memory/`) allowing cross‑agent recall.
- **Watchdog & Heartbeat** – resource checks and error monitoring every 30 min.
- **Task Broker Pattern** – tasks are placed in `memory/tasks/<task_id>/` with assignments; agents pick up pieces and write partials.

---

## Current Agents

| Agent | Domain | Status | Channel Binding |
|-------|--------|--------|-----------------|
| `prof` | TPT content (lesson plans, images, vocab) | ✅ Running (persistent) | Discord `#prof` |
| `hunter` | Web3 bounty scanning & airdrop eligibility | ✅ Running (persistent) | Discord `#hunter` |
| `degen-trader` | Autonomous Solana memecoin trading | ✅ Running (persistent) | Discord `#degen-trader` |
| `developer` | Code review, CI/CD, architecture | 🛠️ Scaffold | Not bound |
| `marketer` | Growth campaigns, analytics | 🛠️ Scaffold | Not bound |

---

## Process Example: AI Training Data Curation

1. User requests: “Generate 50 high‑quality prompt‑completion pairs for RLHF training.”
2. Coordinator spawns `developer` to draft a data schema and `prof` to design pedagogical prompts.
3. `developer` writes a Python script to format outputs; `prof` reviews for clarity.
4. Results assembled in `memory/tasks/xyz/final/` and delivered to user.
5. All steps logged; improvements noted for future self‑evolution.

---

## Why This Matters for AI Training Roles

- **Coordination skill** – RLHF projects often involve multiple annotators, pipelines, and versioning. Experience designing a task broker shows you can structure complex human‑in‑the‑loop workflows.
- **Evaluation mindset** – Agents emit logs and metrics; you can monitor quality, detect errors, and adjust parameters — directly analogous to model evaluation.
- **Iterative improvement** – The framework supports “capability‑evolver” style self‑reflection; you understand how to close the feedback loop.
- **Full‑stack ownership** – From infrastructure (gateway, secrets) to agent logic to memory management, you’ve built and maintained a production‑grade system.

---

## Tech Stack

- **Platform:** OpenClaw (gateway, sessions, bindings)
- **Languages:** Python 3.12+, Shell
- **Data:** JSONL logs, vector memory (Ollama nomic‑embed‑text)
- **Cloud/Infra:** Linux (Ubuntu), systemd, cron, Docker (optional)
- **APIs:** OpenRouter, Etherscan, Alchemy, Dune (as needed by agents)
- **Tools:** Git, VS Code, resource monitoring, heartbeat state

---

## Repository Structure

```
xander-hive-framework/
├── README.md                 # This file
├── ARCHITECTURE.md           # Deep dive
├── CV_BLURB.md              # Short professional blurb
├── agents/                   # Per‑agent directories
│   ├── main/
│   ├── prof/
│   ├── hunter/
│   ├── degen-trader/
│   ├── developer/
│   └── marketer/
├── memory/                   # Shared vector memory
│   ├── tasks/
│   ├── 2026-03-*.md
│   ├── todo.json
│   └── heartbeat-state.json
├── scripts/                  # Utilities
│   ├── resource_check.py
│   ├── resource_monitor.py
│   └── backup_to_github.sh
├── openclaw.json             # Central configuration
├── skills/                   # Custom skills (if any)
└── docs/                     # Detailed design docs
```

---

## Getting Started (for collaborators)

> Note: This is a personal/private workspace; external contributions are currently closed.

If you’re evaluating my work for a contract:

1. Explore the agent directories to see SOUL.md, IDENTITY.md, and recent daily notes.
2. Check `memory/todo.json` for active tasks and priorities.
3. Review `openclaw.json` to understand bindings and security posture.
4. Run `openclaw status` to see live sessions (if you have access).

---

## Metrics & Maturity

- **Agents:** 6 defined (3 active, 2 scaffolded, 1 placeholder)
- **Daily notes:** Since 2026‑03‑11
- **Task completion:** 12/12 dashboard milestones done; multiple delegated tasks in flight.
- **Resource guardrails:** Automated CPU/RAM checks and alerting.
- **Security:** In progress (see `openclaw status` audit; fixing groupPolicy and sandbox).

---

## Ongoing Work

- Integrate top ClawHub skills (tavily‑web‑search, github, memory‑hygiene, security stack)
- Enable persistent marketer agent and bind Discord channel
- Implement backup pipeline to remote GitHub repository
- Add email notifications via SMTP relay
- Continuous improvement: agents propose parameter changes weekly

---

## Contact

For professional inquiries: **xanderaicorp@gmail.com**  
GitHub: github.com/GBOYEE (repos: `bounty-hunter`, `xander-hive-framework`)  
LinkedIn: [your profile]

---

*Built with relentless curiosity and a service‑first mindset. We don’t chase the state‑of‑the‑art; we engineer what works.*
