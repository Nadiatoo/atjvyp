#!/usr/bin/env python3
"""Claude Code hook: After file write/edit, sync significant learnings to ClawMem.
Triggers on PostToolUse for Write/Edit tools.
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timezone, timedelta

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
CROSS_SYSTEM = os.path.join(WORKSPACE, ".learnings", "CROSS_SYSTEM.md")
TZ_SHANGHAI = timezone(timedelta(hours=8))

def main():
    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, Exception):
        hook_input = {}

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    # Only track Write and Edit operations that modify files
    if tool_name not in ("Write", "Edit"):
        print(json.dumps({"skipped": True, "reason": f"not a Write/Edit operation ({tool_name})"}))
        return 0

    file_path = tool_input.get("file_path", "")
    if not file_path:
        print(json.dumps({"skipped": True, "reason": "no file_path"}))
        return 0

    # Log the modification for potential learning capture
    now = datetime.now(TZ_SHANGHAI)
    entry = {
        "timestamp": now.isoformat(),
        "tool": tool_name,
        "file": file_path,
        "action": "file_modified"
    }

    # Check if this is a significant file worth logging
    significant_dirs = [
        ".openclaw/workspace/scripts",
        ".openclaw/skills",
        ".hermes/hermes-agent",
        ".openclaw/workspace/config"
    ]

    is_significant = any(sig in file_path for sig in significant_dirs)

    if is_significant:
        # Append to cross-system log
        today = now.strftime("%Y-%m-%d")
        log_entry = f"| {today} | claude-code | technical | Modified `{os.path.basename(file_path)}` | pending | — |\n"

        os.makedirs(os.path.dirname(CROSS_SYSTEM), exist_ok=True)
        if os.path.exists(CROSS_SYSTEM):
            with open(CROSS_SYSTEM, "a") as f:
                f.write(log_entry)

    output = {"captured": is_significant, "file": file_path, "entry": entry}
    print(json.dumps(output, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
