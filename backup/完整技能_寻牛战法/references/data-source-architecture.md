# 数据源架构（2026-05-19 老涂确认）

## 主数据源矩阵

### P0 核心层

| 数据源 | 用途 | 费用 | 覆盖范围 | 验证状态 |
|--------|------|:----:|---------|:--------:|
| **Tushare Pro** | A股日线行情（回测主力） | 500元/年 | A股全量日线 | ✅ 已验证稳定 |
| **东方财富 API** | 实时行情、指数、涨停/龙虎榜 | 免费 | A股实时 | ✅ 已验证 |
| **DeepSeek API** | LLM分析、策略推理 | API按量 | 对话/分析 | ✅ 主力模型 |
| **千问VL (Qwen)** | 图片识别（图表/截图/知识库） | 免费额度 | 多模态 | ✅ 已验证 |

### P1 辅助层

| 数据源 | 用途 | 费用 | 备注 |
|--------|------|:----:|------|
| **AkShare** | 涨停池/龙虎榜/板块数据 | 免费 | 偶有连接问题，重试即可 |
| **DuckDuckGo** | 新闻搜索 | 免费 | 中文搜索效果有限 |
| **Browser-use** | 浏览器自动化 | 免费 | 备用 |

### P2 备用层

| 数据源 | 用途 | 费用 |
|--------|------|:----:|
| **baostock** | Tushare挂了时的备用日线 | 免费 |
| **Jina AI** | 网页转Markdown（待测试） | 免费额度 |

### 不推荐使用的

| 数据源 | 原因 |
|--------|------|
| **SerpAPI** | 付费，免费源够用 |
| **Tavily** | 付费，性价比低 |
| **yfinance** | 国内连接限频严重 |

## 个股研报数据获取流程

```python
① Knowledge Base查询 → 题材覆盖 + 核心逻辑 + 相关文章
② Tushare Pro → 日线行情、财务数据
③ 东方财富 (Chrome AppleScript) → 实时行情、板块数据
④ AkShare → 涨停池、龙虎榜补缺
⑤ DuckDuckGo/百度 → 最新新闻、公告
⑥ 整合结论
```

## 注意事项

- 东方财富 Chrome 抓取路径：`document.body.innerText`
- Tushare Pro 日线查询：`pro.daily(ts_code='XXXXXX.SH', start_date=..., end_date=...)`
- AkShare 涨停池：`ak.stock_zt_pool_em(date='YYYYMMDD')`
- AkShare 龙虎榜：`ak.stock_lhb_detail_em(start_date=..., end_date=...)`
- 所有数据源连接异常时，先重试1-2次，不行换源，不要停滞
