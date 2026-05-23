#!/usr/bin/env python3
"""
ACP Hub — 本地多智能体实时通信中心
协议：REST + SSE，兼容 ACP 规范
端口：8700
角色：Hermes(小禾) 启动此服务，小猪 / 富富 作为客户端接入
"""

import json
import time
import threading
import queue
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
from datetime import datetime, timezone, timedelta
from pathlib import Path

PORT = 8700
TZ = timezone(timedelta(hours=8))

# === 消息存储 ===
# { agent_name: queue.Queue }
inboxes: dict[str, queue.Queue] = {}
# [{from, to, content, ts}]
message_log: list[dict] = []
# 在线状态
online_agents: dict[str, float] = {}  # agent_name -> last_heartbeat

MAX_MESSAGES = 500


def now():
    return datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00")


class ACPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 静默模式

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_sse(self, data):
        body = f"data: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Agent-Name")
        self.end_headers()

    def do_GET(self):
        from urllib.parse import unquote
        path = unquote(self.path.rstrip("/"))

        if path == "/agents":
            # 服务发现：返回在线 agent 列表
            agents = [
                {"name": name, "online": True, "last_seen": datetime.fromtimestamp(ts, tz=TZ).isoformat()}
                for name, ts in online_agents.items()
            ]
            self._send_json({"agents": agents})

        elif path.startswith("/agents/") and path.endswith("/listen"):
            # SSE 长连接：agent 监听自己的消息
            agent_name = path.split("/")[2]
            online_agents[agent_name] = time.time()

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            self.wfile.flush()

            if agent_name not in inboxes:
                inboxes[agent_name] = queue.Queue()

            q = inboxes[agent_name]
            # 发一条心跳确认连接
            self.wfile.write(f"data: {json.dumps({'type': 'connected', 'agent': agent_name, 'ts': now()})}\n\n".encode())
            self.wfile.flush()

            # 持续监听
            while True:
                try:
                    msg = q.get(timeout=30)
                    data = json.dumps({"type": "message", **msg}, ensure_ascii=False)
                    self.wfile.write(f"data: {data}\n\n".encode())
                    self.wfile.flush()
                except queue.Empty:
                    # 发心跳保持连接
                    self.wfile.write(f": heartbeat\n\n".encode())
                    self.wfile.flush()
                    online_agents[agent_name] = time.time()

        elif path.startswith("/messages/"):
            # 读取历史消息
            agent_name = path.split("/")[2]
            limit = 50
            msgs = [m for m in message_log if m["to"] == agent_name or m["from"] == agent_name][-limit:]
            self._send_json({"messages": msgs, "count": len(msgs)})

        else:
            self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        from urllib.parse import unquote
        path = unquote(self.path.rstrip("/"))
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len else b"{}"
        data = json.loads(body)

        if path == "/send":
            from_agent = data.get("from", "unknown")
            to_agent = data.get("to", "all")
            content = data.get("content", "")
            urgent = data.get("urgent", False)

            msg = {
                "from": from_agent,
                "to": to_agent,
                "content": content,
                "ts": now(),
                "urgent": urgent,
            }

            # 存日志
            message_log.append(msg)
            if len(message_log) > MAX_MESSAGES:
                message_log.pop(0)

            # 推送到目标 inbox
            targets = [to_agent] if to_agent != "all" else list(inboxes.keys())
            delivered = []
            for t in targets:
                if t in inboxes:
                    inboxes[t].put(msg)
                    delivered.append(t)
                elif t == "all":
                    continue
                else:
                    # 目标 agent 不在线，创建 inbox 暂存
                    inboxes[t] = queue.Queue()
                    inboxes[t].put(msg)
                    delivered.append(t)

            self._send_json({"status": "sent", "delivered_to": delivered, "ts": now()})

        elif path == "/heartbeat":
            agent_name = data.get("from", "unknown")
            online_agents[agent_name] = time.time()
            self._send_json({"status": "ok", "agent": agent_name, "ts": now()})

        elif path == "/mark_read":
            # 标记消息已读（简单实现：清除 inbox 中的旧消息）
            agent_name = data.get("from", "unknown")
            if agent_name in inboxes:
                # 不删除队列，只是确认存活
                pass
            self._send_json({"status": "ok"})

        else:
            self._send_json({"error": "not found"}, 404)


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), ACPHandler)
    print(f"ACP Hub 启动 → http://127.0.0.1:{PORT}")
    print(f"端点: GET /agents, POST /send, GET /agents/<name>/listen")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("ACP Hub 已停止")
        server.shutdown()


if __name__ == "__main__":
    main()
