# 知识星球·题材数据库 提取方案（2026-05-17 更新）

## 系统状态

- **数据源**：知识星球「题材星球·数据库」（群号 48884255558588）
- **文章数量**：382篇（含2023-2026年内容），实际提取155篇有效文章
- **内容类型**：图文混排行业题材梳理（产业链图谱、数据表格），以图片/图表为主
- **知识库规模**：282题材 × 1368只个股双向索引
- **输出目录**：`~/Downloads/2026复盘/知识星球数据库/_知识库/`

## 已验证可行的提取方式

### AppleScript + Chrome JS 执行（推荐，唯一可行方案）

**前提条件**（一次设置永久有效）：
- Chrome 开启「允许 Apple 事件中的 JavaScript」
  - 菜单栏路径：查看 → 开发者 → 勾选"允许 Apple 事件中的 JavaScript"
  - 或命令行：`defaults write com.google.Chrome AppleEventScriptEnabled -bool true`（可能需重启 Chrome）
- Chrome 已登录知识星球（微信扫码登录）

**工作流程**：
1. 用户打开知识星球群页面，登录态有效
2. 通过 `osascript` 在 Chrome current tab 执行 JavaScript
3. 提取文章列表 → 逐篇导航 → 提取文本+图片+链接
4. 千问VL识别图片内容
5. 构建双向索引知识库

**优缺点**：
- ✅ 不关浏览器、不开调试端口、不影响正常使用
- ✅ 直接复用已登录的会话，无需处理 Cookie/LocalStorage
- ✅ macOS 原生支持，零依赖
- ❌ 会占用 Chrome 当前 tab（只能在空闲时跑）
- ❌ 每篇文章 ~1分钟，382篇需5-6小时

### AppleScript JS 执行核心代码

```python
import subprocess, json

def osa_js(code):
    """在Chrome当前标签页执行JS并返回结果"""
    s = json.dumps(code)
    r = subprocess.run(["osascript", "-e", f'''
        tell application "Google Chrome"
            tell active tab of window 1
                set result to (execute javascript {s})
                return result
            end tell
        end tell
    '''], capture_output=True, text=True, timeout=30)
    return r.stdout.strip() if r.returncode == 0 else None

def osa_nav(url):
    """导航到URL"""
    u = json.dumps(url)
    subprocess.run(["osascript", "-e", f'''
        tell application "Google Chrome"
            set URL of active tab of window 1 to {u}
        end tell
    '''], capture_output=True, timeout=10)
```

### 关键技术要点

**获取文章链接**：
- 知识星球文章使用短链接 `https://t.zsxq.com/xxxxx`
- 需先滚动页面加载全部内容（`window.scrollTo`×15~20次）再收集链接
- 文章链接选择器：`t.zsxq.com` 或 `/topic/`、`/post/`

**获取文章发布日期**：
- 日期在 `div.date` 元素中，格式如 `2026-01-13 20:46`
- 用于过滤旧文章（跳过2024年及以前的）

**千问VL读图**：
- 模型：`qwen-vl-max`
- API：兼容 OpenAI 接口格式
- Key：`QWEN_API_KEY`（存在 `~/.hermes/.env`）
- 读图 prompt：`"完整提取这张图里的所有文字和数据"`
- 对中文图表、数据表格识别效果好，但复杂图表/非表格图片可能识别失败

**提取策略**：先提取页面DOM文本（表格），再通过VL识别补充图片中的表格数据。两路合并。

## 知识库构建模式

### 输出结构

```
知识星球数据库/_知识库/
├── 按题材/           # 每个题材一个MD文件：公司列表+核心逻辑
├── 按个股/           # 每只个股一个MD文件：所属题材+各题材逻辑
├── _个股索引.md       # 总速查表：个股→题材数→题材列表
└── _knowledge_graph.json  # 程序用JSON
```

### 提取公司名的可靠方法

**只从Markdown表格第三列提取**（非表格内容/描述性文字不提取）：

```python
def extract_table_companies(content):
    companies = {}
    for line in content.split("\n"):
        if line.startswith("|") and line.endswith("|"):
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 3:
                name = cols[2].strip()
                logic = cols[3].strip() if len(cols) > 3 else ""
                if is_valid_company(name):
                    companies[name] = logic
    return companies
```

**注意表格格式差异**：部分表格首列为空（层级缩进），公司名实际在 `cols[1]` 而非 `cols[2]`。需同时检测 `cols[1]` 和 `cols[2]`。

### VL识别文字提取（补充）

每张图片下方已有千问VL识别文字（`> **图片识别**: ...`），从中可以进一步提取表格数据：

