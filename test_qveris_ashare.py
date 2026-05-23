#!/usr/bin/env python3
"""
测试QVeris获取A股数据
"""

import os
import sys
import json
import requests
from datetime import datetime

def test_qveris_ashare_data():
    """测试QVeris获取A股数据"""
    
    api_key = os.getenv('QVERIS_API_KEY')
    if not api_key:
        print("❌ 错误: 未设置QVERIS_API_KEY环境变量")
        print("请设置: export QVERIS_API_KEY=your_key")
        return False
    
    base_url = "https://qveris.ai/api/v1"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("🔍 测试QVeris获取A股数据")
    print("=" * 60)
    
    # 测试工具：尝试获取A股数据
    test_cases = [
        {
            "name": "A股行情数据",
            "tool_id": "stock_market_data",
            "params": {
                "symbol": "000001.SS",  # 上证指数
                "interval": "1d",
                "period": "1mo"
            }
        },
        {
            "name": "A股新闻搜索",
            "tool_id": "news_search",
            "params": {
                "query": "上证指数 A股",
                "count": 3,
                "region": "cn-zh"
            }
        },
        {
            "name": "A股公司信息",
            "tool_id": "company_info",
            "params": {
                "symbol": "000001.SZ"  # 平安银行
            }
        }
    ]
    
    success_count = 0
    for test_case in test_cases:
        print(f"\n📊 测试: {test_case['name']}")
        print(f"   工具ID: {test_case['tool_id']}")
        
        payload = {
            "tool_id": test_case["tool_id"],
            "params": test_case["params"]
        }
        
        try:
            response = requests.post(
                f"{base_url}/tools/execute",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success", False):
                    print(f"   ✅ 成功")
                    result = data.get("result", {})
                    if "data" in result and result["data"]:
                        print(f"   返回数据量: {len(result['data'])}条")
                        # 显示部分数据
                        if isinstance(result["data"], list) and len(result["data"]) > 0:
                            sample = result["data"][0]
                            print(f"   示例数据: {json.dumps(sample, ensure_ascii=False)[:100]}...")
                    else:
                        print(f"   返回数据: {json.dumps(result, ensure_ascii=False)[:200]}...")
                    success_count += 1
                else:
                    print(f"   ❌ 工具执行失败")
                    print(f"   错误信息: {data.get('error_message', '未知错误')}")
            else:
                print(f"   ❌ HTTP请求失败")
                print(f"   响应: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ 异常: {e}")
    
    print(f"\n📈 测试结果: {success_count}/{len(test_cases)} 成功")
    
    if success_count > 0:
        print("✅ QVeris可以获取A股数据")
        return True
    else:
        print("❌ QVeris获取A股数据测试失败")
        return False

def test_alternative_methods():
    """测试替代方法获取A股数据"""
    
    print("\n🔍 测试替代数据获取方法")
    print("=" * 60)
    
    # 测试直接API调用
    test_endpoints = [
        {
            "name": "EODHD数据",
            "url": "https://eodhistoricaldata.com/api/eod/000001.SS",
            "params": {
                "api_token": "demo",  # 需要替换为真实token
                "period": "d",
                "fmt": "json"
            }
        }
    ]
    
    for endpoint in test_endpoints:
        print(f"\n📊 测试: {endpoint['name']}")
        try:
            response = requests.get(
                endpoint["url"],
                params=endpoint["params"],
                timeout=10
            )
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"   ✅ 成功获取数据")
                    print(f"   数据条数: {len(data)}")
                    print(f"   最新数据: {json.dumps(data[0], ensure_ascii=False)}")
                else:
                    print(f"   响应数据: {response.text[:200]}")
            else:
                print(f"   ❌ 请求失败: {response.text[:100]}")
        except Exception as e:
            print(f"   ❌ 异常: {e}")

def main():
    """主函数"""
    print("🎯 QVeris A股数据获取测试")
    print("=" * 60)
    
    # 测试QVeris
    qveris_success = test_qveris_ashare_data()
    
    if not qveris_success:
        print("\n⚠️ QVeris直接获取A股数据可能有限制")
        print("建议:")
        print("1. 检查QVeris工具库中可用的A股数据工具")
        print("2. 考虑使用EODHD等专业金融数据API")
        print("3. 或者使用混合数据源策略")
        
        # 测试替代方法
        test_alternative_methods()
    
    print("\n" + "=" * 60)
    print("💡 建议的数据源策略:")
    print("1. QVeris用于新闻、宏观数据、部分行情数据")
    print("2. EODHD/Yahoo Finance用于详细的行情数据")
    print("3. 东方财富/新浪财经用于A股特色数据")
    print("4. 建立数据验证和备份机制")

if __name__ == "__main__":
    main()