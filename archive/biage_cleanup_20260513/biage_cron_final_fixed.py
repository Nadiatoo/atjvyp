#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彪哥战法定时任务最终修正版 - 用于openclaw cron
使用最终修正版逻辑
"""

import sys
import os
import json
import datetime

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_biage_analysis():
    """执行彪哥战法分析（最终修正版）"""
    
    print(f"🚀 彪哥战法定时任务执行 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 导入最终修正版
        from biage_v5_final_fixed import BiageFinal
        
        # 获取当前时间
        current_hour = datetime.datetime.now().hour
        is_premarket = current_hour < 12
        
        if is_premarket:
            print("🌅 执行盘前分析（最终修正版）")
            report_type = "盘前"
        else:
            print("🌇 执行盘后分析（最终修正版）")
            report_type = "盘后"
        
        print()
        
        # 初始化分析器
        analyzer = BiageFinal()
        
        # 获取数据
        print("📊 获取市场数据...")
        market_data = analyzer.get_market_data()
        
        # 分析市场
        print("🎯 彪哥战法分析（最终修正版）...")
        analysis = analyzer.analyze(market_data)
        
        if not analysis:
            print("❌ 分析失败")
            return False
        
        # 生成报告
        report = analyzer.generate_report(analysis, market_data)
        print(report)
        
        # 保存结果
        timestamp = datetime.datetime.now().strftime("%Y%m%d")
        if is_premarket:
            filename = f"/tmp/biage_premarket_{timestamp}.json"
        else:
            filename = f"/tmp/biage_aftermarket_{timestamp}.json"
        
        result_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "report_type": report_type,
            "version": "v5.0最终修正版",
            "market_data": market_data,
            "analysis": analysis,
            "report": report
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 分析结果已保存: {filename}")
        
        # 同时保存文本报告
        txt_filename = filename.replace(".json", ".txt")
        with open(txt_filename, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"📄 文本报告已保存: {txt_filename}")
        
        print("\n✅ 彪哥战法定时任务执行成功（最终修正版）")
        return True
        
    except Exception as e:
        print(f"❌ 定时任务执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_biage_analysis()
    sys.exit(0 if success else 1)