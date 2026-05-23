#!/usr/bin/env python3
"""深挖弘信电子AI算力业务"""
import akshare as ak
import warnings
warnings.filterwarnings('ignore')

code = "300657"

print("=== 营收构成（按产品）===")
try:
    df = ak.stock_profit_sheet_by_report_em(symbol=code)
    print("列名:", df.columns.tolist())
    print(df.tail(3).to_string())
except Exception as e:
    print(f"profit_sheet: {e}")

print("\n=== 主营业务构成 ===")
try:
    df = ak.stock_main_info_em(symbol=code)
    print(df.to_string())
except Exception as e:
    print(f"main_info: {e}")

print("\n=== 公司简介 ===")
try:
    df = ak.stock_info_a_code_name_em()
    print(df[df['代码']==code].to_string())
except Exception as e:
    print(f"info: {e}")

print("\n=== 投资关系 ===")
try:
    df = ak.stock_gpzy_em(symbol=code)
    print(df.head(10).to_string())
except Exception as e:
    print(f"gpzy: {e}")
