# 🔍 CI Monitoring Tool

## Overview
`monitor_ci.sh` is an autonomous GitHub Actions monitoring script that watches for CI success/failure and provides real-time feedback.

## Usage

### Basic Monitoring (Latest Run)
```bash
./monitor_ci.sh
```

### Monitor Specific Commit
```bash
./monitor_ci.sh <commit-sha>
```

### Typical Workflow
```bash
# Make changes and commit
git add .
git commit -m "fix: your changes"
git push origin main

# Start monitoring
./monitor_ci.sh
```

## Features

- ✅ **Real-time monitoring** - Polls every 15 seconds
- ✅ **Timeout protection** - Max 5 minutes wait
- ✅ **Error reporting** - Saves logs to `/tmp/ci_error_full.log`
- ✅ **Exit codes**:
  - `0` - CI passed
  - `1` - CI failed
  - `2` - Unknown conclusion
  - `3` - Timeout

## Output Examples

### Success
```
✅ CI PASSED - All checks successful!
🎉 Workflow: Backend CI
🔗 Run ID: 19423447920
```

### Failure
```
❌ CI FAILED - Fetching error logs...
🔍 Workflow: Backend CI
🔗 Run ID: 19423447920
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 ERROR SUMMARY:
[Error details here...]

💾 Full logs saved to: /tmp/ci_error_full.log
🔧 Fix needed. Stopping monitor.
```

## Configuration

Edit these variables at the top of `monitor_ci.sh`:

```bash
MAX_WAIT=300        # 5 minutes max wait
POLL_INTERVAL=15    # Check every 15 seconds
```

## Requirements

- GitHub CLI (`gh`) installed and authenticated
- Internet connection
- Bash shell

## Integration with Development Workflow

### Automated Fix Loop
```bash
#!/bin/bash
# auto_fix_loop.sh

while true; do
  echo "Pushing changes..."
  git push origin main

  echo "Monitoring CI..."
  ./monitor_ci.sh

  if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
    break
  else
    echo "❌ Tests failed. Review /tmp/ci_error_full.log"
    echo "Fix errors and try again? (y/n)"
    read -r answer
    if [ "$answer" != "y" ]; then
      break
    fi
  fi
done
```

## Troubleshooting

### "No workflow runs found"
- Wait a few seconds for GitHub Actions to start
- Check `.github/workflows/` directory exists
- Verify workflows are enabled in repo settings

### Script exits with code 3 (timeout)
- Increase `MAX_WAIT` value
- Check GitHub Actions status page
- Verify workflow file syntax is correct

## Notes

- The script monitors the **most recent** workflow run
- Works with any GitHub Actions workflow
- Does not require `jq` or other external dependencies
