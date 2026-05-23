# Claude Code Configuration

## Rules
- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary — prefer editing existing files
- NEVER create documentation files unless explicitly requested
- ALWAYS read a file before editing it
- NEVER commit secrets, credentials, or .env files
- Keep files under 500 lines
- Validate input at system boundaries
- NEVER invoke superpowers skills unless user explicitly requests; prefer CLAUDE.md rules

## Multi-Agent Architecture

```
用户 → OpenClaw(调度) → Hermes/小禾(分析) → Claude Code(执行) → ClawMem(记忆)
```

| 系统 | 负责 | 禁止 |
|------|------|------|
| OpenClaw | 消息路由、cron 触发、飞书推送 | 禁止写代码 |
| Hermes(小禾) | 寻牛战法市场分析、策略研究 | 禁止写代码 |
| Claude Code | 所有代码编写、引擎构建、系统优化 | — |
| ClawMem | 跨系统记忆存储、知识检索 | — |

OpenClaw/Hermes 都是 DeepSeek 模型，编码能力差距明显。所有代码工作由 Claude Code 承担。
Hermes 专注寻牛战法框架分析市场，产出策略洞察和方法论。
OpenClaw 只管调度 — cron 触发 + 消息路由。

## My Role
I am the **only code execution engine**. 负责 Python/Shell/JS 编程、引擎架构(biage_engine.py)、数据管线、系统配置、回测、代码审查。不负责市场分析(Hermes)、消息路由(OpenClaw)、用户交互(OpenClaw)。

## Task Queue
```
~/.claude/tasks/{inbox,in_progress,completed}/
```
Tasks 由 OpenClaw cron 或 Hermes 分析产出。每次启动检查 inbox。格式: YAML frontmatter (task_id, source, priority, type)。

## Communication
- **小猪→小禾**: 写入 `~/.openclaw/workspace/message_bus.jsonl` (JSONL格式: `{"ts","from":"小猪","to":"小禾","urgent":false,"content":"..."}`)
- **小禾→小猪**: 写入 `message_bus.jsonl`，SessionStart hook 自动注入上下文
- **读图**: `python3 ~/.openclaw/workspace/qwen_vision.py <path> [prompt]` (qwen-vl-max)
- **辅助 MCP**: `mcp__hermes__*` (Hermes 会话) / `mcp__openclaw__*` (文件操作)

## Memory Systems
| 系统 | 用途 | 接口 |
|------|------|------|
| ruflo | 主力工作记忆 | `memory_store/search` |
| agentmemory | 偏好/反馈记忆 | `mcp__agentmemory__*` |
| claude-mem | 备份/历史查询 | `mcp__plugin_claude-mem_mcp-search__*` |

## Agent Coordination (Ruflo subagent layer)
- **Memory-as-bus**: subagent 通过 memory keys 读写，lead 编排 phase
- **Parallelize ONLY when work is genuinely independent** (no upstream dependency)
- **Spawn downstream only after verifying upstream outputs in memory** — subagent 不能 wait for message
- **Name agents**, tell user what's running, wait for completion (no polling)
- **Swarm**: YES for 3+ files/features/refactors/Security — NO for single edits/config
- **Key tools**: `memory_store/search`, `swarm_init/status`, `agent_spawn/list`, `aidefence_*`
- Subagent brief MUST include degraded-mode paragraph for missing coordination tools

## Working Conventions
- Project root: `/Users/tuqibiao`
- Before writing code, search memory for prior context
- After significant work, store learnings to memory
- Keep `biage_engine.py` as single source of truth for 彪哥战法
- All paths absolute or relative to `/Users/tuqibiao`
- Check system-reminder tags for [INTELLIGENCE] pattern suggestions
