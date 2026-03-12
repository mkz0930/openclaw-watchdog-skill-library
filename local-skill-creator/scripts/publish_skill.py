#!/usr/bin/env python3
"""
publish_skill.py — 一键发布 skill 到 GitHub + 注册到 MemOS

用法:
  python3 publish_skill.py <skill_dir> [--repo <github_repo_path>] [--owner <owner_name>]

默认 repo: ~/.openclaw/workspace/openclaw-watchdog-skill-library

流程:
  1. quick_validate 验证（含 README.md 检查）
  2. 复制到 GitHub repo 目录
  3. git add + commit + push
  4. 调用 OpenClaw memory_write_public 注册到 MemOS（让 skill_search 可检索）

注意: 步骤 4 需要在 OpenClaw agent 环境中运行才能调用 memory_write_public。
     在普通 shell 中运行时会跳过此步骤并提示手动注册。
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


def run(cmd, cwd):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'❌ Command failed: {" ".join(cmd)}')
        print(result.stderr)
        raise SystemExit(1)
    return result.stdout.strip()


def get_skill_meta(skill_path: Path) -> dict:
    """从 SKILL.md frontmatter 或 _meta.json 读取 name/description"""
    meta = skill_path / '_meta.json'
    skill_md = skill_path / 'SKILL.md'

    if meta.exists():
        try:
            d = json.loads(meta.read_text(encoding='utf-8'))
            return {'name': d.get('name', skill_path.name), 'description': d.get('description', '')}
        except Exception:
            pass

    if skill_md.exists() and HAS_YAML:
        try:
            content = skill_md.read_text(encoding='utf-8')
            m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if m:
                fm = yaml.safe_load(m.group(1))
                if isinstance(fm, dict):
                    return {'name': fm.get('name', skill_path.name), 'description': fm.get('description', '')}
        except Exception:
            pass

    return {'name': skill_path.name, 'description': ''}


def print_memos_registration(skill_name: str, description: str, owner: str):
    """打印 MemOS 注册指令，供 AI agent 在 OpenClaw 环境中执行"""
    print()
    print('📋 MemOS 注册（在 OpenClaw agent 中执行以下操作）:')
    print('   调用 memory_write_public，内容如下:')
    print(f'   skill: {skill_name}')
    print(f'   description: {description}')
    if owner:
        print(f'   owner: {owner}')
    print(f'   path: ~/.openclaw/skills/{skill_name}/')
    print(f'   github: {GITHUB_BASE}/{skill_name}')
    print()
    print('   或直接让 AI 执行: "把这个 skill 注册到 MemOS public memory"')


def main():
    ap = argparse.ArgumentParser(description='发布 skill 到 GitHub + 注册到 MemOS')
    ap.add_argument('skill_dir', help='skill 目录路径')
    ap.add_argument('--repo', default=str(DEFAULT_REPO), help=f'GitHub repo 本地路径（默认: {DEFAULT_REPO}）')
    ap.add_argument('--owner', default='', help='skill 作者/所有者（可选，用于 MemOS 标注）')
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

    # 4. git add + commit + push
    run(['git', 'add', skill_name], cwd=repo_path)
    run(['git', 'commit', '-m', f'feat: publish skill {skill_name}'], cwd=repo_path)
    run(['git', 'push'], cwd=repo_path)
    print(f'🚀 Pushed to GitHub: {GITHUB_BASE}/{skill_name}')

    # 5. MemOS 注册提示
    print_memos_registration(skill_name, description, args.owner)

    print(f'✅ Done!')


if __name__ == '__main__':
    main()
