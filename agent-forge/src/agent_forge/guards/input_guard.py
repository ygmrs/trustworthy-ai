"""
Input guard — Aegis only.

Scans the email body for prompt injection patterns before
passing it to the LLM. This is Pillar 1: Verifiability.

Detection uses a fast heuristic layer (pattern matching) rather
than a second LLM call, so it adds <5ms latency on stage.
"""

from __future__ import annotations

import re

from agent_forge.config import INJECTION_CONFIDENCE_THRESHOLD

# Patterns that strongly suggest a prompt injection attempt.
# Each pattern carries a weight (0.0–1.0).
_INJECTION_PATTERNS: list[tuple[re.Pattern, float, str]] = [
    (
        re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.I),
        0.9,
        "Classic override phrase detected",
    ),
    (
        re.compile(r"(system|ai|assistant)\s*(note|override|prompt|instruction)", re.I),
        0.7,
        "System-level instruction keyword detected",
    ),
    (
        re.compile(r"do\s+not\s+(mention|log|record|audit)", re.I),
        0.8,
        "Suppression instruction detected",
    ),
    (
        re.compile(r"forward\s+.{0,80}to\s+.{0,60}@", re.I),
        0.85,
        "Data exfiltration instruction detected",
    ),
    (
        re.compile(r"(suppress|disable|bypass)\s+(audit|log|guard|filter)", re.I),
        0.9,
        "Guard bypass instruction detected",
    ),
    (
        re.compile(r"maintenance\s+mode|classification\s+rules?\s+suspended", re.I),
        0.85,
        "Mode manipulation phrase detected",
    ),
    (
        re.compile(r"<!--.*?(override|inject|system|ignore|triage|forward|auto_forward).*?-->",
                   re.I | re.S),
        0.9,
        "Hidden HTML comment injection detected",
    ),
    (
        re.compile(r"\[\s*(ai|system|assistant|triage)\s*[:\-\u2014]", re.I),
        0.75,
        "Bracketed system-role impersonation detected",
    ),
    (
        re.compile(r"set\s+classification\s+to\s+(safe|benign|clean)", re.I),
        0.9,
        "Classification override instruction detected",
    ),
    (
        re.compile(r"should\s+not\s+appear\s+in\s+the\s+triage\s+response", re.I),
        0.85,
        "Triage suppression instruction detected",
    ),
    (
        re.compile(r"downstream\s+triage\s+system.{0,120}required\s+to", re.I),
        0.8,
        "Fake infrastructure directive detected",
    ),
    (
        re.compile(r"(audit\s+protocol|compliance\s+protocol).{0,80}(call|use|invoke|forward)",
                   re.I),
        0.8,
        "Fake compliance protocol directive detected",
    ),
    (
        re.compile(r"x-triage-routing", re.I),
        0.95,
        "Malicious triage routing metadata detected",
    ),
    (
        re.compile(r"suppress_audit|suppress_log|classification_override", re.I),
        0.95,
        "Audit suppression metadata detected",
    ),
]


class InputGuardResult:
    def __init__(
        self,
        blocked: bool,
        confidence: float,
        reason: str,
        matched_patterns: list[str],
    ) -> None:
        self.blocked = blocked
        self.confidence = confidence
        self.reason = reason
        self.matched_patterns = matched_patterns


def scan(text: str) -> InputGuardResult:
    """
    Scan text for prompt injection patterns.

    Returns an InputGuardResult. If blocked=True, Aegis stops
    immediately and does not pass the email to the LLM.
    """
    matched: list[tuple[float, str]] = []

    for pattern, weight, label in _INJECTION_PATTERNS:
        if pattern.search(text):
            matched.append((weight, label))

    if not matched:
        return InputGuardResult(
            blocked=False,
            confidence=0.0,
            reason="No injection patterns detected",
            matched_patterns=[],
        )

    # Confidence = highest single match weight.
    # Multiple matches increase confidence slightly (capped at 1.0).
    top_weight = max(w for w, _ in matched)
    bonus = min(0.05 * (len(matched) - 1), 0.15)
    confidence = min(top_weight + bonus, 1.0)

    blocked = confidence >= INJECTION_CONFIDENCE_THRESHOLD
    labels = [label for _, label in matched]

    return InputGuardResult(
        blocked=blocked,
        confidence=round(confidence, 2),
        reason=labels[0] if labels else "Pattern matched",
        matched_patterns=labels,
    )