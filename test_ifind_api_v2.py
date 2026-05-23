#!/usr/bin/env python3
"""
iFinD API连接测试脚本 v2
基于官网示例代码：https://quantapi.10jqka.com.cn/gwstatic/static/ds_web/quantapi-web/example.html
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime, timedelta

# 配置参数
REFRESH_TOKEN = "eyJzaWduX3RpbWUiOiIyMDI2LTA0LTIwIDE7OjQ2OjU2In0=.eyJ1aWQiOiI4NjI5MDAwNzMiLCJ1c2VyIjp7InJlZnJlc2hUb2tlbkV4cGlyZWRUaW1lIjoiMjAyNi0wNS0yMCAxNjoMzc6MDMiLCJ1c2VySWQiOiI4NjI5MDAwNzMifX0=.3CF5C8F32F6F9B854BFFAF1DD4771664AE4EFBECB9EB6AA4B06EBBCAFC7B69D6"
ACCESS_TOKEN = "a4d2c1699a51c951fffda4be589fe33809407b77.signs_ODYyOTAwMDcz"
BASE_URL = "https://quantapi.51ifind.com/api/v1"

def test_token_validation():
    """测试Refresh Token有效性"""
    print("=" * 60)
    print("1. 测试Refresh Token有效性")
    print("=" * 60)
    
    url = f"{BASE_URL}/get_access_token"
    headers = {
        "Content-Type": "application/json",
        "refresh_token": REFRESH_TOKEN
    }
    
    try:
        response = requests.post(url, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get("code") == 0:
                new_access_token = data["data"]["access_token"]
                print(f"✅ Refresh Token验证成功")
                print(f"新的Access Token: {new_access_token[:20]}...")
                return new_access_token
            else:
                print(f"❌ Refresh Token验证失败: {data.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 连接异常: {e}")
    
    return None

def test_with_access_token(access_token):
    """使用Access Token测试API"""
    print("\n" + "=" * 60)
    print("2. 使用Access Token测试API端点")
    print("=" * 60)
    
    headers = {
        "Content-Type": "application/json",
        "access_token": access_token
    }
    
    # 测试1: 基础数据 - 获取股票基本信息
    print("\n📊 测试1: 基础数据 - 股票基本信息")
    url = f"{BASE_URL}/basic_data_service"
    params = {
        "codes": "000001.SZ,600000.SH",
        "indipara": [
            {
                "indicator": "ths_total_shares_stock",
                "indiparams": [datetime.now().strftime("%Y%m%d")]
            }
        ]
    }
    
    try:
        response = requests.post(url, json=params, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print("✅ 基础数据接口测试成功")
                print(f"返回数据结构: {list(data.keys())}")
            else:
                print(f"❌ API错误: {data.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ 连接异常: {e}")
    
    # 测试2: 历史行情 - 获取近期股价
    print("\n📈 测试2: 历史行情 - 近期股价")
    url = f"{BASE_URL}/cmd_history_quotation"
    
    # 使用昨天和今天的日期
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    params = {
        "codes": "000001.SZ",
        "indicators": "open,high,low,close",
        "startdate": yesterday,
        "enddate": today,
        "functionpara": {"Fill": "Blank"}
    }
    
    try:
        response = requests.post(url, json=params, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print("✅ 历史行情接口测试成功")
                # 尝试解析数据
                if "data" in data and "tables" in data["data"]:
                    print(f"数据表数量: {len(data['data']['tables'])}")
                else:
                    print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}")
            else:
                print(f"❌ API错误: {data.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ 连接异常: {e}")
    
    # 测试3: 高频序列 - 获取分钟线数据
    print("\n⏰ 测试3: 高频序列 - 分钟线数据")
    url = f"{BASE_URL}/high_frequency"
    
    # 使用今天的时间
    start_time = f"{today} 09:30:00"
    end_time = f"{today} 15:00:00"
    
    params = {
        "codes": "000001.SZ",
        "indicators": "open,high,low,close",
        "starttime": start_time,
        "endtime": end_time
    }
    
    try:
        response = requests.post(url, json=params, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print("✅ 高频序列接口测试成功")
                print(f"高频数据响应结构: {list(data.keys())}")
            else:
                print(f"❌ API错误: {data.get('message', '未知错误')}")
                print(f"完整响应: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ 连接异常: {e}")
    
    return headers

def test_direct_access():
    """直接使用提供的Access Token测试"""
    print("\n" + "=" * 60)
    print("3. 直接使用提供的Access Token测试")
    print("=" * 60)
    
    headers = {
        "Content-Type": "application/json",
        "access_token": ACCESS_TOKEN
    }
    
    # 测试最简单的端点
    print("\n🔍 测试API端点连通性")
    
    endpoints = [
        ("基础数据", "/basic_data_service"),
        ("历史行情", "/cmd_history_quotation"),
        ("专题报表", "/data_pool"),
    ]
    
    for name, endpoint in endpoints:
        url = BASE_URL + endpoint
        print(f"\n测试 {name} ({endpoint})...")
        
        # 构建最小化请求
        params = {
            "codes": "000001.SZ",
        }
        
        try:
            response = requests.post(url, json=params, headers=headers, timeout=5)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ 端点响应正常")
                    print(f"响应code: {data.get('code', '无')}")
                    print(f"响应message: {data.get('message', '无')[:50]}")
                except:
                    print(f"✅ 端点响应正常（非JSON格式）")
                    print(f"响应长度: {len(response.text)} 字符")
            elif response.status_code == 400:
                print("⚠️  参数错误（正常，需要更完整的参数）")
            elif response.status_code == 401:
                print("❌ 认证失败")
            elif response.status_code == 404:
                print("❌ 端点不存在")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 连接异常: {e}")

def main():
    print("🚀 iFinD API连接测试开始")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    
    # 首先尝试Refresh Token验证
    new_access_token = test_token_validation()
    
    if new_access_token:
        # 使用新的Access Token测试
        test_with_access_token(new_access_token)
    else:
        print("\n⚠️  Refresh Token验证失败，尝试使用提供的Access Token")
        test_direct_access()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()