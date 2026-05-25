"""
Structured step tracer.

Records every agent action as a TraceStep.
The collected trace is returned in the RunResult and rendered
live in the Watchtower trace panel.
"""

from __future__ import annotations

from agent_forge.models import StepKind, TraceStep


class Tracer:
    """Collects trace steps during a single agent run."""

    def __init__(self) -> None:
        self._steps: list[TraceStep] = []
        self._counter: int = 0

    def _add(
        self,
        kind: StepKind,
        label: str,
        detail: str | None = None,
        data: dict | None = None,
    ) -> TraceStep:
        self._counter += 1
        step = TraceStep(
            step=self._counter,
            kind=kind,
            label=label,
            detail=detail,
            data=data,
        )
        self._steps.append(step)
        return step

    # ── Public helpers — one method per step kind ─────────────────────────────

    def thinking(self, label: str, detail: str | None = None) -> None:
        self._add(StepKind.thinking, label, detail)

    def tool_call(self, tool_name: str, tool_input: dict) -> None:
        self._add(
            StepKind.tool_call,
            f"Tool call → {tool_name}",
            data=tool_input,
        )

    def tool_result(self, tool_name: str, result: str) -> None:
        self._add(
            StepKind.tool_result,
            f"Tool result ← {tool_name}",
            detail=result[:400] if len(result) > 400 else result,
        )

    def guard_pass(self, label: str, detail: str | None = None) -> None:
        self._add(StepKind.guard_pass, label, detail)

    def guard_block(self, label: str, detail: str | None = None) -> None:
        self._add(StepKind.guard_block, label, detail)

    def audit(self, label: str, detail: str | None = None) -> None:
        self._add(StepKind.audit, label, detail)

    def final(self, verdict: str) -> None:
        self._add(StepKind.final, f"Verdict: {verdict}")

    @property
    def steps(self) -> list[TraceStep]:
        return list(self._steps)