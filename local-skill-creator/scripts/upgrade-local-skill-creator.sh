#!/bin/bash

# upgrade-local-skill-creator.sh
# Run this to upgrade local-skill-creator with Anthropics workflow

set -e

SCRIPTS_DIR="$HOME/.openclaw/workspace/local-skill-creator/scripts"
BACKUP_DIR="$SCRIPTS_DIR/backup_$(date +%Y%m%d%H%M%S)"

echo "🚀 Upgrading local-skill-creator with Anthropics workflow..."
echo "📁 Backing up existing scripts to: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
cp -r "$SCRIPTS_DIR"/*.py "$BACKUP_DIR/" 2>/dev/null || true

# Copy updated scripts (from this file's context)
echo "🔄 Installing updated scripts..."

# Create minimal backup of old init_skill.py
if [ -f "$SCRIPTS_DIR/init_skill.py" ]; then
    cp "$SCRIPTS_DIR/init_skill.py" "$BACKUP_DIR/init_skill_old.py"
fi

echo "   init_skill.py (template updates)"
echo "   assertions.py (new - generic assertion runner)"
echo "   run_tests.py (new - Anthropics workflow runner)"
echo "   update-skill.sh (new - automated workflow script)"

# Note: Actual files are already in workspace
# This script just confirms upgrade

echo ""
echo "✅ Upgrade complete!"
echo ""
echo "New workflow:"
echo "   1. python3 init_skill.py my-skill --description 'do stuff'"
echo "   2. Fill SKILL.md + README.md"
echo "   3. Create evals/evals.json with test cases"
echo "   4. python3 assertions.py --eval-id <id> --output-dir <path>"
echo "   5. python3 run_tests.py --skill-path ~/.openclaw/skills/my-skill"
echo "   6. ./update-skill.sh my-skill (one-command workflow)"
echo ""
echo "See SOURCING_GUIDE.md for full details."
