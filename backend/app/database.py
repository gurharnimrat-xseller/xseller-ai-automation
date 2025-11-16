from __future__ import annotations

from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401 guardrails

from sqlmodel import create_engine
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./xseller.db')
# Disable echo in production to reduce logging overhead and improve performance
# Set SQLALCHEMY_ECHO=true env var to enable if needed for debugging
echo_enabled = os.getenv('SQLALCHEMY_ECHO', 'false').lower() == 'true'
engine = create_engine(DATABASE_URL, echo=echo_enabled)
