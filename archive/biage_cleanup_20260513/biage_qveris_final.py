#!/usr/bin/env python3
"""
彪哥战法盘前分析 - QVeris数据源最终版
"""

import subprocess
import json
import re
from datetime import datetime

def run_qveris_search(query, limit=10):
    """搜索QVeris工具并返回search_id"""
    script_path = "/Users/tuqibiao/.openclaw/workspace/skills/qveris-official/scripts/qveris_tool.mjs"
    cmd = ["node", script_path, "search", query, f"--limit={limit}"]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"搜索错误: {result.stderr[:200]}")
            return None, None
        
        output = result.stdout
        
        # 提取search_id
        search_id = None
        for line in output.split('\n'):
            if line.startswith("Search ID:"):
                search_id = line.split("Search ID:")[1].strip()
                break
        
        # 提取工具ID
        tool_id = None
        for line in output.split('\n'):
            if "ID:" in line and not line.startswith("Search ID:"):
                tool_id = line.split("ID:")[1].strip()
                break
        
        return search_id, tool_id, output
        
    except Exception as e:
        print(f"搜索异常: {e}")
        return None, None, None

def run_qveris_execute(tool_id, search_id, params):
    """执行QVeris工具"""
    script_path = "/Users/tuqibiao/.openclaw/workspace/skills/qveris-official/scripts/qveris_tool.mjs"
    cmd = ["node", script_path, "execute", tool_id, "--search-id", search_id, "--params", json.dumps(params)]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"执行错误: {result.stderr[:200]}")
            return None
        
        return result.stdout
        
    except Exception as e:
        print(f"执行异常: {e}")
        return None

def get_market_data_via_qveris():
    """通过QVeris获取市场数据"""
    print("通过QVeris获取市场数据...")
    
    # 搜索股票市场工具
    search_id, tool_id, search_output = run_qveris_search("stock market real-time price", limit=10)
    
    if not search_id or not tool_id:
        print("未找到合适的股票市场工具")
        return {}
    
    print(f"找到工具: {tool_id}")
    
    # 尝试获取主要指数
    indices = [
        {"symbol": "NDX", "name": "纳斯达克"},
        {"symbol": "DJI", "name": "道琼斯"}, 
        {"symbol": "SPX", "name": "标普500"},
        {"symbol": "^HSI", "name": "恒生指数"},
        {"symbol": "^N225", "name": "日经225"}
    ]
    
    market_data = {}
    
    for idx in indices:
        params = {"symbol": idx["symbol"]}
        output = run_qveris_execute(tool_id, search_id, params)
        
        if output:
            try:
                # 尝试解析JSON
                for line in output.split('\n'):
                    line = line.strip()
                    if line.startswith('{') or line.startswith('['):
                        data = json.loads(line)
                        
                        if isinstance(data, dict):
                            price = data.get("close") or data.get("price") or data.get("last") or 0
                            change = data.get("change") or data.get("change_amount") or 0
                            change_pct = data.get("change_pct") or data.get("change_percent") or 0
                            
                            market_data[idx["name"]] = {
                                "price": float(price) if price else 0,
                                "change": float(change) if change else 0,
                                "change_pct": float(change_pct) if change_pct else 0
                            }
                            break
            except Exception as e:
                print(f"解析{idx['name']}数据时出错: {e}")
    
    return market_data

def get_crypto_data_via_qveris():
    """通过QVeris获取加密货币数据"""
    print("通过QVeris获取加密货币数据...")
    
    search_id, tool_id, _ = run_qveris_search("cryptocurrency price bitcoin", limit=10)
    
    if not search_id or not tool_id:
        print("未找到合适的加密货币工具")
        return {}
    
    cryptos = [
        {"symbol": "BTC", "name": "比特币"},
        {"symbol": "ETH", "name": "以太坊"},
        {"symbol": "SOL", "name": "Solana"}
    ]
    
    crypto_data = {}
    
    for crypto in cryptos:
        params = {"symbol": crypto["symbol"]}
        output = run_qveris_execute(tool_id, search_id, params)
        
        if output:
            try:
                for line in output.split('\n'):
                    line = line.strip()
                    if line.startswith('{') or line.startswith('['):
                        data = json.loads(line)
                        
                        if isinstance(data, dict):
                            price = data.get("price") or data.get("last") or data.get("close") or 0
                            change_pct = data.get("change_24h") or data.get("change_percent_24h") or data.get("change_pct") or 0
                            
                            crypto_data[crypto["name"]] = {
                                "price": float(price) if price else 0,
                                "change_pct": float(change_pct) if change_pct else 0
                            }
                            break
            except Exception as e:
                print(f"解析{crypto['name']}数据时出错: {e}")
    
    return crypto_data

