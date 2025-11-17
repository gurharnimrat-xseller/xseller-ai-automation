#!/bin/bash
# Autonomous GitHub Actions CI Monitor
# Watches for CI success/failure and reports status

set -e

COMMIT_SHA="${1:-HEAD}"
MAX_WAIT=300  # 5 minutes max wait
POLL_INTERVAL=15  # Check every 15 seconds
ELAPSED=0

echo "🔍 Monitoring GitHub Actions for commit: $COMMIT_SHA"
echo "⏱️  Max wait time: ${MAX_WAIT}s, Poll interval: ${POLL_INTERVAL}s"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

while [ $ELAPSED -lt $MAX_WAIT ]; do
  # Get the most recent workflow run (simpler format without jq)
  RUN_LIST=$(gh run list --limit 1 2>/dev/null)

  if [ -z "$RUN_LIST" ]; then
    echo "⏳ $(date '+%H:%M:%S'): Waiting for workflow to start..."
    sleep $POLL_INTERVAL
    ELAPSED=$((ELAPSED + POLL_INTERVAL))
    continue
  fi

  # Parse status and conclusion from gh run list output
  # Format: STATUS  CONCLUSION  NAME  ...
  STATUS=$(echo "$RUN_LIST" | tail -1 | awk '{print $1}')
  CONCLUSION=$(echo "$RUN_LIST" | tail -1 | awk '{print $2}')

  # Get workflow name and run ID
  RUN_ID=$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId' 2>/dev/null || echo "unknown")
  WORKFLOW_NAME=$(echo "$RUN_LIST" | tail -1 | awk '{for(i=3;i<=NF;i++) printf "%s ", $i; print ""}' | sed 's/ *$//')

  echo "⏳ $(date '+%H:%M:%S'): [$WORKFLOW_NAME] Status: $STATUS (Run #$RUN_ID)"

  # Check if completed
  if [ "$STATUS" = "completed" ]; then
    if [ "$CONCLUSION" = "success" ]; then
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      echo "✅ CI PASSED - All checks successful!"
      echo "🎉 Workflow: $WORKFLOW_NAME"
      echo "🔗 Run ID: $RUN_ID"
      exit 0
    elif [ "$CONCLUSION" = "failure" ]; then
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      echo "❌ CI FAILED - Fetching error logs..."
      echo "🔍 Workflow: $WORKFLOW_NAME"
      echo "🔗 Run ID: $RUN_ID"
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

      # Save full logs
      gh run view $RUN_ID --log-failed > /tmp/ci_error_full.log 2>&1 || true

      # Show concise error summary
      echo ""
      echo "📋 ERROR SUMMARY:"
      grep -i "error\|fail\|✗" /tmp/ci_error_full.log 2>/dev/null | head -30 || echo "No clear error pattern found. Check full logs."

      echo ""
      echo "💾 Full logs saved to: /tmp/ci_error_full.log"
      echo "🔧 Fix needed. Stopping monitor."
      exit 1
    else
      echo "⚠️  Unknown conclusion: $CONCLUSION"
      exit 2
    fi
  fi

  sleep $POLL_INTERVAL
  ELAPSED=$((ELAPSED + POLL_INTERVAL))
done

echo "⏱️  Timeout reached after ${MAX_WAIT}s - workflow still running"
exit 3
