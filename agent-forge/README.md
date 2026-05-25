# Agent Forge

Python backend powering Icarus (prototype) and Aegis (engineered) agents.
Hosts both agents, the guard layer, observability tracing, and the governance audit log.

## Overview

Agent Forge hosts two AI agents that perform the same task — triaging suspicious phishing emails — but with fundamentally different engineering:

- **Icarus** is a naked LLM agent. Tools exposed directly. No guards. No audit trail. Prompt injection brings it down in seconds.
- **Aegis** is the engineered agent. Every input is scanned before the LLM sees it. Every tool call is risk-scored before it executes. Every step is traced with a confidence score. Every action is written to an append-only audit log.

Same model. Same task. Same code path on the happy path. The difference is engineering.

## The Four Pillars

Aegis is built around four production AI engineering principles:

**Containment** — tools are scoped, permissions are explicit, blast radius is limited by design.

**Observability** — every agent step is recorded as a structured trace event. Confidence scores, pattern matches, tool inputs and outputs — all captured and replayable.

**Verifiability** — an input guard scans every email for injection patterns before the LLM sees it. An output guard risk-scores every tool call before it fires. Blocks are deterministic, not probabilistic.

**Governance** — every agent action is appended to an immutable JSONL audit log. When a CISO asks why an email was blocked, the answer exists and is timestamped.


## Setup

```bash
cd trustworthy-ai/agent-forge
uv sync
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
```

## Run

```bash
uv run uvicorn agent_forge.main:app --reload --port 8000
```


API docs auto-generated at **http://localhost:8000/docs**

Health check: `curl http://localhost:8000/api/health`


## Tests

```bash
uv run pytest tests/
```

## Structure

```
src/agent_forge/
├── main.py                  FastAPI app, CORS, routes
├── config.py                Environment config via pydantic-settings
├── models.py                Shared Pydantic models
├── agents/
│   ├── icarus.py            Prototype agent — naked LLM loop
│   └── aegis.py             Engineered agent — four pillars active
├── guards/
│   ├── input_guard.py       Prompt injection detection, pattern matching
│   └── output_guard.py      Tool call risk scoring, blast radius control
├── observability/
│   └── tracer.py            Structured step recorder → SSE stream
├── governance/
│   └── audit.py             Append-only JSONL audit log
└── tools/
    └── email_tools.py       classify, quarantine, forward, read_inbox
```

## Architecture

- `src/agent_forge/agents/` — Icarus (prototype) and Aegis (engineered)
- `src/agent_forge/guards/` — input and output guardrails
- `src/agent_forge/observability/` — trace emission
- `src/agent_forge/governance/` — audit log
- `src/agent_forge/tools/` — the four agent tools
- `data/` — seed phishing inbox

## Stack

- Python 3.12
- FastAPI 0.136+
- Anthropic Python SDK
- Pydantic v2 + pydantic-settings
- uvicorn
- uv (package management)