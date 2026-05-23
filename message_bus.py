#!/usr/bin/env python3
"""
============================================================================
三方消息总线 v1.0
============================================================================
富富(OpenClaw) ↔ 小禾(Hermes) ↔ 小猪(Claude Code)

基于共享 JSONL 文件的异步消息通道。
每条消息是 append-only JSON line，各 agent 各自维护 read_pointer。

用法:
  python3 message_bus.py send --from 小猪 --to 富富 --msg "数据管道已交付"
  python3 message_bus.py check --agent 小猪           # 查未读消息
  python3 message_bus.py read --agent 小猪 --to 富富  # 读指定人的消息
  python3 message_bus.py list                        # 列出最近消息
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

BUS_FILE = Path(os.path.expanduser("~/.openclaw/workspace/message_bus.jsonl"))
POINTER_DIR = Path(os.path.expanduser("~/.openclaw/workspace/.msg_pointers"))
TZ_SH = timezone(timedelta(hours=8))

AGENTS = {"富富": "OpenClaw 调度", "小禾": "Hermes 分析", "小猪": "Claude Code 执行"}


def _ensure():
    BUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    POINTER_DIR.mkdir(parents=True, exist_ok=True)
    if not BUS_FILE.exists():
        BUS_FILE.touch()


def _pointer_path(agent: str) -> Path:
    return POINTER_DIR / f"{agent}.pos"


def _read_pointer(agent: str) -> int:
    p = _pointer_path(agent)
    return int(p.read_text().strip()) if p.exists() else 0


def _write_pointer(agent: str, pos: int):
    _pointer_path(agent).write_text(str(pos))


def send_message(sender: str, to: str, content: str, urgent: bool = False) -> dict:
    """发送消息到总线"""
    _ensure()
    msg = {
        "ts": datetime.now(TZ_SH).isoformat(),
        "from": sender,
        "to": to,
        "urgent": urgent,
        "content": content,
    }
    with open(BUS_FILE, "a") as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    return msg


def check_messages(agent: str) -> list:
    """检查发给指定 agent 的未读消息"""
    _ensure()
    if not BUS_FILE.exists():
        return []

    last = _read_pointer(agent)
    messages = []
    with open(BUS_FILE) as f:
        for i, line in enumerate(f):
            if i < last:
                continue
            try:
                msg = json.loads(line.strip())
                if msg.get("to") == agent or msg.get("to") == "all":
                    messages.append({"line": i, **msg})
            except json.JSONDecodeError:
                continue

    return messages


def mark_read(agent: str):
    """标记 agent 的所有消息为已读"""
    _ensure()
    count = 0
    with open(BUS_FILE) as f:
        for count, _ in enumerate(f, 1):
            pass
    _write_pointer(agent, count)
    return count


def list_recent(n: int = 20):
    """列出最近 n 条消息"""
    _ensure()
    if not BUS_FILE.exists():
        return []
    lines = []
    with open(BUS_FILE) as f:
        for line in f:
            lines.append(line.strip())
    recent = lines[-n:]
    return [json.loads(l) for l in recent if l]


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(description="三方消息总线")
    sub = parser.add_subparsers(dest="cmd")

    send_p = sub.add_parser("send", help="发送消息")
    send_p.add_argument("--from", dest="sender", required=True)
    send_p.add_argument("--to", required=True)
    send_p.add_argument("--msg", required=True)
    send_p.add_argument("--urgent", action="store_true")

    sub.add_parser("check", help="检查未读").add_argument("--agent", required=True)
    read_p = sub.add_parser("read", help="读取消息")
    read_p.add_argument("--agent", required=True)
    read_p.add_argument("--to", default="")

    sub.add_parser("list", help="最近消息")
    sub.add_parser("ack", help="标记已读").add_argument("--agent", required=True)
    sub.add_parser("agents", help="列出 agents")

    args = parser.parse_args()

    if args.cmd == "send":
        r = send_message(args.sender, args.to, args.msg, args.urgent)
        print(json.dumps(r, ensure_ascii=False))

    elif args.cmd == "check":
        msgs = check_messages(args.agent)
        if not msgs:
            print("(无未读消息)")
        for m in msgs:
            urgent = "🔴" if m.get("urgent") else "📩"
            print(f"{urgent} [{m['ts'][:19]}] {m['from']} → {m['to']}: {m['content']}")

    elif args.cmd == "read":
        msgs = check_messages(args.agent)
        for m in msgs:
            if not args.to or m.get("from") == args.to or m.get("to") == args.to:
                print(f"[{m['ts'][:19]}] {m['from']} → {m['to']}: {m['content']}")

    elif args.cmd == "list":
        for m in list_recent(20):
            print(f"[{m['ts'][:19]}] {m['from']} → {m['to']}: {m['content'][:100]}")

    elif args.cmd == "ack":
        n = mark_read(args.agent)
        print(f"标记已读: {n} 条")

    elif args.cmd == "agents":
        for name, desc in AGENTS.items():
            print(f"  {name}: {desc}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
