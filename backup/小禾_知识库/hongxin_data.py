#!/usr/bin/env python3
"""获取弘信电子（300657）数据"""
import akshare as ak
import warnings, json
warnings.filterwarnings('ignore')

code = "300657"

print("=== 年度财务数据（近5年）===")
df = ak.stock_financial_abstract_ths(symbol=code, indicator='按年度')
print(df[['报告期','营业总收入','净利润','销售毛利率','净资产收益率','基本每股收益']].tail(5).to_string(index=False))

print("\n=== 最新季度数据 ===")
df_q = ak.stock_financial_abstract_ths(symbol=code, indicator='按报告期')
print(df_q[['报告期','营业总收入','净利润','净利润同比增长率','营业总收入同比增长率','销售毛利率','基本每股收益']].tail(6).to_string(index=False))

print("\n=== 研报评级 ===")
try:
    df_r = ak.stock_research_report_em(symbol=code)
    print(df_r[['报告名称','最新评级','机构名称','日期','2026-盈利预测-收益','2026-盈利预测-市盈率']].head(10).to_string(index=False))
except Exception as e:
    print(f"研报获取失败: {e}")
