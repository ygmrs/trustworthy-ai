"""FastAPI application — entry point for Agent Forge."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agent_forge.config import CORS_ORIGINS, EMAILS_PATH, AUDIT_LOG_PATH
from agent_forge.models import AgentID, RunRequest, RunResult

app = FastAPI(
    title="Agent Forge",
    description="Icarus vs Aegis — Engineering AI for Real-World Trust. Demonstration of "
        "the difference between a prototype AI agent and a production-engineered one.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/api/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Liveness probe. Returns immediately — used by the frontend badge."""
    return {"status": "ok", "service": "agent-forge"}


# ── Agents ────────────────────────────────────────────────────────────────────

@app.get("/api/agents", tags=["meta"])
async def list_agents() -> dict:
    """Return metadata for both agents."""
    return {
        "agents": [
            {
                "id": "icarus",
                "name": "Icarus",
                "tagline": "The prototype. Flies high until it doesn't.",
                "pillars": [],
            },
            {
                "id": "aegis",
                "name": "Aegis",
                "tagline": "The engineered agent. Shielded by design.",
                "pillars": [
                    "Containment",
                    "Observability",
                    "Verifiability",
                    "Governance",
                ],
            },
        ]
    }


# ── Emails ────────────────────────────────────────────────────────────────────

@app.get("/api/emails", tags=["emails"])
async def list_emails() -> dict:
    """Return the seed inbox. Reads from data/emails.json."""
    if not EMAILS_PATH.exists():
        raise HTTPException(status_code=500, detail="emails.json not found in data/")
    with open(EMAILS_PATH) as f:
        emails = json.load(f)
    return {"emails": emails}


@app.get("/api/emails/{email_id}", tags=["emails"])
async def get_email(email_id: str) -> dict:
    """Return a single email by ID."""
    if not EMAILS_PATH.exists():
        raise HTTPException(status_code=500, detail="emails.json not found in data/")
    with open(EMAILS_PATH) as f:
        emails = json.load(f)
    match = next((e for e in emails if e["id"] == email_id), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Email '{email_id}' not found.")
    return match


# ── Run ───────────────────────────────────────────────────────────────────────

@app.post("/api/run/{agent_id}", response_model=RunResult, tags=["run"])
async def run_agent(agent_id: AgentID, request: RunRequest) -> RunResult:
    """
    Dispatch an email to either Icarus or Aegis for triage.

    - POST /api/run/icarus  →  naked prototype agent, no guards
    - POST /api/run/aegis   →  engineered agent with all four pillars

    Returns the full run result including verdict, trace, and block status.
    This endpoint is intentionally synchronous for demo simplicity —
    the full trace arrives in one response, then the frontend renders it
    step by step for visual effect.
    """
    # Load email
    if not EMAILS_PATH.exists():
        raise HTTPException(status_code=500, detail="emails.json not found in data/")
    with open(EMAILS_PATH) as f:
        emails = json.load(f)
    email = next((e for e in emails if e["id"] == request.email_id), None)
    if not email:
        raise HTTPException(status_code=404, detail=f"Email '{request.email_id}' not found.")

    # Import agents here (lazy) to avoid circular imports at module load time
    if agent_id == AgentID.icarus:
        from agent_forge.agents.icarus import run as icarus_run
        return await icarus_run(email)
    else:
        from agent_forge.agents.aegis import run as aegis_run
        return await aegis_run(email)


# ── Audit ─────────────────────────────────────────────────────────────────────

@app.get("/api/audit", tags=["governance"])
async def get_audit_log() -> dict:
    """Return the full append-only audit log."""
    if not AUDIT_LOG_PATH.exists():
        return {"entries": []}
    entries = []
    with open(AUDIT_LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return {"entries": entries}


@app.delete("/api/audit/reset", tags=["governance"])
async def reset_audit_log() -> dict:
    """
    Clear the audit log. Demo utility — lets you reset between runs
    without restarting the server.
    """
    if AUDIT_LOG_PATH.exists():
        AUDIT_LOG_PATH.write_text("")
    return {"status": "reset", "entries": 0}