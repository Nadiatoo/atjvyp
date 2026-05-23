#!/usr/bin/env python3
"""获取蓝思科技财务数据"""
import akshare as ak
import warnings
warnings.filterwarnings('ignore')

print("=== 年度财务数据（近5年）===")
df = ak.stock_financial_abstract_ths(symbol='300433', indicator='按年度')
print(df[['报告期','营业总收入','净利润','销售毛利率','净资产收益率','基本每股收益']].tail(5).to_string(index=False))

print("\n=== 最新4期（含季度）===")
df_q = ak.stock_financial_abstract_ths(symbol='300433', indicator='按报告期')
print(df_q[['报告期','营业总收入','净利润','净利润同比增长率','营业总收入同比增长率','销售毛利率','基本每股收益']].head(4).to_string(index=False))
