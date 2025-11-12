#!/usr/bin/env python3
"""
Script to run claude_start.yml workflow and perform required checks.

This script:
1. Triggers the claude_start.yml workflow via workflow_dispatch
2. Waits for the workflow to complete
3. Finds or creates the "Start Claude M01 (auto)" issue
4. Returns workflow run URL and latest comment from the issue
5. Checks for new PRs today with feat(scraper) or feat(rank) in titles
6. Posts wake comment to the issue if no PRs exist
"""
from agents.checks.router import should_offload, offload_to_gemini  # guardrails

import sys
import time
import json
import subprocess
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any


def run_command(cmd: List[str]) -> str:
    """Run a command and return its output."""
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def trigger_workflow() -> str:
    """Trigger the claude_start.yml workflow and return the run ID."""
    print("🚀 Triggering claude_start.yml workflow...")
    
    # Trigger workflow dispatch
    cmd = [
        "gh", "workflow", "run", "claude_start.yml",
        "--ref", "main"
    ]
    
    try:
        run_command(cmd)
        print("✅ Workflow triggered successfully")
        
        # Wait a moment for the workflow to appear
        time.sleep(5)
        
        # Get the latest run ID
        cmd = [
            "gh", "run", "list",
            "--workflow=claude_start.yml",
            "--limit", "1",
            "--json", "databaseId,status,conclusion,createdAt"
        ]
        
        output = run_command(cmd)
        runs = json.loads(output)
        
        if runs:
            run_id = runs[0]["databaseId"]
            print(f"📋 Workflow run ID: {run_id}")
            return str(run_id)
        else:
            raise Exception("Could not find workflow run")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error triggering workflow: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)


def wait_for_workflow(run_id: str, timeout: int = 300) -> Dict[str, Any]:
    """Wait for workflow to complete and return its info."""
    print(f"⏳ Waiting for workflow {run_id} to complete...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        cmd = [
            "gh", "run", "view", run_id,
            "--json", "status,conclusion,url,createdAt"
        ]
        
        try:
            output = run_command(cmd)
            run_info = json.loads(output)
            
            status = run_info.get("status", "")
            conclusion = run_info.get("conclusion", "")
            
            if status == "completed":
                print(f"✅ Workflow completed with conclusion: {conclusion}")
                return run_info
            
            print(f"   Status: {status}... (waiting)")
            time.sleep(10)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error checking workflow status: {e}")
            time.sleep(10)
    
    raise TimeoutError(f"Workflow did not complete within {timeout} seconds")


def find_or_create_issue() -> int:
    """Find or create the 'Start Claude M01 (auto)' issue and return its number."""
    issue_title = "Start Claude M01 (auto)"
    
    print(f"\n🔍 Looking for issue: '{issue_title}'")
    
    # Search for existing issue
    cmd = [
        "gh", "issue", "list",
        "--search", f"is:issue '{issue_title}'",
        "--json", "number,title,state",
        "--limit", "10"
    ]
    
    try:
        output = run_command(cmd)
        issues = json.loads(output)
        
        # Look for exact match
        for issue in issues:
            if issue["title"] == issue_title:
                issue_number = issue["number"]
                state = issue["state"]
                print(f"✅ Found existing issue #{issue_number} (state: {state})")
                return issue_number
        
        # If not found, create it
        print(f"📝 Issue not found. Creating new issue...")
        cmd = [
            "gh", "issue", "create",
            "--title", issue_title,
            "--body", (
                "This issue is used to track Claude M01 automation tasks.\n\n"
                "The automation system will post wake comments here to start Claude when needed."
            )
        ]
        
        output = run_command(cmd)
        # Output is the issue URL
        issue_number = int(output.split("/")[-1])
        print(f"✅ Created issue #{issue_number}")
        return issue_number
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error finding/creating issue: {e}")
        sys.exit(1)


def get_latest_comment(issue_number: int) -> Optional[str]:
    """Get the latest comment body from the issue."""
    print(f"\n💬 Fetching latest comment from issue #{issue_number}...")
    
    cmd = [
        "gh", "issue", "view", str(issue_number),
        "--json", "comments",
        "--jq", ".comments | sort_by(.createdAt) | reverse | .[0].body"
    ]
    
    try:
        output = run_command(cmd)
        if output and output != "null":
            print(f"✅ Found latest comment ({len(output)} chars)")
            return output
        else:
            print("ℹ️  No comments found on this issue")
            return None
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not fetch comments: {e}")
        return None


