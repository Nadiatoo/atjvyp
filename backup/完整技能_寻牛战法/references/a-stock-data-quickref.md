# a-stock-data 快速参考

小猪安装的A股全栈数据工具包（V3.1，2026-05-19验证）

## 路径
`~/.claude/skills/a-stock-data/SKILL.md`（1025行，完整代码可直接复用）

## 七层数据源

| 层 | 端点 | 用途 |
|---|------|------|
| 行情 | mootdx(7709) + 腾讯API + 百度K线 | K线/盘口/指数/ETF |
| 研报 | 东财reportapi + 同花顺 + iwencai | 研报搜索/下载/一致预期 |
| 信号 | 同花顺热点 + 东财push2 + datacenter-web | 强势股/题材归因/北向/龙虎榜/解禁 |
| 资金 | datacenter-web + push2his | 融资融券/大宗交易/股东/分红/资金流 |
| 新闻 | 东财 + cls.cn | 个股新闻/快讯/全球 |
| 基础 | mootdx + 新浪 | F10/财务三表/行业 |
| 公告 | 巨潮cninfo | 公告检索/下载 |

## 快速启用
```bash
pip install mootdx requests pandas stockstats
# 然后从SKILL.md复制相应端点的Python代码到terminal执行
```
