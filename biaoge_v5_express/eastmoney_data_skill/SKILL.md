# 东方财富数据采集Skill - 彪哥战法专用版

## 描述
专门为彪哥战法v5.0设计的东方财富数据采集工具，支持获取全市场统计数据。

## 功能
1. **全市场统计数据**：上涨家数、下跌家数、涨停家数、跌停家数
2. **资金流向数据**：主力资金、北向资金、散户资金
3. **板块轮动数据**：热门板块、领涨板块
4. **市场情绪指标**：恐慌贪婪指数、市场热度

## 安装
```bash
# 无需额外安装，已集成到彪哥战法v5.0中
```

## 使用方法

### 1. 获取全市场统计数据
```python
from eastmoney_data import get_market_stats

# 获取今日市场统计数据
stats = get_market_stats()
print(f"上涨家数: {stats['rise_count']}")
print(f"下跌家数: {stats['fall_count']}")
print(f"涨停家数: {stats['limit_up']}")
print(f"跌停家数: {stats['limit_down']}")
```

### 2. 获取资金流向数据
```python
from eastmoney_data import get_money_flow

# 获取资金流向数据
flow = get_money_flow()
print(f"主力资金: {flow['main_flow']}亿")
print(f"北向资金: {flow['north_flow']}亿")
```

### 3. 获取板块轮动数据
```python
from eastmoney_data import get_sector_rotation

# 获取板块轮动数据
sectors = get_sector_rotation(top_n=10)
for sector in sectors:
    print(f"{sector['name']}: {sector['change']}%")
```

## 数据源
- 东方财富网公开API
- 新浪财经数据接口
- 腾讯财经数据接口

## 注意事项
1. 数据有延迟，实时性约1-3分钟
2. 免费接口有频率限制
3. 建议使用本地缓存减少API调用

## 彪哥战法集成
已集成到彪哥战法v5.0的以下模块：
1. 数据采集器 (`src/data/collectors/stock_collector.py`)
2. 状态分析引擎 (`src/state_evolution/optimized_state_matcher.py`)
3. 回测系统 (`real_data_backtest.py`)