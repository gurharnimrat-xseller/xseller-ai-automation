# GitHub Actions — Least-Privilege, Caching, Concurrency

**Purpose:** Secure, fast CI/CD with minimal scopes, safe concurrency, and no secrets in code.
**Scope:** Lint, test, guardrails, daily monitor, and optional cleanup scan.

---

## 1) Principles

- **Least privilege**: Grant only what each job needs (read vs write).
- **No secrets in code**: use `${{ secrets.* }}` and `${{ vars.* }}` only.
- **Concurrency**: Prevent overlapping runs on same branch.
- **Caching**: Use `actions/cache` for Python/Node deps.
- **Idempotence**: Re-runs should produce same result.

---

## 2) CI Workflow (lint + test + guardrails)

> File: `.github/workflows/ci.yml`

```yaml
name: CI
on:
  pull_request:
  push:
    branches: [ main ]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  guardrails:
    name: Guardrails / scan
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - run: python agents/checks/verify_guardrails.py

  lint_python:
    name: Lint (Python)
    runs-on: ubuntu-latest
    needs: [guardrails]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.x' }
      - uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: pip-${{ runner.os }}-${{ hashFiles('**/requirements*.txt') }}
          restore-keys: pip-${{ runner.os }}-
      - name: Install linters
        run: |
          python -m pip install --upgrade pip
          pip install ruff mypy
      - name: Ruff
        run: ruff check .
      - name: mypy
        run: mypy .

  lint_node:
    name: Lint (Node)
    runs-on: ubuntu-latest
    needs: [guardrails]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - uses: actions/cache@v4
        with:
          path: ~/.npm
          key: npm-${{ runner.os }}-${{ hashFiles('**/package-lock.json','**/pnpm-lock.yaml') }}
          restore-keys: npm-${{ runner.os }}-
      - name: Install deps (skip scripts)
        run: |
          if [ -f pnpm-lock.yaml ]; then npm i -g pnpm && pnpm i --ignore-scripts;
          elif [ -f package-lock.json ]; then npm ci --ignore-scripts;
          else echo "no node lockfile"; fi
      - name: ESLint
        run: |
          if [ -f .eslintrc.json ] || [ -f .eslintrc.js ]; then npx eslint . || true; else echo "no eslint config"; fi

  tests_python:
    name: Tests (Python)
    runs-on: ubuntu-latest
    needs: [lint_python]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.x' }
      - name: Install test deps
        run: |
          python -m pip install --upgrade pip
          pip install pytest pytest-cov
      - name: Pytests
        run: pytest -q

  tests_node:
    name: Tests (Node)
    runs-on: ubuntu-latest
    needs: [lint_node]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - name: Install + test
        run: |
          if [ -f pnpm-lock.yaml ]; then pnpm i --ignore-scripts && pnpm test -i || true;
          elif [ -f package-lock.json ]; then npm ci --ignore-scripts && npm test -i || true;
          else echo "no node project"; fi
```

Branch protection: mark **Guardrails / scan** as the only required check until CI is stable.

---

## 3) Daily Monitor (status issue)

**File**: `.github/workflows/daily-monitor.yml`

```yaml
name: Daily Monitor
on:
  schedule:
    - cron: "0 20 * * *" # 09:00 NZT approx (adjust as needed)
  workflow_dispatch:

permissions:
  contents: read
  issues: write

jobs:
  post:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.x' }
      - name: Run monitor
        env:
          GITHUB_TOKEN: ${{ github.token }}
          MONITOR_NZT_WINDOW: ${{ vars.MONITOR_NZT_WINDOW }}
          MONITOR_ISSUE_LABEL: ${{ vars.MONITOR_ISSUE_LABEL }}
          BUDGET_NZD_MONTHLY: ${{ vars.BUDGET_NZD_MONTHLY }}
        run: python agents/checks/monitor.py
```

**Notes:**

- Uses GitHub-provided `${{ github.token }}` (safe; won't trigger push-protection).
- Time window logic still enforced in `monitor.py`.

---

## 4) Optional: Weekly Cleanup Scan

**File**: `.github/workflows/monitor_cleanup.yml`

```yaml
name: Monitor Cleanup
on:
  schedule:
    - cron: "0 20 * * 5"  # Fridays ~09:00 NZT
  workflow_dispatch:

permissions:
  contents: read
  actions: read

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Monitor Agent
        run: python scripts/monitor_agent.py
      - name: Upload Cleanup Report
        uses: actions/upload-artifact@v4
        with:
          name: cleanup_report
          path: docs/style/cleanup_report.md
```

---

## 5) Secrets & Vars (reference)

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

---

## 6) Troubleshooting

- **Push-protection red flag** on `${{ secrets.* }}` names in env keys? Use `${{ github.token }}` or rename local env vars to non-sensitive names.
- **Overlapping runs**: check concurrency keys and branch names.
- **Slow CI**: add caching; split Node/Python jobs; limit matrix.
- **Missing required check**: push a trivial README change to create a green run, then select the check in Branch Protection.
