#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试EGPS推送功能
"""

import sys
import os
import json
import requests
from datetime import datetime
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_egps_analysis():
    """测试EGPS分析获取"""
    print("测试EGPS分析获取...")
    
    try:
        base_url = "http://localhost:8000"
        
        # 测试连接
        print("  测试系统连接...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"  ✅ 系统状态: {response.json().get('status', '未知')}")
        else:
            print(f"  ❌ 系统连接失败: {response.status_code}")
            return False
        
        # 测试经济周期分析
        print("  测试经济周期分析...")
        response = requests.get(f"{base_url}/api/v1/analysis/economic-cycle", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ 周期位置: {data.get('cycle_position', '未知')}")
            print(f"  ✅ 增长率: {data.get('growth_rate', 0)}%")
        else:
            print(f"  ❌ 经济周期分析失败: {response.status_code}")
            return False
        
        # 测试政策环境分析
        print("  测试政策环境分析...")
        response = requests.get(f"{base_url}/api/v1/analysis/policy-environment", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ 政策数量: {data.get('policy_count', 0)}条")
            print(f"  ✅ 关键主题: {data.get('key_policy_themes', ['无'])[0]}")
        else:
            print(f"  ❌ 政策环境分析失败: {response.status_code}")
            return False
        
        print("✅ EGPS分析测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_feishu_message_format():
    """测试飞书消息格式化"""
    print("\n测试飞书消息格式化...")
    
    # 模拟分析结果
    mock_analysis = {
        "economic_cycle": {
            "cycle_position": "early_expansion",
            "growth_rate": 3.2,
            "inflation_level": "moderate",
            "risk_level": "low",
            "investment_implications": {
                "asset_allocation": {"equity": 60, "bonds": 30, "cash": 10},
                "sector_preferences": ["technology", "consumer_discretionary", "financials"],
                "risk_adjustment": "moderate_growth"
            }
        },
        "policy_environment": {
            "policy_count": 15,
            "recent_policy_count": 3,
            "key_policy_themes": ["人工智能", "新能源", "科技创新"]
        },
        "system_status": {
            "status": "运行中",
            "database": "正常",
            "perception_dimensions": 2
        }
    }
    
    # 导入格式化函数
    sys.path.insert(0, str(project_root))
    from egps_daily_report import format_feishu_message
    
    message = format_feishu_message(mock_analysis)
    
    print("✅ 飞书消息格式化测试通过")
    print(f"消息类型: {message.get('msg_type', '未知')}")
    print(f"消息标题: {message['content']['post']['zh_cn']['title']}")
    
    # 显示部分内容
    content = message['content']['post']['zh_cn']['content']
    print("\n消息预览:")
    for section in content[:5]:  # 显示前5个部分
        for item in section:
            if item.get('tag') == 'text':
                print(item.get('text', ''), end='')
    
    print("\n...")
    return True

def test_feishu_config():
    """测试飞书配置"""
    print("\n测试飞书配置...")
    
    feishu_webhook = os.getenv("FEISHU_WEBHOOK_URL")
    
    if feishu_webhook:
        print(f"✅ 飞书Webhook已配置")
        print(f"URL: {feishu_webhook[:50]}...")
        
        # 测试简单消息
        test_message = {
            "msg_type": "text",
            "content": {
                "text": "🔧 EGPS系统飞书推送测试\n时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        try:
            response = requests.post(
                feishu_webhook,
                json=test_message,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    print("✅ 飞书连接测试成功")
                    return True
                else:
                    print(f"❌ 飞书返回错误: {result}")
                    return False
            else:
                print(f"❌ 飞书请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 飞书连接异常: {e}")
            return False
    else:
        print("⚠️  FEISHU_WEBHOOK_URL环境变量未设置")
        print("请设置环境变量:")
        print("  export FEISHU_WEBHOOK_URL='你的飞书Webhook URL'")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("EGPS推送功能测试")
    print("=" * 60)
    
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("EGPS分析获取", test_egps_analysis),
        ("飞书消息格式化", test_feishu_message_format),
        ("飞书配置检查", test_feishu_config),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n▶️ 测试: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！EGPS推送功能就绪")
        print("\n配置说明:")
        print("1. 确保EGPS系统运行: http://localhost:8000")
        print("2. 设置飞书Webhook环境变量:")
        print("   export FEISHU_WEBHOOK_URL='你的飞书Webhook URL'")
        print("3. 定时任务已配置在HEARTBEAT.md中")
        print("4. 工作日08:00自动推送分析报告")
    else:
        print("⚠️  部分测试失败，请检查配置")
    
    print("=" * 60)

if __name__ == "__main__":
    main()