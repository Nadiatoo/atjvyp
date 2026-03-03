#!/usr/bin/env python3
"""
盘前消息综合分析工具
结合 RSS + Exa搜索 + QVeris智能选股
输出格式化的盘前分析报告
"""

import subprocess
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加 workspace 到路径
sys.path.insert(0, '/Users/tuqibiao/.openclaw/workspace/scripts')
from fetch_rss_news import load_config, fetch_rss, filter_by_keywords, analyze_themes


def get_hot_stocks():
    """获取近5日强势股（热门题材）"""
    cmd = """
    node ~/.openclaw/workspace/skills/qveris-official/scripts/qveris_tool.mjs \
        execute ths_ifind.smart_stock_picking.v1 \
        --search-id a9e31d58-f9e2-44ed-8ce8-e92003d47c4c \
        --params '{"searchstring":"近5日涨幅排名前20的股票"}' \
        --timeout 60 --json 2>/dev/null
    """
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=70)
        data = json.loads(result.stdout)
        if data.get('status_code') == 200:
            return data['data']['data'][:10]  # Top 10
    except:
        pass
    return []


def get_exa_news(query):
    """使用 Exa 搜索新闻"""
    cmd = f"""
    export PATH="$PATH:/Users/tuqibiao/Library/Python/3.13/bin" && \
    mcporter call 'exa.web_search_exa(query: "{query}", numResults: 5)' 2>/dev/null
    """
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout[:1000]  # 限制长度
    except:
        return ""


def analyze_themes_from_stocks(stocks):
    """从强势股分析题材"""
    # 简单映射：股票名称 -> 可能题材
    theme_keywords = {
        '石油': '石油/能源',
        '燃气': '天然气',
        '航运': '航运/物流',
        '轮船': '航运/物流',
        '有色': '有色金属',
        '钨业': '稀有金属',
        '军工': '军工',
        '科技': '科技',
        '智能': '人工智能',
    }
    
    themes = {}
    for stock in stocks:
        name = stock['股票简称']
        for kw, theme in theme_keywords.items():
            if kw in name:
                if theme not in themes:
                    themes[theme] = []
                themes[theme].append({
                    'name': name,
                    'code': stock['股票代码'],
                    'change': stock.get('区间涨跌幅:前复权[20260225-20260303]', 0)
                })
    
    return themes


def generate_premarket_report():
    """生成盘前分析报告"""
    report = []
    report.append("📈 【彪哥战法】盘前消息分析")
    report.append(f"📅 {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
    report.append("=" * 50)
    
    # 1. 热门题材（基于强势股）
    report.append("\n🔥 近5日热门题材（基于强势股）:")
    stocks = get_hot_stocks()
    if stocks:
        themes = analyze_themes_from_stocks(stocks)
        for i, (theme, items) in enumerate(sorted(themes.items(), key=lambda x: len(x[1]), reverse=True)[:5], 1):
            report.append(f"\n{i}. {theme}")
            for item in items[:3]:  # 最多显示3只
                report.append(f"   • {item['name']} ({item['code']}) +{item['change']:.1f}%")
    else:
        report.append("暂无法获取强势股数据")
    
    # 2. RSS 新闻
    report.append("\n\n📰 财经新闻（RSS）:")
    config = load_config()
    all_entries = []
    for source in config['sources']:
        entries = fetch_rss(source['url'], source['name'], 5)
        for e in entries:
            e['source'] = source['name']
        all_entries.extend(entries)
    
    if all_entries:
        # 按关键词过滤
        filtered = filter_by_keywords(all_entries, config['keywords'])
        if filtered:
            for i, entry in enumerate(filtered[:5], 1):
                report.append(f"{i}. {entry['title']}")
                if entry.get('matched_keywords'):
                    report.append(f"   🏷️ {', '.join(entry['matched_keywords'][:3])}")
        else:
            # 显示全部
            for i, entry in enumerate(all_entries[:5], 1):
                report.append(f"{i}. {entry['title']}")
    else:
        report.append("暂无新闻数据")
    
    # 3. 盘前策略
    report.append("\n\n💡 盘前策略:")
    if stocks:
        # 基于强势股给出策略
        top_theme = None
        themes = analyze_themes_from_stocks(stocks)
        if themes:
            top_theme = max(themes.items(), key=lambda x: len(x[1]))
        
        if top_theme:
            report.append(f"• 关注热点: {top_theme[0]}板块近期强势")
            report.append(f"• 策略: 观察开盘资金承接，逢低关注龙头股")
        else:
            report.append("• 策略: 观察市场情绪，等待主线明朗")
    else:
        report.append("• 策略: 观察大盘走势，控制仓位")
    
    report.append("• 风险提示: 关注港股表现及外围消息")
    
    return "\n".join(report)


if __name__ == "__main__":
    print(generate_premarket_report())
