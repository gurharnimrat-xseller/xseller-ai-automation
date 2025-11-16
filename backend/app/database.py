from __future__ import annotations

from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401 guardrails

from sqlmodel import create_engine
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./xseller.db')
engine = create_engine(DATABASE_URL, echo=True)
