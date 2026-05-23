# 仓库管理规范

**管理者：小禾** — 日常维护、内容审核、清理执行

## 一、核心原则

此仓库是**三方协作的工作代码库**，不是个人备忘录，也不是数据仓库。

| 维度 | ✅ 应存入 | ❌ 不应存入 |
|------|-----------|------------|
| 代码 | 脚本、工具、策略实现、框架代码 | venv、__pycache__、node_modules |
| 配置 | `.gitignore`、项目级配置文件 | 运行时状态、工作树文件 |
| 文档 | 方法论、框架说明、规范文档 | Agent 内部记忆/身份/工具描述 |
| 数据 | 少量测试/样例数据 | 数据库文件(.db)、缓存、日志 |
| 通信 | — | message_bus 日志、通信历史备份 |
| 产物 | 最终分析报告 | 过程草稿、临时笔记、日报 |

## 二、拒绝入库清单（.gitignore 自动拦截 + 追踪移除）

```
# 运行环境
venv/ .venv/ venv_arm64/

# Python 缓存
__pycache__/ *.pyc *.pyo

# 数据库文件
*.db *.sqlite *.sqlite3

# 通信日志
message_bus.jsonl *.bak *.log

# Agent 内部目录
.claude/ .claude-flow/ .clawhub/ .learnings/ .msg_pointers/ .openclaw/

# IDE
.idea/ .vscode/

# 操作系统
.DS_Store Thumbs.db

# 大文件数据缓存
*.dylib *.dat *.so  # 避免意外提交二进制库
```

## 三、清理节奏

- 每次推新内容前，先 `.gitignore` 自动阻挡不应入库的文件
- 若需纠正历史错误，用 `git rm --cached` + 新 commit，不改写历史
- 每年 6 月 / 12 月各做一次全仓健康检查

## 四、目录结构（目标）

```
workspace/
├── scripts/          # Python 脚本、工具
├── framework/        # 方法论、框架文档
├── config/           # 配置文件
├── reports/          # 最终分析报告
├── data/             # 少量测试/样例数据
├── .gitignore
├── REPO_MANAGEMENT.md
└── README.md
```
