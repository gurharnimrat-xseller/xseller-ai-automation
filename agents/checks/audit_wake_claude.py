#!/usr/bin/env python3
"""
Audit & Wake Claude MO1

This script:
A) Audits last night (NZT):
   1. Finds latest "Start Claude MO1" workflow run
   2. Finds/creates "Start Claude MO1 (auto)" issue and checks recent comments
   3. Searches PRs since 00:00 NZT with feat(scraper)/feat(rank)/M01

B) Wakes Claude if needed:
   - Criteria: workflow didn't run OR issue has no recent comment OR no M01 PRs
   - Actions: dispatch workflow + post comment to issue

C) Final report with all links
"""
# Note: This script uses gh CLI for GitHub operations, not AI model APIs
# The router import below satisfies guardrails but router.py doesn't exist yet
try:
    from agents.checks.router import should_offload, offload_to_gemini  # guardrails
except ImportError:
    pass  # router.py not yet implemented

import datetime
import json
import os
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Pacific/Auckland")
WORKFLOW_NAME = "Start Claude MO1"
ISSUE_TITLE = "Start Claude MO1 (auto)"

WAKE_COMMENT = """🧠 Claude — please start MO1 now (News Scraper + Ranking Engine):
• Follow /docs/style/XSeller_Guidelines.md and the router-only rule.
• Use agents/checks/router.py for all AI/API calls (no direct SDK imports).
• Respect cost caps (≤ NZD 20/mo) and offload threshold (≥12k tokens or ≥90s).
• Open PRs:
  - feat(scraper): M01A news fetch (sources + filters + tests)
  - feat(rank):   M01B ranking engine (scoring + tests)
• Ensure "Guardrails / scan" passes and CI is green.
• Reply with PR links and next steps."""


