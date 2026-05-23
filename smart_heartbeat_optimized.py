#!/usr/bin/env python3
"""
智能心跳检查脚本 - 优化版
基于任务距离动态控制检查频率，避免Token浪费

返回码说明：
0 = 需要详细检查（距离任务<2小时）
1 = 简单返回HEARTBEAT_OK（距离任务>2小时或非工作日）
"""

import os
import sys
import time
from datetime import datetime, timedelta
import json

# 配置文件路径
CONFIG_FILE = "/tmp/heartbeat_optimized_config.json"
LAST_CHECK_FILE = "/tmp/heartbeat_last_check.json"

def load_config():
    """加载配置"""
    default_config = {
        "min_interval_seconds": 1800,  # 最小检查间隔：30分钟
        "detailed_check_hours": 2,     # 详细检查阈值：2小时
        "max_cache_age": 3600,         # 缓存最大有效期：1小时
        "workdays": [1, 2, 3, 4, 5]    # 工作日：周一到周五
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    return default_config

def save_last_check(result_code, check_time=None):
    """保存上次检查结果"""
    if check_time is None:
        check_time = time.time()
    
    data = {
        "last_check_time": check_time,
        "last_result_code": result_code,
        "last_check_human": datetime.fromtimestamp(check_time).strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        with open(LAST_CHECK_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except:
        pass

def load_last_check():
    """加载上次检查结果"""
    if os.path.exists(LAST_CHECK_FILE):
        try:
            with open(LAST_CHECK_FILE, 'r') as f:
                data = json.load(f)
                # 检查缓存是否过期
                if time.time() - data["last_check_time"] > 3600:  # 1小时过期
                    return None
                return data
        except:
            pass
    return None

def is_workday():
    """判断是否为工作日"""
    now = datetime.now()
    return now.weekday() in [0, 1, 2, 3, 4]  # 周一到周五

def get_next_task_time():
    """获取下一个任务时间"""
    now = datetime.now()
    
    # 今日任务时间
    today_tasks = [
        ("08:00", "盘前分析"),
        ("17:00", "盘后分析")
    ]
    
    # 首先尝试找到今天未来的任务
    for task_time_str, task_name in today_tasks:
        task_time = datetime.strptime(f"{now.strftime('%Y-%m-%d')} {task_time_str}", "%Y-%m-%d %H:%M")
        
        # 如果任务时间在未来
        if task_time > now:
            time_diff = (task_time - now).total_seconds() / 3600  # 小时
            return {
                "task_time": task_time,
                "task_name": task_name,
                "hours_until": time_diff,
                "human_time": task_time.strftime("%Y-%m-%d %H:%M")
            }
    
    # 如果今天所有任务都已过，返回明天第一个任务
    tomorrow = now + timedelta(days=1)
    task_time_str, task_name = today_tasks[0]
    task_time = datetime.strptime(f"{tomorrow.strftime('%Y-%m-%d')} {task_time_str}", "%Y-%m-%d %H:%M")
    
    time_diff = (task_time - now).total_seconds() / 3600  # 小时
    return {
        "task_time": task_time,
        "task_name": task_name,
        "hours_until": time_diff,
        "human_time": task_time.strftime("%Y-%m-%d %H:%M")
    }

def should_skip_check(config, last_check):
    """判断是否应该跳过检查"""
    if last_check is None:
        return False
    
    current_time = time.time()
    time_since_last = current_time - last_check["last_check_time"]
    
    # 如果上次检查在最小间隔内
    if time_since_last < config["min_interval_seconds"]:
        # 如果上次结果是1（不需要详细检查），且距离任务>2小时，可以跳过
        if last_check["last_result_code"] == 1:
            next_task = get_next_task_time()
            if next_task and next_task["hours_until"] > config["detailed_check_hours"]:
                return True
    
    return False

def main():
    """主函数"""
    # 加载配置
    config = load_config()
    
    # 加载上次检查结果
    last_check = load_last_check()
    
    # 判断是否应该跳过检查
    if should_skip_check(config, last_check):
        print(f"跳过检查：距离上次检查不足{config['min_interval_seconds']//60}分钟，且上次结果为1")
        print(f"上次检查时间：{last_check['last_check_human']}")
        sys.exit(1)
    
    # 获取当前时间
    now = datetime.now()
    current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # 判断是否为工作日
    workday = is_workday()
    
    # 获取下一个任务
    next_task = get_next_task_time()
    
    # 输出基本信息
    print(f"当前时间: {current_time_str}")
    print(f"是否为工作日: {'是' if workday else '否'}")
    
    if next_task:
        print(f"下一个任务: {next_task['task_name']} ({next_task['human_time']})")
        print(f"距离下一个任务: {next_task['hours_until']:.1f}小时")
        
        # 判断是否需要详细检查
        if workday and next_task["hours_until"] < config["detailed_check_hours"]:
            print("建议: 执行详细心跳检查")
            result_code = 0
        else:
            print("建议: 简单返回HEARTBEAT_OK，跳过详细检查")
            result_code = 1
    else:
        print("未找到定时任务")
        result_code = 1
    
    # 保存本次检查结果
    save_last_check(result_code)
    
    # 返回结果码
    sys.exit(result_code)

if __name__ == "__main__":
    main()