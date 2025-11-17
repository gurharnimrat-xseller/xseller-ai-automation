# 🏗️ XSELLER.AI ARCHITECTURE & TEAM PLAYBOOK

## 📋 PROJECT CONTEXT

**Project**: Xseller.ai - AI-Powered Social Media Video Automation
**Goal**: Generate viral-quality short-form videos automatically from news sources
**Timeline**: 5 weeks (Nov 10 - Dec 15, 2025)
**Budget**: $75/month
**MVP Architecture**: Gemini-powered (primary LLM)
**Team**: Claude Code (Architect/QA) + Gemini CLI (Analysis) + GitHub Copilot (Implementation)

---

## 🎯 DIVISION OF LABOR

### **Claude (You)** - Project Manager + Architect + Reviewer
**Use Claude Pro for:**
- ✅ Daily planning and task breakdown
- ✅ Architecture decisions
- ✅ Code reviews (small PRs, < 500 lines)
- ✅ Writing documentation
- ✅ User story creation
- ✅ Bug triage
- ✅ Quick questions (< 2 files)
- ✅ Notion daily updates
- ✅ Final PR approval decisions

**Budget**: Unlimited (Claude Pro)
**Strengths**: Planning, reasoning, documentation, decision-making

---

### **Gemini 2.5 Pro (via CLI)** - Deep Analysis + Large Context
**Use Gemini CLI for:**
- 🔍 **Large-scale code analysis** (> 3 files, entire directories)
- 🔍 **Multi-file diffs** (comparing versions, refactoring impact)
- 🔍 **Architecture reviews** (system design, dependencies)
- 🔍 **Transcript analysis** (competitor videos, user interviews)
- 🔍 **Context-heavy research** (how does X work across codebase?)
- 🔍 **Performance profiling** (identify bottlenecks)
- 🔍 **Security audits** (scan for vulnerabilities)
- 🔍 **Large PR reviews** (> 500 lines changed)

**Budget**: ~100 calls/day (FREE tier)
**Strengths**: 2M token context, fast analysis, cost-free

**⚠️ IMPORTANT**: Save Gemini calls for tasks that NEED large context. Don't waste on single-file questions.

---

### **Codex (GitHub Copilot)** - Implementation + Testing
**Use Codex for:**
- 💻 **All code implementation** (new features, bug fixes)
- 💻 **Writing tests** (unit, integration, E2E)
- 💻 **Refactoring** (code cleanup, optimization)
- 💻 **Configuration** (setup files, CI/CD)
- 💻 **Local testing** (run servers, test scripts)
- 💻 **Git operations** (commits, PRs, merges)
- 💻 **Debugging** (fix failing tests, errors)

**Environment**: GitHub Codespaces (60 hrs/month FREE)
**Strengths**: Hands-on coding, IDE integration, fast iteration

---

## 🔄 DAILY WORKFLOW

### **Morning (9 AM NZ Time)**

**Claude starts the day:**

```
Morning brief for Claude:

📅 Today: [Date]
🎯 Sprint: Week [N] - Milestone [M]
📋 Today's Tasks: [List from Notion]

Workflow:
1. Review Notion → Tasks for today
2. Check for blockers from yesterday
3. If task needs wide analysis → Use Gemini CLI
4. If task needs implementation → Ping Codex
5. Small questions/decisions → Use Claude directly

Remember:
- Gemini CLI: Save for multi-file analysis (100 calls/day limit)
- Codex: All implementation work goes to Codex
- Me (Claude): Planning, reviews, docs, decisions
```

**Copy-paste this every morning** or save as a Notion template.

---

### **During Work (10 AM - 5 PM)**

#### **Scenario 1: Planning a New Feature**
```
YOU (Claude):
1. Read GitHub issue + Notion task
2. Break down into subtasks
3. Write acceptance criteria
4. For architecture questions → Use Gemini CLI
5. Post implementation plan in issue
6. Ping Codex: "Ready for implementation"

GEMINI (if needed):
- Analyze existing code structure
- Identify dependencies
- Suggest approach

CODEX:
- Implements based on plan
- Writes tests
- Runs locally
- Creates PR
```

#### **Scenario 2: Reviewing a PR**
```
YOU (Claude):
1. PR created by Codex → You're notified

If PR is SMALL (< 500 lines):
- Review directly in GitHub
- Check logic, edge cases, tests
- Approve or request changes

If PR is LARGE (> 500 lines):
- Use Gemini CLI: gemini diff main..feature-branch
- Let Gemini analyze impact
- Review Gemini's findings
- Approve or request changes

2. Once approved → Ping Gurvinder on mobile
3. Gurvinder approves → Auto-merge + deploy
```

