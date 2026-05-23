#!/usr/bin/env python3
"""
测试最近交易日的数据
"""

import requests
import json
from datetime import datetime, timedelta

ACCESS_TOKEN = "a4d2c1699a51c951fffda4be589fe33809407b77.signs_ODYyOTAwMDcz"
BASE_URL = "https://quantapi.51ifind.com/api/v1"

def get_headers():
    return {
        "Content-Type": "application/json",
        "access_token": ACCESS_TOKEN
    }

def test_recent_dates():
    """测试最近几个日期，找到有效交易日"""
    print("测试最近日期...")
    
    # 测试过去5天
    for days_ago in range(1, 6):
        test_date = datetime.now() - timedelta(days=days_ago)
        date_str = test_date.strftime("%Y-%m-%d")
        
        print(f"\n测试日期: {date_str} ({days_ago}天前)")
        
        url = f"{BASE_URL}/cmd_history_quotation"
        params = {
            "codes": "000001.SZ",
            "indicators": "close",
            "startdate": date_str,
            "enddate": date_str,
            "functionpara": {"Fill": "Blank", "period": "D"}
        }
        
        try:
            response = requests.post(url, json=params, headers=get_headers(), timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("errorcode") == 0:
                    tables = data.get("tables", [])
                    if tables and "table" in tables[0]:
                        close_data = tables[0]["table"].get("close")
                        if close_data and close_data[0] is not None:
                            print(f"✅ 找到有效交易日: {date_str}, 收盘价: {close_data[0]}")
                            return date_str
                        else:
                            print(f"❌ 数据为空")
                else:
                    print(f"❌ API错误: {data.get('errmsg')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    return None

def test_with_valid_date(valid_date):
    """使用有效日期测试完整数据"""
    print(f"\n使用有效日期 {valid_date} 测试...")
    
    # 测试历史行情
    url = f"{BASE_URL}/cmd_history_quotation"
    params = {
        "codes": "000001.SZ,600000.SH",
        "indicators": "open,high,low,close,volume,changeRatio",
        "startdate": valid_date,
        "enddate": valid_date,
        "functionpara": {"Fill": "Blank", "period": "D"}
    }
    
    try:
        response = requests.post(url, json=params, headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("errorcode") == 0:
                print("✅ 历史行情数据:")
                for table in data.get("tables", []):
                    print(f"\n证券: {table.get('thscode')}")
                    for indicator, values in table.get("table", {}).items():
                        if values and values[0] is not None:
                            print(f"  {indicator}: {values[0]}")
            else:
                print(f"❌ API错误: {data.get('errmsg')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    # 测试实时数据（最新价）
    print(f"\n测试最新价数据...")
    url = f"{BASE_URL}/basic_data_service"
    
    # 使用正确的指标格式
    today_str = datetime.now().strftime("%Y%m%d")
    
    params = {
        "codes": "000001.SZ",
        "indipara": [
            {
                "indicator": "ths_close_price_stock",
                "indiparams": ["", "1", ""]  # 最新价
            }
        ]
    }
    
    try:
        response = requests.post(url, json=params, headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
    except Exception as e:
        print(f"❌ 异常: {e}")

def main():
    print("🚀 测试最近交易日数据")
    
    # 先找到有效交易日
    valid_date = test_recent_dates()
    
    if valid_date:
        # 使用有效日期测试
        test_with_valid_date(valid_date)
    else:
        print("未找到有效交易日，尝试其他日期...")
        
        # 测试一些已知日期
        test_dates = ["2026-04-17", "2026-04-16", "2026-04-15", "2026-04-14"]
        
        for test_date in test_dates:
            print(f"\n测试已知日期: {test_date}")
            url = f"{BASE_URL}/cmd_history_quotation"
            params = {
                "codes": "000001.SZ",
                "indicators": "close",
                "startdate": test_date,
                "enddate": test_date,
                "functionpara": {"Fill": "Blank", "period": "D"}
            }
            
            try:
                response = requests.post(url, json=params, headers=get_headers(), timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("errorcode") == 0:
                        tables = data.get("tables", [])
                        if tables and "table" in tables[0]:
                            close_data = tables[0]["table"].get("close")
                            if close_data and close_data[0] is not None:
                                print(f"✅ 找到数据: {test_date}, 收盘价: {close_data[0]}")
                                test_with_valid_date(test_date)
                                break
            except Exception as e:
                print(f"❌ 异常: {e}")

if __name__ == "__main__":
    main()