def check_prs_today() -> List[Dict[str, Any]]:
    """Check for PRs created today with feat(scraper) or feat(rank) in titles."""
    print("\n🔎 Checking for PRs created today with feat(scraper) or feat(rank)...")
    
    # Get today's date in ISO format
    today = datetime.now(timezone.utc).date()
    
    # Search for PRs with feat(scraper) or feat(rank)
    searches = ["feat(scraper)", "feat(rank)"]
    all_prs = []
    
    for search_term in searches:
        cmd = [
            "gh", "pr", "list",
            "--search", f"is:pr {search_term}",
            "--json", "number,title,url,createdAt",
            "--limit", "50"
        ]
        
        try:
            output = run_command(cmd)
            prs = json.loads(output)
            
            # Filter to only today's PRs
            for pr in prs:
                created_at = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
                if created_at.date() == today:
                    pr["search_term"] = search_term
                    all_prs.append(pr)
                    
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Error searching for '{search_term}': {e}")
    
    if all_prs:
        print(f"✅ Found {len(all_prs)} PR(s) created today:")
        for pr in all_prs:
            print(f"   - PR #{pr['number']}: {pr['title']}")
            print(f"     URL: {pr['url']}")
    else:
        print("ℹ️  No PRs found today with feat(scraper) or feat(rank)")
    
    return all_prs


def post_wake_comment(issue_number: int) -> None:
    """Post the standard wake comment to the issue."""
    print(f"\n💬 Posting wake comment to issue #{issue_number}...")
    
    wake_comment = """@claude Start M01

Please review the current status and proceed with M01 tasks:

1. Check the Notion board for pending tasks
2. Review any open PRs
3. Continue with the next milestone deliverable
4. Update progress in Notion

Remember to follow the collaboration playbook in `.claude/claude.md`.
"""
    
    cmd = [
        "gh", "issue", "comment", str(issue_number),
        "--body", wake_comment
    ]
    
    try:
        run_command(cmd)
        print("✅ Wake comment posted successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error posting comment: {e}")
        sys.exit(1)


def main():
    """Main function to orchestrate the workflow."""
    print("=" * 60)
    print("Claude Start Workflow Automation")
    print("=" * 60)
    
    # Step 1: Trigger workflow
    run_id = trigger_workflow()
    
    # Step 2: Wait for completion
    run_info = wait_for_workflow(run_id)
    workflow_url = run_info["url"]
    
    # Step 3: Find or create issue
    issue_number = find_or_create_issue()
    
    # Get repository info
    repo_info = run_command(["gh", "repo", "view", "--json", "nameWithOwner"])
    repo = json.loads(repo_info)["nameWithOwner"]
    issue_url = f"https://github.com/{repo}/issues/{issue_number}"
    
    # Step 4: Get latest comment
    latest_comment = get_latest_comment(issue_number)
    
    # Step 5: Check for PRs today
    prs_today = check_prs_today()
    
    # Step 6: Post wake comment if no PRs
    if not prs_today:
        print("\n⚠️  No PRs found today - posting wake comment...")
        post_wake_comment(issue_number)
    else:
        print(f"\n✅ Found {len(prs_today)} PR(s) today - skipping wake comment")
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"\n🔗 Workflow Run URL:")
    print(f"   {workflow_url}")
    print(f"\n🔗 Issue URL (Start Claude M01 (auto)):")
    print(f"   {issue_url}")
    
    if latest_comment:
        print(f"\n💬 Latest Comment Body:")
        print("─" * 60)
        print(latest_comment)
        print("─" * 60)
    else:
        print(f"\n💬 Latest Comment Body: None")
    
    if prs_today:
        print(f"\n📋 PRs Created Today:")
        for pr in prs_today:
            print(f"   - {pr['title']}")
            print(f"     {pr['url']}")
    else:
        print(f"\n📋 PRs Created Today: None (wake comment posted)")
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
