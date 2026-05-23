#!/usr/bin/env python3
"""
会话清理脚本
策略：
1. 保留最近7天内的会话
2. 保留大于100KB的重要会话
3. 清理旧的、小的会话文件
"""

import os
import json
import shutil
from datetime import datetime, timedelta
import time

def cleanup_sessions():
    """清理会话文件"""
    sessions_dir = "/Users/tuqibiao/.openclaw/agents/main/sessions"
    backup_dir = "/Users/tuqibiao/.openclaw/workspace/session_backup_20260416"
    
    # 确保备份目录存在
    os.makedirs(backup_dir, exist_ok=True)
    
    # 计算7天前的时间戳
    seven_days_ago = time.time() - (7 * 24 * 3600)
    
    # 统计信息
    stats = {
        "total_files": 0,
        "kept_files": 0,
        "backup_files": 0,
        "deleted_files": 0,
        "kept_by_age": 0,
        "kept_by_size": 0,
        "backup_by_importance": 0
    }
    
    print("🔍 开始清理会话文件")
    print("=" * 60)
    
    # 遍历所有会话文件
    for filename in os.listdir(sessions_dir):
        if not filename.endswith('.jsonl'):
            continue
            
        filepath = os.path.join(sessions_dir, filename)
        stats["total_files"] += 1
        
        # 获取文件信息
        file_stat = os.stat(filepath)
        file_size = file_stat.st_size
        file_mtime = file_stat.st_mtime
        file_age_days = (time.time() - file_mtime) / (24 * 3600)
        
        # 判断是否保留
        keep = False
        reason = ""
        
        # 规则1：保留最近7天内的文件
        if file_mtime > seven_days_ago:
            keep = True
            reason = "最近7天内"
            stats["kept_by_age"] += 1
        
        # 规则2：保留大于100KB的重要文件
        elif file_size > 100 * 1024:  # 100KB
            keep = True
            reason = f"重要文件 ({file_size/1024:.1f}KB)"
            stats["kept_by_size"] += 1
        
        # 规则3：对于中等大小的文件（10KB-100KB），备份后删除
        elif file_size > 10 * 1024:  # 10KB
            # 备份文件
            backup_path = os.path.join(backup_dir, filename)
            shutil.copy2(filepath, backup_path)
            stats["backup_files"] += 1
            stats["backup_by_importance"] += 1
            reason = f"已备份 ({file_size/1024:.1f}KB)"
        
        # 规则4：删除小的、旧的文件
        else:
            reason = f"删除 ({file_size/1024:.1f}KB, {file_age_days:.1f}天前)"
        
        # 输出文件信息
        mtime_str = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M')
        print(f"{filename[:36]}... | {mtime_str} | {file_size/1024:6.1f}KB | {reason}")
        
        # 执行操作
        if keep:
            stats["kept_files"] += 1
        elif file_size > 10 * 1024:
            # 已备份，现在删除原文件
            os.remove(filepath)
            stats["deleted_files"] += 1
        else:
            # 直接删除小文件
            os.remove(filepath)
            stats["deleted_files"] += 1
    
    print("=" * 60)
    print("📊 清理统计:")
    print(f"  总文件数: {stats['total_files']}")
    print(f"  保留文件: {stats['kept_files']}")
    print(f"    - 按时间保留: {stats['kept_by_age']}")
    print(f"    - 按大小保留: {stats['kept_by_size']}")
    print(f"  备份文件: {stats['backup_files']}")
    print(f"    - 重要文件备份: {stats['backup_by_importance']}")
    print(f"  删除文件: {stats['deleted_files']}")
    
    # 计算节省空间
    backup_size = sum(os.path.getsize(os.path.join(backup_dir, f)) 
                     for f in os.listdir(backup_dir) if f.endswith('.jsonl'))
    
    print(f"\n💾 备份大小: {backup_size/1024:.1f}KB")
    print(f"📅 备份位置: {backup_dir}")
    print(f"🕒 清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 生成清理报告
    report_path = os.path.join(backup_dir, "cleanup_report.md")
    with open(report_path, 'w') as f:
        f.write(f"# 会话清理报告\n\n")
        f.write(f"**清理时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 清理策略\n")
        f.write(f"1. 保留最近7天内的会话文件\n")
        f.write(f"2. 保留大于100KB的重要会话文件\n")
        f.write(f"3. 备份10KB-100KB的中等重要性文件\n")
        f.write(f"4. 删除小于10KB的旧文件\n\n")
        f.write(f"## 清理统计\n")
        f.write(f"- 总文件数: {stats['total_files']}\n")
        f.write(f"- 保留文件: {stats['kept_files']}\n")
        f.write(f"- 备份文件: {stats['backup_files']}\n")
        f.write(f"- 删除文件: {stats['deleted_files']}\n\n")
        f.write(f"## 备份信息\n")
        f.write(f"- 备份目录: {backup_dir}\n")
        f.write(f"- 备份大小: {backup_size/1024:.1f}KB\n")
    
    print(f"\n📋 清理报告已保存: {report_path}")

if __name__ == "__main__":
    cleanup_sessions()