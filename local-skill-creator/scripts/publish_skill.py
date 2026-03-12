#!/usr/bin/env python3
"""
publish_skill.py — 一键发布 skill 到 GitHub + 输出 MemOS 注册数据

用法:
  python3 publish_skill.py <skill_dir> [--repo <path>] [--owner <name>] [--json]

默认 repo: ~/.openclaw/workspace/openclaw-watchdog-skill-library

流程:
  1. quick_validate 验证（含 README.md 检查）
  2. 复制到 GitHub repo 目录
  3. git add + commit + push
  4. 输出结构化 JSON（供 AI agent 自动调用 memory_write_public 注册到 MemOS）

AI agent 使用方式:
  result = exec("python3 publish_skill.py <dir> --json")
  data = json.loads(result)  # 读取 memos_content 和 memos_summary
  memory_write_public(content=data['memos_content'], summary=data['memos_summary'])
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
        print(f'❌ Command failed: {" ".join(cmd)}', file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(1)
    return result.stdout.strip()


def get_skill_meta(skill_path: Path) -> dict:
    """从 SKILL.md frontmatter 或 _meta.json 读取 name/description"""
    meta = skill_path / '_meta.json'
    skill_md = skill_path / 'SKILL.md'
    name = skill_path.name
    description = ''

    if meta.exists():
        try:
            d = json.loads(meta.read_text(encoding='utf-8'))
            name = d.get('name', name)
            description = d.get('description', '')
        except Exception:
            pass

    # fallback to SKILL.md frontmatter if description still empty
    if not description and skill_md.exists() and HAS_YAML:
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

    return {'name': name, 'description': description}


def build_memos_content(skill_name: str, description: str, owner: str, skill_path: Path) -> tuple[str, str]:
    """构建 MemOS public memory 内容"""
    owner_line = f'\n- owner: {owner}' if owner else ''
    content = f"""## Skill: {skill_name}

- description: {description}{owner_line}
- path: ~/.openclaw/skills/{skill_name}/
- github: {GITHUB_BASE}/{skill_name}
- installed: true
"""
    summary = f'Skill {skill_name}: {description[:80]}'
    return content, summary


def main():
    ap = argparse.ArgumentParser(description='发布 skill 到 GitHub + 输出 MemOS 注册数据')
    ap.add_argument('skill_dir', help='skill 目录路径')
    ap.add_argument('--repo', default=str(DEFAULT_REPO), help=f'GitHub repo 本地路径（默认: {DEFAULT_REPO}）')
    ap.add_argument('--owner', default='', help='skill 作者/所有者（可选）')
    ap.add_argument('--json', action='store_true', dest='output_json',
                    help='输出 JSON 格式结果（供 AI agent 自动注册 MemOS）')
    args = ap.parse_args()

    skill_path = Path(args.skill_dir).expanduser().resolve()
    repo_path = Path(args.repo).expanduser().resolve()

    if not skill_path.exists():
        raise SystemExit(f'❌ Skill dir not found: {skill_path}')
    if not repo_path.exists():
        raise SystemExit(f'❌ Repo not found: {repo_path}')

    # 1. validate
    if not args.output_json:
        print(f'🔍 Validating {skill_path.name}...')
    if not validate_skill(skill_path, quiet=args.output_json):
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
    if not args.output_json:
        print(f'📁 Copied to {dest}')

    # 4. git add + commit + push (skip if no changes)
    run(['git', 'add', skill_name], cwd=repo_path)
    diff = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=repo_path)
    if diff.returncode != 0:
        run(['git', 'commit', '-m', f'feat: publish skill {skill_name}'], cwd=repo_path)
        run(['git', 'push'], cwd=repo_path)
        if not args.output_json:
            print(f'🚀 Pushed to GitHub: {GITHUB_BASE}/{skill_name}')
    else:
        if not args.output_json:
            print(f'ℹ️  No changes, skipping push. {GITHUB_BASE}/{skill_name}')

    # 5. 构建 MemOS 注册数据
    memos_content, memos_summary = build_memos_content(skill_name, description, args.owner, skill_path)

    if args.output_json:
        # 输出 JSON 供 AI agent 自动调用 memory_write_public
        print(json.dumps({
            'skill_name': skill_name,
            'description': description,
            'github_url': f'{GITHUB_BASE}/{skill_name}',
            'memos_content': memos_content,
            'memos_summary': memos_summary,
        }, ensure_ascii=False))
    else:
        print(f'\n✅ Published! {GITHUB_BASE}/{skill_name}')
        print(f'\n📋 MemOS 注册数据已准备好，AI agent 将自动调用 memory_write_public 完成注册。')


if __name__ == '__main__':
    main()
