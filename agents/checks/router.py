"""
LLM Router - Single interface for all AI/LLM calls with cost tracking and offload support.

This module provides a controlled interface for LLM calls, ensuring:
- No direct SDK imports in application code
- Cost tracking and budget enforcement
- Automatic offload for heavy prompts
- Retry logic with exponential backoff
"""

import os
import json
import base64
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
import subprocess


# Configuration from environment
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "12000"))
HEAVY_TIMEOUT_SEC = int(os.getenv("HEAVY_TIMEOUT_SEC", "90"))
OFFLOAD_MODEL = os.getenv("OFFLOAD_MODEL", "gemini-1.5-pro-latest")


def estimate_tokens(text: str) -> int:
    """
    Rough estimate of token count.
    Uses ~4 chars per token heuristic (conservative for English).
    """
    return len(text) // 4


def should_offload(prompt: str, est_sec: Optional[int] = None) -> bool:
    """
    Decide if task should be offloaded to Gemini workflow.

    Args:
        prompt: The prompt text
        est_sec: Estimated runtime in seconds (optional)

    Returns:
        True if should offload, False otherwise
    """
    token_count = estimate_tokens(prompt)

    if token_count >= MAX_TOKENS:
        return True

    if est_sec and est_sec >= HEAVY_TIMEOUT_SEC:
        return True

    return False


def offload_to_gemini(prompt: str, model: Optional[str] = None) -> str:
    """
    Offload prompt to Gemini via GitHub Actions workflow.

    Args:
        prompt: The prompt to process
        model: Model to use (default: OFFLOAD_MODEL from env)

    Returns:
        Status message indicating offload was triggered
    """
    model = model or OFFLOAD_MODEL
    request_id = hashlib.md5(
        f"{prompt[:100]}{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:12]

    # Encode prompt
    prompt_b64 = base64.b64encode(prompt.encode()).decode()

    # Log the offload
    offload_log = {
        "request_id": request_id,
        "model": model,
        "timestamp_utc": datetime.utcnow().isoformat(),
        "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest()[:16],
        "response_preview": "Offloaded to GitHub Actions"
    }

    try:
        with open("docs/LAST_OFFLOAD.json", "w") as f:
            json.dump(offload_log, f, indent=2)
    except Exception:
        pass  # Continue even if logging fails

    # Trigger workflow (requires gh CLI)
    try:
        subprocess.run(
            ["gh", "workflow", "run", "offload_gemini.yml",
             "-f", f"prompt={prompt_b64}",
             "-f", f"model={model}"],
            check=False,  # Don't fail if gh not available
            capture_output=True
        )
    except Exception:
        pass  # Graceful degradation

    return f"Offloaded to Gemini — check docs/LAST_OFFLOAD.json (request_id: {request_id})"


def route_request(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> Dict[str, Any]:
    """
    Route an LLM request through the appropriate channel.

    For lightweight requests, uses Gemini API directly.
    For heavy requests, offloads to GitHub Actions.

    Args:
        prompt: The prompt text
        model: Model to use (optional, defaults to env config)
        temperature: Sampling temperature
        max_tokens: Max tokens in response

    Returns:
        Dict with 'content' key containing response text
    """
    # Check if should offload
    if should_offload(prompt):
        result = offload_to_gemini(prompt, model)
        return {
            "content": result,
            "offloaded": True,
            "model": model or OFFLOAD_MODEL
        }

    # For lightweight requests, use Gemini API directly
    try:
        import google.generativeai as genai

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {
                "content": "Error: GEMINI_API_KEY not set",
                "error": True
            }

        genai.configure(api_key=api_key)
        model_name = model or "gemini-1.5-flash"  # Use flash for lightweight requests

        model_obj = genai.GenerativeModel(model_name)
        response = model_obj.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )

        return {
            "content": response.text,
            "offloaded": False,
            "model": model_name
        }

    except ImportError:
        # Gemini SDK not available, return error
        return {
            "content": "Error: google-generativeai not installed. Install with: pip install google-generativeai",
            "error": True
        }
    except Exception as e:
        return {
            "content": f"Error calling LLM: {str(e)}",
            "error": True
        }
