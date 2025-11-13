# Quick Start: Claude Start Automation

## 🎯 What This Does

Automates the entire Claude Start workflow process:
- ✅ Triggers `claude_start.yml` workflow on main
- ✅ Returns workflow run URL
- ✅ Finds/creates "Start Claude M01 (auto)" issue
- ✅ Returns issue link and latest comment
- ✅ Checks for PRs today with `feat(scraper)` or `feat(rank)`
- ✅ Posts wake comment if no PRs exist

## 🚀 How to Run (2 Steps)

### Step 1: Go to Actions
Navigate to: **Actions → "Run Claude Start Automation"**

### Step 2: Run It
Click: **"Run workflow"** → Select **main** → Click **"Run workflow"**

## 📊 What You'll Get

The workflow will output:
```
🔗 Workflow Run URL:
   https://github.com/[owner]/[repo]/actions/runs/[id]

🔗 Issue URL (Start Claude M01 (auto)):
   https://github.com/[owner]/[repo]/issues/[number]

💬 Latest Comment Body:
   [Last comment text from the issue]

📋 PRs Created Today:
   [List of PRs with feat(scraper) or feat(rank)]
   OR
   None (wake comment posted)
```

## 📖 Full Documentation

- **User Guide**: [docs/CLAUDE_START_AUTOMATION.md](docs/CLAUDE_START_AUTOMATION.md)
- **Technical Docs**: [scripts/README_claude_start.md](scripts/README_claude_start.md)

## 🛠️ Files Created

| File | Purpose |
|------|---------|
| `.github/workflows/claude_start.yml` | Target workflow |
| `.github/workflows/run_claude_start.yml` | **Main workflow to run** |
| `scripts/run_claude_start.py` | Automation script |
| `scripts/test_claude_start.sh` | Validation script |
| `docs/CLAUDE_START_AUTOMATION.md` | Complete guide |

## ✅ Tested & Verified

- All validation checks pass
- CodeQL security scan: 0 issues
- YAML and Python syntax validated
- Documentation complete

---
**Ready to use!** Just go to Actions and run the workflow. 🎉
