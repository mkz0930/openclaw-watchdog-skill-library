#!/usr/bin/env python3
"""
publish_skill.py — 一键发布 skill 到 GitHub

用法:
  python3 publish_skill.py <skill_dir> [--repo <github_repo_path>]

默认 repo: ~/openclaw-watchdog-skill-library (workspace 里的 git repo)

流程:
  1. quick_validate 验证
  2. 复制到 GitHub repo 目录
  3. git add + commit + push
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from quick_validate import validate_skill

DEFAULT_REPO = Path.home() / '.openclaw/workspace/openclaw-watchdog-skill-library'


def run(cmd, cwd):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'❌ Command failed: {" ".join(cmd)}')
        print(result.stderr)
        raise SystemExit(1)
    return result.stdout.strip()


def main():
    ap = argparse.ArgumentParser(description='发布 skill 到 GitHub')
    ap.add_argument('skill_dir', help='skill 目录路径')
    ap.add_argument('--repo', default=str(DEFAULT_REPO), help=f'GitHub repo 本地路径（默认: {DEFAULT_REPO}）')
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

    # 2. copy to repo
    dest = repo_path / skill_path.name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(skill_path, dest)
    print(f'📁 Copied to {dest}')

    # 3. git add + commit + push
    skill_name = skill_path.name
    run(['git', 'add', skill_name], cwd=repo_path)
    run(['git', 'commit', '-m', f'feat: publish skill {skill_name}'], cwd=repo_path)
    out = run(['git', 'push'], cwd=repo_path)
    print(f'🚀 Pushed to GitHub')
    if out:
        print(out)

    print(f'\n✅ Done! https://github.com/mkz0930/openclaw-watchdog-skill-library/tree/master/{skill_name}')


if __name__ == '__main__':
    main()
