#!/usr/bin/env python3
"""
publish_skill.py — 一键发布 skill 到 GitHub + 自动写入 MemOS 注册队列

用法:
  python3 publish_skill.py <skill_dir> [--repo <path>] [--owner <name>]

默认 repo: ~/.openclaw/workspace/openclaw-watchdog-skill-library

流程:
  1. quick_validate 验证（含 README.md 检查）
  2. 复制到 GitHub repo 目录
  3. git add + commit + push
  4. 写入 ~/.openclaw/skills/.pending-memos.json（MemOS 注册队列）

AI agent 在发布后读取队列并自动调用 memory_write_public:
  python3 register_memos.py  →  读取队列 JSON
  → memory_write_public(content, summary)
  → python3 register_memos.py --clear  →  清空队列
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from quick_validate import validate_skill

DEFAULT_REPO = Path.home() / '.openclaw/workspace/openclaw-watchdog-skill-library'
GITHUB_BASE = 'https://github.com/mkz0930/openclaw-watchdog-skill-library/tree/master'
PENDING_FILE = Path.home() / '.openclaw/skills/.pending-memos.json'


def run(cmd, cwd):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'❌ Command failed: {" ".join(cmd)}', file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(1)
    return result.stdout.strip()


def get_skill_meta(skill_path: Path) -> dict:
    """从 SKILL.md frontmatter 或 _meta.json 读取 name/description（优先 SKILL.md）"""
    meta = skill_path / '_meta.json'
    skill_md = skill_path / 'SKILL.md'
    name = skill_path.name
    description = ''

    # 优先从 SKILL.md frontmatter 读（最权威）
    if skill_md.exists() and HAS_YAML:
        try:
            content = skill_md.read_text(encoding='utf-8')
            m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if m:
                fm = yaml.safe_load(m.group(1))
                if isinstance(fm, dict):
                    name = fm.get('name', name)
                    description = fm.get('description', '')
        except Exception:
            pass

    # fallback: _meta.json
    if not description and meta.exists():
        try:
            d = json.loads(meta.read_text(encoding='utf-8'))
            name = d.get('name', name)
            description = d.get('description', '')
        except Exception:
            pass

    return {'name': name, 'description': description}


def build_memos_entry(skill_name: str, description: str, owner: str) -> dict:
    """构建 MemOS 注册条目"""
    owner_line = f'\n- owner: {owner}' if owner else ''
    content = (
        f'## Skill: {skill_name}\n\n'
        f'- description: {description}{owner_line}\n'
        f'- path: ~/.openclaw/skills/{skill_name}/\n'
        f'- github: {GITHUB_BASE}/{skill_name}\n'
        f'- installed: true\n'
    )
    summary = f'Skill {skill_name}: {description[:80]}'
    return {
        'skill_name': skill_name,
        'description': description,
        'owner': owner,
        'github_url': f'{GITHUB_BASE}/{skill_name}',
        'memos_content': content,
        'memos_summary': summary,
    }


def append_to_pending(entry: dict):
    """追加到 pending 队列"""
    items = []
    if PENDING_FILE.exists():
        try:
            items = json.loads(PENDING_FILE.read_text(encoding='utf-8'))
        except Exception:
            items = []
    # 去重：同名 skill 覆盖
    items = [i for i in items if i.get('skill_name') != entry['skill_name']]
    items.append(entry)
    PENDING_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description='发布 skill 到 GitHub + 写入 MemOS 注册队列')
    ap.add_argument('skill_dir', help='skill 目录路径')
    ap.add_argument('--repo', default=str(DEFAULT_REPO), help=f'GitHub repo 本地路径（默认: {DEFAULT_REPO}）')
    ap.add_argument('--owner', default='', help='skill 作者/所有者（可选）')
    args = ap.parse_args()

    skill_path = Path(args.skill_dir).expanduser().resolve()
    repo_path = Path(args.repo).expanduser().resolve()

    if not skill_path.exists():
        raise SystemExit(f'❌ Skill dir not found: {skill_path}')
    if not repo_path.exists():
        raise SystemExit(f'❌ Repo not found: {repo_path}')

    # 1. validate
    print(f'🔍 Validating {skill_path.name}...')
    if not validate_skill(skill_path):
        raise SystemExit(1)

    # 2. read meta
    meta = get_skill_meta(skill_path)
    skill_name = skill_path.name
    description = meta.get('description', '')

    # 3. copy to repo
    dest = repo_path / skill_name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(skill_path, dest)
    print(f'📁 Copied to {dest}')

    # 4. git add + commit + push (skip if no changes)
    run(['git', 'add', skill_name], cwd=repo_path)
    diff = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=repo_path)
    if diff.returncode != 0:
        run(['git', 'commit', '-m', f'feat: publish skill {skill_name}'], cwd=repo_path)
        run(['git', 'push'], cwd=repo_path)
        print(f'🚀 Pushed to GitHub: {GITHUB_BASE}/{skill_name}')
    else:
        print(f'ℹ️  No changes to push. {GITHUB_BASE}/{skill_name}')

    # 5. 写入 MemOS 注册队列
    entry = build_memos_entry(skill_name, description, args.owner)
    append_to_pending(entry)
    print(f'📋 Added to MemOS queue: {PENDING_FILE}')
    print(f'   → AI agent 将自动读取队列并调用 memory_write_public 完成注册')
    print(f'\n✅ Done! Run: python3 register_memos.py  to process the queue.')


if __name__ == '__main__':
    main()
