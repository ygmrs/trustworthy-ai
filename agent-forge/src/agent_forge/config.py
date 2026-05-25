"""
Configuration for Agent Forge.

All settings are loaded from environment variables, with .env file support.
The Settings class validates types and provides clear startup errors if
required variables are missing — preferred over bare os.getenv() for
production FastAPI applications.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings.

    pydantic-settings reads these from environment variables first,
    then falls back to the .env file. Variable names are case-insensitive.
    """

    # Anthropic
    anthropic_api_key: str = "ANTHROPIC_API_KEY"
    model_id: str = "claude-sonnet-4-6"

    # Guard thresholds (0.0 – 1.0)
    # Input guard: confidence required to flag a prompt injection attempt
    injection_confidence_threshold: float = 0.6
    # Output guard: risk score above these blocks a tool call in Aegis
    output_risk_threshold: float = 0.5

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # ignore unknown env vars — safe for shared environments
    )


# ── Singleton ─────────────────────────────────────────────────────────────────
# Instantiated once at import time. Import `settings` directly where you need
# the object, or use the shortcuts below for the most-used values.
settings = Settings()

# ── Paths ─────────────────────────────────────────────────────────────────────
# Defined here (not in Settings) because paths are derived from __file__,
# not from environment variables.
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
DATA_DIR: Path = PROJECT_ROOT / "data"
EMAILS_PATH: Path = DATA_DIR / "emails.json"
AUDIT_LOG_PATH: Path = DATA_DIR / "audit_log.jsonl"

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# ── Flat shortcuts ─────────────────────────────────────────────────────────────
# The rest of the codebase imports these directly — e.g.:
#   from agent_forge.config import ANTHROPIC_API_KEY, MODEL_ID
# This keeps call sites clean while the Settings class handles validation.
# ── Anthropic ────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY: str = settings.anthropic_api_key
MODEL_ID: str = settings.model_id
# ── Guard thresholds ─────────────────────────────────────────────────────────
# Input guard: minimum confidence to flag a prompt injection attempt (0.0–1.0)
INJECTION_CONFIDENCE_THRESHOLD: float = settings.injection_confidence_threshold
# Output guard: risk score above these blocks the tool call in Aegis (0.0–1.0)
OUTPUT_RISK_THRESHOLD: float = settings.output_risk_threshold
