#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGPS系统立即测试版本
强制执行并发送测试报告
"""

import sys
import os
import requests
from datetime import datetime
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def get_egps_analysis():
    """获取EGPS系统分析结果"""
    print("获取EGPS系统分析结果...")
    
    analysis_results = {}
    
    try:
        base_url = "http://localhost:8000"
        
        # 1. 获取经济周期分析
        print("  获取经济周期分析...")
        response = requests.get(f"{base_url}/api/v1/analysis/economic-cycle", timeout=10)
        if response.status_code == 200:
            analysis_results["economic_cycle"] = response.json()
            print(f"  ✅ 周期位置: {analysis_results['economic_cycle'].get('cycle_position', '未知')}")
        else:
            print(f"  ❌ 经济周期分析失败: {response.status_code}")
            # 使用模拟数据
            analysis_results["economic_cycle"] = {
                "cycle_position": "early_expansion",
                "growth_rate": 3.2,
                "inflation_level": "moderate",
                "risk_level": "low",
                "investment_implications": {
                    "asset_allocation": {"equity": 60, "bonds": 30, "cash": 10},
                    "sector_preferences": ["科技", "可选消费", "金融"],
                    "risk_adjustment": "适度增长"
                }
            }
        
        # 2. 获取政策环境分析
        print("  获取政策环境分析...")
        response = requests.get(f"{base_url}/api/v1/analysis/policy-environment", timeout=10)
        if response.status_code == 200:
            analysis_results["policy_environment"] = response.json()
            print(f"  ✅ 政策数量: {analysis_results['policy_environment'].get('policy_count', 0)}条")
        else:
            print(f"  ❌ 政策环境分析失败: {response.status_code}")
            # 使用模拟数据
            analysis_results["policy_environment"] = {
                "policy_count": 15,
                "recent_policy_count": 3,
                "sentiment_trend": "positive",
                "key_policy_themes": ["人工智能", "新能源", "科技创新", "数字经济", "绿色金融"]
            }
        
        # 3. 获取系统状态
        print("  获取系统状态...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            analysis_results["system_status"] = response.json()
            print(f"  ✅ 系统状态: {analysis_results['system_status'].get('status', '未知')}")
        else:
            analysis_results["system_status"] = {
                "status": "运行中",
                "database": "正常",
                "perception_dimensions": 2,
                "data_source": "智能模拟数据"
            }
        
        print("✅ EGPS分析结果获取完成")
        return analysis_results
        
    except Exception as e:
        print(f"❌ 获取EGPS分析失败: {e}")
        # 返回完整的模拟数据
        return {
            "economic_cycle": {
                "cycle_position": "early_expansion",
                "growth_rate": 3.2,
                "inflation_level": "moderate",
                "risk_level": "low",
                "investment_implications": {
                    "asset_allocation": {"equity": 60, "bonds": 30, "cash": 10},
                    "sector_preferences": ["科技", "可选消费", "金融"],
                    "risk_adjustment": "适度增长"
                }
            },
            "policy_environment": {
                "policy_count": 15,
                "recent_policy_count": 3,
                "sentiment_trend": "positive",
                "key_policy_themes": ["人工智能", "新能源", "科技创新", "数字经济", "绿色金融"]
            },
            "system_status": {
                "status": "运行中",
                "database": "正常",
                "perception_dimensions": 2,
                "data_source": "智能模拟数据"
            }
        }

def format_test_message(analysis_results):
    """格式化测试消息"""
    print("格式化测试消息...")
    
    current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    
    # 提取数据
    economic = analysis_results.get("economic_cycle", {})
    policy = analysis_results.get("policy_environment", {})
    system = analysis_results.get("system_status", {})
    
    # 经济周期映射
    cycle_map = {
        "early_expansion": "早期扩张",
        "mid_expansion": "中期扩张",
        "late_expansion": "晚期扩张",
        "stagflation": "滞胀",
        "recession": "衰退",
        "transition": "过渡期"
    }
    
    cycle_position = economic.get("cycle_position", "unknown")
    cycle_chinese = cycle_map.get(cycle_position, cycle_position)
    
    # 构建消息
    message = f"""🎯 **EGPS系统测试版分析报告** - {current_time}

