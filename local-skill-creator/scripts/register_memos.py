#!/usr/bin/env python3
"""
register_memos.py — 读取 pending MemOS 注册队列并输出注册数据

publish_skill.py 发布后会把注册数据写入:
  ~/.openclaw/skills/.pending-memos.json

本脚本读取该文件，输出待注册的 skill 列表。
AI agent 读取输出后调用 memory_write_public 完成注册，然后清空队列。

用法:
  python3 register_memos.py          # 输出待注册列表（JSON）
  python3 register_memos.py --clear  # 清空队列
"""
import argparse
import json
import sys
from pathlib import Path

PENDING_FILE = Path.home() / '.openclaw/skills/.pending-memos.json'


def load_pending() -> list:
    if not PENDING_FILE.exists():
        return []
    try:
        return json.loads(PENDING_FILE.read_text(encoding='utf-8'))
    except Exception:
        return []


def save_pending(items: list):
    PENDING_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description='读取 pending MemOS 注册队列')
    ap.add_argument('--clear', action='store_true', help='清空队列')
    args = ap.parse_args()

    if args.clear:
        save_pending([])
        print('✅ Queue cleared.')
        return

    items = load_pending()
    if not items:
        print('[]')
        return

    print(json.dumps(items, ensure_ascii=False))


if __name__ == '__main__':
    main()
