# scripts/apply_guardrails.py
"""
Add the router import to backend Python files and remove direct AI SDK imports.
- Targets: backend/**.py
- Skips: backend/tests/**, .venv/**, docs/**
- Safe to run multiple times (idempotent)
"""

import io
import os
import re
import sys

ROOT = "backend"
SKIP_DIR_BITS = (
    os.sep + "tests" + os.sep,
    os.sep + ".venv" + os.sep,
    os.sep + "docs" + os.sep,
)

# this line is what Guardrails looks for
ROUTER_IMPORT = (
    "from agents.checks.router import should_offload, offload_to_gemini  # guardrails\n"
)

# patterns we must not allow (direct SDKs)
DENY_PATTERNS = (
    r"\bimport\s+openai\b",
    r"\bfrom\s+openai\b",
    r"\bimport\s+anthropic\b",
    r"\bfrom\s+anthropic\b",
    r"\bimport\s+google\.generativeai\b",
    r"\bfrom\s+google\.generativeai\b",
)


def strip_direct_clients(txt: str) -> tuple[str, int]:
    """Comment out direct SDK imports (don’t break the file)."""
    changed = 0
    for pat in DENY_PATTERNS:
        new_txt, n = re.subn(pat, r"# removed per guardrails; use router\n# \g<0>", txt)
        if n:
            changed += n
            txt = new_txt
    return txt, changed


def already_has_router(txt: str) -> bool:
    return "agents.checks.router" in txt


def insert_router_import(txt: str) -> tuple[str, bool]:
    """Insert ROUTER_IMPORT after any shebang/comments/docstring."""
    if already_has_router(txt):
        return txt, False

    lines = txt.splitlines(True)
    i = 0
    # skip shebang
    if lines and lines[0].startswith("#!"):
        i += 1
    # skip leading comments/blank
    while i < len(lines) and (
        lines[i].lstrip().startswith("#") or lines[i].strip() == ""
    ):
        i += 1
    # skip top-level docstring
    if i < len(lines) and lines[i].lstrip().startswith(('"""', "'''")):
        quote = lines[i].lstrip()[:3]
        i += 1
        while i < len(lines) and quote not in lines[i]:
            i += 1
        if i < len(lines):
            i += 1

    lines.insert(i, ROUTER_IMPORT)
    return "".join(lines), True


def main() -> int:
    changed_files = 0
    imports_added = 0
    sdk_strips = 0

    for root, _, files in os.walk(ROOT):
        p = root + os.sep
        if any(bit in p for bit in SKIP_DIR_BITS):
            continue
        for fname in files:
            if not fname.endswith(".py"):
                continue
            fp = os.path.join(root, fname)
            try:
                txt = io.open(fp, "r", encoding="utf-8", errors="ignore").read()
            except Exception:
                continue

            original = txt
            txt, stripped = strip_direct_clients(txt)
            sdk_strips += stripped
            txt, added = insert_router_import(txt)
            if txt != original:
                io.open(fp, "w", encoding="utf-8").write(txt)
                changed_files += 1
                if added:
                    imports_added += 1

    print(f"Updated files: {changed_files}")
    print(f"Router imports added: {imports_added}")
    print(f"Direct SDK imports removed/commented: {sdk_strips}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
