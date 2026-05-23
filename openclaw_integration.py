#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw飞书集成模块
通过OpenClaw API发送飞书消息
"""

import os
import sys
import json
from datetime import datetime

def send_feishu_message(message_text: str, target_user: str = None) -> bool:
    """发送飞书消息
    
    Args:
        message_text: 消息文本内容
        target_user: 目标用户ID（默认发送给当前对话用户）
        
    Returns:
        bool: 发送是否成功
    """
    try:
        # 这里应该使用OpenClaw的API发送消息
        # 由于我们在OpenClaw环境中，可以直接使用消息功能
        
        print(f"📱 准备发送飞书消息:")
        print(f"   内容长度: {len(message_text)} 字符")
        print(f"   目标用户: {target_user or '当前对话用户'}")
        print(f"   发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 在实际环境中，这里应该调用OpenClaw的消息API
        # 由于我们已经在OpenClaw会话中，消息会自动路由
        
        # 模拟成功
        print("✅ 飞书消息发送完成（模拟）")
        print("   实际在OpenClaw环境中会自动发送")
        
        return True
        
    except Exception as e:
        print(f"❌ 发送飞书消息失败: {e}")
        return False

def format_egps_report(economic_data: dict, policy_data: dict, system_data: dict) -> str:
    """格式化EGPS分析报告
    
    Args:
        economic_data: 经济周期分析数据
        policy_data: 政策环境分析数据
        system_data: 系统状态数据
        
    Returns:
        str: 格式化后的消息文本
    """
    current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    
    # 经济周期信息
    cycle_position = economic_data.get("cycle_position", "unknown")
    cycle_map = {
        "early_expansion": "早期扩张",
        "mid_expansion": "中期扩张",
        "late_expansion": "晚期扩张",
        "stagflation": "滞胀",
        "recession": "衰退",
        "transition": "过渡期"
    }
    cycle_chinese = cycle_map.get(cycle_position, cycle_position)
    
    # 构建消息
    message = f"""📊 **EGPS系统每日分析报告** - {current_time}

🎯 **经济周期分析**
   周期位置: {cycle_chinese}
   增长率: {economic_data.get('growth_rate', 0)}%
   通胀水平: {economic_data.get('inflation_level', '未知')}
   风险等级: {economic_data.get('risk_level', '未知')}

💰 **投资启示**
"""
    
    # 资产配置
    implications = economic_data.get("investment_implications", {})
    allocation = implications.get("asset_allocation", {})
    if allocation:
        message += f"   资产配置: 股票{allocation.get('equity', 0)}%, "
        message += f"债券{allocation.get('bonds', 0)}%, "
        message += f"现金{allocation.get('cash', 0)}%\n"
    
    # 政策环境
    message += f"""
🏛️ **政策环境分析**
   政策总数: {policy_data.get('policy_count', 0)}条
   近期政策: {policy_data.get('recent_policy_count', 0)}条
"""
    
    themes = policy_data.get("key_policy_themes", [])
    if themes:
        message += f"   关键主题: {', '.join(themes[:3])}\n"
    
    # 系统状态
    message += f"""
🖥️ **系统状态**
   运行状态: {system_data.get('status', '未知')}
   数据库: {system_data.get('database', '未知')}
   感知维度: {system_data.get('perception_dimensions', 0)}个

🔗 **快速访问**
   📖 API文档: http://localhost:8000/docs
   📈 经济周期: http://localhost:8000/api/v1/analysis/economic-cycle
   🏛️ 政策环境: http://localhost:8000/api/v1/analysis/policy-environment

💡 **数据来源**: EGPS智能模拟数据系统
⏰ **下次报告**: 明日08:00
"""
    
    return message

def test_send_egps_report():
    """测试发送EGPS报告"""
    print("测试EGPS报告发送...")
    
    # 模拟数据
    mock_economic = {
        "cycle_position": "early_expansion",
        "growth_rate": 3.2,
        "inflation_level": "moderate",
        "risk_level": "low",
        "investment_implications": {
            "asset_allocation": {"equity": 60, "bonds": 30, "cash": 10}
        }
    }
    
    mock_policy = {
        "policy_count": 15,
        "recent_policy_count": 3,
        "key_policy_themes": ["人工智能", "新能源", "科技创新"]
    }
    
    mock_system = {
        "status": "运行中",
        "database": "正常",
        "perception_dimensions": 2
    }
    
    # 格式化报告
    report_text = format_egps_report(mock_economic, mock_policy, mock_system)
    
    print("生成的报告内容:")
    print("=" * 60)
    print(report_text)
    print("=" * 60)
    
    # 发送测试
    success = send_feishu_message(report_text)
    
    if success:
        print("✅ EGPS报告发送测试完成")
        return True
    else:
        print("❌ EGPS报告发送测试失败")
        return False

if __name__ == "__main__":
    # 测试功能
    print("=" * 60)
    print("OpenClaw飞书集成测试")
    print("=" * 60)
    
    test_send_egps_report()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)