# 数据源矩阵（2026-05-19定稿）

## 行情数据

| 优先级 | 数据源 | 用途 | 费用 | 稳定性 |
|:------:|--------|------|:---:|:------:|
| **P0** | Tushare Pro | 日线行情（回测核心） | 500元/年 | ✅ 稳定 |
| **P0** | 东方财富（Chrome） | 实时行情/指数/概念/财务 | 免费 | ✅ 稳定 |
| **P1** | AkShare | 涨停池/龙虎榜/板块排行 | 免费 | ⚠️ 偶断 |
| **P2** | baostock | 历史日线备用 | 免费 | 🔴 慢/超时 |
| **P3** | yfinance | 美股/港股 | 免费 | 🔴 国内限频严重 |

## 搜索/新闻

| 优先级 | 数据源 | 用途 | 费用 | 稳定性 |
|:------:|--------|------|:---:|:------:|
| **P1** | DuckDuckGo | 日常新闻搜索 | 免费 | ⚠️ 中文结果有限 |
| **P2** | Jina AI | 公众号/财经长文抓取 | 免费额度 | 🔵 待测试 |
| **P3** | SerpAPI/Tavily | 付费搜索 | 💰 | ❌ 性价比低，不推荐 |

## LLM/识别

| 优先级 | 数据源 | 用途 | 费用 | 稳定性 |
|:------:|--------|------|:---:|:------:|
| **P0** | DeepSeek API | 市场分析/策略推理 | 按量计费 | ✅ 稳定 |
| **P0** | 千问VL (Qwen) | 图片识别/图表OCR | API按量 | ✅ 稳定 |

## 数据采集方式

### 大盘指数（最稳 — Chrome+AppleScript）
```
https://www.eastmoney.com/
→ 页面文本直接包含 "上证指数\t4131.53\t-3.86\t-0.09%" 格式
→ 一次打开可拿三大指数+成交额
→ execute javascript 提取 body.innerText 即可
```

### 涨停池（AkShare）
```python
from akshare import stock_zt_pool_em
df = stock_zt_pool_em(date='20260518')
# 列位置: 名称[2], 连板数[14], 所属行业[15], 封板资金
df['连板数'].value_counts().sort_index()
df['所属行业'].value_counts().head(8)
```

### 龙虎榜（AkShare）
```python
from akshare import stock_lhb_detail_em
df = stock_lhb_detail_em(start_date='20260518', end_date='20260518')
# 列位置: 名称[2], 龙虎榜净买额[6]/1e4, 涨跌幅[5]
```

### 个股行情/财务（Tushare Pro）
```python
import tushare as ts
pro = ts.pro_api()
df = pro.daily(ts_code='603969.SH', start_date='20260101', end_date='20260518')
```

## 知识库

| 数据源 | 内容 | 格式 |
|--------|------|------|
| 知识星球·题材数据库 | 155篇产业链梳理 | SQLite + JSON + MD |
| 金融梦想家公众号 | 2280篇市场分析 | SQLite + JSON |
| knowledge_base.db | 1094公司 + 282题材 + 关联 | SQLite (query_kb.py查询) |

### 查询方式
```bash
python3 ~/.openclaw/workspace/query_kb.py --company 中科曙光    # 查公司→题材
python3 ~/.openclaw/workspace/query_kb.py --theme AI算力芯片      # 查题材→公司
python3 ~/.openclaw/workspace/query_kb.py --search 液冷           # 关键词搜索
python3 ~/.openclaw/workspace/query_kb.py --company 宁德时代 --articles  # 查相关文章
```

### 研报自动生成
```bash
python3 ~/.openclaw/workspace/generate_report.py 中科曙光
```

## 通信架构（过渡期）

```
小禾(我) ──── Claude Comms ────────→ 小猪 (文件级消息)
         ──── Ruflo task ─────────→ 小猪 (自动路由)
等待统一为标准ACP协议（hermes acp做服务端）
ACP Hub (端口8700) 已废弃
```
