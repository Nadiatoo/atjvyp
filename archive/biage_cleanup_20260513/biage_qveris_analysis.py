#!/usr/bin/env python3
"""
彪哥战法盘前分析 - QVeris数据源
简化版本，直接使用找到的工具
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
            print(f"错误: {result.stderr[:200]}")
            return None
        
        return result.stdout
    except Exception as e:
        print(f"异常: {e}")
        return None

def get_stock_price(symbol):
    """获取股票价格"""
    # 使用找到的实时股票价格工具
    tool_id = "eodhd.real_time.retrieve.v1.3b8a5cf8"
    params = {"symbol": symbol}
    
    output = run_qveris(["execute", tool_id, "--params", json.dumps(params)])
    
    if output:
        try:
            # 尝试解析JSON
            for line in output.split('\n'):
                if line.strip().startswith('{'):
                    data = json.loads(line.strip())
                    return data
        except:
            pass
    
    return None

def get_crypto_price(symbol):
    """获取加密货币价格"""
    # 搜索加密货币价格工具
    output = run_qveris(["search", "cryptocurrency real-time price", "--limit=5"])
    
    if output:
        lines = output.split('\n')
        for line in lines:
            if "ID:" in line and "crypto" in line.lower():
                tool_id = line.split("ID:")[1].strip()
                params = {"symbol": symbol}
                
                result = run_qveris(["execute", tool_id, "--params", json.dumps(params)])
                if result:
                    try:
                        for line in result.split('\n'):
                            if line.strip().startswith('{'):
                                return json.loads(line.strip())
                    except:
                        pass
    
    return None

def get_financial_news():
    """获取财经新闻"""
    tool_id = "eodhd.news.retrieve.v1.fe8bf94c"
    params = {"limit": 10, "s": "general"}
    
    output = run_qveris(["execute", tool_id, "--params", json.dumps(params)])
    
    if output:
        try:
            for line in output.split('\n'):
                if line.strip().startswith('['):
                    data = json.loads(line.strip())
                    return data
        except:
            pass
    
    return []

def analyze_market():
    """分析市场"""
    print("=" * 60)
    print("【彪哥战法】全球市场盘前分析 (QVeris数据源)")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # 获取主要指数数据（使用已知的符号）
    indices = [
        {"symbol": "NDX", "name": "纳斯达克", "type": "index"},
        {"symbol": "DJI", "name": "道琼斯", "type": "index"},
        {"symbol": "SPX", "name": "标普500", "type": "index"},
        {"symbol": "HSI", "name": "恒生指数", "type": "index"},
        {"symbol": "N225", "name": "日经225", "type": "index"}
    ]
    
    print("\n📊 【全球市场数据】")
    market_data = {}
    
    for idx in indices:
        data = get_stock_price(idx["symbol"])
        if data:
            price = data.get("close") or data.get("price") or 0
            change = data.get("change") or 0
            change_pct = data.get("change_pct") or 0
            
            market_data[idx["name"]] = {
                "price": price,
                "change": change,
                "change_pct": change_pct
            }
            
            print(f"  {idx['name']}: {price:.2f} ({change_pct:+.2f}%)")
        else:
            print(f"  {idx['name']}: 数据获取失败")
    
    # 获取加密货币
    print("\n🌍 【加密货币市场】")
    cryptos = [
        {"symbol": "BTC-USD", "name": "比特币"},
        {"symbol": "ETH-USD", "name": "以太坊"}
    ]
    
    crypto_data = {}
    for crypto in cryptos:
        data = get_crypto_price(crypto["symbol"])
        if data:
            price = data.get("price") or data.get("close") or 0
            change_pct = data.get("change_24h") or data.get("change_pct") or 0
            
            crypto_data[crypto["name"]] = {
                "price": price,
                "change_pct": change_pct
            }
            
            print(f"  {crypto['name']}: ${price:,.0f} ({change_pct:+.1f}%)")
        else:
            print(f"  {crypto['name']}: 数据获取失败")
    
    # 获取财经新闻
    print("\n📰 【国际财经要闻】")
    news_items = get_financial_news()
    
    if news_items and isinstance(news_items, list):
        for i, news in enumerate(news_items[:6], 1):
            if isinstance(news, dict):
                title = news.get("title", "无标题")
                date = news.get("date", "")
                print(f"  {i}. {title[:60]}... [{date}]")
    else:
        print("  暂无重要新闻")
    
    # 市场分析
    print("\n🎯 【盘前分析】")
    
    # 简单趋势分析
    positive_count = sum(1 for data in market_data.values() if data.get("change_pct", 0) > 0)
    negative_count = sum(1 for data in market_data.values() if data.get("change_pct", 0) < 0)
    
    if positive_count > negative_count:
        trend = "偏多"
        a股预期 = "高开概率较大"
    elif negative_count > positive_count:
        trend = "偏空"
        a股预期 = "低开概率较大"
    else:
        trend = "震荡"
        a股预期 = "平开或小幅波动"
    
    print(f"  全球趋势: {trend}")
    print(f"  A股预期: {a股预期}")
    
    # 重点关注
    print("\n📌 【重点关注】")
    
    nasdaq_data = market_data.get("纳斯达克")
    if nasdaq_data and nasdaq_data.get("change_pct", 0) > 1:
        print("  • 美股科技股大涨，A股科技板块可能跟随")
    elif nasdaq_data and nasdaq_data.get("change_pct", 0) < -1:
        print("  • 美股科技股大跌，A股可能承压")
    
    btc_data = crypto_data.get("比特币")
    if btc_data and abs(btc_data.get("change_pct", 0)) > 3:
        print(f"  • 比特币24小时涨跌{btc_data['change_pct']:+.1f}%，影响数字货币概念股")
    
    # 新闻影响分析
    if news_items:
        print("\n💡 【新闻影响分析】")
        
        important_keywords = ["美联储", "加息", "降息", "通胀", "贸易", "关税", "芯片", "AI", "原油", "战争"]
        
        for i, news in enumerate(news_items[:4], 1):
            if isinstance(news, dict):
                title = news.get("title", "")
                
                for keyword in important_keywords:
                    if keyword in title:
                        impact = ""
                        if "加息" in title or "紧缩" in title:
                            impact = "偏空 - 流动性收紧，利好银行，利空科技股"
                        elif "降息" in title or "宽松" in title:
                            impact = "偏多 - 流动性宽松，利好科技股"
                        elif "通胀" in title:
                            impact = "需观察 - 通胀预期升温，利好资源股"
                        elif "贸易" in title or "关税" in title:
                            impact = "偏空 - 贸易环境恶化，利好国产替代"
                        elif "芯片" in title or "AI" in title:
                            impact = "关注 - 科技竞争加剧，利好半导体/AI板块"
                        elif "原油" in title:
                            impact = "关注 - 油价波动，利好油气/化工"
                        
                        if impact:
                            print(f"  {i}. {title[:50]}...")
                            print(f"     → {impact}")
                            break
    
    print("\n" + "=" * 60)
    print("分析完成 - 彪哥战法提醒：投资有风险，入市需谨慎")
    print("=" * 60)
    
    # 保存结果
    result = {
        "timestamp": datetime.now().isoformat(),
        "market_data": market_data,
        "crypto_data": crypto_data,
        "news_count": len(news_items) if news_items else 0,
        "analysis": {
            "trend": trend,
            "a股预期": a股预期,
            "positive_count": positive_count,
            "negative_count": negative_count
        }
    }
    
    with open("/Users/tuqibiao/.openclaw/workspace/biage_qveris_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return result

if __name__ == "__main__":
    analyze_market()