"""
XSeller AI Automation Backend - Core Application Module
"""
# Fix import path: ensure agents module can be found from repo root
import sys
import os
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401,E402
