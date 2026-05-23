#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彪哥战法定时任务执行脚本
用法: python3 biage_cron.py [premarket|aftermarket]
"""

import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_analysis():
    """执行分析"""
    try:
        from biage_v5_qveris_fixed import BiageV5QVeris
        
        analyzer = BiageV5QVeris()
        market_data = analyzer.get_market_data()
        analysis = analyzer.analyze(market_data)
        
        if analysis:
            report = analyzer.generate_report(analysis)
            print(report)
            return True
        else:
            print("❌ 分析失败")
            return False
            
    except Exception as e:
        print(f"❌ 执行异常: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 biage_cron.py [premarket|aftermarket]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command in ["premarket", "aftermarket"]:
        success = run_analysis()
        sys.exit(0 if success else 1)
    else:
        print(f"未知命令: {command}")
        sys.exit(1)