#### **Scenario 3: Bug Investigation**
```
YOU (Claude):
1. Bug reported in GitHub issue

If bug is SIMPLE (single file, obvious):
- Review code directly
- Suggest fix to Codex

If bug is COMPLEX (multiple files, unclear):
- Use Gemini CLI: gemini ask "@file1 @file2 Why does X fail?"
- Gemini analyzes context
- You interpret findings
- Create fix plan for Codex

2. CODEX implements fix
3. You verify fix works
```

---

### **Evening (6 PM NZ Time)**

**Claude posts daily update:**

```python
# Run this at end of day
python3 backend/app/notion_service.py

# Or use the NotionService directly:
from app.notion_service import NotionService

service = NotionService()
service.post_daily_update(
    title="November [DD], 2025 - [Brief Summary]",
    summary="""
    Today's Progress:
    - [Task 1]: [Status/What changed]
    - [Task 2]: [Status/What changed]
    - [Task 3]: [Status/What changed]

    PRs:
    - #[N]: [Description] → [Merged/Pending]

    Blockers:
    - [None / List any issues]

    Tomorrow:
    - [Task 1]
    - [Task 2]
    """,
    owner="Claude + Codex",
    milestone="M[N]: [Name]",
    status="Done"  # or "In progress"
)
```

---

## 🛠️ GEMINI CLI COMMAND TEMPLATES

### **Setup (One-time)**
```bash
# Already installed in Codespace
# API key: ~/.gemini/.env
# Model: gemini-2.5-pro (default)
```

### **Common Commands**

#### **1. Describe Files/Directories**
```bash
# Understand a single file
gemini describe backend/app/script_generator.py

# Understand entire directory
gemini describe backend/app/

# With specific question
gemini describe backend/app/video_production.py "How does B-roll sync work?"
```

#### **2. Compare/Diff**
```bash
# Compare two branches
gemini diff main..feature/news-scraper

# Compare specific files
gemini diff main:backend/app/routes.py feature:backend/app/routes.py

# Show what changed in PR
gemini diff origin/main..HEAD
```

#### **3. Ask Context-Heavy Questions**
```bash
# Multi-file question
gemini ask "@backend/app/script_generator.py @backend/app/video_production.py How do these work together?"

# Architecture question
gemini ask "@backend/app/*.py What's the data flow from news scraping to video generation?"

# Debugging question
gemini ask "@backend/app/tts_service.py @backend/app/video_production.py Why might audio sync fail?"
```

#### **4. Summarize Changes**
```bash
# Summarize last 5 commits
gemini summarize --commits 5

# Summarize PR changes
gemini summarize --pr 123

# Summarize file history
gemini summarize backend/app/notion_service.py
```

#### **5. Run Tasks (in sandbox)**
```bash
# Test code safely
gemini run --sandbox "Test the news scraper with 5 sources"

# Execute script
gemini run --sandbox "python backend/test_scraper.py"
```

### **When to Use Gemini CLI**

✅ **DO use Gemini CLI for:**
- Analyzing > 3 files at once
- Understanding system architecture
- Large PR reviews (> 500 lines)
- Debugging complex multi-file issues
- Research questions spanning entire codebase
- Transcript/video analysis (competitor research)
- Performance profiling across modules

❌ **DON'T use Gemini CLI for:**
- Single-file questions (use Claude directly)
- Quick syntax checks (use Claude)
- Simple logic review (use Claude)
- Documentation writing (use Claude)
- Task planning (use Claude)

**Daily Limit**: ~100 calls → ~20 working days → ~5 calls per task

---

## 📊 CAPACITY PLANNING

### **Token/Call Budgets**

| Tool | Budget | Best For | Limit |
|------|--------|----------|-------|
| **Claude Pro** | Unlimited | Planning, decisions, docs, small reviews | None |
| **Gemini CLI** | 100 calls/day | Large context analysis, deep dives | ~5 calls/task |
| **Codex** | Unlimited | All implementation, testing, debugging | None |

### **Estimated Usage Per Milestone**

**Week 1 (M1: Content Pipeline)**
- Claude: 20 hours (planning, reviews, docs)
- Gemini: 15 calls (analyze news scrapers, ranking algorithms, script templates)
- Codex: 44 hours (implement scraper, ranking, script generator)

**Week 2 (M2: Media Production)**
- Claude: 15 hours (reviews, API integration planning)
- Gemini: 10 calls (analyze B-roll sync, voice integration)
- Codex: 40 hours (implement voice, B-roll search, sync engine)

