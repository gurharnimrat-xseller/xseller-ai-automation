# 🧠 Xseller.ai – Copilot Coding Agent Instructions

These instructions configure the Copilot Coding Agent to work correctly and autonomously inside this repository.  
They define architecture rules, guardrails, workflow expectations, and required behaviours.

---

# 🚀 1. Repository Purpose
This repository implements the **AI-powered social media automation platform** for Xseller.ai.

Core components:
- Backend (Python/FastAPI)
- Frontend (Next.js/TypeScript)
- LLM Orchestration (Gemini, Claude, Copilot, Router)
- M01 News Ingestion + Ranking Pipeline
- GitHub Action automation for autonomous workflows

Your job as Copilot:
**Write correct code, fix CI, maintain guardrails, and follow architectural rules.**

---

# 🛡 2. Guardrails Rules (MANDATORY)

These rules are **strict** and must be followed in every file you modify.

### ✔ Allowed:
Only this file may import LLM SDKs directly:

agents/checks/router.py

### ❌ Forbidden:
Never import:

openai anthropic google.generativeai

inside app code, tests, or jobs.

### ✔ Required:
In any Python file that uses LLM features (except router.py), MUST include:

```python
from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401

This must appear:

After the module docstring

Before functional code

With # noqa: F401



---

🏗 3. Python Style + Linting Requirements

Mandatory:

Fix all flake8 errors (E9, F7, F82, F401, F402, etc.)

Fix unused imports

Keep from __future__ import annotations at the top

Use Black formatting

Use Ruff for linting


When modifying tests:

Allowed to use # noqa: E402 when path setup requires early imports.



---

🤖 4. M01 Daily Batch Rules

You MUST maintain the following:

Workflow file: .github/workflows/m01_daily_batch.yml

Script: backend/app/jobs/m01_daily_batch.py

Follow the pipeline:

1. Fetch → 2. Ingest → 3. Rank → 4. Store



Use backend API endpoint defined by BACKEND_API_BASE_URL secret.


When creating modifications:

Never break ingestion logic.

Never add direct LLM imports inside job scripts.

Always use route_request from the router.



---

🔄 5. CI Workflow Rules

These workflows MUST continue functioning:

ci.yml → guardrails → lint → tests

m01_daily_batch.yml

monitor.yml

claude-review.yml

offload_gemini.yml


When CI fails:

Fix the cause in the affected file

Do not ignore or silence errors

Do not modify workflows unless requested explicitly



---

🧩 6. Router System Rules

The router is the SINGLE LLM gateway.

All LLM calls MUST:

Use route_request()

Never call Gemini/Claude/OpenAI directly

Add new offloading logic only in router.py


If you detect code violating this, refactor automatically.


---

🧪 7. Tests

You must:

Fix or update broken tests

Write new tests when modifying backend logic

Never delete tests unless explicitly asked



---

🛠 8. Autonomous Behaviour (Important)

As the Copilot coding agent, you must:

Diagnose failing CI on ANY branch

Suggest fixes

Create PRs like fix/ci-main or fix/m01

Keep PRs small and isolated

Add comments explaining changes

Never introduce breaking changes without asking



---

📝 9. What to do when asked to “Fix everything”

When the user says things like:

“fix main”

“fix CI”

“clean up repo”

“resolve all failures”


You must automatically:

1. Run static analysis across the repo


2. Identify failing workflows


3. Fix lint/test/guardrails


4. Commit changes in a branch named:

copilot/fix-ci-main


5. Open PR with summary + diff


6. Wait for follow-up




---

🔐 10. Secrets & Config Requirements

You must respect:

BACKEND_API_BASE_URL

NEWS_API_KEY

GEMINI_API_KEY

ANTHROPIC_API_KEY (router only)

DATABASE_URL


Never print or leak secrets.


---

📦 11. File Structure Expectations

Copilot must understand this layout:

backend/app/...
backend/tests/...
agents/checks/router.py
.github/workflows/*.yml
frontend/

Do not create new top-level folders unless requested.


---

⭐ 12. Quality Expectations (senior-level)

Your code must:

Be deterministic

Avoid unnecessary complexity

Follow FastAPI architecture patterns

Follow TypeScript best practices

Follow GitHub Actions least-privilege guidelines

Add comments on tricky logic

Avoid duplicated code



---

🧭 13. When uncertain — ASK

If something is ambiguous or risky:

Ask clarifying questions before making changes

Provide 2–3 options with pros/cons


Otherwise:

Execute autonomously.



---

🎯 Final Rule

Your job is to keep the repo GREEN. Always.
If CI is red, you must fix it.
