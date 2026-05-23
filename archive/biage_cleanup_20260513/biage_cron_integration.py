#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彪哥战法定时任务集成脚本
用于openclaw cron定时任务调用
"""

import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        from biage_v5_final import BiageV5Final
        
        print("🚀 彪哥战法定时任务执行开始")
        print("=" * 50)
        
        analyzer = BiageV5Final()
        market_data = analyzer.get_market_data()
        analysis = analyzer.analyze(market_data)
        
        if analysis:
            # 根据时间决定报告类型
            import datetime
            current_hour = datetime.datetime.now().hour
            
            if current_hour < 12:
                report_type = "premarket"
                print("🌅 执行盘前分析")
            else:
                report_type = "standard"
                print("🌇 执行盘后分析")
            
            report = analyzer.generate_report(analysis, report_type)
            print(report)
            
            # 保存到标准位置供其他系统使用
            import json
            timestamp = datetime.datetime.now().strftime("%Y%m%d")
            
            if report_type == "premarket":
                filename = f"/tmp/biage_premarket_{timestamp}.json"
            else:
                filename = f"/tmp/biage_aftermarket_{timestamp}.json"
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "report_type": report_type,
                    "analysis": analysis,
                    "report": report
                }, f, ensure_ascii=False, indent=2)
            
            print(f"📁 结果已保存: {filename}")
            print("✅ 定时任务执行成功")
            return 0
        else:
            print("❌ 分析失败")
            return 1
            
    except Exception as e:
        print(f"❌ 定时任务异常: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