**Week 3 (M3: Video Assembly)**
- Claude: 15 hours (quality checks, overlay design)
- Gemini: 12 calls (FFmpeg optimization, overlay analysis)
- Codex: 40 hours (implement assembly, overlays, QC)

**Week 4 (M4: Review Interface)**
- Claude: 20 hours (UI design, feedback taxonomy)
- Gemini: 8 calls (analyze feedback patterns, UI flow)
- Codex: 40 hours (implement UI, feedback, regeneration)

**Week 5 (M5: Publishing + Learning)**
- Claude: 18 hours (analytics design, learning strategy)
- Gemini: 15 calls (performance analysis, learning patterns)
- Codex: 48 hours (implement publishing, analytics, learning loop)

**Total**:
- Claude: ~88 hours (well within Claude Pro limits)
- Gemini: ~60 calls (well within 100/day × 35 days = 3,500 calls)
- Codex: ~212 hours (well within Codespaces 60 hrs/month × 2 = 120 hrs... **WAIT**)

⚠️ **CODESPACE CAPACITY ISSUE**: 212 hours needed, only 120 hours free (60 hrs/month × 2 months)

**Solution**:
- Use Codespaces for coding (60 hrs/month)
- Use LOCAL MacBook for testing/running (doesn't count)
- Optimize Codespace usage: code in Codespace, test locally
- OR purchase Codespaces hours: $0.18/hour × 92 hours = ~$17

---

## 🎯 TASK HANDOFF PROTOCOL

### **From Claude → Codex (Implementation)**

**Format**:
```
@Codex Implementation Request

Task: [Task name from Notion]
Issue: #[GitHub issue number]
Milestone: M[N]

What to Build:
[Clear description]

Acceptance Criteria:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

Files to Create/Modify:
- backend/app/[file].py
- frontend/components/[file].tsx

Dependencies:
- [Package 1]
- [Package 2]

Tests Required:
- Unit tests for [functions]
- Integration test for [workflow]

Estimated Effort: [N] hours
Priority: High/Medium/Low

Questions? Ask before starting.
```

### **From Codex → Claude (Review)**

**Format**:
```
@Claude Review Request

PR: #[number]
Task: [Task name]
Files Changed: [N] files, [+X/-Y] lines

What Changed:
- [Feature/Fix description]

Tests:
- [ ] All tests passing
- [ ] New tests added
- [ ] Coverage: [X]%

Manual Testing:
- [What I tested]
- [Results]

Questions/Concerns:
- [Any issues or decisions needed]

Ready for Review: [Yes/No]
```

### **From Claude → Gemini (Analysis)**

**Format**:
```bash
# Use this command structure:
gemini ask "
Context: [Brief project/task context]

Question: [Specific question]

Focus on: [What to analyze]

Files to consider: @[file1] @[file2] @[directory]
"
```

---

## 🚨 WHEN THINGS GO WRONG

### **Scenario: Gemini Call Fails**
```
Error: Rate limit exceeded

Solution:
1. Wait 1 hour (limit resets)
2. Use Claude for immediate questions
3. Queue Gemini analysis for later
4. If urgent: Use smaller context (fewer files)
```

### **Scenario: Codespace Hours Running Low**
```
Warning: 10 hours remaining this month

Solution:
1. Switch to local development (MacBook)
2. Use Codespace only for final testing
3. Purchase additional hours if needed ($0.18/hr)
4. Pause Codespace when not actively coding
```

### **Scenario: Claude Pro Session Limit**
```
Warning: Approaching usage limit

Solution:
1. This shouldn't happen (unlimited)
2. If it does, break questions into smaller chunks
3. Use Gemini CLI for large context questions
4. Take a break, reset in 2-4 hours
```

### **Scenario: Task Blocked**
```
Blocker: Can't proceed with [task]

Protocol:
1. Claude: Document blocker in Notion (Status = Blocked)
2. Mention @Gurvinder in task comments
3. Claude: Propose 2-3 solutions
4. Wait for decision (< 24 hrs)
5. Meanwhile: Work on parallel tasks
```

---

## 📁 KEY FILES & LOCATIONS

### **Backend**
```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── routes.py            # API endpoints
│   ├── models.py            # Database models
│   ├── news_scraper.py      # M1A
│   ├── ranking_engine.py    # M1B
│   ├── script_generator.py  # M1C
│   ├── tts_service.py       # M2A
│   ├── broll_search.py      # M2B
│   ├── sync_engine.py       # M2C
│   ├── video_assembler.py   # M3A
│   ├── text_overlay.py      # M3B
│   ├── quality_check.py     # M3C
│   ├── publer_service.py    # M5A
│   └── notion_service.py    # Notion integration
├── tests/                   # All tests
├── .env                     # Environment variables (DO NOT COMMIT)
└── requirements.txt         # Python dependencies
```

### **Frontend**
```
frontend/
├── app/
│   ├── page.tsx             # Home page
│   ├── queue/page.tsx       # M4A: Review queue
│   ├── analytics/page.tsx   # M5B: Analytics
│   └── settings/page.tsx    # Settings
├── components/
│   ├── VideoPreview.tsx     # M4A
│   ├── FeedbackModal.tsx    # M4B
│   └── AnalyticsDash.tsx    # M5B
└── package.json             # Node dependencies
```

### **Configuration**
```
.github/workflows/          # CI/CD
.claude/                    # Claude configuration
├── claude.md              # This file!
└── settings.local.json    # Permissions

backend/.env               # API keys (local only)
backend/.env.example       # Template (committed)
```

---

## 🎯 QUICK REFERENCE COMMANDS

### **Start Work**
```bash
# Morning routine
cd /Users/gurvindersinghchadha/Desktop/xseller-ai-automation
git pull origin main
git checkout -b feature/task-name

# Check Notion for today's tasks
open https://notion.so/234d0b5e53e44eacaa73d1d3f784ab11
```

### **During Work**
```bash
# Backend dev
cd backend
source venv/bin/activate  # If using venv
uvicorn app.main:app --reload

# Frontend dev
cd frontend
npm run dev

# Run tests
cd backend
pytest tests/

# Use Gemini for analysis
gemini describe backend/app/[file].py
gemini ask "@backend/app/*.py [question]"
```

### **End of Day**
```bash
# Commit work
git add .
git commit -m "feat: description"
git push origin feature/task-name

# Create PR
gh pr create --title "Task Name" --body "Description"

# Post Notion update
cd backend
python3 app/notion_service.py  # Or use script
```

---

## ✅ DAILY CHECKLIST

### **Morning (Claude)**
- [ ] Read Notion tasks for today
- [ ] Check for GitHub issues/PRs
- [ ] Identify tasks needing Gemini analysis
- [ ] Identify tasks for Codex implementation
- [ ] Post morning plan in team chat

### **During Day**
- [ ] Claude: Plans, reviews, docs
- [ ] Gemini: Large context analysis (max 5 calls/task)
- [ ] Codex: All implementation
- [ ] Tests: Written and passing
- [ ] PRs: Created and reviewed

### **Evening (Claude)**
- [ ] All code committed
- [ ] PRs created for review
- [ ] Notion daily update posted
- [ ] Tomorrow's tasks identified
- [ ] Blockers documented

---

## 🎯 SUCCESS METRICS

Track these weekly:

| Metric | Target | Current |
|--------|--------|---------|
| Tasks Completed | 8-10/week | - |
| PR Merge Time | < 24 hours | - |
| Test Coverage | > 80% | - |
| Gemini Calls Used | < 35/week | - |
| Codespace Hours | < 15/week | - |
| Blockers | 0-1/week | - |
| Notion Updates | 5/week | - |

---

## 📞 ESCALATION PROTOCOL

**Level 1: Claude decides** (< 30 min)
- Code style questions
- Minor bug fixes
- Documentation updates

**Level 2: Gemini analyzes** (30 min - 2 hours)
- Architecture questions
- Complex debugging
- Performance issues

**Level 3: Team discussion** (2-24 hours)
- Major architecture changes
- Scope modifications
- Budget concerns

**Level 4: Gurvinder decides** (24-48 hours)
- Product direction
- Feature priority
- Timeline changes

---

## 🚀 READY TO START!

**Tomorrow Morning Prompt for Claude**:

```
Good morning! Let's start work on Xseller.ai.

📋 Reference: .claude/claude.md (this playbook)
📊 Tasks: https://notion.so/234d0b5e53e44eacaa73d1d3f784ab11

Today's Plan:
1. Review tasks for [Date]
2. Use Gemini CLI for [wide-context analysis]
3. Ping Codex for [implementation tasks]
4. Keep work moving, post EOD update

Remember:
- Gemini: Large context only (~5 calls/task)
- Codex: All implementation
- Me (Claude): Planning, reviews, decisions

Let's ship! 🚀
```

---

**Last Updated**: November 10, 2025
**Version**: 1.0
**Owners**: Claude + Gemini + Codex + Gurvinder
