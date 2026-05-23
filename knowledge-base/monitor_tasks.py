#!/usr/bin/env python3
"""
监控08:00任务执行情况
"""

import os
import sys
import time
import subprocess
from datetime import datetime, timedelta

def check_openclaw_status():
    """检查OpenClaw状态"""
    print("🔍 检查OpenClaw状态...")
    try:
        result = subprocess.run(
            ["openclaw", "gateway", "status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "running" in result.stdout or "active" in result.stdout:
            print("✅ OpenClaw网关运行正常")
            return True
        else:
            print("❌ OpenClaw网关状态异常")
            print(result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ OpenClaw检查超时")
        return False
    except Exception as e:
        print(f"❌ OpenClaw检查失败: {e}")
        return False

def check_cron_tasks():
    """检查定时任务状态"""
    print("\n🔍 检查定时任务状态...")
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ 定时任务列表获取成功")
            
            # 查找08:00相关任务
            lines = result.stdout.split('\n')
            task_found = False
            
            for line in lines:
                if "08:00" in line or "盘前分析" in line or "EGPS" in line:
                    print(f"📋 任务: {line.strip()}")
                    task_found = True
            
            if not task_found:
                print("⚠️ 未找到08:00相关任务")
                
            return True
        else:
            print("❌ 定时任务列表获取失败")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ 定时任务检查超时")
        return False
    except Exception as e:
        print(f"❌ 定时任务检查失败: {e}")
        return False

def check_task_execution():
    """检查任务执行情况"""
    print("\n🔍 检查任务执行情况...")
    
    # 检查日志文件
    log_dir = "/tmp/openclaw"
    if os.path.exists(log_dir):
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        log_files.sort(reverse=True)  # 最新的在前
        
        if log_files:
            latest_log = os.path.join(log_dir, log_files[0])
            print(f"📝 最新日志文件: {log_files[0]}")
            
            try:
                # 读取最后100行
                with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[-100:]
                
                # 查找08:00相关日志
                task_logs = []
                for line in lines:
                    if "08:00" in line or "cron" in line or "task" in line or "执行" in line:
                        task_logs.append(line.strip())
                
                if task_logs:
                    print("📋 找到任务执行日志:")
                    for log in task_logs[-5:]:  # 显示最后5条
                        print(f"  {log}")
                else:
                    print("📭 未找到任务执行日志")
                    
            except Exception as e:
                print(f"❌ 日志读取失败: {e}")
        else:
            print("📭 未找到日志文件")
    else:
        print("📭 日志目录不存在")
    
    return True

def check_knowledge_base():
    """检查知识库状态"""
    print("\n🔍 检查知识库状态...")
    
    kb_dir = "/Users/tuqibiao/.openclaw/workspace/knowledge-base"
    if os.path.exists(kb_dir):
        # 检查文件数量
        result = subprocess.run(
            ["find", "raw/domains", "-name", "*.md"],
            cwd=kb_dir,
            capture_output=True,
            text=True
        )
        
        file_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        print(f"📚 知识库文件数: {file_count}")
        
        # 检查处理报告
        report_dir = os.path.join(kb_dir, "raw/processed/replays")
        if os.path.exists(report_dir):
            reports = [f for f in os.listdir(report_dir) if f.startswith("batch_report")]
            if reports:
                reports.sort(reverse=True)
                latest_report = reports[0]
                print(f"📊 最新处理报告: {latest_report}")
            else:
                print("📭 未找到处理报告")
        else:
            print("📭 处理报告目录不存在")
        
        return True
    else:
        print("❌ 知识库目录不存在")
        return False

def wait_for_task_completion(timeout_minutes=10):
    """等待任务完成"""
    print(f"\n⏳ 等待任务执行完成 (最多等待{timeout_minutes}分钟)...")
    
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=timeout_minutes)
    
    while datetime.now() < end_time:
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"🕐 当前时间: {current_time} - 等待中...")
        
        # 每30秒检查一次
        time.sleep(30)
        
        # 检查是否有新日志
        log_dir = "/tmp/openclaw"
        if os.path.exists(log_dir):
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            if log_files:
                latest_log = os.path.join(log_dir, sorted(log_files, reverse=True)[0])
                
                try:
                    with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # 检查任务完成标志
                    if "completed" in content.lower() or "finished" in content.lower() or "success" in content.lower():
                        print("✅ 检测到任务完成标志")
                        return True
                        
                except:
                    pass
        
        # 检查是否已经过了08:10
        if datetime.now().hour == 8 and datetime.now().minute >= 10:
            print("🕐 时间已到08:10，开始下一步工作")
            return True
    
    print("⏰ 等待超时，继续下一步工作")
    return False

def main():
    """主函数"""
    print("📊 08:00任务执行监控")
    print("="*60)
    print(f"🕐 开始时间: {datetime.now().strftime('%H:%M:%S')}")
    print("")
    
    # 检查当前状态
    status_checks = [
        ("OpenClaw状态", check_openclaw_status),
        ("定时任务", check_cron_tasks),
        ("知识库状态", check_knowledge_base)
    ]
    
    all_ok = True
    for check_name, check_func in status_checks:
        print(f"\n📋 {check_name}检查:")
        if not check_func():
            all_ok = False
    
    if not all_ok:
        print("\n⚠️ 系统状态检查发现问题")
        return
    
    print("\n" + "="*60)
    print("🎯 监控计划:")
    print("1. 等待08:00任务自动执行")
    print("2. 监控执行日志")
    print("3. 检查执行结果")
    print("4. 08:10后开始知识库完善工作")
    print("="*60)
    
    # 等待任务执行
    wait_for_task_completion()
    
    # 检查执行情况
    print("\n" + "="*60)
    print("📋 任务执行后检查:")
    check_task_execution()
    
    print("\n" + "="*60)
    print("✅ 监控完成")
    print("🚀 可以开始知识库完善工作")

if __name__ == "__main__":
    main()