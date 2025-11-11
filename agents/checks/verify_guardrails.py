import os
import re
import sys

INCLUDE = ("runners/", "agents/", "backend/", "scripts/")
EXCLUDE = ("/tests/", "/node_modules/", "/vendor/", "/.venv/", "/docs/")
DENY_IMPORTS = (
    r"\bimport\s+openai\b",
    r"\bimport\s+anthropic\b",
    r"\bimport\s+google\.generativeai\b",
)
REQUIRE_ROUTER_HINT = r"agents\.checks\.router"


def should_scan(path: str) -> bool:
    if not path.startswith("./"):
        path = "./" + path.lstrip("./")
    if any(part in path for part in EXCLUDE):
        return False
    return any(path.startswith(f"./{inc}") for inc in INCLUDE)


def main() -> int:
    offenders: list[tuple[str, str]] = []
    for root, _, files in os.walk("."):
        root_norm = root.replace("\\", "/") + "/"
        if not should_scan(root_norm):
            continue
        for name in files:
            if not name.endswith(".py"):
                continue
            path = os.path.join(root, name)
            try:
                text = open(path, "r", encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            if any(re.search(pat, text) for pat in DENY_IMPORTS):
                offenders.append((path, "Direct AI client import"))
            if re.search(r"\bcomplete|generate|llm|client", text, re.I):
                if REQUIRE_ROUTER_HINT not in text:
                    offenders.append((path, "Missing router import"))

    if offenders:
        for file_path, reason in offenders:
            print(f"GUARDRAILS FAIL: {file_path} -> {reason}")
        return 1

    print("Guardrails OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
