#!/usr/bin/env python3
"""
彪哥战法简单盘前分析 - 使用QVeris数据源
"""

import subprocess
import json
import csv
from datetime import datetime
from io import StringIO

def run_qveris_search(query, limit=5):
    """搜索QVeris工具"""
    script_path = "/Users/tuqibiao/.openclaw/workspace/skills/qveris-official/scripts/qveris_tool.mjs"
    cmd = ["node", script_path, "search", query, f"--limit={limit}"]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return None, None
    
    output = result.stdout
    
    # 提取search_id和tool_id
    search_id = None
    tool_id = None
    
    for line in output.split('\n'):
        if line.startswith("Search ID:"):
            search_id = line.split("Search ID:")[1].strip()
        elif "ID:" in line and not line.startswith("Search ID:"):
            parts = line.split("ID:")
            if len(parts) > 1:
                tool_id = parts[1].strip()
                break
    
    return search_id, tool_id

def run_qveris_execute(tool_id, search_id, params):
    """执行QVeris工具"""
    script_path = "/Users/tuqibiao/.openclaw/workspace/skills/qveris-official/scripts/qveris_tool.mjs"
    cmd = ["node", script_path, "execute", tool_id, "--search-id", search_id, "--params", json.dumps(params)]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return None
    
    return result.stdout

def parse_csv_data(csv_text):
    """解析CSV数据"""
    if not csv_text:
        return None
    
    try:
        # 找到CSV数据部分
        lines = csv_text.split('\n')
        csv_start = -1
        
        for i, line in enumerate(lines):
            if line.strip().startswith('code,') or ',' in line and 'close' in line.lower():
                csv_start = i
                break
        
        if csv_start == -1:
            return None
        
        csv_content = '\n'.join(lines[csv_start:])
        reader = csv.DictReader(StringIO(csv_content))
        
        data = []
        for row in reader:
            data.append(row)
        
        return data
    except Exception as e:
        print(f"解析CSV数据出错: {e}")
        return None

def get_stock_price(ticker):
    """获取股票价格"""
    search_id, tool_id = run_qveris_search("stock price", limit=3)
    
    if not search_id or not tool_id:
        return None
    
    params = {"ticker": ticker}
    output = run_qveris_execute(tool_id, search_id, params)
    
    if not output:
        return None
    
    data = parse_csv_data(output)
    if data and len(data) > 0:
        return data[0]
    
    return None

def generate_biage_report():
    """生成彪哥战法报告"""
    print("=" * 60)
    print("【彪哥战法】盘前市场分析简报")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("数据来源: QVeris实时金融数据")
    print("=" * 60)
    
    # 主要股票指数
    tickers = [
        {"ticker": "NDX.US", "name": "纳斯达克指数"},
        {"ticker": "DJI.US", "name": "道琼斯指数"},
        {"ticker": "SPX.US", "name": "标普500指数"},
        {"ticker": "AAPL.US", "name": "苹果公司"},
        {"ticker": "MSFT.US", "name": "微软公司"},
        {"ticker": "NVDA.US", "name": "英伟达公司"}
    ]
    
    print("\n📊 【美股市场主要指数】")
    
    market_data = []
    total_change = 0
    count = 0
    
    for item in tickers:
        data = get_stock_price(item["ticker"])
        
        if data:
            try:
                close_price = float(data.get("close", 0))
                change = float(data.get("change", 0))
                change_p = float(data.get("change_p", 0)) if data.get("change_p") else 0
                
                market_data.append({
                    "name": item["name"],
                    "price": close_price,
                    "change": change,
                    "change_pct": change_p
                })
                
                total_change += change_p
                count += 1
                
                print(f"  {item['name']}: {close_price:.2f} ({change_p:+.2f}%)")
            except:
                print(f"  {item['name']}: 数据解析失败")
        else:
            print(f"  {item['name']}: 数据获取失败")
    
    print("\n🌍 【市场趋势分析】")
    
    if count > 0:
        avg_change = total_change / count
        
        if avg_change > 0.5:
            trend = "偏多"
            a股预期 = "高开概率较大，关注科技股"
            reason = "美股主要指数普遍上涨"
        elif avg_change < -0.5:
            trend = "偏空"
            a股预期 = "低开概率较大，注意风险"
            reason = "美股主要指数普遍下跌"
        else:
            trend = "震荡"
            a股预期 = "平开或小幅波动"
            reason = "美股指数涨跌互现"
        
        print(f"  平均涨跌幅: {avg_change:+.2f}%")
        print(f"  市场趋势: {trend}")
        print(f"  判断依据: {reason}")
    else:
        trend = "数据不足"
        a股预期 = "需观察"
        print("  数据获取不足，无法进行趋势分析")
    
    print(f"\n🎯 【A股开盘预期】")
    print(f"  {a股预期}")
    
    print("\n📌 【彪哥战法操作建议】")
    
    if "高开" in a股预期:
        print("  1. 可关注科技、新能源等弹性板块")
        print("  2. 逢低布局，避免追高")
        print("  3. 控制仓位在5-7成")
    elif "低开" in a股预期:
        print("  1. 保持谨慎，控制风险")
        print("  2. 回避高位股，持有现金")
        print("  3. 仓位控制在3成以下")
    else:
        print("  1. 市场方向不明，观望为主")
        print("  2. 小仓位试探，快进快出")
        print("  3. 关注成交量变化")
    
    print("\n💡 【核心要点】")
    print("  • 纳斯达克指数对A股科技板块影响显著")
    print("  • 关注苹果、英伟达等龙头股走势")
    print("  • 注意市场情绪和成交量变化")
    
    print("\n⚠️  【风险提示】")
    print("  • 市场有风险，投资需谨慎")
    print("  • 本分析仅供参考，不构成投资建议")
    print("  • 实时数据可能存在延迟")
    print("  • 注意仓位管理和风险控制")
    
    print("\n" + "=" * 60)
    print("彪哥战法：顺势而为，控制风险，知行合一")
    print("=" * 60)
    
    # 保存分析结果
    result = {
        "timestamp": datetime.now().isoformat(),
        "analysis": {
            "trend": trend,
            "a股预期": a股预期,
            "market_data": market_data,
            "avg_change": avg_change if count > 0 else 0
        }
    }
    
    with open("/Users/tuqibiao/.openclaw/workspace/biage_simple_report.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n✓ 分析报告已保存")

if __name__ == "__main__":
    generate_biage_report()