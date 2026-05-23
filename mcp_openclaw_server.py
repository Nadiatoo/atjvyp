#!/usr/bin/env python3
"""MCP server exposing OpenClaw workspace tools to other agents (Hermes)."""

import json
import os
import subprocess
import sys
import glob
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
LEARNINGS_DIR = os.path.join(WORKSPACE, ".learnings")
CLAUDE_TASKS_DIR = os.path.expanduser("~/.claude/tasks")
HERMES_BIN = os.path.expanduser("~/.local/bin/hermes")

TZ_SHANGHAI = timezone(timedelta(hours=8))

def handle_list_tools():
    return {
        "tools": [
            {
                "name": "read_memory",
                "description": "Read daily memory files from OpenClaw workspace",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "Date in YYYY-MM-DD format. Omit for latest."
                        }
                    }
                }
            },
            {
                "name": "list_memory_files",
                "description": "List available daily memory files",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "number",
                            "description": "Max files to return (default 10)"
                        }
                    }
                }
            },
            {
                "name": "read_workspace_file",
                "description": "Read any file from the OpenClaw workspace",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path from workspace root"
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "list_workspace_files",
                "description": "List files in workspace directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path from workspace root"
                        }
                    }
                }
            },
            {
                "name": "run_shell",
                "description": "Run a shell command and get output",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Shell command to run"
                        }
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "read_learnings",
                "description": "Read self-improving system learning records",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file": {
                            "type": "string",
                            "enum": ["LEARNINGS.md", "ERRORS.md", "FEATURE_REQUESTS.md"],
                            "description": "Which learning file to read"
                        }
                    },
                    "required": ["file"]
                }
            },
            {
                "name": "dispatch_task_to_claude_code",
                "description": "Write a structured task to Claude Code's inbox for execution",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title (short summary)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Full task description with acceptance criteria"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["critical", "high", "normal", "low"],
                            "description": "Task priority level"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["code_write", "code_review", "data_analysis", "report_generate", "memory_update", "skill_improve"],
                            "description": "Type of work"
                        },
                        "source": {
                            "type": "string",
                            "description": "Source system (openclaw or hermes)"
                        },
                        "source_agent": {
                            "type": "string",
                            "description": "Name of the agent creating this task"
                        },
                        "context_files": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of file paths for context"
                        }
                    },
                    "required": ["title", "description", "source"]
                }
            },
            {
                "name": "dispatch_task_to_hermes",
                "description": "Dispatch a task to Hermes kanban/queue for planning and orchestration",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Task description"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["critical", "high", "normal", "low"],
                            "description": "Priority"
                        },
                        "target_executor": {
                            "type": "string",
                            "description": "Target executor (claude-code, market_analyst, etc.)"
                        }
                    },
                    "required": ["title", "description"]
                }
            },
            {
                "name": "write_workspace_file",
                "description": "Write content to a file in the OpenClaw workspace",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path from workspace root"
                        },
                        "content": {
                            "type": "string",
                            "description": "File content to write"
                        }
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "query_agent_status",
                "description": "Check if agents are running (Hermes gateway, Claude Code)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "system_name": {
                            "type": "string",
                            "enum": ["hermes", "claude-code", "openclaw", "all"],
                            "description": "Which system to check"
                        }
                    }
                }
            },
            {
                "name": "message_bus_send",
                "description": "Send a message to another agent via the shared message bus. Use for real-time coordination between 富富/小禾/小猪.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "from": {
                            "type": "string",
                            "description": "Sender name (富富/小禾/小猪)"
                        },
                        "to": {
                            "type": "string",
                            "description": "Recipient (富富/小禾/小猪/all)"
                        },
                        "message": {
                            "type": "string",
                            "description": "Message content"
                        },
                        "urgent": {
                            "type": "boolean",
                            "description": "Mark as urgent (default false)"
                        }
                    },
                    "required": ["from", "to", "message"]
                }
            },
            {
                "name": "message_bus_check",
                "description": "Check unread messages for an agent from the shared message bus",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent": {
                            "type": "string",
                            "description": "Agent name to check messages for (富富/小禾/小猪)"
                        }
                    },
                    "required": ["agent"]
                }
            }
        ]
    }

