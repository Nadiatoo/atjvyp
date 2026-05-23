#!/usr/bin/env python3
"""Claude Code hook: Inject relevant ClawMem context before Write/Edit operations.
Checks current task from in_progress/ and searches memory for related context.
"""

import os
import sys
import json

TASKS_DIR = os.path.expanduser("~/.claude/tasks")
IN_PROGRESS = os.path.join(TASKS_DIR, "in_progress")

def main():
    # Find current in-progress task
    task_context = None
    if os.path.isdir(IN_PROGRESS):
        tasks = sorted(
            [f for f in os.listdir(IN_PROGRESS) if f.endswith(".md")],
            reverse=True
        )
        if tasks:
            task_file = os.path.join(IN_PROGRESS, tasks[0])
            with open(task_file, "r") as f:
                content = f.read()
            # Extract key fields from YAML frontmatter
            for line in content.split("\n"):
                if line.startswith("task_id:"):
                    task_context = {"task_file": task_file, "task_id": line.split('"')[1] if '"' in line else line.split(":")[1].strip()}
                    break

    output = {"task_context": task_context, "note": "Memory context check — see CLAUDE.md for memory_search usage"}
    print(json.dumps(output, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
