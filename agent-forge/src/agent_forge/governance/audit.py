"""
Append-only audit log.

Every agent action — tool calls, blocks, verdicts — is written here
as a JSONL entry. The log is read by GET /api/audit and displayed
in the Watchtower audit panel.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent_forge.config import AUDIT_LOG_PATH


def _ensure_log_file() -> None:
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not AUDIT_LOG_PATH.exists():
        AUDIT_LOG_PATH.touch()


def log_entry(
    agent_id: str,
    action: str,
    email_id: str,
    detail: str | None = None,
    data: dict[str, Any] | None = None,
) -> None:
    """Append one entry to the audit log."""
    _ensure_log_file()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_id": agent_id,
        "email_id": email_id,
        "action": action,
        "detail": detail,
        "data": data,
    }
    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")