def handle_call_tool(name, args):
    if name == "list_memory_files":
        limit = args.get("limit", 10)
        files = sorted(glob.glob(os.path.join(MEMORY_DIR, "*.md")), reverse=True)[:limit]
        result = []
        for f in files:
            fname = os.path.basename(f)
            size = os.path.getsize(f)
            result.append({"name": fname, "size": size})
        return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]}

    elif name == "read_memory":
        date = args.get("date")
        if date:
            target = os.path.join(MEMORY_DIR, f"{date}.md")
        else:
            files = sorted(glob.glob(os.path.join(MEMORY_DIR, "*.md")), reverse=True)
            target = files[0] if files else None
        if target and os.path.exists(target):
            with open(target, "r", encoding="utf-8") as f:
                content = f.read()
            return {"content": [{"type": "text", "text": content[:8000]}]}
        return {"content": [{"type": "text", "text": "File not found"}]}

    elif name == "read_workspace_file":
        rel_path = args.get("path", "")
        full_path = os.path.normpath(os.path.join(WORKSPACE, rel_path))
        if not full_path.startswith(WORKSPACE):
            return {"content": [{"type": "text", "text": "Access denied: path outside workspace"}]}
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"content": [{"type": "text", "text": content[:10000]}]}
        return {"content": [{"type": "text", "text": "File not found"}]}

    elif name == "list_workspace_files":
        rel_path = args.get("path", "")
        full_path = os.path.normpath(os.path.join(WORKSPACE, rel_path))
        if not full_path.startswith(WORKSPACE):
            return {"content": [{"type": "text", "text": "Access denied: path outside workspace"}]}
        if os.path.isdir(full_path):
            items = os.listdir(full_path)
            result = [{"name": f, "is_dir": os.path.isdir(os.path.join(full_path, f))} for f in items]
            return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]}

    elif name == "run_shell":
        cmd = args.get("command", "")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15, cwd=WORKSPACE)
            output = result.stdout[-5000:] if len(result.stdout) > 5000 else result.stdout
            if result.stderr:
                output += "\n--- stderr ---\n" + result.stderr[-2000:]
            return {"content": [{"type": "text", "text": output or "(no output)"}]}
        except subprocess.TimeoutExpired:
            return {"content": [{"type": "text", "text": "Command timed out"}]}

    elif name == "read_learnings":
        fname = args.get("file", "LEARNINGS.md")
        target = os.path.join(LEARNINGS_DIR, fname)
        if os.path.exists(target):
            with open(target, "r", encoding="utf-8") as f:
                content = f.read()
            return {"content": [{"type": "text", "text": content[:8000]}]}
        return {"content": [{"type": "text", "text": "File not found"}]}

    elif name == "dispatch_task_to_claude_code":
        title = args.get("title", "Untitled")
        description = args.get("description", "")
        priority = args.get("priority", "normal")
        task_type = args.get("type", "code_write")
        source = args.get("source", "unknown")
        source_agent = args.get("source_agent", "")
        context_files = args.get("context_files", [])

        now = datetime.now(TZ_SHANGHAI)
        ts = now.strftime("%Y%m%d-%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in "._-")[:40]
        task_id = f"{source[:8]}-{ts}"
        filename = f"{ts}-{task_id}.md"

        inbox_dir = os.path.join(CLAUDE_TASKS_DIR, "inbox")
        os.makedirs(inbox_dir, exist_ok=True)

        context_lines = "\n".join(f"- {f}" for f in context_files) if context_files else "(none)"

        content = f"""---
task_id: "{task_id}"
source: "{source}"
source_agent: "{source_agent}"
priority: "{priority}"
type: "{task_type}"
created_at: "{now.isoformat()}"
status: "pending"
context_refs: {json.dumps(context_files)}
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

        return {"content": [{"type": "text", "text": json.dumps({
            "status": "dispatched",
            "task_id": task_id,
            "file": filepath,
            "inbox": inbox_dir
        }, ensure_ascii=False, indent=2)}]}

    elif name == "dispatch_task_to_hermes":
        title = args.get("title", "Untitled")
        description = args.get("description", "")
        priority = args.get("priority", "normal")
        target = args.get("target_executor", "claude-code")

        try:
            result = subprocess.run(
                [HERMES_BIN, "kanban", "add",
                 "--title", title,
                 "--description", description,
                 "--priority", priority,
                 "--target", target],
                capture_output=True, text=True, timeout=15
            )
            return {"content": [{"type": "text", "text": json.dumps({
                "status": "dispatched" if result.returncode == 0 else "failed",
                "output": result.stdout.strip() or result.stderr.strip(),
                "exit_code": result.returncode
            }, ensure_ascii=False, indent=2)}]}
        except subprocess.TimeoutExpired:
            return {"content": [{"type": "text", "text": "Hermes kanban command timed out"}]}
        except FileNotFoundError:
            return {"content": [{"type": "text", "text": f"Hermes CLI not found at {HERMES_BIN}"}]}

    elif name == "write_workspace_file":
        rel_path = args.get("path", "")
        content = args.get("content", "")

        full_path = os.path.normpath(os.path.join(WORKSPACE, rel_path))
        if not full_path.startswith(WORKSPACE):
            return {"content": [{"type": "text", "text": "Access denied: path outside workspace"}]}

        # Prevent overwriting critical config files
        dangerous = [".git", "config/agents.json", "config/mcporter.json", "mcp_openclaw_server.py"]
        rel_norm = os.path.relpath(full_path, WORKSPACE)
        if any(rel_norm.startswith(d) for d in dangerous):
            return {"content": [{"type": "text", "text": f"Write blocked: protected path ({rel_norm})"}]}

        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        return {"content": [{"type": "text", "text": json.dumps({
            "status": "written",
            "path": rel_norm,
            "size": len(content)
        }, ensure_ascii=False, indent=2)}]}

    elif name == "query_agent_status":
        system = args.get("system_name", "all")
        results = {}

        # Check Hermes gateway
        if system in ("hermes", "all"):
            try:
                r = subprocess.run(
                    ["pgrep", "-f", "hermes.*gateway"],
                    capture_output=True, text=True, timeout=5
                )
                pids = [p.strip() for p in r.stdout.strip().split("\n") if p.strip()]
                results["hermes"] = {
                    "running": len(pids) > 0,
                    "pids": pids,
                    "count": len(pids)
                }
            except Exception:
                results["hermes"] = {"running": False, "error": "check failed"}

        # Check Claude Code
        if system in ("claude-code", "all"):
            try:
                r = subprocess.run(
                    ["pgrep", "-f", "claude"],
                    capture_output=True, text=True, timeout=5
                )
                pids = [p.strip() for p in r.stdout.strip().split("\n") if p.strip()]
                # Also check for task files
                inbox = os.path.join(CLAUDE_TASKS_DIR, "inbox")
                inbox_count = 0
                completed_count = 0
                if os.path.isdir(inbox):
                    inbox_count = len([f for f in os.listdir(inbox) if f.endswith(".md")])
                completed_dir = os.path.join(CLAUDE_TASKS_DIR, "completed")
                if os.path.isdir(completed_dir):
                    completed_count = len([f for f in os.listdir(completed_dir) if f.endswith(".md")])
                results["claude-code"] = {
                    "running": len(pids) > 0,
                    "pids": pids,
                    "tasks_pending": inbox_count,
                    "tasks_completed": completed_count
                }
            except Exception:
                results["claude-code"] = {"running": False, "error": "check failed"}

        # Check OpenClaw gateway
        if system in ("openclaw", "all"):
            try:
                r = subprocess.run(
                    ["pgrep", "-f", "openclaw"],
                    capture_output=True, text=True, timeout=5
                )
                pids = [p.strip() for p in r.stdout.strip().split("\n") if p.strip()]
                results["openclaw"] = {
                    "running": len(pids) > 0,
                    "pids": pids
                }
            except Exception:
                results["openclaw"] = {"running": False, "error": "check failed"}

        return {"content": [{"type": "text", "text": json.dumps(results, ensure_ascii=False, indent=2)}]}

    elif name == "message_bus_send":
        sender = args.get("from", "unknown")
        to = args.get("to", "all")
        msg_text = args.get("message", "")
        urgent = args.get("urgent", False)

        bus_file = os.path.expanduser("~/.openclaw/workspace/message_bus.jsonl")
        os.makedirs(os.path.dirname(bus_file), exist_ok=True)

        entry = {
            "ts": datetime.now(TZ_SHANGHAI).isoformat(),
            "from": sender,
            "to": to,
            "urgent": urgent,
            "content": msg_text,
        }
        with open(bus_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return {"content": [{"type": "text", "text": json.dumps({
            "status": "sent",
            "to": to,
            "ts": entry["ts"]
        }, ensure_ascii=False)}]}

    elif name == "message_bus_check":
        agent = args.get("agent", "")
        bus_file = os.path.expanduser("~/.openclaw/workspace/message_bus.jsonl")
        pointer_file = os.path.expanduser(f"~/.openclaw/workspace/.msg_pointers/{agent}.pos")

        if not os.path.exists(bus_file):
            return {"content": [{"type": "text", "text": "(无消息)"}]}

        last_pos = 0
        if os.path.exists(pointer_file):
            with open(pointer_file) as f:
                last_pos = int(f.read().strip() or 0)

        messages = []
        with open(bus_file, encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i < last_pos:
                    continue
                try:
                    msg = json.loads(line.strip())
                    if msg.get("to") in (agent, "all"):
                        messages.append(msg)
                except json.JSONDecodeError:
                    continue

        return {"content": [{"type": "text", "text": json.dumps({
            "agent": agent,
            "unread": len(messages),
            "messages": messages[-20:]
        }, ensure_ascii=False, indent=2)}]}

    return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}]}

def main():
    import sys
    import json

    # MCP stdio protocol
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue

        msg_id = msg.get("id")
        method = msg.get("method")
        params = msg.get("params", {})

        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "openclaw-workspace", "version": "1.0.0"},
                    "capabilities": {"tools": {}}
                }
            }
        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": handle_list_tools()
            }
        elif method == "tools/call":
            result = handle_call_tool(params.get("name"), params.get("arguments", {}))
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": result
            }
        elif method == "notifications/initialized":
            continue
        else:
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }

        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
