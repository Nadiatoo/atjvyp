#!/usr/bin/env python3
"""
彪哥战法盘前分析器 - QVeris数据源版本
使用QVeris API获取全球市场数据和财经新闻
"""

import os
import json
import subprocess
import sys
from datetime import datetime
import time

def run_qveris_command(command, args):
    """运行QVeris CLI命令"""
    try:
        script_path = "/Users/tuqibiao/.openclaw/workspace/skills/qveris-official/scripts/qveris_tool.mjs"
        cmd = ["node", script_path] + command + args
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"QVeris命令失败: {result.stderr}")
            return None
        
        return result.stdout
    except subprocess.TimeoutExpired:
        print("QVeris命令超时")
        return None
    except Exception as e:
        print(f"运行QVeris命令时出错: {e}")
        return None

def search_qveris_tools(query, limit=10):
    """搜索QVeris工具"""
    print(f"搜索QVeris工具: {query}")
    output = run_qveris_command(["search", query], [f"--limit={limit}"])
    
    if not output:
        return []
    
    try:
        # 解析输出
        lines = output.strip().split('\n')
        tools = []
        current_tool = {}
        
        for line in lines:
            if line.startswith("Tool ID:"):
                if current_tool:
                    tools.append(current_tool)
                current_tool = {"id": line.split("Tool ID:")[1].strip()}
            elif line.startswith("Name:"):
                current_tool["name"] = line.split("Name:")[1].strip()
            elif line.startswith("Description:"):
                current_tool["description"] = line.split("Description:")[1].strip()
            elif line.startswith("Success rate:"):
                try:
                    rate_str = line.split("Success rate:")[1].strip().replace("%", "")
                    current_tool["success_rate"] = float(rate_str)
                except:
                    current_tool["success_rate"] = 0
            elif line.startswith("Avg execution time:"):
                try:
                    time_str = line.split("Avg execution time:")[1].strip().replace("ms", "")
                    current_tool["avg_time"] = int(time_str)
                except:
                    current_tool["avg_time"] = 0
        
        if current_tool:
            tools.append(current_tool)
        
        return tools
    except Exception as e:
        print(f"解析QVeris搜索结果时出错: {e}")
        return []

def execute_qveris_tool(tool_id, params, search_id=None):
    """执行QVeris工具"""
    args = [tool_id]
    if search_id:
        args.extend(["--search-id", search_id])
    args.extend(["--params", json.dumps(params)])
    
    output = run_qveris_command(["execute"], args)
    
    if not output:
        return None
    
    try:
        # 尝试解析JSON输出
        lines = output.strip().split('\n')
        for line in lines:
            if line.startswith("{") or line.startswith("["):
                return json.loads(line)
        
        # 如果不是JSON，返回原始输出
        return output
    except Exception as e:
        print(f"解析QVeris执行结果时出错: {e}")
        return output

def get_global_market_data():
    """获取全球市场数据"""
    print("获取全球市场数据...")
    
    # 搜索股票市场数据工具
    tools = search_qveris_tools("real-time stock market price data API", limit=15)
    
    if not tools:
        print("未找到股票市场数据工具")
        return {}
    
    # 选择成功率最高的工具
    tools.sort(key=lambda x: x.get("success_rate", 0), reverse=True)
    selected_tool = tools[0]
    
    print(f"选择工具: {selected_tool.get('name', '未知')} (成功率: {selected_tool.get('success_rate', 0)}%)")
    
    # 获取主要指数数据
    market_data = {}
    
    # 美股指数
    indices = [
        {"symbol": "NDX", "name": "纳斯达克"},
        {"symbol": "DJI", "name": "道琼斯"},
        {"symbol": "SPX", "name": "标普500"}
    ]
    
    for idx in indices:
        params = {"symbol": idx["symbol"]}
        result = execute_qveris_tool(selected_tool["id"], params)
        
        if result and isinstance(result, dict):
            price = result.get("price")
            change = result.get("change")
            change_pct = result.get("change_pct")
            
            if price is not None:
                market_data[idx["name"]] = {
                    "price": price,
                    "change": change or 0,
                    "change_pct": change_pct or 0
                }
        
        time.sleep(1)  # 避免请求过快
    
    return market_data

def get_crypto_data():
    """获取加密货币数据"""
    print("获取加密货币数据...")
    
    tools = search_qveris_tools("cryptocurrency market price data", limit=10)
    
    if not tools:
        print("未找到加密货币数据工具")
        return {}
    
    tools.sort(key=lambda x: x.get("success_rate", 0), reverse=True)
    selected_tool = tools[0]
    
    crypto_data = {}
    
    # 主要加密货币
    cryptos = [
        {"symbol": "BTC", "name": "比特币"},
        {"symbol": "ETH", "name": "以太坊"},
        {"symbol": "SOL", "name": "Solana"}
    ]
    
    for crypto in cryptos:
        params = {"symbol": crypto["symbol"]}
        result = execute_qveris_tool(selected_tool["id"], params)
        
        if result and isinstance(result, dict):
            price = result.get("price")
            change_pct = result.get("change_24h")
            
            if price is not None:
                crypto_data[crypto["name"]] = {
                    "price": price,
                    "change_pct": change_pct or 0
                }
        
        time.sleep(1)
    
    return crypto_data

