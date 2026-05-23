#!/usr/bin/env python3
"""
彪哥战法盘前分析 + 飞书推送
整合盘前分析和飞书消息发送功能
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime

def send_to_feishu(message):
    """发送消息到飞书"""
    try:
        # 使用OpenClaw的message工具发送飞书消息
        # 这里使用subprocess调用openclaw命令行工具
        cmd = [
            "openclaw", "message", "send",
            "--channel", "feishu",
            "--message", message
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 飞书消息发送成功")
            return True
        else:
            print(f"❌ 飞书消息发送失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 飞书发送异常: {e}")
        return False

def run_premarket_analysis():
    """运行盘前分析"""
    try:
        # 导入盘前分析模块
        sys.path.append('/Users/tuqibiao/.openclaw/workspace')
        
        # 执行盘前分析脚本
        cmd = ["python3", "/Users/tuqibiao/.openclaw/workspace/biage_premarket_qveris.py"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 盘前分析执行成功")
            
            # 从输出中提取报告内容
            output = result.stdout
            
            # 查找报告开始位置
            report_start = output.find("📈 【彪哥战法】盘前消息分析")
            if report_start != -1:
                report = output[report_start:]
                
                # 截取到适当长度（飞书消息有长度限制）
                if len(report) > 4000:
                    report = report[:4000] + "\n...\n(报告过长，已截断)"
                
                return {
                    "success": True,
                    "report": report,
                    "full_output": output
                }
            else:
                # 如果没有找到标准格式，使用最后1000字符
                report = output[-1000:] if len(output) > 1000 else output
                return {
                    "success": True,
                    "report": f"盘前分析报告:\n{report}",
                    "full_output": output
                }
        else:
            print(f"❌ 盘前分析执行失败: {result.stderr}")
            return {
                "success": False,
                "error": result.stderr
            }
            
    except Exception as e:
        print(f"❌ 盘前分析异常: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """主函数"""
    print("=" * 60)
    print("彪哥战法盘前分析 + 飞书推送")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 运行盘前分析
    analysis_result = run_premarket_analysis()
    
    if not analysis_result["success"]:
        print(f"❌ 分析失败: {analysis_result.get('error', '未知错误')}")
        
        # 发送错误消息到飞书
        error_msg = f"❌ 彪哥战法盘前分析失败\n错误: {analysis_result.get('error', '未知错误')}"
        send_to_feishu(error_msg)
        sys.exit(1)
    
    # 获取报告
    report = analysis_result["report"]
    
    # 添加时间戳
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    full_message = f"📈 【彪哥战法】盘前消息分析 [{time_str}]\n━━━━━━━━━━━━━━━━━━━━━━━━━\n{report}"
    
    # 发送到飞书
    print("\n📤 正在发送飞书消息...")
    send_success = send_to_feishu(full_message)
    
    if send_success:
        print("✅ 盘前分析报告已发送到飞书")
    else:
        print("❌ 飞书消息发送失败，但分析已完成")
        
        # 保存报告到文件
        report_file = f"/tmp/premarket_feishu_failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(full_message)
        print(f"✅ 报告已保存到: {report_file}")
    
    print("\n" + "=" * 60)
    print("执行完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()