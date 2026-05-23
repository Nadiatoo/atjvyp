#!/usr/bin/env python3
"""A股个股财务数据采集脚本
用法: python3 fetch_stock_finance.py 300433

依赖: pip install akshare
数据来源: 同花顺iFinD (通过akshare)
"""
import sys
import akshare as ak
import warnings
warnings.filterwarnings('ignore')

code = sys.argv[1] if len(sys.argv) > 1 else "300433"

print(f"=== {code} 年度财务数据（近5年）===")
df = ak.stock_financial_abstract_ths(symbol=code, indicator='按年度')
cols = [c for c in ['报告期','营业总收入','净利润','销售毛利率','净资产收益率','基本每股收益','净利润同比增长率'] if c in df.columns]
print(df[cols].tail(5).to_string(index=False))

print(f"\n=== {code} 最新季度（最近6期）===")
df_q = ak.stock_financial_abstract_ths(symbol=code, indicator='按报告期')
cols_q = [c for c in ['报告期','营业总收入','净利润','净利润同比增长率','营业总收入同比增长率','销售毛利率','基本每股收益'] if c in df_q.columns]
print(df_q[cols_q].tail(6).to_string(index=False))

print(f"\n=== {code} 券商研报 ===")
try:
    df_r = ak.stock_research_report_em(symbol=code)
    print(df_r[['日期','机构','评级','2026-盈利预测-收益','2026-盈利预测-市盈率']].head(10).to_string(index=False))
except Exception as e:
    print(f"研报获取失败: {e}")

print(f"\n=== {code} 实时行情（腾讯证券）===")
import subprocess, json
result = subprocess.run(
    ['curl', '-s', '--max-time', '10', f'https://qt.gtimg.cn/q=sz{code}'],
    capture_output=True, text=True)
line = result.stdout
if line:
    parts = line.split('~')
    print(f"名称: {parts[1] if len(parts)>1 else ''}")
    print(f"现价: {parts[3] if len(parts)>3 else ''}")
    print(f"涨跌幅: {parts[32] if len(parts)>32 else ''}%")
    print(f"PE: {parts[39] if len(parts)>39 else ''}")
    print(f"PB: {parts[46] if len(parts)>46 else ''}")
    print(f"总市值: {parts[45] if len(parts)>45 else ''}亿")