def get_forex_data():
    """获取外汇数据"""
    print("获取外汇数据...")
    
    tools = search_qveris_tools("forex exchange rate real-time data", limit=10)
    
    if not tools:
        print("未找到外汇数据工具")
        return {}
    
    tools.sort(key=lambda x: x.get("success_rate", 0), reverse=True)
    selected_tool = tools[0]
    
    forex_data = {}
    
    # 主要货币对
    pairs = [
        {"pair": "USDCNY", "name": "美元/人民币"},
        {"pair": "EURUSD", "name": "欧元/美元"},
        {"pair": "USDJPY", "name": "美元/日元"}
    ]
    
    for pair in pairs:
        params = {"pair": pair["pair"]}
        result = execute_qveris_tool(selected_tool["id"], params)
        
        if result and isinstance(result, dict):
            rate = result.get("rate")
            change = result.get("change")
            
            if rate is not None:
                forex_data[pair["name"]] = {
                    "rate": rate,
                    "change": change or 0
                }
        
        time.sleep(1)
    
    return forex_data

def get_financial_news():
    """获取财经新闻"""
    print("获取财经新闻...")
    
    tools = search_qveris_tools("financial news headlines API", limit=10)
    
    if not tools:
        print("未找到财经新闻工具")
        return []
    
    tools.sort(key=lambda x: x.get("success_rate", 0), reverse=True)
    selected_tool = tools[0]
    
    params = {
        "category": "finance",
        "limit": 10,
        "language": "zh"
    }
    
    result = execute_qveris_tool(selected_tool["id"], params)
    
    if result and isinstance(result, list):
        return result[:8]  # 返回前8条
    
    return []

def analyze_market_trend(market_data, crypto_data, forex_data):
    """分析市场趋势"""
    analysis = {
        "global_trend": "震荡",
        "a股预期": "平开或小幅波动",
        "key_points": [],
        "sector_analysis": []
    }
    
    # 分析美股趋势
    us_market_up = 0
    us_market_down = 0
    
    for name, data in market_data.items():
        change_pct = data.get("change_pct", 0)
        if change_pct > 0:
            us_market_up += 1
        elif change_pct < 0:
            us_market_down += 1
    
    if us_market_up > us_market_down:
        analysis["global_trend"] = "偏多"
    elif us_market_down > us_market_up:
        analysis["global_trend"] = "偏空"
    
    # A股开盘预期
    nasdaq_data = market_data.get("纳斯达克")
    if nasdaq_data:
        nasdaq_change = nasdaq_data.get("change_pct", 0)
        if nasdaq_change > 1:
            analysis["a股预期"] = "高开概率大，关注科技股"
            analysis["key_points"].append("美股科技股大涨，A股科技板块可能跟随")
        elif nasdaq_change < -1:
            analysis["a股预期"] = "低开概率大，注意风险"
            analysis["key_points"].append("美股科技股大跌，A股可能承压")
    
    # 加密货币分析
    btc_data = crypto_data.get("比特币")
    if btc_data:
        btc_change = btc_data.get("change_pct", 0)
        if abs(btc_change) > 3:
            analysis["key_points"].append(f"比特币24小时涨跌{btc_change:+.1f}%，影响数字货币概念股")
    
    # 外汇分析
    usdcny_data = forex_data.get("美元/人民币")
    if usdcny_data:
        usdcny_change = usdcny_data.get("change", 0)
        if usdcny_change > 0.5:
            analysis["key_points"].append("人民币贬值，利好出口企业")
        elif usdcny_change < -0.5:
            analysis["key_points"].append("人民币升值，利好进口和航空股")
    
    return analysis

