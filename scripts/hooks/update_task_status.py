#!/usr/bin/env python3
"""Claude Code hook: Update task status when task moves between directories.
Triggered on PostToolUse for Bash (mv, cp) operations on task files,
or can be called directly to move a task file.
"""

import os
import sys
import json
import shutil
from datetime import datetime, timezone, timedelta

TASKS_DIR = os.path.expanduser("~/.claude/tasks")
INBOX = os.path.join(TASKS_DIR, "inbox")
IN_PROGRESS = os.path.join(TASKS_DIR, "in_progress")
COMPLETED = os.path.join(TASKS_DIR, "completed")
HERMES_BIN = os.path.expanduser("~/.local/bin/hermes")
TZ_SHANGHAI = timezone(timedelta(hours=8))


def update_frontmatter(filepath, updates):
    """Update YAML frontmatter fields in a task file."""
    if not os.path.exists(filepath):
        return False
    with open(filepath, "r") as f:
        content = f.read()

    for key, value in updates.items():
        # Replace existing field or add after last frontmatter field
        if f"{key}:" in content.split("---")[1] if "---" in content else "":
            import re
            content = re.sub(
                rf'^{key}:.*$',
                f'{key}: "{value}"',
                content,
                flags=re.MULTILINE
            )
        else:
            # Add before closing ---
            parts = content.split("---", 2)
            if len(parts) >= 2:
                parts[1] = parts[1].rstrip() + f'\n{key}: "{value}"\n'
                content = "---".join(parts)

    with open(filepath, "w") as f:
        f.write(content)
    return True


def move_task(task_file, from_dir, to_dir, new_status):
    """Move a task file between directories and update status."""
    src = os.path.join(from_dir, task_file)
    dst = os.path.join(to_dir, task_file)

    if not os.path.exists(src):
        return {"error": f"source not found: {src}"}

    # Update status in frontmatter
    update_frontmatter(src, {
        "status": new_status,
        "updated_at": datetime.now(TZ_SHANGHAI).isoformat()
    })

    # Move file
    os.makedirs(to_dir, exist_ok=True)
    shutil.move(src, dst)

    return {"moved": task_file, "from": from_dir, "to": to_dir, "status": new_status}


def main():
    if len(sys.argv) > 1:
        # Direct invocation: move a specific task
        action = sys.argv[1]
        if action == "start" and len(sys.argv) > 2:
            result = move_task(sys.argv[2], INBOX, IN_PROGRESS, "executing")
        elif action == "complete" and len(sys.argv) > 2:
            result = move_task(sys.argv[2], IN_PROGRESS, COMPLETED, "completed")
        elif action == "fail" and len(sys.argv) > 2:
            result = move_task(sys.argv[2], IN_PROGRESS, COMPLETED, "failed")
        else:
            result = {"error": f"unknown action: {action}"}
    else:
        # Hook mode: read stdin for hook input
        try:
            hook_input = json.load(sys.stdin)
        except Exception:
            hook_input = {}
        result = {"hook": "update_task_status", "input": hook_input}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