def get_news_via_qveris():
    """通过QVeris获取财经新闻"""
    print("通过QVeris获取财经新闻...")
    
    search_id, tool_id, _ = run_qveris_search("financial news headlines", limit=10)
    
    if not search_id or not tool_id:
        print("未找到合适的新闻工具")
        return []
    
    params = {"limit": 8, "language": "en"}
    output = run_qveris_execute(tool_id, search_id, params)
    
    news_items = []
    
    if output:
        try:
            for line in output.split('\n'):
                line = line.strip()
                if line.startswith('['):
                    data = json.loads(line)
                    if isinstance(data, list):
                        news_items = data[:6]
                        break
                elif line.startswith('{'):
                    data = json.loads(line)
                    if "items" in data:
                        news_items = data["items"][:6]
                        break
        except Exception as e:
            print(f"解析新闻数据时出错: {e}")
    
    return news_items

def analyze_market_trend(market_data):
    """分析市场趋势"""
    if not market_data:
        return "数据不足", "需观察"
    
    positive_count = 0
    negative_count = 0
    
    for name, data in market_data.items():
        change_pct = data.get("change_pct", 0)
        if change_pct > 0:
            positive_count += 1
        elif change_pct < 0:
            negative_count += 1
    
    if positive_count > negative_count:
        trend = "偏多"
    elif negative_count > positive_count:
        trend = "偏空"
    else:
        trend = "震荡"
    
    # A股预期
    nasdaq_change = market_data.get("纳斯达克", {}).get("change_pct", 0)
    if nasdaq_change > 1:
        a股预期 = "高开概率大，关注科技股"
    elif nasdaq_change < -1:
        a股预期 = "低开概率大，注意风险"
    else:
        a股预期 = "平开或小幅波动"
    
    return trend, a股预期

def generate_biage_report():
    """生成彪哥战法报告"""
    print("=" * 60)
    print("【彪哥战法】全球市场盘前分析报告")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取数据
    market_data = get_market_data_via_qveris()
    crypto_data = get_crypto_data_via_qveris()
    news_items = get_news_via_qveris()
    
    # 分析趋势
    trend, a股预期 = analyze_market_trend(market_data)
    
    # 生成报告
    report = f"""
📊 【全球市场概览】

"""
    
    # 市场数据
    if market_data:
        for name, data in market_data.items():
            price = data.get("price", 0)
            change_pct = data.get("change_pct", 0)
            report += f"{name}: {price:.2f} ({change_pct:+.2f}%)\n"
    else:
        report += "市场数据获取失败\n"
    
    report += f"""
🌍 【加密货币】

"""
    
    if crypto_data:
        for name, data in crypto_data.items():
            price = data.get("price", 0)
            change_pct = data.get("change_pct", 0)
            report += f"{name}: ${price:,.0f} ({change_pct:+.1f}%)\n"
    else:
        report += "加密货币数据获取失败\n"
    
    report += f"""
📰 【财经要闻摘要】

"""
    
    if news_items:
        for i, news in enumerate(news_items[:4], 1):
            if isinstance(news, dict):
                title = news.get("title", news.get("headline", "无标题"))
                source = news.get("source", "未知")
                report += f"{i}. {title[:50]}... [{source}]\n"
    else:
        report += "暂无重要新闻\n"
    
    report += f"""
🎯 【彪哥战法分析】

• 全球趋势: {trend}
• A股预期: {a股预期}
• 数据来源: QVeris实时数据
• 分析时间: {datetime.now().strftime('%H:%M')}

📌 【操作建议】

"""
    
    if trend == "偏多":
        report += "1. 可关注科技、成长板块\n"
        report += "2. 逢低布局，避免追高\n"
        report += "3. 控制仓位，留有余地\n"
    elif trend == "偏空":
        report += "1. 保持谨慎，控制风险\n"
        report += "2. 回避高位股，持有现金\n"
        report += "3. 等待市场企稳信号\n"
    else:
        report += "1. 市场方向不明，观望为主\n"
        report += "2. 小仓位试探，快进快出\n"
        report += "3. 关注成交量变化\n"
    
    report += f"""
💡 【风险提示】

• 市场有风险，投资需谨慎
• 本分析仅供参考，不构成投资建议
• 实时数据可能存在延迟
• 注意仓位管理和风险控制

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
彪哥战法核心：顺势而为，控制风险，知行合一
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    print(report)
    
    # 保存结果
    result = {
        "timestamp": datetime.now().isoformat(),
        "market_data": market_data,
        "crypto_data": crypto_data,
        "news_count": len(news_items),
        "analysis": {
            "trend": trend,
            "a股预期": a股预期,
            "report": report
        }
    }
    
    with open("/Users/tuqibiao/.openclaw/workspace/biage_qveris_report.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("✓ 报告已保存到 biage_qveris_report.json")
    
    return report

if __name__ == "__main__":
    generate_biage_report()