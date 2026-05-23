# 多 Agent 消息总线协议

## 概述

所有 Agent 间通信统一走 **文件级 inbox/outbox 机制**，不依赖任何 MCP/WebSocket/HTTP 等实时通道。

无论任务由哪个 Agent 处理，通信链路必须保持双向通畅。

## 目录结构

```
~/.claude/tasks/            ← 富富（OpenClaw Agent）的任务队列
  ├── inbox/                ← 各 Agent 发给富富的消息
  │   └── YYYYMMDD-HHMMSS-{source}-{topic}.md
  ├── in_progress/          ← 正在处理的任务
  ├── completed/            ← 已完成的任务
  └── README.md             ← 官方格式说明

~/.hermes/tasks/            ← 小禾（Hermes Agent）的任务队列
  ├── inbox/                ← 各 Agent 发给小禾的消息
  │   └── comms-{source}-{topic}-{timestamp}.md
  ├── processed/            ← 小禾已处理的任务
  └── images/               ← 图片附件
```

## 命名规范

**发给富富（富富的 inbox）：**
```
YYYYMMDD-HHMMSS-{source}-{topic}.md
```
- source: hermes | piggy | openclaw
- 示例: `20260521-170000-hermes-deep-analysis.md`

**发给小禾（小禾的 inbox）：**
```
comms-{source}-{topic}-{timestamp}.md
```
- source: 富富 | 小禾 | 小猪
- 示例: `comms-富富-盘后分析请求-20260521_170000.md`

**发给小猪（Claude Code）：**
与富富的 inbox 共用 `~/.claude/tasks/inbox/`（Claude Code 默认读取此目录）

## 消息格式（YAML Frontmatter + Markdown）

```markdown
---
task_id: "unique-id"
source: "hermes|piggy|openclaw"
source_agent: "小禾|小猪|富富"
target_agent: "小禾|小猪|富富"
priority: "critical|high|normal|low"
type: "data_analysis|report_generate|code_write|memory_update|skill_improve"
created_at: "2026-05-21T17:00:00+08:00"
status: "pending"
context_refs: []
---

# 任务标题

## Description
任务描述...

## Context Files
(none 或 相关文件路径列表)
```

## 生命周期

```
         发信方写入
    ┌──────────┐
    │  inbox/   │ ← 富富/小禾/小猪 都可以写
    └────┬─────┘
         │ 收信方读取后移动到
    ┌────▼─────┐
    │in_progress│ (仅富富有此环节，小禾直接移 processed)
    └────┬─────┘
         │ 完成后移动到
    ┌────▼─────┐
    │completed/ │ 或 processed/
    └──────────┘
```

## Agent 职责

### 富富（我）的职责
1. **每次会话启动/心跳时** 检查 `~/.claude/tasks/inbox/` 是否有新消息
2. 及时处理小禾发来的任务，处理后移入 `completed/`
3. 如需委托工作给小禾 → 写文件到 `~/.hermes/tasks/inbox/`
4. 如需委托工作给小猪 → 写文件到 `~/.claude/tasks/inbox/`
5. 完成分析报告后 → 推送到飞书

### 小禾的职责
1. 监控 `~/.hermes/tasks/inbox/`
2. 自动消费任务，完成后移入 `processed/`
3. 分析结果通过 `~/.claude/tasks/inbox/` 回传给富富

### 小猪的任务
1. 监控 `~/.claude/tasks/inbox/`
2. 自动消费代码/数据类任务
3. 代码/数据结果直接写入目标路径，或通过飞书回传

## 示例

### 富富 → 小禾（请求深度分析）
写入 `~/.hermes/tasks/inbox/comms-富富-盘后深度分析-20260521_170000.md`

### 小禾 → 富富（返回分析结果）
写入 `~/.claude/tasks/inbox/20260521-173000-hermes-deep-analysis.md`

### 富富 → 小猪（请求代码修改）
写入 `~/.claude/tasks/inbox/20260521-180000-piggy-fix-bug.md`
