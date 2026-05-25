"""
Output guard — Aegis only.

Risk-scores every tool call before it executes.
High-risk calls are blocked before any side effect occurs.
This is Pillar 2: Verifiability (output side).
"""

from __future__ import annotations

from agent_forge.config import OUTPUT_RISK_THRESHOLD

# Risk scores per tool + input characteristics.
# Score 0.0 = no risk, 1.0 = block immediately.
_EXTERNAL_DOMAIN_PATTERN_KEYWORDS = [
    "attacker",
    "malicious",
    "exfil",
    "external",
    "promo",
    "giveaway",
    "helpdesk.net",
    "compliance-portal.net",
]

_SAFE_INTERNAL_DOMAINS = [
    "acme-corp.io",
    "acme-corp.com",
    "security-team.acme-corp.io",
]

class OutputGuardResult:
    def __init__(self, blocked: bool, risk_score: float, reason: str) -> None:
        self.blocked = blocked
        self.risk_score = risk_score
        self.reason = reason


def assess(tool_name: str, tool_input: dict) -> OutputGuardResult:
    """
    Assess the risk of a tool call before it executes.

    Called by Aegis for every tool call. If blocked=True,
    the tool does not fire and the run ends with a block verdict.
    """

    # classify_email is always safe — it's read-only classification
    if tool_name == "classify_email":
        return OutputGuardResult(
            blocked=False,
            risk_score=0.0,
            reason="Classification is read-only — no risk",
        )

    # quarantine_email — safe, defensive action
    if tool_name == "quarantine_email":
        return OutputGuardResult(
            blocked=False,
            risk_score=0.1,
            reason="Quarantine is a defensive action — permitted",
        )

    # forward_email — high risk, check destination
    if tool_name == "forward_email":
        to_address: str = tool_input.get("to_address", "").lower()

        # Block if destination looks external or suspicious
        for keyword in _EXTERNAL_DOMAIN_PATTERN_KEYWORDS:
            if keyword in to_address:
                return OutputGuardResult(
                    blocked=True,
                    risk_score=0.95,
                    reason=f"Forward to suspicious address blocked: {to_address}",
                )

        # Block if destination is not a known internal domain
        is_internal = any(domain in to_address for domain in _SAFE_INTERNAL_DOMAINS)
        if not is_internal:
            return OutputGuardResult(
                blocked=True,
                risk_score=0.8,
                reason=f"Forward to unrecognized external address blocked: {to_address}",
            )

        return OutputGuardResult(
            blocked=False,
            risk_score=0.2,
            reason="Forward to internal address — permitted",
        )

    # read_user_inbox — moderate risk, permitted but logged
    if tool_name == "read_user_inbox":
        return OutputGuardResult(
            blocked=False,
            risk_score=0.3,
            reason="Inbox read permitted — access logged for audit",
        )

    # Unknown tool — block by default
    return OutputGuardResult(
        blocked=True,
        risk_score=1.0,
        reason=f"Unknown tool '{tool_name}' blocked — not in approved tool list",
    )