#!/usr/bin/env python3
"""
简单测试QVeris获取市场数据
"""

import subprocess
import json
from datetime import datetime

def run_qveris(command):
    """运行QVeris命令"""
    script_path = "/Users/tuqibiao/.openclaw/workspace/skills/qveris-official/scripts/qveris_tool.mjs"
    cmd = ["node", script_path] + command
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"错误: {result.stderr}")
            return None
        
        return result.stdout
    except Exception as e:
        print(f"异常: {e}")
        return None

def main():
    print("测试QVeris市场数据获取...")
    
    # 搜索股票数据工具
    print("\n1. 搜索股票数据工具...")
    output = run_qveris(["search", "real-time stock price", "--limit=5"])
    if output:
        print(output[:500])
    
    # 搜索加密货币工具
    print("\n2. 搜索加密货币工具...")
    output = run_qveris(["search", "cryptocurrency price", "--limit=3"])
    if output:
        print(output[:500])
    
    # 搜索新闻工具
    print("\n3. 搜索财经新闻工具...")
    output = run_qveris(["search", "financial news", "--limit=3"])
    if output:
        print(output[:500])
    
    print("\n测试完成")

if __name__ == "__main__":
    main()