# Pull Request: XSeller AI Guidelines Integration

**Branch:** docs/guidelines
**Author:** Claude Architect
**Reviewer:** Gurvinder (Owner)
**Status:** 🚀 Ready for Review

---

## 📦 Deliverables Added

| File | Description |
|------|--------------|
| `docs/style/XSeller_Guidelines.md` | Full coding & orchestration guide |
| `docs/style/python_router.md` | Core LLM router with offload logic |
| `docs/style/python_retry_backoff.md` | Retry + backoff resilience pattern |
| `docs/style/ts_zod_api.md` | Frontend schema validation via Zod |
| `docs/style/actions_least_privilege.md` | Secure CI/CD workflows |
| `docs/style/quick_start.md` | Setup guide & checklist |
| `docs/style/xseller_architecture.png` | Architecture diagram |
| `docs/style/PR_BODY.md` | PR template for documentation update |

---

## 🧭 4 Tracks Summary

| Track | Focus | Enforcement |
|--------|--------|-------------|
| Code Style | Ruff/mypy (Python), ESLint/Prettier (TS) | CI lint jobs |
| Stack-Specific | Python 3.11 + Next.js TS | Verified via guardrails |
| AI/LLM Agents | Router pattern + cost budget | Guardrails + Monitor |
| API Patterns | Retry, Idempotency, Circuit breaker | Test fixtures |

---

## 🧩 Repository Integrations

- **Router Enforced:** All AI calls through `agents.checks.router`
- **Guardrails Active:** Verifies imports, types, naming
- **Offload Logic:** >12K tokens or >90s auto-routed to Gemini
- **Budget Enforcement:** NZD 20/month; pause on breach
- **Monitoring:** Daily Summary in 05:00–10:00 NZT window
- **Branch Protection:** Requires "Guardrails / scan" check

---

## ✅ Acceptance Checklist

- [ ] All 7 files added to `docs/style/`
- [ ] Diagram verified present
- [ ] CI workflows lint + test pass
- [ ] Guardrails / scan passes
- [ ] No direct SDK imports in repo
- [ ] All paths unchanged; no renames
- [ ] PR reviewers assigned
- [ ] README badges visible
- [ ] Monitor posting daily

---

## 🧠 Risk & Test Plan

| Area | Risk | Mitigation |
|------|------|-------------|
| Router Enforcement | Missing import breaks build | Guardrails fail PR |
| Workflow Secrets | Hardcoded keys | Push-protection + CI scan |
| Budget Limits | API overrun | Monitor pause trigger |
| Documentation Drift | Style mismatch | Weekly cleanup workflow |
| Token Overload | Long prompts | Router offload to Gemini |

**Tests to Run**
1. Run guardrails locally → `python agents/checks/verify_guardrails.py`
2. Trigger monitor manually via `workflow_dispatch`
3. Simulate heavy prompt → confirm offload logs in `docs/LAST_OFFLOAD.json`
4. Merge dummy PR → ensure Monitor issue posts at 09 AM NZT

---

## 📈 Deployment Plan

1. Merge this PR → main
2. Verify all GitHub Actions run green
3. Confirm Daily Monitor Issue created next NZT cycle
4. Tag release `v1.0-guidelines`

---

🧾 **Summary**
This PR finalizes the documentation, guardrails, and CI workflows aligned with XSeller's enterprise-grade automation plan.
Once merged, all contributors and agents will operate under unified style, performance, and cost guardrails — ready for Phase 2 scaling.
