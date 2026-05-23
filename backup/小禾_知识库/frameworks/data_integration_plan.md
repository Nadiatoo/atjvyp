# 小禾数据工具整合方案

## 目标
将 a-stock-data（28个免费API端点）和 TradingAgents-astock（多Agent框架）的能力整合到小禾的日常分析流程中。

## 现状问题
- 涨停池靠 AkShare（有时不稳定）
- 板块排行靠新浪API（限流风险）
- 研报只能搜标题，拿不到全文
- 北向资金/资金流向没有实时数据

## 整合方案

### Phase 1：数据源替换（立即收益）
| 当前数据源 | 替换为 a-stock-data | 收益 |
|-----------|-------------------|------|
| AkShare 涨停池 | 同花顺热点API（零鉴权73ms） | 更稳定，更快 |
| AkShare 龙虎榜 | 东财数据中心API | 字段更全 |
| Sina 指数 | 腾讯API | 不限流 |
| AkShare 行业排行 | 东财push2行业排行 | 实时 |
| — | 同花顺热点题材归因 | **新能力** |
| — | 东财研报PDF下载 | **新能力** |
| — | 财联社快讯 | **新能力** |
| — | 巨潮公告全文 | **新能力** |

### Phase 2：数据整合层
编写 unified_data_client.py 封装所有接口，输出统一JSON格式：
- 行情：indices.json / realtime_quotes.json
- 涨停跌停：limit_up.json / limit_down.json
- 板块排行：sector_rank.json
- 热点题材：hot_themes.json
- 盘前盘后：overnight.json / close_report.json

### Phase 3：接入寻牛分析框架
数据自动流入四季分析流程：
```
数据采集层（Phase 1+2）
    ↓
大盘四季判定
板块四季判定
风格四季判定
    ↓
策略输出
```
