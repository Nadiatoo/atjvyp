#!/usr/bin/env python3
"""
ACP Client CLI — 连接 ACP Hub 发送/接收消息
用法:
  python3 acp_client.py send --from 小猪 --to 小禾 --msg "内容"
  python3 acp_client.py check --agent 小猪
  python3 acp_client.py agents
  python3 acp_client.py heartbeat --agent 小猪
"""

import json
import sys
import argparse
import urllib.request
import urllib.error
import urllib.parse

HUB = "http://127.0.0.1:8700"


def _safe_path(path):
    """URL-encode 中文路径"""
    return urllib.parse.quote(path, safe="/")


def _request(method, path, body=None):
    url = f"{HUB}{_safe_path(path)}"
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as e:
        print(json.dumps({"error": f"Hub 不可达: {e.reason}"}, ensure_ascii=False))
        sys.exit(1)


def cmd_send(args):
    body = {"from": args.from_agent, "to": args.to, "content": args.msg}
    if args.urgent:
        body["urgent"] = True
    result = _request("POST", "/send", body=body)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_check(args):
    msgs = _request("GET", f"/messages/{args.agent}")
    unread = msgs.get("messages", [])
    if not unread:
        print("(无消息)")
    else:
        for m in unread:
            mark = "🔴" if m.get("urgent") else "📩"
            print(f"{mark} [{m['ts'][:19]}] {m['from']} → {m['to']}: {m['content']}")
        print(f"\n共 {len(unread)} 条")


def cmd_agents(args):
    result = _request("GET", "/agents")
    agents = result.get("agents", [])
    if not agents:
        print("(无在线 agent)")
    else:
        for a in agents:
            print(f"  🟢 {a['name']} (活跃: {a['last_seen'][:19]})")


def cmd_heartbeat(args):
    body = {"from": args.agent}
    result = _request("POST", "/heartbeat", body=body)
    print(json.dumps(result, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="ACP Client")
    sub = parser.add_subparsers(dest="cmd")

    p_send = sub.add_parser("send")
    p_send.add_argument("--from", dest="from_agent", required=True)
    p_send.add_argument("--to", required=True)
    p_send.add_argument("--msg", required=True)
    p_send.add_argument("--urgent", action="store_true")

    p_check = sub.add_parser("check")
    p_check.add_argument("--agent", required=True)

    p_agents = sub.add_parser("agents")

    p_hb = sub.add_parser("heartbeat")
    p_hb.add_argument("--agent", required=True)

    args = parser.parse_args()
    if args.cmd == "send":
        cmd_send(args)
    elif args.cmd == "check":
        cmd_check(args)
    elif args.cmd == "agents":
        cmd_agents(args)
    elif args.cmd == "heartbeat":
        cmd_heartbeat(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