def analyze_news_impact(news_items):
    """分析新闻影响"""
    impacts = []
    
    if not news_items:
        return impacts
    
    for news in news_items[:6]:
        if isinstance(news, dict):
            title = news.get("title", "")
            source = news.get("source", "未知")
        else:
            title = str(news)
            source = "QVeris"
        
        # 简单关键词分析
        direction = "需关注"
        benefit = "待观察"
        harm = "待观察"
        macro = "事件驱动"
        
        title_lower = title.lower()
        
        # 货币政策
        if any(kw in title_lower for kw in ["加息", "紧缩", "鹰派"]):
            direction = "偏空"
            benefit = "银行"
            harm = "科技/成长股"
            macro = "全球流动性收紧"
        elif any(kw in title_lower for kw in ["降息", "宽松", "鸽派"]):
            direction = "偏多"
            benefit = "科技/成长股"
            harm = "银行"
            macro = "全球流动性宽松"
        elif any(kw in title_lower for kw in ["通胀", "cpi", "物价"]):
            direction = "需观察"
            benefit = "资源/周期"
            harm = "消费/制造"
            macro = "通胀预期升温"
        
        # 贸易政策
        elif any(kw in title_lower for kw in ["关税", "贸易战", "制裁"]):
            direction = "偏空"
            benefit = "国产替代"
            harm = "出口链/科技"
            macro = "贸易环境恶化"
        elif any(kw in title_lower for kw in ["豁免", "取消关税", "贸易缓和"]):
            direction = "偏多"
            benefit = "出口链"
            harm = "国产替代"
            macro = "贸易环境改善"
        
        # 科技政策
        elif any(kw in title_lower for kw in ["芯片", "半导体", "ai", "人工智能"]):
            direction = "关注"
            benefit = "半导体/AI"
            harm = "-"
            macro = "科技竞争加剧"
        
        # 能源政策
        elif any(kw in title_lower for kw in ["原油", "石油", "油价上涨"]):
            direction = "关注"
            benefit = "油气/化工"
            harm = "航空/航运"
            macro = "成本压力上升"
        
        impacts.append({
            "news": title[:50],
            "source": source,
            "direction": direction,
            "benefit": benefit,
            "harm": harm,
            "macro": macro
        })
    
    return impacts

def generate_report(market_data, crypto_data, forex_data, news_items, analysis, news_impacts):
    """生成分析报告"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    report = f"""
【彪哥战法】全球市场盘前简报 (QVeris数据源)
时间: {current_time}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 【美股市场】
"""
    
    # 美股数据
    for name, data in market_data.items():
        change_pct = data.get("change_pct", 0)
        price = data.get("price", 0)
        report += f"- {name}: {price:.2f} ({change_pct:+.2f}%)\n"
    
    report += f"""
🌍 【加密货币市场】
"""
    
    # 加密货币数据
    for name, data in crypto_data.items():
        price = data.get("price", 0)
        change_pct = data.get("change_pct", 0)
        report += f"- {name}: ${price:,.0f} ({change_pct:+.1f}%)\n"
    
    report += f"""
💱 【外汇市场】
"""
    
    # 外汇数据
    for name, data in forex_data.items():
        rate = data.get("rate", 0)
        change = data.get("change", 0)
        report += f"- {name}: {rate:.4f} ({change:+.3f})\n"
    
    report += f"""
📰 【国际财经要闻】
"""
    
    # 新闻
    if news_items:
        for i, news in enumerate(news_items[:6], 1):
            if isinstance(news, dict):
                title = news.get("title", "")
                source = news.get("source", "未知")
            else:
                title = str(news)
                source = "QVeris"
            report += f"{i}. [{source}] {title[:60]}...\n"
    else:
        report += "暂无重要新闻\n"
    
    report += f"""
🎯 【盘前分析】
- 全球趋势: {analysis['global_trend']}
- A股预期: {analysis['a股预期']}
"""
    
    if analysis['key_points']:
        report += f"""
📌 【重点关注】
"""
        for point in analysis['key_points']:
            report += f"• {point}\n"
    
    if news_impacts:
        report += f"""
💡 【新闻影响深度分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for i, impact in enumerate(news_impacts[:4], 1):
            emoji = {"偏多": "🟢", "偏空": "🔴", "需观察": "🟡", "关注": "🔵", "需关注": "⚪"}.get(impact['direction'], "⚪")
            
            report += f"""
┌─ 新闻 {i} {'─' * 60}
│ 📰 标题: {impact['news']}
│ 📍 来源: {impact['source']}
│ {emoji} 市场方向: {impact['direction']}
│ 🌍 宏观影响: {impact['macro']}
├─ 板块影响 {'─' * 60}
"""
            
            if impact['benefit'] != '待观察' and impact['benefit'] != '-':
                report += f"│ ✅ 受益板块: {impact['benefit']}\n"
            
            if impact['harm'] != '待观察' and impact['harm'] != '-':
                report += f"│ ❌ 受损板块: {impact['harm']}\n"
            
            report += f"├─ 交易建议 {'─' * 60}\n"
            
            if impact['direction'] == '偏多':
                report += f"│ 💡 策略: 关注受益板块龙头，逢低布局\n"
                report += f"│ ⚠️  风险: 避免追高，等待回调确认\n"
            elif impact['direction'] == '偏空':
                report += f"│ 💡 策略: 回避受损板块，持有现金观望\n"
                report += f"│ ⚠️  风险: 受损板块可能持续下跌\n"
            elif impact['direction'] == '关注':
                report += f"│ 💡 策略: 密切关注板块动向，小仓位试探\n"
                report += f"│ ⚠️  风险: 持续性待观察，不宜重仓\n"
            else:
                report += f"│ 💡 策略: 保持观望，等待信号明确\n"
                report += f"│ ⚠️  风险: 不确定性较高，控制仓位\n"
            
            report += f"└{'─' * 69}\n"