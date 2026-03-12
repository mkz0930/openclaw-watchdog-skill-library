#!/usr/bin/env python3
"""
init_skill.py — 创建 skill 脚手架

用法:
  python3 init_skill.py <skill-name> [--description "..."] [--path ~/.openclaw/skills]

默认 path: ~/.openclaw/skills
自动生成: SKILL.md, README.md, scripts/, references/
"""
import argparse
import re
from pathlib import Path

SKILL_TEMPLATE = """\
---
name: {skill_name}
description: "{description}"
---

# {skill_title}

## 适用场景

描述什么时候用这个 skill。

## 使用方法

1. 步骤一
2. 步骤二
3. 步骤三

## 关键参数 / 注意事项

- 参数说明
- 常见坑

## 故障排查

| 现象 | 原因 | 解决 |
|------|------|------|
| ... | ... | ... |

## 参考资料

- `scripts/`: 可执行脚本
- `references/`: 详细文档
"""

README_TEMPLATE = """\
# {skill_title}

{description}

## 用途

TODO: 描述这个 skill 解决什么问题。

## 适用场景

- 场景一
- 场景二

## 使用方法

```bash
# TODO: 填写调用方式
```

## 关键参数

| 参数 | 说明 |
|------|------|
| ... | ... |

## 注意事项

- 注意事项一

## 详细指南

见同目录 `SKILL.md`。
"""


def title_case(name: str) -> str:
    return ' '.join(word.capitalize() for word in name.split('-'))


def validate_name(name: str):
    if not re.fullmatch(r'[a-z0-9-]{1,64}', name):
        raise ValueError('skill name must use lowercase letters, digits, hyphens; max 64 chars')
    if name.startswith('-') or name.endswith('-') or '--' in name:
        raise ValueError('skill name cannot start/end with hyphen or contain consecutive hyphens')


def main():
    ap = argparse.ArgumentParser(description='创建 skill 脚手架')
    ap.add_argument('skill_name', help='skill 名称（小写字母、数字、连字符）')
    ap.add_argument('--path', default='~/.openclaw/skills', help='输出目录（默认: ~/.openclaw/skills）')
    ap.add_argument('--description', default='TODO: describe what this skill does and when to use it.')
    args = ap.parse_args()

    validate_name(args.skill_name)
    out = Path(args.path).expanduser().resolve() / args.skill_name
    if out.exists():
        raise SystemExit(f'Error: {out} already exists')

    (out / 'scripts').mkdir(parents=True)
    (out / 'references').mkdir(parents=True)

    title = title_case(args.skill_name)
    desc = args.description.replace('"', '\\"')

    (out / 'SKILL.md').write_text(SKILL_TEMPLATE.format(
        skill_name=args.skill_name,
        skill_title=title,
        description=desc,
    ), encoding='utf-8')

    (out / 'README.md').write_text(README_TEMPLATE.format(
        skill_title=title,
        description=args.description,
    ), encoding='utf-8')

    print(f'✅ Skill created: {out}')
    print(f'   → 填写 SKILL.md 和 README.md 内容')
    print(f'   → 完成后运行: python3 quick_validate.py {out}')


if __name__ == '__main__':
    main()
