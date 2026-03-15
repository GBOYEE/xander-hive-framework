# XANDER Hive Framework — Architecture Deep Dive

## 1. Design Philosophy

The hive is built around **three principles**:

1. **Autonomy** – Each agent runs in its own persistent session, makes decisions within its domain, and writes state to disk. No agent blocks another.
2. **Shared Memory** – A vector store (`memory/`) allows agents to recall past tasks, lessons learned, and context across sessions. This mimics a collective memory.
3. **Iterative Refinement** – The coordinator can re‑spawn agents with updated parameters; agents themselves can propose changes (self‑evolution).

These map directly to RLHF concepts:
- **Reinforcement** – Agents receive feedback via task outcomes (success/failure logs) and adjust heuristics.
- **Learning from Human Feedback** – Human approvals (`/approve`) and corrections are stored in memory and influence future behavior.
- **Alignment** – The `agentguard` and `prompt‑guard` skills (to be installed) enforce policy compliance during execution.

---

## 2. Task Broker Pattern

### Flow

1. User request → `main` coordinator.
2. Coordinator creates a task folder: `memory/tasks/<uuid>/`
   - `brief.json` – original request, priority, constraints
   - `assignments.json` – maps agent IDs to subtasks
   - `partials/` – agents drop intermediate results
   - `final/` – coordinator assembles final response
3. Agents are notified via `sessions_send` or by placing a `todo` file in their inbox.
4. Each agent picks its slice, works autonomously, writes a partial result and a `status` file.
5. Coordinator monitors; when all assignments are done, it synthesizes and returns to user.
6. After delivery, agents write a `notes.md` with lessons learned.

This pattern enables **parallelism** and **fault isolation** — if one agent fails, others can continue or the coordinator can reassign.

---

## 3. Memory & State

- **Vector Memory** – powered by Ollama `nomic‑embed‑text`. Agents store daily notes (`memory/YYYY‑MM‑DD.md`) and key facts; semantic search (`memory_search`) surfaces relevant context across agents.
- **Agent State** – Each agent has a `state.json` in its workspace (e.g., `agents/hunter/state.json`) storing counters, last run timestamps, configuration overrides.
- **Heartbeat State** – `memory/heartbeat‑state.json` tracks last check timestamps; used for watchdog alerts.

---

## 4. Self‑Evolution Loop

Agents can propose improvements:

- Every 24 hours (or after N tasks), an agent writes a `proposal.md` in its own memory folder, suggesting parameter tweaks, new skills to install, or process changes.
- The `main` coordinator reviews proposals; approved ones are applied (e.g., updating `openclaw.json`, installing a ClawHub skill, or modifying a script).
- This mirrors the **capability‑evolver** skill from ClawHub but is custom‑built for our hive.

---

## 5. Security Model

Current security posture (see `openclaw status` audit):

- **Gateway** runs on loopback only (no external exposure).
- **Tool sandboxing** – Agents default to `sandbox=inherit` (not fully isolated); we plan to tighten with `sandbox.mode="all"` and `tools.fs.workspaceOnly=true`.
- **Prompt injection defense** – Will install `prompt‑guard` and `agentguard` skills.
- **Credential management** – Secrets stored via `openclaw secrets set`; never in plaintext.

---

## 6. Integration Points for AI Training

The hive’s coordination and evaluation infrastructure is directly reusable for RLHF pipelines:

- **Task decomposition** – Breaking a large annotation job into subtasks for different annotators (agents).
- **Quality monitoring** – Heartbeat and error watchdog provide real‑time metrics on annotator performance.
- **Feedback loops** – Agents can be assigned to review each other’s outputs (e.g., `prof` reviews `hunter`’s bounty reports for clarity).
- **Versioning** – All task artifacts are persisted; easy to roll back or audit.

If hired for an AI training role, I could adapt this framework to manage a team of human annotators or automated evaluation pipelines.

---

## 7. Future Roadmap

- Install ClawHub skills: `tavily‑web‑search`, `github`, `memory‑hygiene`, `agentguard`, `prompt‑guard`, `capability‑evolver`.
- Create `developer` and `marketer` persistent agents with Discord bindings.
- Implement `backup_to_github.sh` for off‑site storage.
- Add SMTP relay for email notifications.
- Publish weekly self‑reflection summaries to `memory/` for transparency.

---

*This architecture is a living document; changes tracked in git history.*
