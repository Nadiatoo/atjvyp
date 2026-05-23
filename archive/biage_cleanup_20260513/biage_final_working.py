#!/usr/bin/env python3
"""
彪哥战法盘前分析 - 最终工作版本
使用QVeris数据源
"""

import subprocess
import json
import csv
from datetime import datetime
from io import StringIO

def get_stock_data(ticker):
    """获取股票数据"""
    # 搜索工具
    script_path = "/Users/tuqibiao/.openclaw/workspace/skills/qveris-official/scripts/qveris_tool.mjs"
    
    # 搜索股票价格工具
    search_cmd = ["node", script_path, "search", "stock price", "--limit=3"]
    search_result = subprocess.run(search_cmd, capture_output=True, text=True, timeout=30)
    
    if search_result.returncode != 0:
        return None
    
    # 提取search_id
    search_id = None
    for line in search_result.stdout.split('\n'):
        if line.startswith("Search ID:"):
            search_id = line.split("Search ID:")[1].strip()
            break
    
    if not search_id:
        return None
    
    # 使用找到的第一个工具
    tool_id = "eodhd.live_prices.retrieve.v1.178541d4"
    
    # 执行工具
    params = {"ticker": ticker}
    execute_cmd = ["node", script_path, "execute", tool_id, "--search-id", search_id, "--params", json.dumps(params), "--json"]
    
    execute_result = subprocess.run(execute_cmd, capture_output=True, text=True, timeout=30)
    
    if execute_result.returncode != 0:
        return None
    
    try:
        result_data = json.loads(execute_result.stdout)
        if result_data.get("success") and "result" in result_data:
            csv_data = result_data["result"].get("data", "")
            
            # 解析CSV
            if csv_data:
                reader = csv.DictReader(StringIO(csv_data))
                for row in reader:
                    return row
    except:
        pass
    
    return None

