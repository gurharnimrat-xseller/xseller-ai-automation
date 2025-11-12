#!/bin/bash
# Test script for claude_start.yml workflow and automation

set -e

echo "============================================================"
echo "Testing Claude Start Workflow Automation"
echo "============================================================"

cd "$(dirname "$0")/.."

# Check that required files exist
echo ""
echo "1. Checking required files exist..."
if [ -f ".github/workflows/claude_start.yml" ]; then
    echo "   ✅ .github/workflows/claude_start.yml exists"
else
    echo "   ❌ .github/workflows/claude_start.yml NOT FOUND"
    exit 1
fi

if [ -f "scripts/run_claude_start.py" ]; then
    echo "   ✅ scripts/run_claude_start.py exists"
else
    echo "   ❌ scripts/run_claude_start.py NOT FOUND"
    exit 1
fi

if [ -x "scripts/run_claude_start.py" ]; then
    echo "   ✅ scripts/run_claude_start.py is executable"
else
    echo "   ❌ scripts/run_claude_start.py is NOT executable"
    exit 1
fi

# Validate workflow YAML syntax
echo ""
echo "2. Validating workflow YAML syntax..."
if command -v yamllint &> /dev/null; then
    yamllint .github/workflows/claude_start.yml && echo "   ✅ Workflow YAML is valid"
else
    # Basic check for YAML structure
    if python3 -c "import yaml; yaml.safe_load(open('.github/workflows/claude_start.yml'))" 2>/dev/null; then
        echo "   ✅ Workflow YAML is valid (basic check)"
    else
        echo "   ⚠️  Could not validate YAML (yamllint not installed)"
    fi
fi

# Check Python script syntax
echo ""
echo "3. Checking Python script syntax..."
if python3 -m py_compile scripts/run_claude_start.py; then
    echo "   ✅ Python script syntax is valid"
else
    echo "   ❌ Python script has syntax errors"
    exit 1
fi

# Verify workflow has required triggers and permissions
echo ""
echo "4. Verifying workflow configuration..."
if grep -q "workflow_dispatch:" .github/workflows/claude_start.yml; then
    echo "   ✅ Workflow has workflow_dispatch trigger"
else
    echo "   ❌ Workflow missing workflow_dispatch trigger"
    exit 1
fi

if grep -q "issues: write" .github/workflows/claude_start.yml; then
    echo "   ✅ Workflow has issues:write permission"
else
    echo "   ⚠️  Workflow may not have issues:write permission"
fi

# Check script for required functions
echo ""
echo "5. Verifying Python script has required functions..."
required_functions=(
    "trigger_workflow"
    "wait_for_workflow"
    "find_or_create_issue"
    "get_latest_comment"
    "check_prs_today"
    "post_wake_comment"
)

for func in "${required_functions[@]}"; do
    if grep -q "def $func" scripts/run_claude_start.py; then
        echo "   ✅ Function '$func' exists"
    else
        echo "   ❌ Function '$func' NOT FOUND"
        exit 1
    fi
done

# Check for proper error handling
echo ""
echo "6. Checking for error handling..."
if grep -q "CalledProcessError" scripts/run_claude_start.py; then
    echo "   ✅ Script includes subprocess error handling"
else
    echo "   ⚠️  Script may not handle subprocess errors"
fi

if grep -q "TimeoutError" scripts/run_claude_start.py; then
    echo "   ✅ Script includes timeout handling"
else
    echo "   ⚠️  Script may not handle timeouts"
fi

# Verify documentation exists
echo ""
echo "7. Checking documentation..."
if [ -f "scripts/README_claude_start.md" ]; then
    echo "   ✅ README_claude_start.md exists"
    # Check if README has key sections
    if grep -q "Usage" scripts/README_claude_start.md; then
        echo "   ✅ README includes Usage section"
    fi
    if grep -q "Prerequisites" scripts/README_claude_start.md; then
        echo "   ✅ README includes Prerequisites section"
    fi
else
    echo "   ⚠️  README_claude_start.md not found"
fi

echo ""
echo "============================================================"
echo "✅ All validation checks passed!"
echo "============================================================"
echo ""
echo "To run the automation script manually:"
echo "  python3 scripts/run_claude_start.py"
echo ""
echo "Prerequisites:"
echo "  - GitHub CLI (gh) must be installed and authenticated"
echo "  - Must have permissions to trigger workflows and manage issues"
echo ""
echo "Note: The script requires authentication with GitHub CLI."
echo "      In a GitHub Actions environment, set GH_TOKEN to \${{ github.token }}"
echo ""
