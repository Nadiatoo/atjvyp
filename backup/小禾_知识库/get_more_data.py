#!/usr/bin/env python3
"""获取研报+公告+利润表"""
import akshare as ak
import warnings
warnings.filterwarnings('ignore')

print("=== 券商研报 ===")
try:
    df = ak.stock_research_report_em(symbol="300433")
    print(df.head(10).to_string())
except Exception as e:
    print(f"失败: {e}")
    # 看看有哪些列
    try:
        print(f"列名: {df.columns.tolist()}")
    except:
        pass

print("\n=== 最新公告 ===")
try:
    df = ak.stock_notice_report(symbol="SZ300433")
    print(df[['日期','标题']].head(10).to_string(index=False))
except Exception as e:
    print(f"失败: {e}")

print("\n=== 利润表（2025年报）===")
try:
    df = ak.stock_profit_sheet_by_report_em(symbol="300433", period="年报")
    print(df.tail(5).to_string())
except Exception as e:
    print(f"失败: {e}")