def generate_biage_analysis():
    """生成彪哥战法分析报告"""
    print("=" * 70)
    print("                    【彪哥战法】盘前市场分析报告")
    print(f"                    分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("                    数据来源: QVeris金融数据平台")
    print("=" * 70)
    
    print("\n" + "📊 " + "美股市场实时数据".center(60, "─"))
    
    # 获取关键股票数据
    stocks = [
        {"ticker": "AAPL.US", "name": "苹果", "sector": "科技"},
        {"ticker": "MSFT.US", "name": "微软", "sector": "科技"},
        {"ticker": "NVDA.US", "name": "英伟达", "sector": "科技"},
        {"ticker": "TSLA.US", "name": "特斯拉", "sector": "新能源"},
        {"ticker": "JPM.US", "name": "摩根大通", "sector": "金融"}
    ]
    
    stock_data = []
    
    for stock in stocks:
        print(f"\n  获取{stock['name']}数据中...", end="", flush=True)
        data = get_stock_data(stock["ticker"])
        
        if data:
            try:
                price = float(data.get("close", 0))
                change = float(data.get("change", 0))
                change_p = float(data.get("change_p", 0)) if data.get("change_p") else 0
                
                stock_data.append({
                    "name": stock["name"],
                    "sector": stock["sector"],
                    "price": price,
                    "change": change,
                    "change_pct": change_p
                })
                
                print(f"\r  {stock['name']:8} ${price:8.2f} ({change_p:+.2f}%) [{stock['sector']}]")
            except:
                print(f"\r  {stock['name']:8} 数据解析失败")
        else:
            print(f"\r  {stock['name']:8} 数据获取失败")
    
    print("\n" + "🌍 " + "市场趋势分析".center(60, "─"))
    
    if stock_data:
        # 计算平均涨跌幅
        tech_stocks = [s for s in stock_data if s["sector"] == "科技"]
        tech_change = sum(s["change_pct"] for s in tech_stocks) / len(tech_stocks) if tech_stocks else 0
        
        total_change = sum(s["change_pct"] for s in stock_data) / len(stock_data)
        
        print(f"\n  科技股平均涨跌: {tech_change:+.2f}%")
        print(f"  整体平均涨跌: {total_change:+.2f}%")
        
        # 趋势判断
        if tech_change > 0.5 and total_change > 0:
            trend = "偏多"
            reason = "科技股领涨，市场情绪积极"
            a股预期 = "高开概率大，科技板块可能表现强势"
        elif tech_change < -0.5 and total_change < 0:
            trend = "偏空"
            reason = "科技股领跌，市场情绪谨慎"
            a股预期 = "低开概率大，注意风险控制"
        elif abs(total_change) < 0.3:
            trend = "震荡"
            reason = "市场波动较小，方向不明"
            a股预期 = "平开或小幅波动，等待方向选择"
        else:
            trend = "分化"
            reason = "板块表现分化，结构性行情"
            a股预期 = "板块轮动，精选个股"
        
        print(f"\n  市场趋势判断: {trend}")
        print(f"  判断依据: {reason}")
    else:
        trend = "数据不足"
        a股预期 = "需观察市场动态"
        print("\n  数据获取不足，建议观察市场开盘情况")
    
    print("\n" + "🎯 " + "彪哥战法A股策略".center(60, "─"))
    print(f"\n  📈 开盘预期: {a股预期}")
    
    print("\n  📋 操作策略:")
    
    if trend == "偏多":
        print("    1. ✅ 关注科技、新能源等弹性板块")
        print("    2. ✅ 逢低布局龙头股，避免追高")
        print("    3. ✅ 仓位建议: 5-7成")
        print("    4. ⚠️  风险控制: 设置止损位")
    elif trend == "偏空":
        print("    1. ⚠️  保持谨慎，控制仓位")
        print("    2. ⚠️  回避高位股，持有现金")
        print("    3. ⚠️  仓位建议: 3成以下")
        print("    4. ✅ 机会关注: 超跌反弹机会")
    elif trend == "震荡":
        print("    1. 🔄 高抛低吸，波段操作")
        print("    2. 🔄 关注成交量变化")
        print("    3. 🔄 仓位建议: 4-6成")
        print("    4. ⚠️  避免追涨杀跌")
    else:
        print("    1. 👀 观望为主，等待信号")
        print("    2. 👀 小仓位试探")
        print("    3. 👀 关注市场情绪")
        print("    4. ⚠️  严格控制风险")
    
    print("\n" + "💡 " + "核心观察要点".center(60, "─"))
    print("\n  1. 纳斯达克指数对A股科技板块的传导效应")
    print("  2. 苹果、英伟达等龙头股走势")
    print("  3. 北向资金流向和成交量变化")
    print("  4. 市场情绪指标和板块轮动")
    
    print("\n" + "⚠️  " + "风险提示".center(60, "─"))
    print("\n  • 市场有风险，投资需谨慎")
    print("  • 本分析基于公开数据，仅供参考")
    print("  • 实时数据可能存在延迟")
    print("  • 投资决策需结合个人风险承受能力")
    
    print("\n" + "=" * 70)
    print("          彪哥战法核心原则: 顺势而为，控制风险，知行合一")
    print("=" * 70)
    
    # 保存分析结果
    result = {
        "timestamp": datetime.now().isoformat(),
        "stock_data": stock_data,
        "analysis": {
            "trend": trend,
            "a股预期": a股预期,
            "tech_change": tech_change if stock_data else 0,
            "total_change": total_change if stock_data else 0
        }
    }
    
    with open("/Users/tuqibiao/.openclaw/workspace/biage_final_report.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 分析报告已保存至: biage_final_report.json")
    
    # 返回简洁摘要
    summary = f"""
【彪哥战法盘前分析摘要】
时间: {datetime.now().strftime('%H:%M')}
趋势: {trend}
A股预期: {a股预期}
数据状态: {'数据获取成功' if stock_data else '数据获取部分失败'}
建议: {'积极关注科技板块' if trend == '偏多' else '谨慎控制仓位'}
"""
    
    return summary

if __name__ == "__main__":
    summary = generate_biage_analysis()
    print(summary)