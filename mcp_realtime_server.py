#!/usr/bin/env python3
"""
MCP 实时通信服务器 — 桥接 WebSocket relay 与 Claude Code MCP 工具

工具:
  realtime_send    — 发送消息到指定 agent
  realtime_check   — 检查新消息（非阻塞）
  realtime_status  — 查看在线状态
"""

import asyncio
import json
import os
import sys
import signal
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import websockets
except ImportError:
    print(json.dumps({"error": "需要 websockets 包"}), flush=True)
    sys.exit(1)

HOST = os.environ.get("REALTIME_BUS_HOST", "127.0.0.1")
PORT = int(os.environ.get("REALTIME_BUS_PORT", "8765"))
AGENT = "小猪"
TZ_SH = timezone(timedelta(hours=8))

# 消息缓冲 — WebSocket 线程写入，MCP 主线程读取
incoming: list[dict] = []
online_agents: list[str] = []
ws_connected = False
_ws = None
_loop = None


def now() -> str:
    return datetime.now(TZ_SH).isoformat()


# ===========================================================================
# WebSocket 长连接（后台 asyncio 线程）
# ===========================================================================

async def _ws_connect():
    global ws_connected, online_agents, _ws
    uri = f"ws://{HOST}:{PORT}"
    backoff = 1

    while True:
        try:
            async with websockets.connect(uri, ping_interval=20) as ws:
                _ws = ws
                await ws.send(json.dumps({"agent": AGENT}, ensure_ascii=False))
                ack = await ws.recv()
                ack_data = json.loads(ack)

                if ack_data.get("type") == "catchup":
                    for msg in ack_data.get("messages", []):
                        incoming.append(msg)

                ws_connected = True
                backoff = 1

                async for raw in ws:
                    msg = json.loads(raw)

                    if msg.get("type") == "pong":
                        continue

                    if msg.get("type") == "system":
                        online_agents = msg.get("online", [])
                        continue

                    incoming.append(msg)

        except Exception:
            ws_connected = False
            _ws = None
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def _ws_send(msg: dict):
    global _ws
    if _ws and ws_connected:
        try:
            await _ws.send(json.dumps(msg, ensure_ascii=False))
            return True
        except Exception:
            return False
    return False


def _run_loop():
    global _loop
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)
    _loop.run_until_complete(_ws_connect())


# 启动后台线程
_ws_thread = threading.Thread(target=_run_loop, daemon=True)
_ws_thread.start()


# ===========================================================================
# MCP 工具处理
# ===========================================================================

def handle_realtime_send(args: dict) -> dict:
    """发送消息"""
    to = args.get("to", "all")
    content = args.get("content", "")
    urgent = args.get("urgent", False)

    msg = {
        "to": to,
        "content": content,
        "urgent": urgent,
        "type": "message",
    }

    # 异步发送
    future = asyncio.run_coroutine_threadsafe(_ws_send(msg), _loop) if _loop else None
    sent = future.result(timeout=5) if future else False

    # 兜底: 写文件总线
    bus_file = Path.home() / ".openclaw/workspace/message_bus.jsonl"
    bus_file.parent.mkdir(parents=True, exist_ok=True)
    envelope = {
        "from": AGENT,
        "to": to,
        "content": content,
        "urgent": urgent,
        "ts": now(),
    }
    with open(bus_file, "a") as f:
        f.write(json.dumps(envelope, ensure_ascii=False) + "\n")

    return {
        "sent": sent or True,  # 文件兜底总是成功
        "via": "ws" if sent else "file",
        "to": to,
        "ts": now(),
    }


def handle_realtime_check(args: dict) -> dict:
    """检查新消息"""
    limit = args.get("limit", 10)
    msgs = []
    while incoming and len(msgs) < limit:
        msgs.append(incoming.pop(0))

    return {
        "agent": AGENT,
        "online": online_agents,
        "ws_connected": ws_connected,
        "unread": len(msgs),
        "messages": msgs[-limit:],
        "ts": now(),
    }


def handle_realtime_status(args: dict) -> dict:
    """查看状态"""
    return {
        "agent": AGENT,
        "online": online_agents,
        "ws_connected": ws_connected,
        "buffer_size": len(incoming),
        "ts": now(),
    }


# ===========================================================================
# MCP stdio 主循环
# ===========================================================================

TOOLS = [
    {
        "name": "realtime_send",
        "description": "通过 WebSocket 实时通道发送消息给富富(OpenClaw)或小禾(Hermes)。毫秒级送达。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "目标 agent: 富富 / 小禾 / all"},
                "content": {"type": "string", "description": "消息内容"},
                "urgent": {"type": "boolean", "default": False},
            },
            "required": ["to", "content"],
        },
    },
    {
        "name": "realtime_check",
        "description": "检查 WebSocket 实时通道中的新消息。非阻塞，返回缓冲中的未读消息。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 10},
            },
        },
    },
    {
        "name": "realtime_status",
        "description": "查看实时通信状态：在线 agent 列表、连接状态、消息缓冲。",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = req.get("method", "")
        rid = req.get("id", 0)

        if method == "initialize":
            print(json.dumps({
                "jsonrpc": "2.0", "id": rid,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "realtime-bus-mcp", "version": "1.0"},
                    "capabilities": {"tools": {}},
                }
            }), flush=True)

        elif method == "tools/list":
            print(json.dumps({
                "jsonrpc": "2.0", "id": rid,
                "result": {"tools": TOOLS},
            }), flush=True)

        elif method == "tools/call":
            name = req.get("params", {}).get("name", "")
            args = req.get("params", {}).get("arguments", {})

            handlers = {
                "realtime_send": handle_realtime_send,
                "realtime_check": handle_realtime_check,
                "realtime_status": handle_realtime_status,
            }

            handler = handlers.get(name)
            if handler:
                try:
                    result = handler(args)
                    print(json.dumps({
                        "jsonrpc": "2.0", "id": rid,
                        "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]},
                    }), flush=True)
                except Exception as e:
                    print(json.dumps({
                        "jsonrpc": "2.0", "id": rid,
                        "result": {"content": [{"type": "text", "text": f"错误: {e}"}], "isError": True},
                    }), flush=True)
            else:
                print(json.dumps({
                    "jsonrpc": "2.0", "id": rid,
                    "result": {"content": [{"type": "text", "text": f"未知工具: {name}"}], "isError": True},
                }), flush=True)


if __name__ == "__main__":
    main()
