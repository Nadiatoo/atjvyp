#!/usr/bin/env python3
"""
iFinD API详细测试脚本
测试实际数据获取能力
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta

# 配置参数
ACCESS_TOKEN = "a4d2c1699a51c951fffda4be589fe33809407b77.signs_ODYyOTAwMDcz"
BASE_URL = "https://quantapi.51ifind.com/api/v1"

def get_headers():
    return {
        "Content-Type": "application/json",
        "access_token": ACCESS_TOKEN
    }

def test_history_quotes():
    """测试历史行情接口"""
    print("=" * 60)
    print("测试历史行情接口")
    print("=" * 60)
    
    url = f"{BASE_URL}/cmd_history_quotation"
    
    # 使用昨天和前天的日期
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    day_before = today - timedelta(days=2)
    
    params = {
        "codes": "000001.SZ,600000.SH",
        "indicators": "open,high,low,close,volume",
        "startdate": day_before.strftime("%Y-%m-%d"),
        "enddate": yesterday.strftime("%Y-%m-%d"),
        "functionpara": {
            "Fill": "Blank",
            "period": "D"
        }
    }
    
    print(f"请求参数:")
    print(json.dumps(params, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(url, json=params, headers=get_headers(), timeout=10)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据结构: {list(data.keys())}")
            
            # 检查是否有错误码
            if "errorcode" in data and data["errorcode"] != 0:
                print(f"❌ API错误: {data.get('errmsg', '未知错误')}")
                print(f"错误码: {data['errorcode']}")
            elif "code" in data and data["code"] != 0:
                print(f"❌ API错误: {data.get('message', '未知错误')}")
                print(f"错误码: {data['code']}")
            else:
                print("✅ 历史行情数据获取成功")
                
                # 尝试解析数据
                if "data" in data:
                    if "tables" in data["data"]:
                        tables = data["data"]["tables"]
                        print(f"数据表数量: {len(tables)}")
                        
                        for i, table in enumerate(tables):
                            print(f"\n表 {i+1}:")
                            print(f"  证券代码: {table.get('thscode', '未知')}")
                            print(f"  时间范围: {table.get('time', '未知')}")
                            
                            if "table" in table:
                                table_data = table["table"]
                                print(f"  字段数量: {len(table_data)}")
                                for key in table_data:
                                    print(f"  - {key}: {len(table_data[key]) if isinstance(table_data[key], list) else 1} 个值")
                    else:
                        print(f"数据内容: {json.dumps(data['data'], indent=2, ensure_ascii=False)[:500]}")
                else:
                    print(f"完整响应: {json.dumps(data, indent=2, ensure_ascii=False)[:800]}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ 连接异常: {e}")

def test_basic_data():
    """测试基础数据接口"""
    print("\n" + "=" * 60)
    print("测试基础数据接口")
    print("=" * 60)
    
    url = f"{BASE_URL}/basic_data_service"
    
    # 测试获取股票基本信息和最新价
    today_str = datetime.now().strftime("%Y%m%d")
    
    params = {
        "codes": "000001.SZ",
        "indipara": [
            {
                "indicator": "ths_total_shares_stock",
                "indiparams": [today_str]
            },
            {
                "indicator": "ths_close_price_stock", 
                "indiparams": ["", "100", ""]  # 最新收盘价
            }
        ]
    }
    
    print(f"请求参数:")
    print(json.dumps(params, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(url, json=params, headers=get_headers(), timeout=10)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据结构: {list(data.keys())}")
            
            # 检查错误
            if "errorcode" in data and data["errorcode"] != 0:
                print(f"❌ API错误: {data.get('errmsg', '未知错误')}")
                print(f"错误码: {data['errorcode']}")
            elif "code" in data and data["code"] != 0:
                print(f"❌ API错误: {data.get('message', '未知错误')}")
                print(f"错误码: {data['code']}")
            else:
                print("✅ 基础数据获取成功")
                print(f"完整响应: {json.dumps(data, indent=2, ensure_ascii=False)[:800]}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ 连接异常: {e}")

def test_data_pool():
    """测试专题报表接口（获取板块成分）"""
    print("\n" + "=" * 60)
    print("测试专题报表接口 - 获取A股全部股票")
    print("=" * 60)
    
    url = f"{BASE_URL}/data_pool"
    
    # 获取全部A股列表
    today_str = datetime.now().strftime("%Y%m%d")
    
    params = {
        "reportname": "p03291",  # 板块成分报表
        "functionpara": {
            "date": today_str,
            "blockname": "001005010",  # 全部A股
            "iv_type": "allcontract"
        },
        "outputpara": "p03291_f001,p03291_f002,p03291_f003"
    }
    
    print(f"请求参数:")
    print(json.dumps(params, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(url, json=params, headers=get_headers(), timeout=15)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据结构: {list(data.keys())}")
            
            if "errorcode" in data and data["errorcode"] != 0:
                print(f"❌ API错误: {data.get('errmsg', '未知错误')}")
                print(f"错误码: {data['errorcode']}")
            elif "code" in data and data["code"] != 0:
                print(f"❌ API错误: {data.get('message', '未知错误')}")
                print(f"错误码: {data['code']}")
            else:
                print("✅ 专题报表数据获取成功")
                
                # 尝试解析
                if "data" in data:
                    data_content = data["data"]
                    if isinstance(data_content, dict) and "tables" in data_content:
                        tables = data_content["tables"]
                        print(f"数据表数量: {len(tables)}")
                        
                        for i, table in enumerate(tables):
                            print(f"\n表 {i+1}:")
                            for key in table:
                                if key == "table" and isinstance(table[key], dict):
                                    print(f"  字段: {list(table[key].keys())}")
                                    for field, values in table[key].items():
                                        if isinstance(values, list):
                                            print(f"  - {field}: {len(values)} 个值")
                                            if len(values) > 0:
                                                print(f"    示例: {values[:3]}")
                                else:
                                    print(f"  {key}: {table[key]}")
                    else:
                        print(f"数据内容类型: {type(data_content)}")
                        print(f"数据内容: {str(data_content)[:500]}")
                else:
                    print(f"完整响应: {json.dumps(data, indent=2, ensure_ascii=False)[:800]}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ 连接异常: {e}")

def test_high_frequency():
    """测试高频序列接口"""
    print("\n" + "=" * 60)
    print("测试高频序列接口 - 分钟线数据")
    print("=" * 60)
    
    url = f"{BASE_URL}/high_frequency"
    
    # 使用昨天的数据
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    
    params = {
        "codes": "000001.SZ",
        "indicators": "open,high,low,close",
        "starttime": f"{date_str} 09:30:00",
        "endtime": f"{date_str} 15:00:00"
    }
    
    print(f"请求参数:")
    print(json.dumps(params, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(url, json=params, headers=get_headers(), timeout=10)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据结构: {list(data.keys())}")
            
            if "errorcode" in data and data["errorcode"] != 0:
                print(f"❌ API错误: {data.get('errmsg', '未知错误')}")
                print(f"错误码: {data['errorcode']}")
            elif "code" in data and data["code"] != 0:
                print(f"❌ API错误: {data.get('message', '未知错误')}")
                print(f"错误码: {data['code']}")
            else:
                print("✅ 高频序列数据获取成功")
                print(f"响应摘要: {json.dumps(data, indent=2, ensure_ascii=False)[:800]}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ 连接异常: {e}")

def main():
    print("🚀 iFinD API详细测试开始")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Access Token: {ACCESS_TOKEN[:20]}...")
    
    # 运行测试
    test_history_quotes()
    test_basic_data()
    test_data_pool()
    test_high_frequency()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()