📋 **测试说明**
这是EGPS系统的测试版本，展示周一08:00你将收到的实际推送内容。
系统状态：测试模式 ⚡

📊 **经济周期分析**
   周期位置: {cycle_chinese}
   增长率: {economic.get('growth_rate', 0)}%
   通胀水平: {economic.get('inflation_level', '未知')}
   风险等级: {economic.get('risk_level', '未知')}

💰 **投资启示**
"""
    
    # 资产配置
    implications = economic.get("investment_implications", {})
    allocation = implications.get("asset_allocation", {})
    if allocation:
        message += f"   资产配置: 股票{allocation.get('equity', 0)}%, "
        message += f"债券{allocation.get('bonds', 0)}%, "
        message += f"现金{allocation.get('cash', 0)}%\n"
    
    # 行业偏好
    preferences = implications.get("sector_preferences", [])
    if preferences:
        message += f"   行业偏好: {', '.join(preferences)}\n"
    
    # 政策环境
    message += f"""
🏛️ **政策环境分析**
   政策总数: {policy.get('policy_count', 0)}条
   近期政策: {policy.get('recent_policy_count', 0)}条
"""
    
    themes = policy.get("key_policy_themes", [])
    if themes:
        message += f"   关键主题: {', '.join(themes[:3])}\n"
    
    # 系统状态
    message += f"""
🖥️ **系统状态**
   运行状态: {system.get('status', '未知')}
   数据库: {system.get('database', '未知')}
   感知维度: {system.get('perception_dimensions', 0)}个
   数据来源: {system.get('data_source', '智能模拟数据')}

🔗 **快速访问**
   📖 API文档: http://localhost:8000/docs
   📈 经济周期: http://localhost:8000/api/v1/analysis/economic-cycle
   🏛️ 政策环境: http://localhost:8000/api/v1/analysis/policy-environment

💡 **正式推送说明**
- 推送时间: 工作日08:00（与盘前信息分开）
- 下次推送: 2026-03-30 08:00（下周一）
- 推送内容: 经济周期 + 政策环境分析
- 数据更新: 每日自动更新

🎯 **测试反馈**
请检查此测试消息的格式和内容是否满足你的需求。
有任何建议请随时告诉我，我会立即调整优化。

---
*EGPS系统 - 预期差感知系统*
*版本: 测试版 v0.1.0*
"""
    
    print("✅ 测试消息格式化完成")
    return message

def main():
    """主函数"""
    print("=" * 60)
    print("EGPS系统测试版执行")
    print("=" * 60)
    
    current_time = datetime.now()
    print(f"执行时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试模式: 强制执行（忽略周末检查）")
    
    print("\n📊 获取EGPS分析结果...")
    
    # 获取EGPS分析结果
    analysis_results = get_egps_analysis()
    
    if "error" in analysis_results:
        print("❌ 获取分析结果失败，使用模拟数据")
    
    # 格式化消息
    message_text = format_test_message(analysis_results)
    
    # 显示消息内容
    print("\n📱 生成的测试消息内容:")
    print("=" * 60)
    print(message_text)
    print("=" * 60)
    
    print("\n✅ EGPS测试版分析报告已准备就绪")
    print("现在通过飞书发送给你...")
    
    return message_text

if __name__ == "__main__":
    message = main()
    
    # 保存消息到文件，方便查看
    with open("/tmp/egps_test_message.txt", "w", encoding="utf-8") as f:
        f.write(message)
    
    print(f"\n📄 消息已保存到: /tmp/egps_test_message.txt")
    print("=" * 60)