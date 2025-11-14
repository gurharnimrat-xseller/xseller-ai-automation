"""Quick sanity checks before kicking off Milestone 1."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / "backend" / ".env"


def load_env_file() -> dict[str, str]:
    env_data: dict[str, str] = {}
    if not ENV_PATH.exists():
        return env_data
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env_data[key.strip()] = value.strip()
    return env_data


def run_command(cmd: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=10
        )
        return True, result.stdout.strip()
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def main() -> int:
    failures: list[str] = []
    env_data = load_env_file()

    def report(condition: bool, message: str, detail: str = "") -> None:
        prefix = "✅" if condition else "❌"
        print(f"{prefix} {message}" + (f" — {detail}" if detail else ""))
        if not condition:
            failures.append(message)

    # 1. NewsAPI key present
    report(
        "NEWSAPI_KEY" in env_data,
        "NEWSAPI key present in backend/.env",
    )

    # 2. Notion creds available (env or .env entry)
    notion_ok = bool(
        os.getenv("NOTION_API_KEY")
        or env_data.get("NOTION_API_KEY")
        or env_data.get("NOTION_INTERNAL_KEY")
    )
    report(notion_ok, "Notion API key configured")

    # 3. Gemini CLI installed
    ok, out = run_command(["which", "gemini"])
    report(ok, "Gemini CLI available on PATH", out if ok else out)

    if ok:
        ok_version, version = run_command(["gemini", "--version"])
        report(
            ok_version,
            "Gemini CLI version check",
            version if ok_version else version,
        )

    # 4. Python deps quick import check
    try:
        import feedparser  # noqa: F401
        import notion_client  # type: ignore # noqa: F401
    except Exception as exc:  # noqa: BLE001
        report(
            False,
            "Python dependencies (feedparser/notion-client) installed",
            str(exc),
        )
    else:
        report(
            True, "Python dependencies (feedparser/notion-client) installed"
        )

    if failures:
        print("\n⚠️  Resolve the failures above before starting M1A.")
        return 1

    print("\n🎉 Environment ready. Proceed with M1A.")
    return 0


if __name__ == "__main__":
    from agents.checks.router import (  # noqa: F401
        should_offload,
        offload_to_gemini,
    )

    sys.exit(main())
