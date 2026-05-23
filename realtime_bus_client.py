#!/usr/bin/env python3
"""
三体通信客户端 — 供 富富/小禾/小猪 连接 WebSocket relay

用法:
  python3 realtime_bus_client.py --agent 小猪          # 交互模式
  python3 realtime_bus_client.py --agent 小猪 --print  # 后台模式
  python3 realtime_bus_client.py --agent 富富 --send '{"to":"小禾","content":"test"}'

兼容: 完全兼容现有 message_bus.py 的消息格式
"""

import asyncio
import json
import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import websockets
except ImportError:
    print("需要 websockets: pip3 install --break-system-packages websockets")
    sys.exit(1)

HOST = os.environ.get("REALTIME_BUS_HOST", "127.0.0.1")
PORT = int(os.environ.get("REALTIME_BUS_PORT", "8765"))
TZ_SH = timezone(timedelta(hours=8))


def now() -> str:
    return datetime.now(TZ_SH).isoformat()


async def connect_and_listen(agent: str, print_mode: bool = False):
    """长连接模式 — 持续监听消息"""
    uri = f"ws://{HOST}:{PORT}"
    backoff = 1

    while True:
        try:
            async with websockets.connect(uri, ping_interval=20) as ws:
                # 握手
                await ws.send(json.dumps({"agent": agent}, ensure_ascii=False))
                ack = await ws.recv()
                ack_data = json.loads(ack)

                if "error" in ack_data:
                    print(f"❌ {ack_data['error']}", file=sys.stderr)
                    return

                if ack_data.get("type") == "catchup":
                    for msg in ack_data.get("messages", []):
                        print(f"[补发] {msg.get('from')}→{msg.get('to')}: {msg.get('content','')[:100]}", file=sys.stderr)

                backoff = 1  # reset on success

                # 消息循环
                async for raw in ws:
                    msg = json.loads(raw)

                    if msg.get("type") == "pong":
                        continue
                    if msg.get("type") == "system":
                        event = msg.get("event", "?")
                        agent_name = msg.get("agent", "?")
                        online = msg.get("online", [])
                        if event == "join":
                            print(f"[{now()}] ✅ {agent_name} 上线 | 在线: {online}", file=sys.stderr)
                        elif event == "leave":
                            print(f"[{now()}] 👋 {agent_name} 下线 | 在线: {online}", file=sys.stderr)
                        continue

                    # 标准消息
                    sender = msg.get("from", "?")
                    content = msg.get("content", "")
                    print(f"[{now()}] 📩 {sender} → {agent}: {content}")

        except (websockets.exceptions.ConnectionClosed, OSError) as e:
            print(f"[{now()}] ⚠️ 连接断开: {e}，{backoff}s 后重连...", file=sys.stderr)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)  # 指数退避，最大 60s


async def send_one(agent: str, to: str, content: str, urgent: bool = False):
    """单次发送模式"""
    uri = f"ws://{HOST}:{PORT}"
    try:
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({"agent": agent}, ensure_ascii=False))
            await ws.recv()  # ack

            msg = {
                "to": to,
                "content": content,
                "urgent": urgent,
                "type": "message",
            }
            await ws.send(json.dumps(msg, ensure_ascii=False))
            print(json.dumps({"status": "sent", "to": to, "ts": now()}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(description="三体通信客户端")
    parser.add_argument("--agent", required=True, choices=["富富", "小禾", "小猪"])
    parser.add_argument("--send", help="发送消息: JSON {to, content, urgent?}")
    parser.add_argument("--print", action="store_true", help="后台模式（输出到 stdout）")
    args = parser.parse_args()

    if args.send:
        data = json.loads(args.send)
        await send_one(
            agent=args.agent,
            to=data.get("to", "all"),
            content=data.get("content", ""),
            urgent=data.get("urgent", False),
        )
    else:
        print(f"[{now()}] 🔌 {args.agent} 连接 ws://{HOST}:{PORT} ...", file=sys.stderr)
        await connect_and_listen(args.agent, print_mode=args.print)


if __name__ == "__main__":
    asyncio.run(main())
