#!/usr/bin/env python3
"""
盘后分析推送脚本 - 带自动降级机制
先以卡片格式（含表格）推送，失败后自动降级为纯文本重推
"""

import json
import subprocess
import sys
import os
from datetime import datetime

WORKSPACE = "/Users/tuqibiao/.openclaw/workspace"
REPORT_FILE = f"{WORKSPACE}/reports/close_report_pro_{datetime.now().strftime('%Y-%m-%d')}.txt"
FEISHU_USER = "ou_14cc6c3abf853cb0c390d4b0518a5b75"


def generate_report():
    """生成盘后分析报告"""
    print("📊 生成盘后分析报告...")
    result = subprocess.run(
        ["python3", f"{WORKSPACE}/combined_market_close_v2.py"],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        print(f"❌ 报告生成失败: {result.stderr[:500]}")
        return None
    
    # 读取生成的报告
    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE) as f:
            return f.read()
    
    # 尝试找最新报告
    reports_dir = f"{WORKSPACE}/reports"
    files = sorted([f for f in os.listdir(reports_dir) if f.startswith("close_report")], reverse=True)
    if files:
        with open(f"{reports_dir}/{files[0]}") as f:
            return f.read()
    
    return result.stdout


def send_via_openclaw(content, use_card=True):
    """通过openclaw CLI发送消息到飞书"""
    # 将内容写入临时文件，避免shell转义问题
    tmp_file = f"/tmp/postmarket_push_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(tmp_file, 'w') as f:
        f.write(content)
    
    mode = "card" if use_card else "text"
    # 使用 openclaw message 命令发送
    cmd = [
        "openclaw", "message", "send",
        "--channel", "feishu",
        "--target", FEISHU_USER,
        "--file", tmp_file,
    ]
    
    if use_card:
        cmd.extend(["--format", "card-table"])
    else:
        cmd.extend(["--format", "text"])
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    # 清理临时文件
    os.remove(tmp_file)
    
    if result.returncode == 0:
        return True, None
    else:
        error_msg = result.stderr + result.stdout
        # 检查是否是表格超限错误
        if "11310" in error_msg or "card table number over limit" in error_msg:
            return False, "table_overflow"
        return False, error_msg[:500]


def main():
    print(f"🚀 盘后分析推送脚本启动 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # 1. 生成报告
    report = generate_report()
    if not report:
        print("❌ 报告生成失败，跳过推送")
        return 1
    
    print(f"✅ 报告生成完成 ({len(report)} chars)")
    
    # 2. 用卡片格式推送（优先）
    print("📤 尝试卡片格式推送（含表格）...")
    success, error = send_via_openclaw(report, use_card=True)
    
    if success:
        print("✅ 卡片推送成功！")
        return 0
    
    if error == "table_overflow":
        print("⚠️ 表格超限，降级为纯文本推送...")
        success, error = send_via_openclaw(report, use_card=False)
        if success:
            print("✅ 纯文本推送成功（降级）")
            return 0
        else:
            print(f"❌ 纯文本推送也失败: {error}")
            return 1
    else:
        print(f"❌ 推送失败: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
