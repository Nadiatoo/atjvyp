#!/usr/bin/env python3
"""Fetch Cambridge Technology (603083.SH) financial data from Tushare Pro."""
import json
import os
import sys

result = {
    "task": "采集剑桥科技(603083) Tushare Pro财务数据",
    "status": "error",
    "reason": "",
    "data": {}
}

# Step 1: Get token
token = None
token_file = os.path.expanduser("~/.tushare_token")
if os.path.exists(token_file):
    with open(token_file, 'r') as f:
        token = f.read().strip()
if not token:
    token = os.environ.get("TUSHARE_TOKEN", "")

if not token:
    result["reason"] = (
        "Tushare Pro token缺失。\n"
        "  - 文件 ~/.tushare_token 存在但为空 (0 bytes)\n"
        "  - 环境变量 TUSHARE_TOKEN 未设置\n"
        "请将有效的Tushare Pro token写入 ~/.tushare_token 或设置环境变量 TUSHARE_TOKEN。"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0)

# Step 2: Verify token
import tushare as ts
try:
    pro = ts.pro_api(token)
    df_test = pro.income(ts_code='603083.SH', start_date='20210101', end_date='20211231', fields='ts_code,end_date')
    if df_test is not None and df_test.empty:
        result["reason"] = "Token似乎有效，但股票代码603083.SH查询返回空数据，请确认股票代码或数据权限。"
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)
except Exception as e:
    result["reason"] = f"Tushare Pro API连接失败: {str(e)}"
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0)

# --- 1. 利润表 近5年 ---
print(">>> 正在获取利润表数据...", file=sys.stderr)
try:
    income_df = pro.income(
        ts_code='603083.SH',
        start_date='20210101',
        end_date='20251231',
        fields='ts_code,end_date,report_type,revenue,n_income,eps_basic'
    )
    income_records = income_df.to_dict('records') if income_df is not None and not income_df.empty else []
except Exception as e:
    income_records = []
    print(f">>> 利润表获取失败: {e}", file=sys.stderr)

# --- 2. 日线行情 近1年 ---
print(">>> 正在获取日线行情数据...", file=sys.stderr)
try:
    from datetime import datetime, timedelta
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    start_str = one_year_ago.strftime('%Y%m%d')
    end_str = today.strftime('%Y%m%d')
    
    daily_df = pro.daily(ts_code='603083.SH', start_date=start_str, end_date=end_str)
    daily_records = daily_df.to_dict('records') if daily_df is not None and not daily_df.empty else []
    
    latest_close = None
    year_high = None
    year_low = None
    avg_volume = None
    
    if daily_records:
        df = daily_df.sort_values('trade_date', ascending=False)
        latest_close = float(df.iloc[0]['close'])
        year_high = float(daily_df['high'].max())
        year_low = float(daily_df['low'].min())
        avg_volume = float(daily_df['vol'].mean())
except Exception as e:
    daily_records = []
    latest_close = year_high = year_low = avg_volume = None
    print(f">>> 日线行情获取失败: {e}", file=sys.stderr)

# --- 3. 财务指标 ---
print(">>> 正在获取财务指标数据...", file=sys.stderr)
try:
    fina_df = pro.fina_indicator(
        ts_code='603083.SH',
        start_date='20210101',
        end_date='20251231',
        fields='ts_code,end_date,roe,grossprofit_margin'
    )
    fina_records = fina_df.to_dict('records') if fina_df is not None and not fina_df.empty else []
except Exception as e:
    fina_records = []
    print(f">>>> 财务指标获取失败: {e}", file=sys.stderr)

result["status"] = "success"
result["data"] = {
    "income": {
        "description": "利润表 - 近5年 (2021~2025, 按报告期)",
        "records_count": len(income_records),
        "records": income_records
    },
    "daily": {
        "description": f"日线行情 - 近1年 ({start_str}~{end_str})",
        "records_count": len(daily_records),
        "latest_close": latest_close,
        "year_high": year_high,
        "year_low": year_low,
        "avg_volume": round(avg_volume) if avg_volume else None,
        "records": daily_records
    },
    "fina_indicator": {
        "description": "财务指标 - ROE & 毛利率 (2021~2025)",
        "records_count": len(fina_records),
        "records": fina_records
    }
}

print(json.dumps(result, ensure_ascii=False, indent=2))
