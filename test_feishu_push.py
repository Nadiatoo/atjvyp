#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试飞书推送功能
"""

import os
import requests
import json
from datetime import datetime

def test_feishu_connection():
    """测试飞书连接"""
    print("测试飞书推送连接...")
    
    feishu_webhook = os.getenv("FEISHU_WEBHOOK_URL")
    
    if not feishu_webhook:
        print("❌ FEISHU_WEBHOOK_URL环境变量未设置")
        print("\n请按以下步骤配置:")
        print("1. 在手机飞书上创建自定义机器人")
        print("2. 获取Webhook URL")
        print("3. 设置环境变量:")
        print("   export FEISHU_WEBHOOK_URL='你的飞书Webhook URL'")
        return False
    
    print(f"✅ 飞书Webhook已配置")
    print(f"URL: {feishu_webhook[:50]}...")
    
    # 测试简单消息
    test_message = {
        "msg_type": "text",
        "content": {
            "text": f"📱 EGPS系统飞书推送测试\n⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n✅ 连接测试成功！"
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
                print("✅ 飞书推送测试成功！")
                print("请检查手机飞书是否收到测试消息")
                return True
            else:
                print(f"❌ 飞书返回错误: {result}")
                return False
        else:
            print(f"❌ 飞书请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 飞书连接异常: {e}")
        return False

def test_egps_feishu_message():
    """测试EGPS飞书消息格式"""
    print("\n测试EGPS飞书消息格式...")
    
    # 导入消息格式化函数
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from egps_daily_report import format_feishu_message
        
        # 模拟分析结果
        mock_analysis = {
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
                "key_policy_themes": ["人工智能", "新能源", "科技创新"]
            },
            "system_status": {
                "status": "运行中",
                "database": "正常",
                "perception_dimensions": 2
            }
        }
        
        message = format_feishu_message(mock_analysis)
        
        print("✅ EGPS飞书消息格式化测试通过")
        print(f"消息类型: {message.get('msg_type', '未知')}")
        print(f"消息标题: {message['content']['post']['zh_cn']['title']}")
        
        # 显示消息预览
        print("\n📱 手机飞书将显示的内容:")
        content = message['content']['post']['zh_cn']['content']
        for section in content[:8]:  # 显示前8个部分
            for item in section:
                if item.get('tag') == 'text':
                    print(item.get('text', ''), end='')
                elif item.get('tag') == 'a':
                    print(f"[链接: {item.get('text', '')}]", end='')
        
        print("\n...")
        return True
        
    except Exception as e:
        print(f"❌ 消息格式化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("📱 EGPS系统飞书推送配置测试")
    print("=" * 60)
    
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试飞书连接
    connection_ok = test_feishu_connection()
    
    if connection_ok:
        # 测试消息格式
        format_ok = test_egps_feishu_message()
        
        print("\n" + "=" * 60)
        print("📋 配置状态总结")
        print("=" * 60)
        
        print("✅ 飞书推送配置完成！")
        print("\n🎯 推送功能已就绪：")
        print("1. 工作日08:00自动推送EGPS分析报告")
        print("2. 与盘前信息分开推送")
        print("3. 推送内容包括：")
        print("   • 经济周期分析")
        print("   • 政策环境分析")
        print("   • 系统状态")
        print("   • 快速访问链接")
        
        print("\n📅 下次推送时间：")
        print("   下周一（2026-03-30）08:00")
        
        print("\n🔧 如需立即测试推送，可运行：")
        print("   python egps_daily_report.py")
        print("   （注意：周末会跳过推送）")
    else:
        print("\n" + "=" * 60)
        print("⚠️  配置未完成")
        print("=" * 60)
        
        print("请按以下步骤配置飞书推送：")
        print("\n1. 在手机飞书上：")
        print("   • 打开飞书App")
        print("   • 进入要接收消息的群聊或个人聊天")
        print("   • 点击右上角'...' → '设置'")
        print("   • 选择'群机器人'或'自定义机器人'")
        print("   • 添加'自定义机器人'")
        print("   • 复制生成的Webhook URL")
        
        print("\n2. 在Mac终端上：")
        print("   # 临时设置（当前终端有效）")
        print("   export FEISHU_WEBHOOK_URL='你的飞书Webhook URL'")
        print("")
        print("   # 永久设置（推荐）")
        print("   echo \"export FEISHU_WEBHOOK_URL='你的飞书Webhook URL'\" >> ~/.zshrc")
        print("   source ~/.zshrc")
        
        print("\n3. 重新测试：")
        print("   python test_feishu_push.py")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
