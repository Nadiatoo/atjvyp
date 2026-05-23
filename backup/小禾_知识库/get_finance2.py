#!/usr/bin/env python3
"""获取蓝思科技补充数据 v2"""
import akshare as ak
import warnings
warnings.filterwarnings('ignore')

print("=== 最新季度数据（最近6期）===")
df_q = ak.stock_financial_abstract_ths(symbol='300433', indicator='按报告期')
print(df_q[['报告期','营业总收入','净利润','净利润同比增长率','营业总收入同比增长率','销售毛利率','基本每股收益']].tail(6).to_string(index=False))

print("\n=== 机构研报观点 ===")
try:
    df_r = ak.stock_research_report_em(symbol="300433")
    print(df_r[['股票代码','研究报告标题','最新评级','机构名称','日期']].head(10).to_string(index=False))
except Exception as e:
    print(f"研报获取失败: {e}")

print("\n=== 个股资金流向（近10日）===")
try:
    df_m = ak.stock_individual_fund_flow(symbol="300433", market="sz")
    print(df_m.tail(10).to_string())
except Exception as e:
    print(f"资金流向获取失败: {e}")
