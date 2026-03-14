#!/usr/bin/env python3
import sys
import zipfile
from pathlib import Path
from quick_validate import validate_skill


def main():
    if len(sys.argv) not in (2, 3):
        print('Usage: package_skill.py <skill_dir> [output_dir]')
        raise SystemExit(1)
    skill_dir = Path(sys.argv[1]).resolve()
    out_dir = Path(sys.argv[2]).resolve() if len(sys.argv) == 3 else Path.cwd()
    ok, msg = validate_skill(skill_dir)
    if not ok:
        print(msg)
        raise SystemExit(1)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f'{skill_dir.name}.skill'
    with zipfile.ZipFile(out_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for p in skill_dir.rglob('*'):
            if p.is_file():
                zf.write(p, p.relative_to(skill_dir.parent))
    print(out_file)


if __name__ == '__main__':
    main()
