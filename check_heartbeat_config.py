#!/usr/bin/env python3
"""
心跳配置检查脚本
用于验证心跳优化配置
"""

import json
import os
from datetime import datetime

def check_heartbeat_config():
    """检查心跳配置"""
    config_path = "/Users/tuqibiao/.openclaw/heartbeat-override.json"
    
    print("🔍 心跳配置检查")
    print("=" * 50)
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            heartbeat = config.get("heartbeat", {})
            
            print(f"📋 配置文件: {config_path}")
            print(f"📝 配置说明: {config.get('note', 'N/A')}")
            print(f"📅 创建时间: {config.get('created_at', 'N/A')}")
            print(f"🔄 更新时间: {config.get('updated_at', 'N/A')}")
            print(f"📋 更新原因: {config.get('update_reason', 'N/A')}")
            print()
            
            print("⚙️ 心跳配置详情:")
            print(f"  • 基础间隔: {heartbeat.get('interval_ms', 0) / 3600000:.1f} 小时")
            print(f"  • 智能检查: {'✅ 启用' if heartbeat.get('smart_check') else '❌ 禁用'}")
            print(f"  • 跳过周末: {'✅ 启用' if heartbeat.get('skip_weekends') else '❌ 禁用'}")
            print(f"  • 跳过非交易日: {'✅ 启用' if heartbeat.get('skip_non_trading_days') else '❌ 禁用'}")
            print(f"  • 最小任务距离: {heartbeat.get('min_task_distance_hours', 0)} 小时")
            print()
            
            dynamic = heartbeat.get('dynamic_frequency', {})
            if dynamic:
                print("📊 动态频率配置:")
                print(f"  • 近任务阈值: {dynamic.get('near_task_hours', 0)} 小时")
                print(f"  • 近任务间隔: {dynamic.get('near_task_interval_ms', 0) / 3600000:.1f} 小时")
                print(f"  • 远任务间隔: {dynamic.get('far_task_interval_ms', 0) / 3600000:.1f} 小时")
                print(f"  • 非交易日间隔: {dynamic.get('non_trading_interval_ms', 0) / 3600000:.1f} 小时")
            
            schedule = heartbeat.get('optimized_schedule', {})
            if schedule:
                print()
                print("📅 优化调度时间:")
                print(f"  • 交易日: {', '.join(schedule.get('trading_days', []))}")
                print(f"  • 非交易日: {', '.join(schedule.get('non_trading_days', []))}")
            
            print()
            print("✅ 配置检查完成")
            
            # 计算预期节省
            old_frequency = 30  # 分钟，原配置
            new_frequency_min = 60  # 分钟，新配置最小间隔
            new_frequency_max = 240  # 分钟，新配置最大间隔
            
            avg_saving = 1 - (new_frequency_min / old_frequency)
            max_saving = 1 - (new_frequency_max / old_frequency)
            
            print()
            print("💰 预期Token节省:")
            print(f"  • 最小节省: {avg_saving*100:.0f}% (每小时→每4小时)")
            print(f"  • 最大节省: {max_saving*100:.0f}% (每小时→每4小时)")
            print(f"  • 平均节省: {((avg_saving + max_saving)/2)*100:.0f}%")
            
        except Exception as e:
            print(f"❌ 读取配置文件失败: {e}")
    else:
        print(f"❌ 配置文件不存在: {config_path}")
    
    print()
    print("=" * 50)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    check_heartbeat_config()