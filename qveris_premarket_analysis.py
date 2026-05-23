#!/usr/bin/env python3
"""
彪哥战法盘前分析器 - QVeris数据源版本
基于QVeris API获取全球市场数据和财经新闻
"""

import json
import os
import sys
from datetime import datetime, timedelta
import subprocess

def run_qveris_command(command, params=None):
    """运行QVeris命令"""
    try:
        cmd = ["node", "scripts/qveris_tool.mjs", command]
        if params:
            cmd.extend(params)
        
        result = subprocess.run(
            cmd,
            cwd="/Users/tuqibiao/.openclaw/workspace/skills/qveris-official",
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"QVeris命令失败: {result.stderr}")
            return None
    except Exception as e:
        print(f"执行QVeris命令时出错: {e}")
        return None

def get_market_summary(market="us"):
    """获取市场摘要数据"""
    try:
        output = run_qveris_command("execute", [
            "yahoo_finance.quote_marketSummary.v1",
            "--search-id", "b6b8436e-ea11-4db7-8f49-bb51b39acfa3",
            "--params", f'{{"market": "{market}"}}'
        ])
        
        if output:
            # 解析输出
            lines = output.strip().split('\n')
            for line in lines:
                if line.startswith('Result:'):
                    json_str = line[7:].strip()
                    try:
                        data = json.loads(json_str)
                        return data.get("data", {}).get("summary", {})
                    except json.JSONDecodeError:
                        # 尝试从完整输出中提取JSON
                        import re
                        json_match = re.search(r'Result:\s*(\{.*\})', output, re.DOTALL)
                        if json_match:
                            try:
                                data = json.loads(json_match.group(1))
                                return data.get("data", {}).get("summary", {})
                            except:
                                pass
        return {}
    except Exception as e:
        print(f"获取市场摘要失败: {e}")
        return {}

def get_financial_news():
    """获取财经新闻"""
    try:
        output = run_qveris_command("execute", [
            "alphavantage.news_sentiment.retrieve.v1.7aca3c4a",
            "--search-id", "09ca1b42-8f33-46a7-bbda-2d4b21012ef3",
            "--params", '{"function": "NEWS_SENTIMENT", "limit": 15}'
        ])
        
        if output:
            # 解析输出
            lines = output.strip().split('\n')
            for line in lines:
                if line.startswith('Result:'):
                    json_str = line[7:].strip()
                    try:
                        data = json.loads(json_str)
                        return data.get("truncated_content", "{}")
                    except json.JSONDecodeError:
                        pass
        return "{}"
    except Exception as e:
        print(f"获取财经新闻失败: {e}")
        return "{}"

def analyze_market_data(us_data, asia_data, news_json):
    """分析市场数据"""
    analysis = {
        "global_trend": "震荡",
        "a股预期": "平开或小幅波动",
        "key_points": [],
        "news_analysis": []
    }
    
    # 分析美国市场
    us_changes = []
    for symbol, data in us_data.items():
        if isinstance(data, dict) and "regularMarketChangePercent" in data:
            change = data.get("regularMarketChangePercent", 0)
            if isinstance(change, (int, float)):
                us_changes.append(change)
    
    # 分析亚洲市场
    asia_changes = []
    for symbol, data in asia_data.items():
        if isinstance(data, dict) and "regularMarketChangePercent" in data:
            change = data.get("regularMarketChangePercent", 0)
            if isinstance(change, (int, float)):
                asia_changes.append(change)
    
    # 判断全球趋势
    all_changes = us_changes + asia_changes
    if all_changes:
        positive_count = sum(1 for c in all_changes if c > 0)
        negative_count = sum(1 for c in all_changes if c < 0)
        
        if positive_count > negative_count:
            analysis["global_trend"] = "偏多"
        elif negative_count > positive_count:
            analysis["global_trend"] = "偏空"
    
    # A股开盘预期
    shanghai_data = asia_data.get("SHH", {})
    if isinstance(shanghai_data, dict):
        sh_change = shanghai_data.get("regularMarketChangePercent", 0)
        if sh_change > 0.5:
            analysis["a股预期"] = "高开概率大"
            analysis["key_points"].append("上证指数昨日上涨，市场情绪积极")
        elif sh_change < -0.5:
            analysis["a股预期"] = "低开概率大，注意风险"
            analysis["key_points"].append("上证指数昨日下跌，市场可能承压")
    
    # 分析新闻
    try:
        news_data = json.loads(news_json)
        feed = news_data.get("feed", [])
        
        for item in feed[:5]:  # 分析前5条新闻
            title = item.get("title", "")
            sentiment = item.get("overall_sentiment_label", "Neutral")
            summary = item.get("summary", "")
            
            # 简单分析新闻影响
            impact = analyze_news_impact(title, summary, sentiment)
            if impact:
                analysis["news_analysis"].append(impact)
    except:
        pass
    
    return analysis

