# XSeller AI News Automation: Coding & Agent Guidelines

**Version 1.0** | November 2025 | Internal MVP & Full App
**Scope**: Code style, AI/LLM orchestration, API resilience, guardrails

---

## Quick Reference

See detailed examples in `/docs/style/`:
- `python_router.md` — Router pattern with cost tracking
- `python_retry_backoff.md` — Exponential backoff + jitter
- `ts_zod_api.md` — TypeScript Zod validation in API routes
- `actions_least_privilege.md` — GitHub Actions security & caching

---

## 1. Code Style Standards

### Python Backend

**Tools**: Ruff (formatter + linter) + mypy (type checker)

**pyproject.toml**:
```toml
[tool.ruff]
line-length = 100
target-version = "py311"
fix = true

[tool.ruff.lint]
select = ["E","F","I"]
ignore = []
per-file-ignores = {}

[tool.black]
line-length = 100

[tool.mypy]
python_version = "3.11"
strict = true
warn_unused_ignores = true
warn_no_return = true
disallow_untyped_defs = true
```

**Conventions**

- `snake_case` for functions and variables
- `PascalCase` for classes
- Type hints required for all public functions and class attributes
- Pydantic models for request/response schemas
- Docstrings (Google style) for public functions/classes

**Testing**

- `pytest` with fixtures
- Coverage target ≥ 80%
- Unit tests for router, retries, idempotency, circuit breaker

### TypeScript / Next.js Frontend

**Tools**: ESLint (strict) + Prettier

**.eslintrc.json**:
```json
{
  "extends": ["next/core-web-vitals", "eslint:recommended"],
  "parserOptions": { "ecmaVersion": 2023 },
  "rules": {
    "no-unused-vars": ["warn", { "args": "none" }],
    "no-undef": "error"
  }
}
```

**Conventions**

- Strict TypeScript mode, no implicit `any`
- Zod for runtime schema validation of API inputs/outputs
- Components in TSX with props typed and validated
- Accessibility: ARIA roles, keyboard nav, focus rings

**Testing**

- Jest + React Testing Library
- Snapshots for key components (PipelineCard states)
- Cypress for integration (dashboard → pipelines → offloads)

### GitHub Actions YAML

**Principles**

- Least-privilege permissions
- Use `concurrency:` groups on workflows that can conflict
- Cache dependencies with `actions/cache`
- No secrets hardcoded; use GitHub Secrets/Vars only

---

## 2. AI/LLM Orchestration (Router Pattern)

**Mandatory**: All LLM/API calls use router functions; no direct SDK imports.

**Import**:
```python
from agents.checks.router import should_offload, offload_to_gemini
```

**Heavy Rule**

- Offload if estimated tokens ≥ 12000 or estimated run time ≥ 90s
- On offload, exit locally and dispatch GitHub Action `offload_gemini.yml`

**Budget**

- NZD 20/mo cap; pause offloads if reached and alert via monitor

**Observability**

- Write `docs/LAST_OFFLOAD.json` with `{ request_id, model, timestamp_utc, prompt_hash, response_preview }`

---

## 3. API Resilience Patterns

**Retry with exponential backoff**

- 3 attempts: 0.5s → 2s → 5s (+ jitter)

**Idempotency**

- Use `idempotency_key = sha256(inputs)` for POST-like operations

**Circuit Breaker**

- Open after 5 consecutive 5xx/429 for 60s, then half-open test

**Tracing**

- `request_id` per hop; pass through headers/context

---

## 4. Guardrails & Security

**Forbidden imports in app code**

- `openai`, `anthropic`, `google.generativeai` (only allowed inside router or action code)
- Guardrails check fails PR if found

**Secrets**

- Only via GitHub Secrets/Vars
- No `.env` committed

**Branch Protection**

- Require PR (1 approval)
- Require status check: Guardrails / scan (only) until CI is green

**Monitoring**

- `monitor.yml` posts Daily Summary in 05:00–10:00 NZT window
- Includes: open PRs, failing checks, last offload link, budget line, next 3 priorities

---

## 5. Repository Conventions

**Paths**

- Keep current layout:
  - `agents/checks/router.py`, `agents/checks/verify_guardrails.py`, `agents/checks/monitor.py`
  - `docs/*` (no moves/renames)
  - Workflows: `.github/workflows/guardrails.yml`, `offload_gemini.yml`, `monitor.yml`

**Commits/PRs**

- Conventional Commits: `feat`, `fix`, `chore`, `docs`, `refactor`
- Small diffs (≤ 300 lines)
- PR template requires router import checks and no direct SDKs

---

## 6. Frontend UI/UX Standards (Dashboard App)

**Sitemap**

- `/` Dashboard (KPIs, offload chart)
- `/pipelines` stage cards (Fetch, Rank, Script, Video, Voice, Post)
- `/offloads` table (request_id, model, timestamp, link)
- `/guardrails` PR checks (Guardrails/CI)
- `/settings` read-only vars

**Responsiveness**

- Breakpoints: md=768, lg=1024, xl=1280
- Sidebar collapses below lg, charts stack on mobile

**Accessibility**

- Keyboard navigable; ARIA roles for button, table, progressbar, chart
- Dark mode toggle + prefers-color-scheme

**Performance**

- React Query caching (30s), skeleton loaders, lazy load charts
- Animations ≤ 150ms ease-in-out

---

## 7. Runbooks

- Rotate `GEMINI_API_KEY` monthly
- If budget cap hit, continue monitor but pause offloads
- If monitor fails, run manually via `workflow_dispatch` and check logs
- Restore guardrails if someone removes router imports (PR should fail by design)

---

## 8. References & Snippets

See `/docs/style/`:

- `python_router.md`
- `python_retry_backoff.md`
- `ts_zod_api.md`
- `actions_least_privilege.md`

**Diagram**: `docs/style/xseller_architecture.png`