1. 正则匹配Markdown表格行：`\|\s*\*{0,2}(公司名)\*{0,2}\s*\|\s*(描述)`  
2. 正则匹配列表项：`-\s+\*{0,2}(公司名)\*{0,2}` 

### 噪音过滤清单

以下关键词出现时过滤（非公司名）：
`龙头, 优势, 环节, 领域, 说明, 总计, 代码, 股票, 核心, 业务, 技术, 市场, 系统, 方案, 数据, 成本, 效率, 服务, 管理, 能力, 布局, 覆盖, 份额, 排名, 地位, 算法, 主要, 重点, 需求, 供给, 总量, 增量, 存量, 概念, 驱动, 逻辑, 公司名称, 股票代码, 类别, 类型, 所有公司`

### 去重策略

1. **题材合并**：相同前缀（前6-8个中文字符匹配度≥5）的题材名自动合并
2. **个股去重**：同一个公司在多个题材中出现时，按文件保留并关联
3. **文件清理**：合并后删除重复题材文件

### 缺失公司检测

扫描原文表格和VL识别文字，找出所有在知识库中尚未录入的公司名。按出现频次≥2的自动补充。典型漏掉的真实公司如：蓝思科技、鸣志电器、恒为科技、中鼎股份、银轮股份。

### AppleScript JS执行前置条件确认

**启用方法**（一次设置永久有效）：
- **推荐**：Chrome 菜单 → 查看 → 开发者 → 勾选"允许 Apple 事件中的 JavaScript"
- **命令行尝试**：`defaults write com.google.Chrome AppleEventScriptEnabled -bool true`（可能需要重启 Chrome 才能生效，不一定有效）

**验证**：
```bash
osascript -e 'tell application "Google Chrome" to tell active tab of window 1 to set t to execute javascript "document.title"'
# 成功 → 返回页面标题
# 失败 → 提示需要开启设置
```

## 用户偏好嵌入

| 偏好 | 具体内容 |
|------|---------|
| **不写脚本给用户跑** | 所有代码由agent自己执行（terminal后台），用户只需说"跑知识星球" |
| **不推介terminal操作** | 任何需要手动终端命令的方案先打回简化 |
| **有Cookie就直接用** | 当用户已登录时，优先AppleScript操作当前Chrome，而非新建实例 |
| **结果导向** | 优先一页可读的知识库，其次才是程序接口 |

## 不推荐的方案（踩坑记录）

| 方案 | 失败原因 |
|------|---------|
| **Cookie 注入** | zsxq_access_token 等注入后仍显示未登录，知识星球额外依赖微信 OAuth session |
| **launch_persistent_context（同一用户目录）** | 老涂 Chrome 已运行时同一 profile 被锁 |
| **CDP connect** | 需要 Chrome 以 `--remote-debugging-port=9222` 启动 |
| **browser-use** | 国内网络下载扩展超时，启动独立 Chrome 无登录态 |
| **Playwright + temp dir + cookie** | cookie 注入后知识星球不认 |

## SQLite 数据库（2026-05-17 已上线）

### 数据库文件
`~/.openclaw/workspace/knowledge_base.db`（1094家公司, 282个题材, 1724条关联）

### 表结构
```sql
-- 公司表
CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,   -- 公司名称
    stock_code TEXT              -- 股票代码（425条有值）
);

-- 题材表  
CREATE TABLE themes (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL    -- 题材名称
);

-- 关联表（公司→题材→逻辑）
CREATE TABLE associations (
    company_id INTEGER REFERENCES companies(id),
    theme_id INTEGER REFERENCES themes(id),
    description TEXT,            -- 核心逻辑/优势
    PRIMARY KEY (company_id, theme_id)
);
```

### 查询接口
`~/.openclaw/workspace/query_kb.py`：小猪已写好，支持三种查询模式：

```bash
# 查公司相关题材
python3 ~/.openclaw/workspace/query_kb.py --company 中科曙光

# 查题材包含的公司
python3 ~/.openclaw/workspace/query_kb.py --theme AI算力芯片

# 全文关键词搜索
python3 ~/.openclaw/workspace/query_kb.py --search 液冷

# 输出 JSON 格式（供程序调用）
python3 ~/.openclaw/workspace/query_kb.py --company 中科曙光 --json
```

### 数据清洗
小猪写 `clean_and_build_db.py` 一次完成：噪音移除（273条） → HTML标签拆分（1条） → SQLite建库 → 建索引。原1368家公司清洗后保留1094家（移除的包括"所有公司""存储芯片""图中显示"等VL识别噪音）。
