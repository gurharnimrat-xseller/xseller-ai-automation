# Claude Start Workflow Automation

This directory contains the automation script for running the `claude_start.yml` workflow.

## Files

- `run_claude_start.py` - Main automation script

## What it does

The `run_claude_start.py` script performs the following tasks:

1. **Triggers the workflow**: Runs `.github/workflows/claude_start.yml` on the main branch via `workflow_dispatch`
2. **Waits for completion**: Monitors the workflow until it completes
3. **Manages the tracking issue**: Finds or creates the issue titled "Start Claude M01 (auto)"
4. **Reports status**: Returns:
   - Workflow run URL
   - Link to the "Start Claude M01 (auto)" issue
   - The latest comment body posted on that issue
5. **Checks for PRs**: Searches for any PRs created today with titles containing:
   - `feat(scraper)`
   - `feat(rank)`
6. **Posts wake comment**: If no matching PRs are found, posts a standard wake comment to the issue instructing Claude to start M01

## Usage

### Method 1: Via GitHub Actions (Recommended)

The easiest way to run the automation is via the GitHub Actions workflow:

1. Go to the repository's **Actions** tab
2. Select **"Run Claude Start Automation"** workflow
3. Click **"Run workflow"** button
4. Select the branch (usually `main`)
5. Click **"Run workflow"**

The workflow will:
- Automatically trigger the `claude_start.yml` workflow
- Execute the Python automation script with proper authentication
- Display all results in the workflow logs

### Method 2: Running the script locally

For local execution or testing:

#### Prerequisites

- GitHub CLI (`gh`) must be installed and authenticated
- Must have permissions to trigger workflows and manage issues

#### Running the script

```bash
# From the repository root
python3 scripts/run_claude_start.py
```

The script will:
- Automatically trigger the workflow
- Wait for it to complete (up to 5 minutes)
- Create the issue if it doesn't exist
- Check for PRs and post the wake comment if needed
- Print a summary with all the required information

### Example Output

```
============================================================
Claude Start Workflow Automation
============================================================
🚀 Triggering claude_start.yml workflow...
✅ Workflow triggered successfully
📋 Workflow run ID: 12345678

⏳ Waiting for workflow 12345678 to complete...
   Status: in_progress... (waiting)
✅ Workflow completed with conclusion: success

🔍 Looking for issue: 'Start Claude M01 (auto)'
✅ Found existing issue #42 (state: open)

💬 Fetching latest comment from issue #42...
✅ Found latest comment (324 chars)

🔎 Checking for PRs created today with feat(scraper) or feat(rank)...
ℹ️  No PRs found today with feat(scraper) or feat(rank)

⚠️  No PRs found today - posting wake comment...
💬 Posting wake comment to issue #42...
✅ Wake comment posted successfully

============================================================
📊 SUMMARY
============================================================

🔗 Workflow Run URL:
   https://github.com/owner/repo/actions/runs/12345678

🔗 Issue URL (Start Claude M01 (auto)):
   https://github.com/owner/repo/issues/42

💬 Latest Comment Body:
────────────────────────────────────────────────────────────
@claude Start M01

Please review the current status...
────────────────────────────────────────────────────────────

📋 PRs Created Today: None (wake comment posted)

✅ Done!
```

## Workflow Files

### `.github/workflows/claude_start.yml`

The main workflow file that represents the "Claude Start" action:
- Can be triggered manually via `workflow_dispatch`
- Logs the start time and run URL
- Has permissions to read contents and write to issues
- Minimal workflow that serves as the trigger point

### `.github/workflows/run_claude_start.yml`

The automation orchestration workflow:
- Triggers the `claude_start.yml` workflow
- Runs the Python automation script
- Has proper authentication via `GITHUB_TOKEN`
- Performs all the required checks and actions
- **This is the workflow you should run** to execute the full automation

## Integration with Claude

This automation is designed to work with the Claude collaboration playbook (`.claude/claude.md`). The wake comment posted to the issue will trigger Claude to:

1. Check the Notion board for pending tasks
2. Review any open PRs
3. Continue with the next milestone deliverable
4. Update progress in Notion

## Troubleshooting

### Workflow not found
- Ensure `.github/workflows/claude_start.yml` exists and is on the main branch
- Check that the workflow name matches exactly

### Permission denied
- Ensure you're authenticated with `gh auth login`
- Check that you have permissions to trigger workflows and create issues

### Timeout errors
- The script waits up to 5 minutes for workflow completion
- If your workflow takes longer, increase the `timeout` parameter in `wait_for_workflow()`
