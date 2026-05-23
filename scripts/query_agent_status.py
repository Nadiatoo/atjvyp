#!/usr/bin/env python3
"""Check whether agents are running — Hermes gateway, OpenClaw, Claude Code."""

import os
import sys
import json
import subprocess
import argparse


def check_process(name_pattern):
    """Check if a process matching pattern is running."""
    try:
        r = subprocess.run(
            ["pgrep", "-f", name_pattern],
            capture_output=True, text=True, timeout=5
        )
        pids = [p.strip() for p in r.stdout.strip().split("\n") if p.strip()]
        return {"running": len(pids) > 0, "pids": pids, "count": len(pids)}
    except Exception as e:
        return {"running": False, "error": str(e)}


def check_claude_tasks():
    """Check Claude Code task queue status."""
    tasks_dir = os.path.expanduser("~/.claude/tasks")
    result = {}

    for status_dir in ["inbox", "in_progress", "completed"]:
        path = os.path.join(tasks_dir, status_dir)
        if os.path.isdir(path):
            count = len([f for f in os.listdir(path) if f.endswith(".md")])
            result[status_dir] = count
        else:
            result[status_dir] = 0

    return result


def main():
    parser = argparse.ArgumentParser(description="Query agent status")
    parser.add_argument("--system", default="all",
                        choices=["hermes", "openclaw", "claude-code", "all"])
    parser.add_argument("--json", action="store_true", default=True,
                        help="Output as JSON (default)")
    args = parser.parse_args()

    results = {}

    if args.system in ("hermes", "all"):
        results["hermes"] = check_process("hermes.*gateway")

    if args.system in ("openclaw", "all"):
        results["openclaw"] = check_process("openclaw")

    if args.system in ("claude-code", "all"):
        cc = check_process("claude")
        cc["task_queue"] = check_claude_tasks()
        results["claude-code"] = cc

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
