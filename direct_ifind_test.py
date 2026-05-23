#!/usr/bin/env python3
"""
直接测试iFinD API连接
使用提供的access_token进行测试
"""

import os
import requests
import json

# 直接从环境变量获取token
refresh_token = "eyJzaWduX3RpbWUiOiIyMDI2LTA0LTIwIDE3OjQ2OjU2In0=.eyJ1aWQiOiI4NjI5MDAwNzMiLCJ1c2VyIjp7InJlZnJlc2hUb2tlbkV4cGlyZWRUaW1lIjoiMjAyNi0wNS0yMCAxNjozNzowMyIsInVzZXJJZCI6Ijg2MjkwMDA3MyJ9fQ==.3CF5C8F32F6F9B854BFFAF1DD4771664AE4EFBECB9EB6AA4B06EBBCAFC7B69D6"
access_token = "a4d2c1699a51c951fffda4be589fe33809407b77.signs_ODYyOTAwMDcz"

base_url = "https://quantapi.10jqka.com.cn"

print("=" * 60)
print("直接iFinD API测试")
print("=" * 60)

# 测试1: 尝试获取用户信息
print("\n1. 测试用户信息API...")
test_endpoints = [
    "/api/v1/user/info",
    "/api/user/info",
    "/user/info",
    "/oauth2/userinfo",
    "/v1/user/info"
]

for endpoint in test_endpoints:
    url = base_url + endpoint
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"   尝试 {endpoint}...")
        response = requests.get(url, headers=headers, timeout=5)
        print(f"     状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"     ✅ 成功!")
            print(f"     响应: {json.dumps(result, ensure_ascii=False)[:200]}...")
            break
        elif response.status_code == 401:
            print(f"     ❌ 未授权 (token可能无效)")
        elif response.status_code == 404:
            print(f"     ❌ 端点不存在")
        else:
            print(f"     ❌ 错误: {response.text[:100]}...")
    except Exception as e:
        print(f"     ❌ 请求异常: {str(e)}")

# 测试2: 尝试获取股票数据
print("\n2. 测试股票数据API...")
stock_endpoints = [
    "/api/v1/stock/quote",
    "/api/stock/quote",
    "/stock/quote",
    "/api/v1/stock/basic",
    "/api/v1/market/quote"
]

symbol = "000001"  # 平安银行
for endpoint in stock_endpoints:
    url = base_url + endpoint
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "symbol": symbol,
        "fields": "symbol,name,last_close,open,high,low,volume,amount"
    }
    
    try:
        print(f"   尝试 {endpoint}...")
        response = requests.get(url, headers=headers, params=params, timeout=5)
        print(f"     状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"     ✅ 成功!")
            print(f"     响应: {json.dumps(result, ensure_ascii=False)[:300]}...")
            break
        elif response.status_code == 401:
            print(f"     ❌ 未授权")
        elif response.status_code == 404:
            print(f"     ❌ 端点不存在")
        else:
            print(f"     ❌ 错误: {response.text[:100]}...")
    except Exception as e:
        print(f"     ❌ 请求异常: {str(e)}")

# 测试3: 尝试市场数据
print("\n3. 测试市场数据API...")
market_endpoints = [
    "/api/v1/market/overview",
    "/api/market/overview",
    "/market/overview",
    "/api/v1/market/today"
]

for endpoint in market_endpoints:
    url = base_url + endpoint
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"   尝试 {endpoint}...")
        response = requests.get(url, headers=headers, timeout=5)
        print(f"     状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"     ✅ 成功!")
            print(f"     响应: {json.dumps(result, ensure_ascii=False)[:300]}...")
            break
        elif response.status_code == 401:
            print(f"     ❌ 未授权")
        elif response.status_code == 404:
            print(f"     ❌ 端点不存在")
        else:
            print(f"     ❌ 错误: {response.text[:100]}...")
    except Exception as e:
        print(f"     ❌ 请求异常: {str(e)}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

# 检查token格式
print("\nToken分析:")
print(f"Refresh Token长度: {len(refresh_token)}")
print(f"Access Token长度: {len(access_token)}")
print(f"Access Token格式: {'Bearer风格' if 'signs_' in access_token else '未知'}")

# 尝试不同的授权头格式
print("\n4. 测试不同授权头格式...")
test_headers = [
    {"Authorization": f"Bearer {access_token}"},
    {"Authorization": f"Token {access_token}"},
    {"Authorization": access_token},
    {"X-Access-Token": access_token},
    {"access_token": access_token}
]

test_url = base_url + "/api/v1/user/info"
for headers in test_headers:
    try:
        print(f"   尝试 {list(headers.keys())[0]}...")
        response = requests.get(test_url, headers=headers, timeout=3)
        print(f"     状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"     ✅ 授权头格式正确!")
            break
    except:
        pass