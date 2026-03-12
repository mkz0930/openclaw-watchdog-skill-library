#!/usr/bin/env python3
"""
quick_validate.py — 验证 skill 目录格式

用法:
  python3 quick_validate.py <skill_dir>

检查项:
  - SKILL.md 存在且有合法 YAML frontmatter（name + description）
  - README.md 存在
"""
import re
import sys
from pathlib import Path
import yaml


def validate_skill(skill_path: Path):
    errors = []

    # 1. SKILL.md
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        errors.append('❌ SKILL.md not found')
    else:
        content = skill_md.read_text(encoding='utf-8')
        m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not m:
            errors.append('❌ SKILL.md: missing YAML frontmatter')
        else:
            try:
                fm = yaml.safe_load(m.group(1))
            except Exception as e:
                errors.append(f'❌ SKILL.md: invalid YAML: {e}')
                fm = None
            if fm is not None:
                if not isinstance(fm, dict):
                    errors.append('❌ SKILL.md: frontmatter must be a mapping')
                else:
                    allowed = {'name', 'description'}
                    extra = set(fm) - allowed
                    if extra:
                        errors.append(f'❌ SKILL.md: unexpected keys: {", ".join(sorted(extra))}')
                    name = fm.get('name', '')
                    desc = fm.get('description', '')
                    if not isinstance(name, str) or not re.fullmatch(r'[a-z0-9-]{1,64}', name) \
                            or name.startswith('-') or name.endswith('-') or '--' in name:
                        errors.append(f'❌ SKILL.md: invalid name: "{name}"')
                    if not isinstance(desc, str) or not desc.strip():
                        errors.append('❌ SKILL.md: description must be a non-empty string')

    # 2. README.md
    readme = skill_path / 'README.md'
    if not readme.exists():
        errors.append('❌ README.md not found (required)')

    if errors:
        for e in errors:
            print(e)
        return False
    print(f'✅ {skill_path.name}: all checks passed')
    return True


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: quick_validate.py <skill_dir>')
        raise SystemExit(1)
    ok = validate_skill(Path(sys.argv[1]).resolve())
    raise SystemExit(0 if ok else 1)
