#!/usr/bin/env python3
"""
小C 后台守护进程 — 每 5 分钟检查消息总线和任务收件箱
如果发现紧急消息或积压任务，触发自动处理

FIX 2026-05-23: 处理完后将 inbox .md 文件移入 processed/ 子目录，
避免每5分钟重复处理同一批任务导致 token 狂烧。
"""

import json
import os
import sys
import subprocess
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

HOME = Path.home()
BUS_FILE = HOME / ".openclaw/workspace/message_bus.jsonl"
POINTER_FILE = HOME / ".openclaw/workspace/.msg_pointers/小C.pos"
TASKS_INBOX = HOME / ".claude/tasks/inbox"
TASKS_PROCESSED = TASKS_INBOX / "processed"
PENDING_LOG = HOME / ".openclaw/workspace/daemon/pending.json"
TZ_SH = timezone(timedelta(hours=8))

# FIX: 已处理文件指纹缓存，防止重复提交同一批任务
PROCESSED_FINGERPRINTS_FILE = HOME / ".openclaw/workspace/daemon/processed_fingerprints.json"


def load_processed_fingerprints() -> set:
    """加载已处理的文件指纹"""
    if PROCESSED_FINGERPRINTS_FILE.exists():
        try:
            return set(json.loads(PROCESSED_FINGERPRINTS_FILE.read_text()))
        except (json.JSONDecodeError, TypeError):
            return set()
    return set()


def save_processed_fingerprints(fingerprints: set):
    """保存已处理的文件指纹"""
    PROCESSED_FINGERPRINTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_FINGERPRINTS_FILE.write_text(json.dumps(list(fingerprints), ensure_ascii=False))


def file_fingerprint(path: Path) -> str:
    """计算文件指纹（文件名 + 前256字节内容）"""
    content = path.read_bytes()[:256]
    return hashlib.sha256(content + path.name.encode()).hexdigest()


def check_bus() -> list:
    """检查 ACP bridge 缓存的入站消息"""
    queue_file = HOME / ".claude" / "comms" / "acp_inbox.jsonl"
    if not queue_file.exists():
        return []

    messages = []
    lines = queue_file.read_text().splitlines()
    queue_file.write_text("")  # 清空已读
    for line in lines[-50:]:
        try:
            msg = json.loads(line)
            if msg.get("to") in ("小猪", "小C", "all") or msg.get("from") in ("小禾",):
                messages.append(msg)
        except json.JSONDecodeError:
            continue
    return messages


def check_tasks() -> list:
    """检查任务收件箱（排除已处理过的文件指纹）"""
    if not TASKS_INBOX.exists():
        return []
    processed_fps = load_processed_fingerprints()
    all_tasks = []
    for f in TASKS_INBOX.iterdir():
        if f.suffix != ".md":
            continue
        # FIX: 跳过已处理的文件
        fp = file_fingerprint(f)
        if fp in processed_fps:
            continue
        all_tasks.append(f.name)
    return sorted(all_tasks)


def archive_processed_tasks(processed_names: list):
    """FIX: 将已处理的 inbox 文件移入 processed/ 子目录"""
    TASKS_PROCESSED.mkdir(parents=True, exist_ok=True)
    fps = load_processed_fingerprints()
    for name in processed_names:
        src = TASKS_INBOX / name
        if src.exists():
            # 记录指纹
            fp = file_fingerprint(src)
            fps.add(fp)
            # 移走
            dst = TASKS_PROCESSED / name
            src.rename(dst)
    save_processed_fingerprints(fps)


def main():
    now = datetime.now(TZ_SH)
    msgs = check_bus()
    tasks = check_tasks()

    has_urgent = any(m.get("urgent") for m in msgs)
    has_backlog = len(tasks) > 3
    has_any = len(msgs) > 0 or len(tasks) > 0

    status = {
        "ts": now.isoformat(),
        "messages_unread": len(msgs),
        "urgent": has_urgent,
        "tasks_pending": len(tasks),
        "backlog": has_backlog,
        "agent_online": False,
    }

    # Write pending log for Claude Code to read on startup
    if has_any:
        status["latest_messages"] = [
            {"from": m["from"], "content": m["content"][:200], "urgent": m.get("urgent", False)}
            for m in msgs[-5:]
        ]
        status["latest_tasks"] = tasks[-5:]

    PENDING_LOG.parent.mkdir(parents=True, exist_ok=True)
    PENDING_LOG.write_text(json.dumps(status, ensure_ascii=False, indent=2))

    # 所有消息自动触发 Claude Code 处理
    if has_any:
        print(f"[{now:%H:%M}] 📩 消息:{len(msgs)} 任务:{len(tasks)} — 自动处理...")
        prompt = "你是小猪(Claude Code)。以下消息和任务需要处理。\n\n"
        for m in msgs[-5:]:
            prompt += f"**{m.get('from', m.get('source_agent', 'unknown'))}**: {m.get('content', '')[:500]}\n\n"
        for t in tasks[-3:]:
            prompt += f"任务文件: ~/.claude/tasks/inbox/{t}\n"
        prompt += "\n处理完后，用 hermes_send MCP tool 回复小禾。"
        try:
            subprocess.run(
                ["claude", "-p", prompt],
                cwd=str(HOME / ".openclaw/workspace"),
                timeout=600,
            )
            # FIX: 处理完后归档 inbox 文件，避免下次重复处理
            archive_processed_tasks(tasks)
        except subprocess.TimeoutExpired:
            print(f"[{now:%H:%M}] ⚠️ 自动处理超时")
        except FileNotFoundError:
            print(f"[{now:%H:%M}] ⚠️ claude CLI 未找到")

    elif has_backlog:
        print(f"[{now:%H:%M}] ⚠️ 任务积压: {len(tasks)} 个, 消息: {len(msgs)} 条")
        subprocess.run([
            "osascript", "-e",
            f'display notification "任务:{len(tasks)} 消息:{len(msgs)}" with title "小C 待处理"'
        ], timeout=5)

    elif has_any:
        print(f"[{now:%H:%M}] 📩 消息:{len(msgs)} 任务:{len(tasks)} — 等待下次会话处理")

    else:
        print(f"[{now:%H:%M}] ✅ 无待办")


if __name__ == "__main__":
    main()
