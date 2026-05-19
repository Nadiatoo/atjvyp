# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

### Agent Team
- 📈 富富 → OpenClaw main agent, 指挥部，管调度+推送
- 🌾 小禾 → Hermes, 参谋部，管深度分析+记忆
- 🐷 小猪（原名小C） → Claude Code, 工程部，管代码+回测

### 整合架构
- **MCP通道**：小猪通过MCP同时连富富和小禾（~/.mcp.json）
- **任务队列**：富富/小禾写task到 ~/.claude/tasks/inbox/ → 小猪处理 → 结果写回 completed/
- **共享记忆**：CROSS_SYSTEM.md 记录三方共享信息
- **ACP通信**：使用 OpenClaw ACP 通道（sessions_send / sessions_spawn runtime="acp"）

### 协作流程
```
【定时分析】富富cron触发 → 采集数据 → 写task给小猪 → 小猪转小禾分析 → 结果回传富富 → 推送
【即时问答】富富收到需求 → ACP呼叫小禾深度分析 → 结果回传富富 → 推送
【工程需求】富富收到需求 → 写task给小猪 → 小猪实现 → 结果回传
【实时通信】每次醒来先查Hub收离线消息，再处理任务
```

### 三体通信（ACP通道，旧Hub退役中）
- **主通道**: OpenClaw ACP（sessions_send / sessions_spawn runtime="acp"）
- **发消息给小禾/小猪**: `sessions_send` 工具
- **启动子任务**: `sessions_spawn` runtime="acp"
- **离线消息缓存**: HTTP Hub（端口8700，`acp_client.py`）暂时保留
  - 查消息: `acp_client.py check --agent 富富`
  - 发消息: `acp_client.py send --from 富富 --to 小禾 --msg "内容"`
- **每次醒来**: 先查Hub收离线消息 + ACP通道收消息
- **服务端**：小猪部署，零依赖

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can keep updating skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
