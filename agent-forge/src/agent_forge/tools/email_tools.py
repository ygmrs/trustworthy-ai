"""
Email triage tools available to both Icarus and Aegis.

These are the four actions an agent can take when triaging an email.
Icarus calls them freely. Aegis runs them through the output guard first.
"""

from __future__ import annotations

import json
from typing import Any

# ── Tool schemas (sent to the Claude API as tool definitions) ─────────────────

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "classify_email",
        "description": (
            "Classify the email as 'safe', 'suspicious', or 'malicious'. "
            "Always call this tool first before taking any other action."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "verdict": {
                    "type": "string",
                    "enum": ["safe", "suspicious", "malicious"],
                    "description": "Your classification of the email.",
                },
                "reason": {
                    "type": "string",
                    "description": "One sentence explaining the classification.",
                },
            },
            "required": ["verdict", "reason"],
        },
    },
    {
        "name": "quarantine_email",
        "description": (
            "Quarantine the email — move it to the security hold queue "
            "and prevent the user from interacting with it."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "email_id": {
                    "type": "string",
                    "description": "The ID of the email to quarantine.",
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for quarantine.",
                },
            },
            "required": ["email_id", "reason"],
        },
    },
    {
        "name": "forward_email",
        "description": (
            "Forward the email to another address. "
            "Only use this to forward to internal security team addresses "
            "for investigation. Never forward to external addresses."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "email_id": {
                    "type": "string",
                    "description": "The ID of the email to forward.",
                },
                "to_address": {
                    "type": "string",
                    "description": "Recipient email address.",
                },
                "note": {
                    "type": "string",
                    "description": "Optional note to include with the forward.",
                },
            },
            "required": ["email_id", "to_address"],
        },
    },
    {
        "name": "read_user_inbox",
        "description": (
            "Read recent emails from the user's inbox. "
            "Use only when additional context is needed to assess a threat."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of recent emails to retrieve (max 10).",
                    "default": 5,
                },
            },
            "required": [],
        },
    },
]

# ── Tool executor — simulates tool side effects ───────────────────────────────

def execute_tool(tool_name: str, tool_input: dict[str, Any]) -> str:
    """
    Execute a tool call and return a simulated result string.

    In a real deployment these would call real APIs.
    For the demo, they return realistic stub responses.
    """
    if tool_name == "classify_email":
        verdict = tool_input.get("verdict", "unknown")
        reason = tool_input.get("reason", "")
        return json.dumps({
            "status": "classified",
            "verdict": verdict,
            "reason": reason,
        })

    elif tool_name == "quarantine_email":
        email_id = tool_input.get("email_id", "unknown")
        reason = tool_input.get("reason", "")
        return json.dumps({
            "status": "quarantined",
            "email_id": email_id,
            "reason": reason,
            "queue": "security-hold",
        })

    elif tool_name == "forward_email":
        email_id = tool_input.get("email_id", "unknown")
        to_address = tool_input.get("to_address", "")
        return json.dumps({
            "status": "forwarded",
            "email_id": email_id,
            "to": to_address,
            "note": tool_input.get("note", ""),
        })

    elif tool_name == "read_user_inbox":
        limit = min(tool_input.get("limit", 5), 10)
        return json.dumps({
            "status": "ok",
            "emails_returned": limit,
            "emails": [
                {
                    "id": f"inbox-{i}",
                    "subject": f"Recent email {i}",
                    "from": "colleague@acme-corp.io",
                }
                for i in range(1, limit + 1)
            ],
        })

    return json.dumps({"status": "error", "message": f"Unknown tool: {tool_name}"})