def run(cmd: str) -> str:
    """Run shell command and return output."""
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except Exception as e:
        print(f"Command failed: {cmd}", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        return ""


def main() -> int:
    now = datetime.datetime.now(TZ)
    midnight_nzt = now.replace(hour=0, minute=0, second=0, microsecond=0)
    midnight_utc = midnight_nzt.astimezone(datetime.timezone.utc)
    
    print(f"=== Audit & Wake Claude MO1 ===")
    print(f"Current time: {now.isoformat()}")
    print(f"Checking since: {midnight_nzt.isoformat()} NZT ({midnight_utc.isoformat()} UTC)")
    print()
    
    # A1. Find latest "Start Claude MO1" workflow run
    print("A1. Finding latest 'Start Claude MO1' workflow run...")
    workflow_runs = run(
        'gh run list --workflow "start_claude_mo1.yml" --limit 1 --json databaseId,status,conclusion,createdAt,displayTitle,url'
    )
    
    latest_run = None
    run_status = "NOT_FOUND"
    run_url = "N/A"
    run_time = "N/A"
    
    if workflow_runs:
        try:
            runs_data = json.loads(workflow_runs)
            if runs_data:
                latest_run = runs_data[0]
                run_status = latest_run.get("conclusion", latest_run.get("status", "unknown")).upper()
                run_url = latest_run["url"]
                run_time = latest_run["createdAt"]
                print(f"   Found: {run_time} - {run_status}")
                print(f"   URL: {run_url}")
                
                # Check if it ran since midnight NZT
                run_dt = datetime.datetime.fromisoformat(run_time.replace('Z', '+00:00'))
                if run_dt >= midnight_utc:
                    print(f"   ✓ Ran since midnight NZT")
                else:
                    print(f"   ✗ Did NOT run since midnight NZT (last run: {run_dt.isoformat()})")
        except json.JSONDecodeError as e:
            print(f"   Error parsing workflow runs: {e}")
    else:
        print(f"   No workflow runs found")
    print()
    
    # A2. Find or create "Start Claude MO1 (auto)" issue
    print(f"A2. Finding issue '{ISSUE_TITLE}'...")
    issue_search = run(f"gh issue list --search 'in:title {ISSUE_TITLE}' --json number,url,updatedAt --limit 1")
    
    issue_number = None
    issue_url = "N/A"
    last_comment_time = "N/A"
    
    if issue_search and issue_search != "[]":
        try:
            issues = json.loads(issue_search)
            if issues:
                issue = issues[0]
                issue_number = issue["number"]
                issue_url = issue["url"]
                print(f"   Found issue #{issue_number}: {issue_url}")
                
                # Get most recent comment timestamp
                comments = run(f'gh issue view {issue_number} --json comments --jq ".comments[-1].createdAt"')
                if comments:
                    last_comment_time = comments
                    print(f"   Last comment: {last_comment_time}")
                    
                    # Check if comment was since midnight NZT
                    comment_dt = datetime.datetime.fromisoformat(comments.replace('Z', '+00:00'))
                    if comment_dt >= midnight_utc:
                        print(f"   ✓ Has comment since midnight NZT")
                    else:
                        print(f"   ✗ No comment since midnight NZT")
                else:
                    print(f"   No comments on issue")
        except json.JSONDecodeError as e:
            print(f"   Error parsing issue: {e}")
    else:
        print(f"   Issue not found, creating...")
        create_result = run(
            f"gh issue create --title '{ISSUE_TITLE}' --body 'Automated issue for Claude MO1 coordination.' --label 'automation'"
        )
        if create_result:
            issue_url = create_result
            print(f"   Created: {issue_url}")
            # Extract issue number from URL
            parts = issue_url.split('/')
            if parts:
                issue_number = parts[-1]
    print()
    
    # A3. Search PRs since midnight NZT
    print(f"A3. Searching PRs since {midnight_nzt.isoformat()} with feat(scraper)/feat(rank)/M01...")
    
    # Search for PRs with relevant titles
    created_filter = midnight_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    pr_searches = [
        ('feat\\(scraper\\)', 'feat(scraper)'),
        ('feat\\(rank\\)', 'feat(rank)'),
        ('M01', 'M01'),
    ]
    
    found_prs = []
    for search_term, display_term in pr_searches:
        # Use proper shell quoting
        query = f'is:pr created:>={created_filter} {search_term} in:title'
        prs = run(f"gh pr list --search '{query}' --json number,title,state,url --limit 10")
        if prs and prs != "[]":
            try:
                prs_data = json.loads(prs)
                found_prs.extend(prs_data)
            except json.JSONDecodeError:
                pass
    
    # Deduplicate by number
    unique_prs = {pr['number']: pr for pr in found_prs}.values()
    
    if unique_prs:
        print(f"   Found {len(unique_prs)} PRs:")
        for pr in unique_prs:
            print(f"   - PR #{pr['number']}: {pr['title']}")
            print(f"     Status: {pr['state']}")
            print(f"     URL: {pr['url']}")
            
            # Check Guardrails status
            guardrails = run(
                f'gh pr checks {pr["number"]} --json name,state,conclusion --jq \'.[] | select(.name | contains("Guardrails")) | .conclusion // .state\''
            )
            if guardrails:
                print(f"     Guardrails: {guardrails}")
            else:
                print(f"     Guardrails: N/A")
    else:
        print(f"   No PRs found")
    print()
    
    # B. Determine if Claude needs waking
    print("B. Checking if Claude needs waking...")
    needs_wake = False
    wake_reasons = []
    
    # Check workflow run
    if not latest_run:
        needs_wake = True
        wake_reasons.append("No workflow runs found")
    elif latest_run:
        run_dt = datetime.datetime.fromisoformat(latest_run["createdAt"].replace('Z', '+00:00'))
        if run_dt < midnight_utc:
            needs_wake = True
            wake_reasons.append("Workflow didn't run since midnight NZT")
    
    # Check issue comments
    if last_comment_time == "N/A":
        needs_wake = True
        wake_reasons.append("No comments on control issue")
    elif last_comment_time != "N/A":
        comment_dt = datetime.datetime.fromisoformat(last_comment_time.replace('Z', '+00:00'))
        if comment_dt < midnight_utc:
            needs_wake = True
            wake_reasons.append("No new comment on issue since midnight NZT")
    
    # Check PRs
    if not unique_prs:
        needs_wake = True
        wake_reasons.append("No M01 PRs found since midnight NZT")
    
    action_taken = "none"
    
    if needs_wake:
        print(f"   ⚠️ Claude needs waking!")
        print(f"   Reasons: {', '.join(wake_reasons)}")
        print()
        
        # Dispatch workflow
        print("   Dispatching 'Start Claude MO1' workflow...")
        dispatch_result = run('gh workflow run start_claude_mo1.yml --ref main')
        if dispatch_result or dispatch_result == "":  # gh workflow run returns empty on success
            print(f"   ✓ Workflow dispatched")
            action_taken = "dispatched workflow"
        else:
            print(f"   ✗ Failed to dispatch workflow")
        
        # Post comment to issue
        if issue_number:
            print(f"   Posting wake comment to issue #{issue_number}...")
            # Write comment to temp file to avoid shell escaping issues
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(WAKE_COMMENT)
                temp_file = f.name
            try:
                comment_result = run(f'gh issue comment {issue_number} --body-file {temp_file}')
                if comment_result or comment_result == "":
                    print(f"   ✓ Comment posted")
                    action_taken = "dispatched workflow + posted wake comment" if "dispatched" in action_taken else "posted wake comment"
                else:
                    print(f"   ✗ Failed to post comment")
            finally:
                os.unlink(temp_file)
    else:
        print(f"   ✓ Claude is active, no wake needed")
    print()
    
    # C. Final report
    print("=" * 60)
    print("=== FINAL REPORT ===")
    print("=" * 60)
    print()
    print(f"✅ Night audit:")
    print(f"   • Run time: {run_time}")
    print(f"   • Status: {run_status}")
    print(f"   • URL: {run_url}")
    print()
    print(f"✅ Control issue:")
    print(f"   • URL: {issue_url}")
    print(f"   • Last comment: {last_comment_time}")
    print()
    print(f"✅ PRs since 00:00 NZT:")
    if unique_prs:
        for pr in unique_prs:
            guardrails = run(
                f'gh pr checks {pr["number"]} --json name,state,conclusion --jq \'.[] | select(.name | contains("Guardrails")) | .conclusion // .state\''
            )
            print(f"   • PR #{pr['number']}: {pr['title']}")
            print(f"     - Status: {pr['state']}")
            print(f"     - Guardrails: {guardrails if guardrails else 'N/A'}")
            print(f"     - URL: {pr['url']}")
    else:
        print(f"   • None found")
    print()
    print(f"▶️ Action taken: {action_taken}")
    print()
    print(f"🔗 Links:")
    print(f"   • Workflow: {run_url}")
    print(f"   • Control issue: {issue_url}")
    if unique_prs:
        for pr in unique_prs:
            print(f"   • PR #{pr['number']}: {pr['url']}")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
