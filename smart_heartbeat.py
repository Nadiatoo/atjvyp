#!/usr/bin/env python3
"""
智能心跳检查脚本
优化OpenClaw心跳检查逻辑，减少不必要的Token消耗
"""

import os
import sys
import json
from datetime import datetime, timedelta
import pytz

# 配置
SHANGHAI_TZ = pytz.timezone('Asia/Shanghai')
WORKDAYS = [0, 1, 2, 3, 4]  # 周一至周五 (0=周一, 4=周五)

def is_workday(now):
    """检查是否为工作日"""
    return now.weekday() in WORKDAYS

def get_next_task_time(now):
    """获取下一个任务执行时间"""
    if not is_workday(now):
        # 非工作日，返回下周一08:00
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0:  # 已经是周一
            days_until_monday = 7
        next_monday = now + timedelta(days=days_until_monday)
        next_task = next_monday.replace(hour=8, minute=0, second=0, microsecond=0)
        return next_task, "下周一08:00（盘前分析）"
    
    # 工作日逻辑
    if now.hour < 8:
        # 08:00之前，返回当天08:00
        next_task = now.replace(hour=8, minute=0, second=0, microsecond=0)
        return next_task, "今天08:00（盘前分析）"
    elif now.hour < 17:
        # 08:00-17:00之间，返回当天17:00
        next_task = now.replace(hour=17, minute=0, second=0, microsecond=0)
        return next_task, "今天17:00（盘后分析）"
    else:
        # 17:00之后，返回下个工作日08:00
        days_to_add = 1
        while True:
            next_day = now + timedelta(days=days_to_add)
            if is_workday(next_day):
                next_task = next_day.replace(hour=8, minute=0, second=0, microsecond=0)
                return next_task, f"{next_day.strftime('%Y-%m-%d')} 08:00（盘前分析）"
            days_to_add += 1

def should_perform_detailed_check(now):
    """判断是否需要执行详细检查"""
    # 非工作日不需要详细检查
    if not is_workday(now):
        return False
    
    # 检查当前时间是否接近任务执行时间
    next_task, _ = get_next_task_time(now)
    time_until_next = (next_task - now).total_seconds()
    
    # 如果距离下一个任务超过2小时，不需要详细检查
    return time_until_next <= 7200  # 2小时

def main():
    """主函数"""
    now = datetime.now(SHANGHAI_TZ)
    next_task, task_desc = get_next_task_time(now)
    time_until_next = (next_task - now).total_seconds()
    
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"是否为工作日: {'是' if is_workday(now) else '否'}")
    print(f"下一个任务: {task_desc}")
    print(f"距离下一个任务: {time_until_next/3600:.1f}小时")
    
    if should_perform_detailed_check(now):
        print("建议: 执行详细心跳检查")
        return 0  # 需要详细检查
    else:
        print("建议: 简单返回HEARTBEAT_OK，跳过详细检查")
        return 1  # 不需要详细检查

if __name__ == "__main__":
    sys.exit(main())