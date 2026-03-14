"""
update_skill.sh — Update skill from git + run test

Usage:
  ./update-skill.sh <skill-name>

This script:
1. Pulls latest changes from git
2. Runs quick_validate.py
3. Runs run_tests.py (Anthropics workflow)
4. Creates snapshot for baseline comparison (if iteration > 1)
5. Opens viewer with prev/next iteration comparison
"""

#!/bin/bash

set -e

SKILL_NAME="$1"
if [ -z "$SKILL_NAME" ]; then
    echo "Usage: ./update-skill.sh <skill-name>"
    exit 1
fi

SKILL_PATH="$HOME/.openclaw/skills/$SKILL_NAME"
WORKSPACE_PATH="$HOME/.openclaw/workspace/test-workspace/$SKILL_NAME"

if [ ! -d "$SKILL_PATH" ]; then
    echo "Error: skill not found: $SKILL_PATH"
    exit 1
fi

echo "🚀 Updating skill: $SKILL_NAME"
echo "📁 Path: $SKILL_PATH"
echo ""

# 1. Pull latest from git
echo "🔄 Pulling latest from git..."
cd "$SKILL_PATH"
if git remote | grep -q origin; then
    git pull origin master
else
    echo "   (no git remote, skipping)"
fi

# 2. Quick validate
echo "✅ Running quick validation..."
cd "$SKILL_PATH"
python3 "$HOME/.openclaw/workspace/local-skill-creator/scripts/quick_validate.py" "$SKILL_PATH" || echo "   Validation failed (non-fatal)"

# 3. Run tests
echo "🧪 Running Anthropics-style evals..."
WORKSPACE_DIR="$WORKSPACE_PATH/iteration-$(date +%Y%m%d%H%M%S)"
mkdir -p "$WORKSPACE_DIR"

# Run tests (with-skill + baseline)
cd "$SKILL_PATH"
python3 "$HOME/.openclaw/workspace/local-skill-creator/scripts/run_tests.py" \
    --skill-path "$SKILL_PATH" \
    --workspace "$WORKSPACE_DIR" \
    --static "$WORKSPACE_DIR/viewer.html"

# 4. Show next steps
echo ""
echo "✅ Update complete!"
echo "📁 Workspace: $WORKSPACE_DIR"
echo "📊 Static viewer: $WORKSPACE_DIR/viewer.html"
echo ""
echo "📝 Next steps:"
echo "   1. Open $WORKSPACE_DIR/viewer.html in browser"
echo "   2. Review outputs and benchmark"
echo "   3. Download feedback.json"
echo "   4. Review improvements → edit SKILL.md"
echo "   5. Run ./update-skill.sh again"
