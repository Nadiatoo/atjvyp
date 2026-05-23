# 恢复指南

> 换电脑后，克隆此仓库即可恢复三方 AI Agent 的全部核心资产。

## 前置

```bash
git clone git@github.com:Nadiatoo/atjvyp.git ~/workspace
cd ~/workspace
```

---

## 一、恢复小禾（Hermes Agent）

```bash
# 1. 安装 Hermes Agent
pip install hermes-agent
# 或: curl -fsSL https://hermes-agent.sh/install | sh

# 2. 恢复配置
mkdir -p ~/.hermes
cp backup/小禾_config.yaml ~/.hermes/config.yaml
# ⚠️ 需要手动填回 API keys（标记为 [REDACTED] 的位置）

# 3. 恢复知识库
cp -r backup/小禾_知识库/ ~/.hermes/knowledge_base/

# 4. 恢复寻牛战法完整技能
cp -r backup/完整技能_寻牛战法/ ~/.hermes/skills/trading/zhuangjiren-seasonal-trading/
```

## 二、恢复小猪（Claude Code）

```bash
# 1. 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 2. 恢复身份指令
mkdir -p ~/.claude
cp backup/小猪_CLAUDE.md ~/.claude/CLAUDE.md

# 3. 恢复完整技能
cp -r backup/小猪_skills/ ~/.claude/skills/
# ⚠️ TradingAgents-astock 体积较大(484MB)，需单独从源码安装
# 见 backup/小猪_skills/TradingAgents-astock/SKILL.md 中的安装指引
```

## 三、恢复富富（OpenClaw）

```bash
# 1. 安装 OpenClaw
pip install openclaw-mcp

# 2. 恢复配置
mkdir -p ~/.openclaw
cp backup/富富_openclaw.json ~/.openclaw/openclaw.json
# ⚠️ 需要手动填回 API keys（标记为 [REDACTED] 的位置）
```

## 四、恢复复盘文件

复盘文件（435MB）因体积较大未入库，如有需要从旧电脑直接拷贝：

```bash
# 从旧电脑
scp -r ~/Downloads/2026复盘/ 新电脑:~/Downloads/
```

文件清单见 `backup/复盘_文件清单.txt`

## 五、备份内容清单

| 文件/目录 | 大小 | 所属 | 说明 |
|-----------|------|------|------|
| `完整技能_寻牛战法/` | 452KB | **核心** | 寻牛战法完整 skill（SKILL.md + 50+参考文档 + 脚本） |
| `小禾_知识库/` | 452KB | 小禾 | 市场分析知识库（行业研究、产业链分析、报告模板） |
| `小禾_config.yaml` | 14KB | 小禾 | Hermes Agent 配置（API keys 已打码） |
| `小猪_skills/` | 72KB | 小猪 | a-stock-data + agent-reach 完整技能 |
| `小猪_skills/TradingAgents-astock/` | 4KB | 小猪 | 仅 SKILL.md + 目录结构（完整版484MB太大） |
| `小猪_CLAUDE.md` | 4KB | 小猪 | Claude Code 身份指令 |
| `富富_openclaw.json` | 8KB | 富富 | OpenClaw 配置（API keys 已打码） |
| `复盘_文件清单.txt` | — | 共享 | 复盘文件夹文件清单 |

## 六、API Keys 清单

| 服务 | 配置文件 | 获取地址 |
|------|---------|---------|
| DeepSeek | 小禾_config.yaml / 富富_openclaw.json | platform.deepseek.com |
| QVeris | 富富_openclaw.json | qveris.com |
| 其他第三方API | 对应配置文件 | 各平台控制台 |
