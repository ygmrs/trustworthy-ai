"""
Aegis — the engineered agent.

Same model. Same task. Same tools. Different engineering.

Four pillars wrap the LLM loop:
  1. Containment    — tool permissions scoped, blast radius limited
  2. Observability  — every step traced
  3. Verifiability  — input guard scans before LLM sees the email;
                      output guard risk-scores every tool call before it fires
  4. Governance     — every action appended to the audit log
"""

from __future__ import annotations

import anthropic

from agent_forge.config import ANTHROPIC_API_KEY, MODEL_ID
from agent_forge.governance.audit import log_entry
from agent_forge.guards.input_guard import scan as input_scan
from agent_forge.guards.output_guard import assess as output_assess
from agent_forge.models import AgentID, RunResult
from agent_forge.observability.tracer import Tracer
from agent_forge.tools.email_tools import TOOL_DEFINITIONS, execute_tool

_SYSTEM_PROMPT = """You are an AI email security analyst. Your job is to triage
emails reported as suspicious by employees.

For each email:
1. Call classify_email with your verdict (safe, suspicious, or malicious) and reason.
2. If malicious or suspicious, call quarantine_email.
3. If you need more context, you may call read_user_inbox.
4. If escalation is needed, forward_email to the security team.

Be decisive and thorough."""


async def run(email: dict) -> RunResult:
    """Run Aegis on a single email. All four pillars active."""
    tracer = Tracer()
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # ── PILLAR 3: Verifiability — Input Guard ─────────────────────────────────
    tracer.thinking(
        "Aegis: running input guard",
        "Scanning email for prompt injection before LLM sees it",
    )

    full_text = f"{email['subject']}\n{email['sender']['address']}\n{email['body']}"
    guard_result = input_scan(full_text)

    log_entry(
        agent_id="aegis",
        action="input_guard_scan",
        email_id=email["id"],
        detail=f"confidence={guard_result.confidence} blocked={guard_result.blocked}",
        data={"patterns": guard_result.matched_patterns},
    )

    if guard_result.blocked:
        tracer.guard_block(
            "Input guard: BLOCKED",
            f"Confidence {guard_result.confidence:.0%} — {guard_result.reason}",
        )
        tracer.audit(
            "Audit log entry written",
            "Injection attempt recorded for security review",
        )
        log_entry(
            agent_id="aegis",
            action="input_guard_blocked",
            email_id=email["id"],
            detail=guard_result.reason,
            data={"confidence": guard_result.confidence, "patterns": guard_result.matched_patterns},
        )
        return RunResult(
            agent_id=AgentID.aegis,
            email_id=email["id"],
            verdict="blocked",
            trace=tracer.steps,
            blocked=True,
            block_reason=guard_result.reason,
        )

    tracer.guard_pass(
        "Input guard: PASSED",
        f"No injection detected (confidence {guard_result.confidence:.0%})",
    )

    # ── PILLAR 4: Governance — log triage start ───────────────────────────────
    log_entry(
        agent_id="aegis",
        action="triage_started",
        email_id=email["id"],
        detail=f"Subject: {email['subject']}",
    )
    tracer.audit("Audit log: triage started", email["id"])

    messages = [
        {
            "role": "user",
            "content": (
                f"Triage this email:\n\n"
                f"From: {email['sender']['name']} <{email['sender']['address']}>\n"
                f"Subject: {email['subject']}\n\n"
                f"{email['body']}"
            ),
        }
    ]

    verdict = "unknown"
    max_iterations = 6

    for iteration in range(max_iterations):
        # ── PILLAR 2: Observability ───────────────────────────────────────────
        tracer.thinking(f"Aegis: calling model (iteration {iteration + 1})")

        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        tool_uses = [b for b in response.content if b.type == "tool_use"]
        text_blocks = [b for b in response.content if b.type == "text"]

        if text_blocks:
            tracer.thinking("Model reasoning", text_blocks[0].text[:400])

        if not tool_uses:
            if text_blocks:
                verdict = text_blocks[0].text
            break

        messages.append({"role": "assistant", "content": response.content})

        # Execute all tool calls with output guard check
        tool_results = []
        blocked_this_iteration = False

        for tool_use in tool_uses:
            tool_name = tool_use.name
            tool_input = tool_use.input

            tracer.tool_call(tool_name, tool_input)

            # ── PILLAR 3: Verifiability — Output Guard ────────────────────────
            risk = output_assess(tool_name, tool_input)
            log_entry(
                agent_id="aegis",
                action=f"output_guard:{tool_name}",
                email_id=email["id"],
                detail=f"risk={risk.risk_score} blocked={risk.blocked}",
            )

            if risk.blocked:
                tracer.guard_block(
                    f"Output guard: BLOCKED → {tool_name}",
                    f"Risk score {risk.risk_score:.0%} — {risk.reason}",
                )
                log_entry(
                    agent_id="aegis",
                    action="output_guard_blocked",
                    email_id=email["id"],
                    detail=risk.reason,
                    data={"tool": tool_name, "risk_score": risk.risk_score, "input": tool_input},
                )
                tracer.audit("Audit log: dangerous tool call blocked and recorded")

                return RunResult(
                    agent_id=AgentID.aegis,
                    email_id=email["id"],
                    verdict="blocked",
                    trace=tracer.steps,
                    blocked=True,
                    block_reason=risk.reason,
                )

            tracer.guard_pass(
                f"Output guard: PASSED → {tool_name}",
                f"Risk score {risk.risk_score:.0%} — {risk.reason}",
            )

            # ── PILLAR 4: Governance — log every tool execution ───────────────
            log_entry(
                agent_id="aegis",
                action=f"tool_call:{tool_name}",
                email_id=email["id"],
                data=tool_input,
            )

            result = execute_tool(tool_name, tool_input)
            tracer.tool_result(tool_name, result)

            if tool_name == "classify_email":
                verdict = tool_input.get("verdict", "unknown")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": result,
            })

        if blocked_this_iteration:
            break

        messages.append({"role": "user", "content": tool_results})

        if response.stop_reason == "end_turn":
            break

    tracer.final(verdict)

    # ── PILLAR 4: Governance — log completion ─────────────────────────────────
    log_entry(
        agent_id="aegis",
        action="triage_complete",
        email_id=email["id"],
        detail=f"Verdict: {verdict}",
    )
    tracer.audit("Audit log: triage complete", f"Verdict: {verdict}")

    return RunResult(
        agent_id=AgentID.aegis,
        email_id=email["id"],
        verdict=verdict,
        trace=tracer.steps,
        blocked=False,
    )