#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试QVeris能否获取A股市场数据
"""

import os
import requests
import json
import datetime

# QVeris API配置
QVERIS_API_KEY = os.getenv("QVERIS_API_KEY", "sk-PYDj7ulDpbYUtxeXnKeUzKLzMjS2IdTZ6N-2uYbX5bo")
QVERIS_API_URL = "https://qveris.ai/api/v1/search"

def test_qveris_market_data():
    """测试QVeris获取市场数据"""
    
    print("🔍 测试QVeris获取A股市场数据")
    print("=" * 60)
    print(f"API密钥: {QVERIS_API_KEY[:10]}...{QVERIS_API_KEY[-10:]}")
    print(f"测试时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 测试不同的查询
    test_queries = [
        {
            "name": "上证指数实时数据",
            "query": "Get real-time Shanghai Composite Index (SSE) price, change, and volume for today"
        },
        {
            "name": "A股全市场数据",
            "query": "Get today's A-share market data: number of rising stocks, falling stocks, limit-up stocks, limit-down stocks"
        },
        {
            "name": "创业板指数据",
            "query": "Get real-time ChiNext Index (399006) price and change percentage"
        },
        {
            "name": "北向资金数据",
            "query": "Get today's northbound capital flow data for A-share market"
        },
        {
            "name": "A股涨停板数据",
            "query": "Get today's limit-up stocks list in A-share market with prices and sectors"
        }
    ]
    
    headers = {
        "Authorization": f"Bearer {QVERIS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    all_results = []
    
    for test in test_queries:
        print(f"📊 测试: {test['name']}")
        print(f"查询: {test['query']}")
        print("-" * 40)
        
        try:
            payload = {
                "query": test['query'],
                "max_results": 3,
                "format": "json"
            }
            
            response = requests.post(
                QVERIS_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 请求成功 (状态码: {response.status_code})")
                
                # 简化显示结果
                if 'results' in result and result['results']:
                    first_result = result['results'][0]
                    print(f"标题: {first_result.get('title', 'N/A')}")
                    print(f"摘要: {first_result.get('snippet', 'N/A')[:200]}...")
                    
                    # 保存详细结果
                    test['result'] = {
                        'status': 'success',
                        'data': first_result
                    }
                else:
                    print("⚠️ 无结果返回")
                    test['result'] = {
                        'status': 'no_results',
                        'data': result
                    }
            else:
                print(f"❌ 请求失败 (状态码: {response.status_code})")
                print(f"错误信息: {response.text[:200]}")
                test['result'] = {
                    'status': 'error',
                    'status_code': response.status_code,
                    'error': response.text[:500]
                }
                
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
            test['result'] = {'status': 'timeout'}
        except requests.exceptions.ConnectionError:
            print("❌ 连接错误")
            test['result'] = {'status': 'connection_error'}
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            test['result'] = {'status': 'exception', 'error': str(e)}
        
        print()
        all_results.append(test)
    
    # 总结测试结果
    print("📋 测试结果总结")
    print("=" * 60)
    
    success_count = sum(1 for r in all_results if r.get('result', {}).get('status') == 'success')
    total_count = len(all_results)
    
    print(f"总测试数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    print()
    
    # 详细结果
    for i, test in enumerate(all_results, 1):
        status = test.get('result', {}).get('status', 'unknown')
        status_icon = "✅" if status == 'success' else "⚠️" if status == 'no_results' else "❌"
        print(f"{i}. {status_icon} {test['name']}: {status}")
    
    print()
    
    # 保存测试结果
    output_file = f"QVeris市场数据测试_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.datetime.now().isoformat(),
            'tests': all_results,
            'summary': {
                'total': total_count,
                'success': success_count,
                'success_rate': success_count/total_count*100
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"📁 详细测试结果已保存至: {output_file}")
    
    return all_results

def test_specific_market_data():
    """测试获取具体的市场数据"""
    
    print("🎯 测试获取具体的A股市场数据")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {QVERIS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 更具体的查询
    specific_queries = [
        {
            "name": "上证指数详细数据",
            "query": """Get detailed real-time data for Shanghai Composite Index (000001.SH):
            - Current price
            - Today's change percentage
            - Today's high and low
            - Trading volume
            - Turnover
            - PE ratio
            - Market capitalization
            Please provide as structured data."""
        },
        {
            "name": "今日A股市场统计",
            "query": """Get today's A-share market statistics:
            - Total number of listed companies
            - Number of rising stocks
            - Number of falling stocks
            - Number of unchanged stocks
            - Number of limit-up stocks (涨停)
            - Number of limit-down stocks (跌停)
            - Total market capitalization
            - Total trading volume
            Please provide numerical data."""
        },
        {
            "name": "北向资金详细流向",
            "query": """Get detailed northbound capital flow data for today:
            - Shanghai-Hong Kong Stock Connect northbound flow
            - Shenzhen-Hong Kong Stock Connect northbound flow
            - Total northbound flow
            - Top 10 net buying stocks
            - Top 10 net selling stocks
            Please provide as structured data."""
        }
    ]
    
    for test in specific_queries:
        print(f"\n📈 测试: {test['name']}")
        print(f"查询: {test['query'][:100]}...")
        print("-" * 40)
        
        try:
            payload = {
                "query": test['query'],
                "max_results": 1,
                "format": "json"
            }
            
            response = requests.post(
                QVERIS_API_URL,
                headers=headers,
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 请求成功")
                
                if 'results' in result and result['results']:
                    first_result = result['results'][0]
                    title = first_result.get('title', '')
                    snippet = first_result.get('snippet', '')
                    
                    print(f"标题: {title}")
                    print(f"数据摘要:")
                    print(snippet[:500])
                    
                    # 检查是否包含数字数据
                    import re
                    numbers = re.findall(r'\d+\.?\d*', snippet)
                    if numbers:
                        print(f"找到 {len(numbers)} 个数字数据点")
                    else:
                        print("⚠️ 未找到数字数据")
                else:
                    print("⚠️ 无结果返回")
            else:
                print(f"❌ 请求失败 (状态码: {response.status_code})")
                
        except Exception as e:
            print(f"❌ 错误: {e}")

def main():
    """主函数"""
    print("🚀 QVeris市场数据获取能力测试")
    print()
    
    # 测试基本功能
    results = test_qveris_market_data()
    
    print("\n" + "="*60)
    print("💡 结论与建议")
    print("="*60)
    
    # 分析结果
    success_tests = [r for r in results if r.get('result', {}).get('status') == 'success']
    
    if success_tests:
        print("✅ QVeris可以获取市场数据")
        print("可获取的数据类型:")
        for test in success_tests:
            print(f"  • {test['name']}")
        
        print("\n🎯 建议:")
        print("1. 使用QVeris作为主要数据源替代AkShare")
        print("2. 开发QVeris数据采集模块")
        print("3. 集成到彪哥战法v5.0系统")
        print("4. 建立数据缓存机制减少API调用")
    else:
        print("❌ QVeris无法获取市场数据或配置有问题")
        print("\n🔧 排查建议:")
        print("1. 检查QVERIS_API_KEY是否正确")
        print("2. 检查网络连接")
        print("3. 查看QVeris API文档")
        print("4. 尝试其他查询方式")
    
    print()
    
    # 测试具体数据
    if success_tests:
        print("进行详细数据测试...")
        test_specific_market_data()

if __name__ == "__main__":
    main()