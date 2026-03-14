#!/bin/bash
# update_skill.sh — 同步本地 skill → Git 工作区 + 提交
# 用法：./update_skill.sh ~/.openclaw/skills/my-skill

set -e

if [ -z "$1" ]; then
  echo "用法: $0 <skill-dir>"
  echo "示例: $0 ~/.openclaw/skills/my-skill"
  exit 1
fi

LOCAL_SKILL="$1"
WORKSPACE_REPO="$HOME/.openclaw/workspace/openclaw-watchdog-skill-library"

if [ ! -d "$LOCAL_SKILL" ]; then
  echo "❌ 错误：找不到 skill 目录: $LOCAL_SKILL"
  exit 1
fi

SKILL_NAME=$(basename "$LOCAL_SKILL")
WORKSPACE_SKILL="$WORKSPACE_REPO/$SKILL_NAME"

echo "📦 同步 skill: $SKILL_NAME"
echo "📍 本地: $LOCAL_SKILL"
echo "📍 Git: $WORKSPACE_SKILL"

# 检查 Git 仓库是否存在
if [ ! -d "$WORKSPACE_REPO/.git" ]; then
  echo "❌ 错误：Git 仓库不存在: $WORKSPACE_REPO"
  exit 1
fi

# 创建 workspace 目录（如果不存在）
mkdir -p "$WORKSPACE_SKILL"

# 同步文件（保留 README.md / SKILL.md）
echo "🔄 同步文件..."
cp -r "$LOCAL_SKILL"/* "$WORKSPACE_SKILL"/ 2>/dev/null || true

# Git 提交
cd "$WORKSPACE_REPO"
git add "$SKILL_NAME"
git commit -m "docs: 更新 skill '$SKILL_NAME' by local-sync" || echo "No changes to commit"
git push origin master

echo "✅ 完成！支持命令：python3 $WORKSPACE_REPO/scripts/update_skill.sh $LOCAL_SKILL"
echo "🔗 查看: https://github.com/mkz0930/openclaw-watchdog-skill-library/tree/master/$SKILL_NAME"
