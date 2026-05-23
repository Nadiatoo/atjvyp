# a-stock-data 工具包 · 关键端点速查

> 来源：`~/.claude/skills/a-stock-data/SKILL.md`（V3.1，38KB）
> 作者：Simon林，项目主页 https://github.com/simonlin1212/a-stock-data
> 小禾用法：在terminal中直接执行代码片段，依赖 `requests pandas`（已预装）

## 一、行情层

### mootdx — K线+五档盘口+逐笔成交（TCP 7709）
```python
from mootdx.quotes import Quotes
client = Quotes.factory(market='std')  # TCP直连通达信
# K线: client.bars(symbol='688017', frequency=9, offset=0, start=0, count=200)
# frequency: 9=日线 5=30分钟 3=5分钟 0=分笔
# 五档: client.quotes(symbols=['688017'])
# 逐笔: client.transaction(symbol='688017', start=0, count=100)
```

### 腾讯财经 — PE/PB/市值/换手率/涨跌停/指数
```python
import requests
r = requests.get('https://web.ifzq.gtimg.cn/appstock/app/fqkline/get',
    params={'param': 'sh688017,day,,,200,qfq'}, timeout=10)
```

### 百度股市通 — K线带MA
```python
r = requests.get('https://gushitong.baidu.com/stock/ab-688017',
    headers={'User-Agent': 'Mozilla/5.0'})
```

## 二、研报层

### 东财研报 — 列表+PDF下载+评级+三年EPS
```python
# 个股研报
r = requests.get('https://reportapi.eastmoney.com/report/list',
    params={'cb': 'jQuery', 'stockCode': '688017', 'pageSize': 20}, timeout=15)
# 搜索
r = requests.get('https://reportapi.eastmoney.com/search',
    params={'cb': 'jQuery', 'keyword': 'AI Agent'}, timeout=15)
```

### 同花顺一致预期
```python
r = requests.get('https://basic.10jqka.com.cn/688017/', timeout=10)
# 提取 EPS 一致预期，正则提取
```

## 三、信号层（最常用）

### ⭐ 同花顺热点 — 当日强势股+题材归因（零鉴权 73ms）
```python
r = requests.get(
    'https://data.10jqka.com.cn/fantong/client/strength/hot_stock/index.html',
    params={'callback': 'jQuery'}, timeout=10)
# 返回：股票名称/代码/涨幅/题材reason tags
```

### ⭐ 北向资金 — hgt/sgt 分钟流向（同花顺）
```python
r = requests.get(
    'https://data.10jqka.com.cn/fantong/client/strength/north_flow/index.html',
    params={'callback': 'jQuery'}, timeout=10)
```

### 东财 push2 — 个股资金流向分钟级
```python
secid = '0.688017'  # 0=深圳/创业板 1=上海
r = requests.get(
    f'https://push2.eastmoney.com/api/qt/stock/get',
    params={'secid': secid, 'fields': 'f47,f48,f49,f50,f51,f52,f55,f57,f58,f62,f64,f66,f69,f72,f75,f78,f84,f87,f99,f100'},
    timeout=10)
```

### ⭐ 龙虎榜 — 全市场+个股席位TOP5
```python
# 全市场龙虎榜
def eastmoney_datacenter(report_name, filter_str='', page_size=50):
    params = {
        'reportName': report_name, 'columns': 'ALL',
        'filter': filter_str, 'pageNumber': '1', 'pageSize': str(page_size),
        'sortColumns': 'TRADE_DATE', 'sortTypes': '-1',
        'source': 'WEB', 'client': 'WEB',
    }
    r = requests.get('https://datacenter-web.eastmoney.com/api/data/v1/get',
                     params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
    return r.json().get('result', {}).get('data', [])
# RPT_DAILYBILLBOARD_DET = 全市场龙虎榜
# RPT_BILLBOARD_NETBUY_DETAILS = 个股席位明细
```

### ⭐ 限售解禁日历
```python
# reportName: RPT_SHAREBONUS_SHAREBNSUCC, filter: "(STOCK_CODE="688017")"
```

### 行业板块排名
```python
r = requests.get('https://push2.eastmoney.com/api/qt/clist/get',
    params={
        'pn': '1', 'pz': '100', 'po': '1', 'np': '1',
        'fs': 'm:90+t:2+f:!50',  # 东财行业板块
        'fields': 'f2,f3,f4,f12,f14,f104,f105',
    }, timeout=10)
```

## 四、资金面/筹码层

| 数据 | reportName | 说明 |
|------|-----------|------|
| 融资融券 | `RPT_RZRQ_TRADE_DET` | 日级融资余额/买入/偿还+融券 |
| 大宗交易 | `RPT_BLOCKDEAL_DET` | 成交价/量+买卖方营业部 |
| 股东户数 | `RPT_HOLDERNUM_PARAM` | 季度股东户数+环比 |
| 分红送转 | `RPT_SHAREBONUS_DET` | 历史每股派息/送股/转增 |

## 五、新闻层

### 财联社快讯
```python
r = requests.get('https://www.cls.cn/v1/roll/get_roll_list',
    params={'app': 'Cailianpress', 'os': 'web', 'sv': '7.2.2'},
    headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.cls.cn/'}, timeout=10)
```

## 六、TradingAgents-Astock 缓存

位置：`~/.tradingagents/cache/northbound_daily.csv`
内容：北向资金日线数据，可直接用 pandas 读取
```python
import pandas as pd
df = pd.read_csv('~/.tradingagents/cache/northbound_daily.csv')
```
