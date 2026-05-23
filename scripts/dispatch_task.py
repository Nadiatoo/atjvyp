#!/usr/bin/env python3
"""Shared task dispatch utility — used by MCP server and cron scripts.
Dispatches tasks to Claude Code inbox or Hermes kanban.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone, timedelta

TZ_SHANGHAI = timezone(timedelta(hours=8))
CLAUDE_TASKS = os.path.expanduser("~/.claude/tasks")
HERMES_BIN = os.path.expanduser("~/.local/bin/hermes")


def dispatch_to_claude(title, description, priority="normal",
                       task_type="code_write", source="manual",
                       source_agent="", context_files=None):
    """Write a task file to Claude Code's inbox."""
    now = datetime.now(TZ_SHANGHAI)
    ts = now.strftime("%Y%m%d-%H%M%S")
    safe_title = "".join(c for c in title if c.isalnum() or c in "._-")[:40]
    task_id = f"{source[:8]}-{ts}"
    filename = f"{ts}-{task_id}.md"

    inbox_dir = os.path.join(CLAUDE_TASKS, "inbox")
    os.makedirs(inbox_dir, exist_ok=True)

    context_lines = "\n".join(f"- {f}" for f in (context_files or [])) or "(none)"

    content = f"""---
task_id: "{task_id}"
source: "{source}"
source_agent: "{source_agent}"
priority: "{priority}"
type: "{task_type}"
created_at: "{now.isoformat()}"
status: "pending"
context_refs: {json.dumps(context_files or [])}
---

# {title}

## Description
{description}

## Context Files
{context_lines}
"""
    filepath = os.path.join(inbox_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return {"task_id": task_id, "file": filepath, "status": "dispatched"}


def dispatch_to_hermes(title, description, priority="normal",
                       target_executor="claude-code"):
    """Dispatch task to Hermes kanban."""
    import subprocess
    try:
        result = subprocess.run(
            [HERMES_BIN, "kanban", "add",
             "--title", title,
             "--description", description,
             "--priority", priority,
             "--target", target_executor],
            capture_output=True, text=True, timeout=15
        )
        return {
            "status": "dispatched" if result.returncode == 0 else "failed",
            "output": result.stdout.strip() or result.stderr.strip()
        }
    except FileNotFoundError:
        return {"status": "error", "output": f"Hermes CLI not found at {HERMES_BIN}"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": "Command timed out"}


def main():
    parser = argparse.ArgumentParser(description="Dispatch tasks between agents")
    parser.add_argument("target", choices=["claude-code", "hermes"],
                        help="Target system")
    parser.add_argument("--title", required=True, help="Task title")
    parser.add_argument("--description", default="", help="Task description")
    parser.add_argument("--priority", default="normal",
                        choices=["critical", "high", "normal", "low"])
    parser.add_argument("--type", default="code_write",
                        choices=["code_write", "code_review", "data_analysis",
                                 "report_generate", "memory_update", "skill_improve"])
    parser.add_argument("--source", default="manual", help="Source system/agent")
    parser.add_argument("--source-agent", default="", help="Specific source agent")
    parser.add_argument("--context-files", nargs="*", default=[],
                        help="List of context file paths")
    parser.add_argument("--target-executor", default="claude-code",
                        help="Target executor for Hermes dispatch")

    args = parser.parse_args()

    if args.target == "claude-code":
        result = dispatch_to_claude(
            args.title, args.description, args.priority,
            args.type, args.source, args.source_agent,
            args.context_files
        )
    else:
        result = dispatch_to_hermes(
            args.title, args.description, args.priority,
            args.target_executor
        )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