def analyze_news_impact(title, summary, sentiment):
    """分析新闻对A股的影响"""
    keywords = {
        "加息": {"direction": "偏空", "benefit": "银行", "harm": "科技/成长股", "macro": "全球流动性收紧"},
        "降息": {"direction": "偏多", "benefit": "科技/成长股", "harm": "银行", "macro": "全球流动性宽松"},
        "通胀": {"direction": "需观察", "benefit": "资源/周期", "harm": "消费/制造", "macro": "通胀预期升温"},
        "贸易战": {"direction": "偏空", "benefit": "国产替代", "harm": "出口链/科技", "macro": "贸易环境恶化"},
        "芯片": {"direction": "关注", "benefit": "半导体/AI", "harm": "-", "macro": "科技竞争加剧"},
        "新能源": {"direction": "关注", "benefit": "新能源", "harm": "传统能源", "macro": "能源转型加速"},
        "原油": {"direction": "关注", "benefit": "油气/化工", "harm": "航空/航运", "macro": "成本压力上升"},
        "战争": {"direction": "偏空", "benefit": "军工/黄金", "harm": "全球贸易", "macro": "避险情绪升温"},
    }
    
    text = (title + " " + summary).lower()
    
    for kw, impact in keywords.items():
        if kw in text:
            return {
                "news": title[:50],
                "direction": impact["direction"],
                "benefit": impact["benefit"],
                "harm": impact["harm"],
                "macro": impact["macro"],
                "sentiment": sentiment
            }
    
    # 如果没有匹配关键词，根据情绪判断
    sentiment_map = {
        "Bullish": {"direction": "偏多", "benefit": "市场整体", "harm": "-", "macro": "积极情绪"},
        "Somewhat-Bullish": {"direction": "偏多", "benefit": "市场整体", "harm": "-", "macro": "谨慎乐观"},
        "Neutral": {"direction": "需观察", "benefit": "待观察", "harm": "待观察", "macro": "中性影响"},
        "Somewhat-Bearish": {"direction": "偏空", "benefit": "-", "harm": "市场整体", "macro": "谨慎悲观"},
        "Bearish": {"direction": "偏空", "benefit": "-", "harm": "市场整体", "macro": "消极情绪"},
    }
    
    if sentiment in sentiment_map:
        impact = sentiment_map[sentiment]
        return {
            "news": title[:50],
            "direction": impact["direction"],
            "benefit": impact["benefit"],
            "harm": impact["harm"],
            "macro": impact["macro"],
            "sentiment": sentiment
        }
    
    return None

def format_market_data(data):
    """格式化市场数据"""
    formatted = {}
    for symbol, info in data.items():
        if isinstance(info, dict):
            name = info.get("shortName", symbol)
            price = info.get("regularMarketPrice", 0)
            change = info.get("regularMarketChange", 0)
            change_pct = info.get("regularMarketChangePercent", 0)
            
            formatted[name] = {
                "price": price,
                "change": change,
                "change_pct": change_pct
            }
    return formatted

def main():
    print("=" * 60)
    print("【彪哥战法】全球市场盘前简报 - QVeris数据源")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # 获取数据
    print("\n📊 【全球市场数据获取中...】")
    
    us_data = get_market_summary("us")
    asia_data = get_market_summary("asia")
    news_json = get_financial_news()
    
    # 格式化数据
    us_formatted = format_market_data(us_data)
    asia_formatted = format_market_data(asia_data)
    
    # 分析市场
    analysis = analyze_market_data(us_data, asia_data, news_json)
    
    # 打印美国市场
    print("\n🌎 【美国市场】")
    if us_formatted:
        for name, data in us_formatted.items():
            if "Futures" in name or "Dow" in name or "Russell" in name:
                print(f"  {name}: {data['change_pct']:+.2f}%")
    else:
        print("  获取失败")
    
    # 打印亚洲市场
    print("\n🌏 【亚洲市场】")
    if asia_formatted:
        important_markets = ["SSE Composite Index", "Nikkei 225", "Hang Seng", "S&P/ASX 200"]
        for name, data in asia_formatted.items():
            if any(market in name for market in important_markets):
                print(f"  {name}: {data['change_pct']:+.2f}%")
    else:
        print("  获取失败")
    
    # 打印分析结果
    print("\n🎯 【盘前分析】")
    print(f"  全球趋势: {analysis['global_trend']}")
    print(f"  A股预期: {analysis['a股预期']}")
    
    if analysis['key_points']:
        print("\n📌 【重点关注】")
        for point in analysis['key_points']:
            print(f"  • {point}")
    
    # 打印新闻分析
    print("\n📰 【财经新闻摘要】")
    try:
        news_data = json.loads(news_json)
        feed = news_data.get("feed", [])
        
        for i, item in enumerate(feed[:3], 1):
            title = item.get("title", "")[:60]
            sentiment = item.get("overall_sentiment_label", "Neutral")
            source = item.get("source", "未知")
            print(f"  {i}. [{source}] {title}... ({sentiment})")
    except:
        print("  新闻解析失败")
    
    if analysis.get('news_analysis'):
        print("\n💡 【新闻影响分析】")
        print("=" * 70)
        for i, impact in enumerate(analysis['news_analysis'][:3], 1):
            emoji = {"偏多": "🟢", "偏空": "🔴", "需观察": "🟡", "关注": "🔵"}.get(impact['direction'], "⚪")
            
            print(f"\n┌─ 新闻 {i} {'─' * 60}")
            print(f"│ 📰 标题: {impact['news']}")
            print(f"│ {emoji} 市场方向: {impact['direction']}")
            print(f"│ 📊 情绪: {impact.get('sentiment', 'N/A')}")
            print(f"│ 🌍 宏观影响: {impact['macro']}")
            
            if impact['benefit'] != '-':
                print(f"│ ✅ 受益板块: {impact['benefit']}")
            
            if impact['harm'] != '-':
                print(f"│ ❌ 受损板块: {impact['harm']}")
            
            print(f"└{'─' * 69}")
    
    # 保存结果
    result = {
        "timestamp": datetime.now().isoformat(),
        "us_market": us_formatted,
        "asia_market": asia_formatted,
        "analysis": analysis
    }
    
    try:
        with open("/Users/tuqibiao/.openclaw/workspace/market_brief_qveris.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 数据已保存到 market_brief_qveris.json")
    except Exception as e:
        print(f"\n⚠️  保存数据失败: {e}")
    
    print("\n" + "=" * 60)
    print("分析完成")
    print("=" * 60)

if __name__ == "__main__":
    main()