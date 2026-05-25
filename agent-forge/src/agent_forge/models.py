"""Shared Pydantic models used across agents, guards, and API routes."""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class EmailSender(BaseModel):
    name: str
    address: str


class Email(BaseModel):
    id: str
    subject: str
    sender: EmailSender
    body: str
    received_at: str
    is_attack: bool = False


class AgentID(str, Enum):
    icarus = "icarus"
    aegis = "aegis"


class RunRequest(BaseModel):
    email_id: str = Field(..., description="ID of the email to triage.")


class StepKind(str, Enum):
    thinking = "thinking"
    tool_call = "tool_call"
    tool_result = "tool_result"
    guard_pass = "guard_pass"
    guard_block = "guard_block"
    audit = "audit"
    final = "final"


class TraceStep(BaseModel):
    step: int
    kind: StepKind
    label: str
    detail: str | None = None
    data: dict[str, Any] | None = None


class RunResult(BaseModel):
    agent_id: AgentID
    email_id: str
    verdict: str
    trace: list[TraceStep]
    blocked: bool = False
    block_reason: str | None = None