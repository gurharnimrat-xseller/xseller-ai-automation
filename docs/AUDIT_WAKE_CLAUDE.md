# Audit & Wake Claude MO1 System

This system automatically audits Claude MO1 activity and wakes Claude if needed.

## Overview

The system performs three main functions:

### A) Audit Last Night (NZT)
1. **Workflow Check**: Finds the latest run of "Start Claude MO1" workflow
   - Reports: time, status, run URL
2. **Control Issue**: Finds or creates issue titled "Start Claude MO1 (auto)"
   - Reports: timestamp of most recent comment
3. **PR Search**: Searches Pull Requests created since today 00:00 NZT whose titles include:
   - `feat(scraper)` or `feat(rank)` or `M01`
   - Reports: PR number, title, status, Guardrails check result

### B) Wake Claude If Needed
Claude is woken if ANY of these conditions are met:
- Workflow didn't run since 00:00 NZT
- Issue has no new comment since 00:00 NZT  
- No M01 PRs found since 00:00 NZT

When waking Claude, the system:
1. Dispatches the "Start Claude MO1" workflow on main
2. Posts a wake comment to the control issue with instructions

### C) Final Report
The script outputs a comprehensive report with:
- ✅ Night audit results (run time/status + URL)
- ✅ Control issue link + last comment time
- ✅ PRs since 00:00 NZT (list with Guardrails status)
- ▶️ Action taken (none | dispatched workflow | posted wake comment | both)
- 🔗 All relevant links

## Usage

### Automatic (Scheduled)
The audit runs automatically daily at 01:00 AM NZT via the `Audit Claude MO1` workflow.

### Manual Trigger
You can manually trigger the audit:

```bash
# Via GitHub CLI
gh workflow run audit_claude.yml

# Via GitHub UI
Go to Actions → Audit Claude MO1 → Run workflow
```

### Local Testing
To test the script locally:

```bash
# Set GH_TOKEN environment variable
export GH_TOKEN="your-github-token"

# Run the script
python3 agents/checks/audit_wake_claude.py
```

## Files

- `agents/checks/audit_wake_claude.py` - Main audit script
- `.github/workflows/start_claude_mo1.yml` - Claude MO1 trigger workflow
- `.github/workflows/audit_claude.yml` - Scheduled audit workflow

## Wake Comment Template

The system posts this message when waking Claude:

```
🧠 Claude — please start MO1 now (News Scraper + Ranking Engine):
• Follow /docs/style/XSeller_Guidelines.md and the router-only rule.
• Use agents/checks/router.py for all AI/API calls (no direct SDK imports).
• Respect cost caps (≤ NZD 20/mo) and offload threshold (≥12k tokens or ≥90s).
• Open PRs:
  - feat(scraper): M01A news fetch (sources + filters + tests)
  - feat(rank):   M01B ranking engine (scoring + tests)
• Ensure "Guardrails / scan" passes and CI is green.
• Reply with PR links and next steps.
```

## Timezone

All times are in New Zealand Time (NZT/Pacific/Auckland). The system:
- Checks activity since midnight (00:00) NZT
- Converts to UTC for GitHub API queries
- Reports times in both NZT and UTC for clarity

## Permissions Required

The workflows need these GitHub permissions:
- `contents: read` - Read repository files
- `issues: write` - Create/comment on issues
- `pull-requests: read` - Read PR data
- `actions: write` - Dispatch workflows and read workflow runs

## Monitoring

Check the audit results in:
1. **GitHub Actions**: View workflow run logs
2. **Control Issue**: See all audit reports and wake comments at issue "Start Claude MO1 (auto)"
3. **Workflow Runs**: Check "Start Claude MO1" workflow history

## Troubleshooting

### Script fails to find workflow
- Ensure `start_claude_mo1.yml` exists in `.github/workflows/`
- Check workflow has run at least once

### Script can't create issue
- Verify workflow has `issues: write` permission
- Check repository allows issue creation

### PR search returns no results
- Verify PR titles match the search patterns
- Check PRs were created after midnight NZT (not UTC)

### Workflow dispatch fails
- Ensure workflow has `actions: write` permission
- Verify workflow exists and is enabled
