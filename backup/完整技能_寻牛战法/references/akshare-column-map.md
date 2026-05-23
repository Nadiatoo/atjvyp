# AkShare 列映射备忘

各API的列序和列名随AkShare版本更新可能有变化。每次首次运行先 `print(list(df.columns))` 确认。

## stock_zt_pool_em (涨停池)

已验证列序 (2026-05-20): 名称(iloc[2]), 封板资金(iloc[9], 单位元), 连板数(iloc[14]), 所属行业(iloc[15])

## stock_zt_pool_dtgc_em (跌停池)

已验证列序 (2026-05-21): 名称(iloc[2]), 涨跌幅(iloc[3]), 连续跌停(iloc[13]), 所属行业(iloc[15])

## stock_info_global_em (全球财经新闻)

列名为中文 (2026-05-22 确认):
- `'标题'` (df.iloc[:, 0] 或 df['标题']) — 新闻标题
- `'摘要'` (df.iloc[:, 1] 或 df['摘要']) — 新闻摘要
- `'发布时间'` (df.iloc[:, 2] 或 df['发布时间']) — 精确到秒的时间戳
- `'链接'` (df.iloc[:, 3] 或 df['链接']) — 东方财富原文链接

遍历示例:
```python
import akshare as ak
df = ak.stock_info_global_em()
for _, row in df.iterrows():
    print(f"[{row['发布时间']}] {row['标题'][:80]}")
```

## stock_lhb_detail_em (龙虎榜详情)

已验证 (2026-05-21): 名称(iloc[2]), 龙虎榜净买额(iloc[6]/1e4, 万元), 涨跌幅(iloc[5])
