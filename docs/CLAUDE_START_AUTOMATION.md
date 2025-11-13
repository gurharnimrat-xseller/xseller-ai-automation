# Claude Start Workflow Automation

This document describes the automated workflow system for triggering and monitoring Claude automation tasks.

## Overview

The Claude Start automation system provides a complete solution for:

1. **Triggering workflows** - Run the `claude_start.yml` workflow via `workflow_dispatch`
2. **Monitoring execution** - Wait for workflow completion and retrieve status
3. **Issue management** - Automatically create/find the tracking issue "Start Claude M01 (auto)"
4. **PR detection** - Check for new pull requests with specific feature tags
5. **Automated notifications** - Post wake comments when no recent work is detected

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│ User triggers via GitHub Actions UI                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ run_claude_start.yml (Orchestrator)                     │
│ - Provides authentication                               │
│ - Runs Python script                                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ scripts/run_claude_start.py (Automation Logic)          │
│                                                          │
│ 1. Trigger claude_start.yml ────────┐                   │
│ 2. Wait for completion              │                   │
│ 3. Find/create tracking issue       │                   │
│ 4. Get latest comment               ├─► GitHub API      │
│ 5. Check for new PRs today          │                   │
│ 6. Post wake comment if needed      │                   │
└────────────────┬────────────────────┴───────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ claude_start.yml (Target Workflow)                      │
│ - Logs execution                                        │
│ - Serves as automation trigger point                   │
└─────────────────────────────────────────────────────────┘
```

## Usage

### Quick Start

1. **Navigate to Actions tab** in GitHub
2. **Select** "Run Claude Start Automation" workflow
3. **Click** "Run workflow"
4. **Select** the `main` branch
5. **Click** "Run workflow" to start

### What Happens Next

The automation will:

1. ✅ Trigger the `claude_start.yml` workflow
2. ✅ Wait for it to complete (up to 5 minutes)
3. ✅ Display the workflow run URL
4. ✅ Find or create the "Start Claude M01 (auto)" issue
5. ✅ Display the issue URL
6. ✅ Show the latest comment from the issue (if any)
7. ✅ Search for PRs created today with titles containing:
   - `feat(scraper)`
   - `feat(rank)`
8. ✅ If no matching PRs are found:
   - Post a wake comment to the issue
   - Confirm successful posting

### Expected Output

```
============================================================
Claude Start Workflow Automation
============================================================
🚀 Triggering claude_start.yml workflow...
✅ Workflow triggered successfully
📋 Workflow run ID: 123456789

⏳ Waiting for workflow 123456789 to complete...
✅ Workflow completed with conclusion: success

🔍 Looking for issue: 'Start Claude M01 (auto)'
✅ Found existing issue #42 (state: open)

💬 Fetching latest comment from issue #42...
✅ Found latest comment (324 chars)

🔎 Checking for PRs created today with feat(scraper) or feat(rank)...
✅ Found 2 PR(s) created today:
   - PR #45: feat(scraper): Add NewsAPI integration
     URL: https://github.com/owner/repo/pull/45
   - PR #46: feat(rank): Implement engagement scoring
     URL: https://github.com/owner/repo/pull/46

✅ Found 2 PR(s) today - skipping wake comment

============================================================
📊 SUMMARY
============================================================

🔗 Workflow Run URL:
   https://github.com/owner/repo/actions/runs/123456789

🔗 Issue URL (Start Claude M01 (auto)):
   https://github.com/owner/repo/issues/42

💬 Latest Comment Body:
────────────────────────────────────────────────────────────
@claude Start M01

Please review the current status and proceed...
────────────────────────────────────────────────────────────

📋 PRs Created Today:
   - feat(scraper): Add NewsAPI integration
     https://github.com/owner/repo/pull/45
   - feat(rank): Implement engagement scoring
     https://github.com/owner/repo/pull/46

✅ Done!
```

## The Wake Comment

When no PRs with `feat(scraper)` or `feat(rank)` are found today, the automation posts this comment to wake Claude:

```markdown
@claude Start M01

