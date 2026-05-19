
# Cross-System Learnings

## 2026-05-13 | openclaw+hermes+claude-code | 三方分工与整合方案

**Source System**: all
**Source Agent**: 富富+小禾+小C
**Category**: decisions
**Importance**: 1.0

**Learning**:
三方团队正式成立：富富(OpenClaw)指挥部、小禾(Hermes)参谋部、小C(Claude Code)工程部。

- 富富：消息路由、cron定时、飞书推送、中转协调。不做深度分析，不写代码。
- 小禾：市场分析、四季框架、五层解读、独立记忆。不写代码。
- 小C：所有代码编写、量化回测、工程实现。不做市场分析。

整合方案：MCP双向通道已打通 + tasks/目录作为任务队列。
所有定时任务采用"富富采集→小C转小禾分析→结果回传富富→推送"流程。

**Propagation**:
- [x] OpenClaw (TOOLS.md + 本文件)
- [x] Hermes (memory)
- [x] Claude Code (CLAUDE.md)

**Impact**:
消除三方越界干活、知识孤岛的问题。

---

## Learnings Log

| Date | Source | Category | Learning | Propagated To | Impact |
|------|--------|----------|----------|---------------|--------|
| 2026-05-13 | all | decisions | 三方分工+整合方案 | TOOLS.md+CLAUDE.md+memory | 避免越界，打通共享 |
## 2026-05-14 | openclaw | 协作边界确认

**Source System**: openclaw
**Source Agent**: 富富
**Category**: decisions
**Importance**: 0.9

**Learning**:
跨系统协作的实际边界：三人从来没有同时在线对话过。所有"三方讨论"实际上是：
- 富富+小禾实时对话
- 小C通过其已有CLAUDE.md配置和代码库间接参与（非实时）
- 向老涂汇报时必须说明实际参与方，不能美化

小C的任务通过写文件到 ~/.claude/tasks/inbox/ 队列异步下发。
小禾的任务通过hermes CLI/MCP实时沟通。
富富是中转枢纽，三方不通直连。

**Propagation**:
- [x] OpenClaw (IDENTITY.md + MEMORY.md + 本文件)
- [x] Hermes (已告知)

**Impact**:
确保老涂对团队协作方式有准确的认知，不产生错误预期。
