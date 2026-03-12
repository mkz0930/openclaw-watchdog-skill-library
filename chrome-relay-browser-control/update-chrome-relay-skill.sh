#!/bin/bash
# update-chrome-relay-skill.sh
# 一键更新 chrome-relay-browser-control skill + 推送到 GitHub

set -e

SKILL_DIR="$HOME/.openclaw/skills/chrome-relay-browser-control"
WORKSPACE_DIR="$HOME/.openclaw/workspace/openclaw-watchdog-skill-library/chrome-relay-browser-control"

echo "📦 检测 skill 目录..."
if [ ! -d "$SKILL_DIR" ]; then
  echo "❌ 错误：找不到 $SKILL_DIR"
  exit 1
fi

echo "📁 创建远程 workspace 目录..."
mkdir -p "$WORKSPACE_DIR"

echo "🔄 同步文件到 workspace..."
cp "$SKILL_DIR"/* "$WORKSPACE_DIR/"

echo "💾 推送到 GitHub..."
cd "$WORKSPACE_DIR/../../.."
git add chrome-relay-browser-control
git commit -m "docs: automatically update chrome-relay-browser-control skill"
git push origin master

echo "✅ 更新完成！"
echo "📍 本地: $SKILL_DIR"
echo "📍 远程: https://github.com/mkz0930/openclaw-watchdog-skill-library"
