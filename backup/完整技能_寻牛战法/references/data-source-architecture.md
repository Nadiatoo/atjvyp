# A股数据源架构（2026-05-23 定型）

三层数据源，各有定位，互补不重叠：

## 第一层：盘中高频实时

| 数据 | 来源 | 延迟 | 方式 |
|------|------|:----:|------|
| 涨停池快照 | a-stock-data（腾讯API） | 30s | HTTP轮询→升级WS |
| 行业板块排行 | a-stock-data（东财） | 实时 | HTTP |
| 主要指数 | a-stock-data（腾讯） | 实时 | HTTP |
| 个股实时行情 | a-stock-data（腾讯/mootdx） | 实时 | HTTP/TCP |
| 涨速榜/跌停池 | Phase 2 东财WS（开发中） | 秒级 | WebSocket推流 |
| 分时数据 | Phase 2 东财WS 1分钟K线 | 秒级 | WebSocket推流 |

## 第二层：历史稳定数据（Tushare MCP）

Tushare MCP Server 配置方式：

```yaml
# ~/.hermes/config.yaml 中
mcp_servers:
  tushare:
    command: npx
    args:
    - -y
    - '@tushare/mcp'
    env:
      TUSHARE_TOKEN: [从tushare.pro获取]
    enabled: true
```

| 数据 | Tushare接口 | 用途 |
|------|:----------:|------|
| 个股K线 | daily | 历史K线（免费API不稳定时的备选） |
| 指数K线 | index_daily | 指数历史数据 |
| 龙虎榜 | top_list | 营业部+机构席位（免费API做不到） |
| 资金流向 | moneyflow | 个股资金流备份 |
| 概念板块 | concept | 879个概念全量 |
| 港股通 | ggt_daily | 北向资金 |
| 业绩预告 | forecast | 业绩预告查询 |
| 融资融券 | margin_detail | 两融明细 |
| 复权因子 | adj_factor | 复权计算 |

## 第三层：统一数据采集客户端

小猪交付的 `unified_data_client.py` 把P0数据统一输出到 `~/.hermes/realtime/`：

```
~/.hermes/realtime/
├── indices.json        # 主要指数
├── limit_up.json       # 涨停池
├── sector_rank.json    # 板块排行
├── hot_themes.json     # 热点题材
└── northbound.json     # 北向资金
```

## 数据源选择策略

| 场景 | 优先 | 备选 |
|------|------|------|
| 盘中盯盘（涨停/板块/指数） | a-stock-data 腾讯API | 东财WS（Phase 2） |
| 查个股历史K线 | Tushare daily | 新浪/腾讯历史 |
| 查龙虎榜 | Tushare top_list | 东财datacenter-web |
| 查资金流向 | Tushare moneyflow | 东财push2 |
| 查概念板块 | Tushare concept | 百度概念归属 |
| 查研报/公告 | a-stock-data 东财reportapi | 巨潮cninfo |
