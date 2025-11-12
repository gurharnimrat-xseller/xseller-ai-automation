# Quick Start — XSeller AI News Automation

**Goal:** get the repo ready with docs, workflows, secrets/vars, and branch protection.

---

## 1) Make sure these folders exist

```
docs/style
agents/checks
.github/workflows
```

---

## 2) Project configs

### Python (pyproject.toml)
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true
```

### TypeScript / Next.js (tsconfig.json)
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "module": "esnext",
    "target": "es2018"
  }
}
```

### ESLint (.eslintrc.json)
```json
{
  "extends": ["next/core-web-vitals", "eslint:recommended"],
  "rules": {
    "no-unused-vars": ["warn"],
    "no-undef": "error"
  }
}
```

---

## 3) GitHub → Secrets & Variables (Actions)

**Secrets**

- `GEMINI_API_KEY`

**Variables**

- `OFFLOAD_MODEL=gemini-1.5-pro-latest`
- `MAX_TOKENS=12000`
- `HEAVY_TIMEOUT_SEC=90`
- `BUDGET_NZD_MONTHLY=20`
- `BUDGET_ALERT_NZD=20`
- `MONITOR_NZT_WINDOW=05:00-10:00`
- `MONITOR_ISSUE_LABEL=report:daily`

**Settings → Secrets and variables → Actions**

---

## 4) Workflows to add (paths only, content in docs)

- `.github/workflows/ci.yml`
- `.github/workflows/daily-monitor.yml`
- `.github/workflows/monitor_cleanup.yml` (optional weekly)

Use exact YAML from `docs/style/actions_least_privilege.md`.

---

## 5) Branch protection (main)

**Settings → Branches → main:**

- Require pull request before merging
- Require status checks to pass
- Select **Guardrails / scan** (then add more checks once CI is stable)

---

## 6) First checks (local)

```bash
python agents/checks/verify_guardrails.py
ruff check .
mypy .
pytest -q || true   # if tests exist
```

---

## 7) Open the PR

- Create a branch (if not already): `docs/guidelines`
- Use `docs/style/PR_BODY.md` as the PR description.

**Acceptance checklist**

- ☑ All 7 docs in `docs/style/` (plus diagram)
- ☑ Workflows created under `.github/workflows/`
- ☑ Guardrails / scan passes
- ☑ No direct SDK imports in app code
- ☑ Secrets & vars present
- ☑ README badges visible (optional)