Please review the current status and proceed with M01 tasks:

1. Check the Notion board for pending tasks
2. Review any open PRs
3. Continue with the next milestone deliverable
4. Update progress in Notion

Remember to follow the collaboration playbook in `.claude/claude.md`.
```

This comment:
- Tags Claude to trigger the Claude Code action
- References M01 (Milestone 1) tasks
- Provides clear next steps
- Links to the collaboration playbook

## Integration with Claude Playbook

This automation integrates with the Claude collaboration system described in `.claude/claude.md`:

- **Daily workflow**: Run this automation each morning to check for work
- **Task tracking**: Uses the "Start Claude M01 (auto)" issue for coordination
- **PR detection**: Monitors for feature work on scraper and ranking systems
- **Wake mechanism**: Automatically prompts Claude when no recent activity detected

## Files Reference

| File | Purpose |
|------|---------|
| `.github/workflows/claude_start.yml` | Target workflow that gets triggered |
| `.github/workflows/run_claude_start.yml` | Orchestrator workflow you run |
| `scripts/run_claude_start.py` | Main automation logic |
| `scripts/test_claude_start.sh` | Validation and testing script |
| `scripts/README_claude_start.md` | Detailed technical documentation |

## Troubleshooting

### Workflow not found
**Problem**: Error finding `claude_start.yml` workflow

**Solution**: 
- Ensure the workflow file exists in `.github/workflows/`
- Check that you're on the correct branch (usually `main`)
- Verify the workflow name matches exactly

### Authentication errors
**Problem**: GitHub API calls fail with permission errors

**Solution**:
- Use the `run_claude_start.yml` workflow (has built-in authentication)
- If running locally, ensure `gh auth login` is completed
- Check that the token has `repo` and `workflow` scopes

### Issue not found/created
**Problem**: Can't find or create the tracking issue

**Solution**:
- Check repository permissions (need `issues: write`)
- Verify you have access to create issues
- Look for the issue manually in the Issues tab

### No PRs detected
**Problem**: PRs exist but aren't being found

**Solution**:
- Check PR title format (must contain exact string `feat(scraper)` or `feat(rank)`)
- Verify PRs were created today (uses UTC timezone)
- Check that PRs aren't in a draft state

## Advanced Usage

### Running Locally

For development or testing:

```bash
# Authenticate with GitHub CLI
gh auth login

# Run the script
cd /path/to/xseller-ai-automation
python3 scripts/run_claude_start.py
```

### Customizing the Wake Comment

To modify the wake comment, edit `scripts/run_claude_start.py`:

```python
def post_wake_comment(issue_number: int) -> None:
    """Post the standard wake comment to the issue."""
    wake_comment = """@claude Start M01

Your custom message here...
"""
    # ... rest of function
```

### Adjusting Timeout

If workflows take longer than 5 minutes, increase the timeout:

```python
# In run_claude_start.py
def wait_for_workflow(run_id: str, timeout: int = 300):  # Change 300 to your value
    # ...
```

## Security Summary

✅ **No security vulnerabilities detected** by CodeQL scanner

- Script uses subprocess safely with proper error handling
- No credentials stored in code
- Uses GitHub's official authentication mechanisms
- All GitHub API calls go through the official GitHub CLI

## Maintenance

### Regular Checks

- **Weekly**: Verify the workflow still runs successfully
- **Monthly**: Check for GitHub CLI updates
- **As needed**: Update PR search criteria if new feature prefixes are added

### Monitoring

Check these indicators of health:

1. Workflow run history in Actions tab
2. Comments on the tracking issue
3. PR detection accuracy
4. Wake comment posting frequency

## Related Documentation

- [Claude Collaboration Playbook](./.claude/claude.md)
- [Technical Documentation](./scripts/README_claude_start.md)
- [Repository Workflows](../.github/workflows/README.md)

---

**Last Updated**: 2025-11-12  
**Version**: 1.0  
**Maintainer**: Claude + GitHub Copilot
