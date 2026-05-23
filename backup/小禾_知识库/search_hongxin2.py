#!/usr/bin/env python3
"""抓弘信电子新闻和公告"""
import akshare as ak
import warnings
warnings.filterwarnings('ignore')

print("=== 公司新闻 ===")
try:
    df = ak.stock_info_js(symbol="300657")
    print(df.head(10).to_string())
except Exception as e:
    print(f"stock_info_js: {e}")
    try:
        df = ak.stock_news_em(symbol="300657")
        print(df[['日期','标题']].head(10).to_string(index=False))
    except Exception as e2:
        print(f"stock_news_em: {e2}")

print("\n=== 最新公告 ===")
try:
    df = ak.stock_notice_report(symbol="300657")
    print(df.head(5).to_string())
except Exception as e:
    print(f"notice: {e}")
