#!/usr/bin/env python3
"""
全球市场数据获取脚本（改进版）
用于彪哥战法盘前分析
"""

import urllib.request
import urllib.parse
import json
import ssl
from datetime import datetime

# 禁用 SSL 验证（某些环境需要）
ssl._create_default_https_context = ssl._create_unverified_context

def fetch_us_stocks():
    """获取美股主要指数"""
    try:
        # 使用东方财富美股接口
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2&secids=100.NDX,100.DJI,100.SPX&fields=f12,f13,f14,f2,f4,f3,f20,f21"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            result = []
            for item in data.get('data', {}).get('diff', []):
                result.append({
                    'name': item.get('f14', ''),
                    'code': item.get('f12', ''),
                    'price': item.get('f2', 0),
                    'change': item.get('f4', 0),
                    'change_pct': item.get('f3', 0),
                })
            return result
    except Exception as e:
        print(f"获取美股数据失败: {e}")
        return []

def fetch_cn_stocks():
    """获取A股主要指数"""
    try:
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2&secids=1.000001,0.399001,0.399006&fields=f12,f13,f14,f2,f4,f3,f20,f21"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            result = []
            for item in data.get('data', {}).get('diff', []):
                result.append({
                    'name': item.get('f14', ''),
                    'code': item.get('f12', ''),
                    'price': item.get('f2', 0),
                    'change': item.get('f4', 0),
                    'change_pct': item.get('f3', 0),
                })
            return result
    except Exception as e:
        print(f"获取A股数据失败: {e}")
        return []

def fetch_zt_pool():
    """获取昨日涨停数据"""
    try:
        from datetime import datetime, timedelta
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        url = f"https://push2ex.eastmoney.com/getTopicZTPool?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&Pageindex=0&pagesize=100&sort=fbt%3Aasc&date={yesterday}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            zt_count = data.get('data', {}).get('tc', 0)
            return zt_count
    except Exception as e:
        print(f"获取涨停数据失败: {e}")
        return 0

def fetch_global_summary():
    """获取全球市场摘要"""
    try:
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2&secids=100.NDX,100.DJI,100.SPX,100.HSI,100.N225&fields=f14,f3"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            result = {}
            for item in data.get('data', {}).get('diff', []):
                name_map = {
                    '纳斯达克': '纳斯达克',
                    '道琼斯': '道指',
                    '标普500': '标普500',
                    '恒生指数': '恒生',
                    '日经225': '日经'
                }
                name = item.get('f14', '')
                for k, v in name_map.items():
                    if k in name:
                        result[v] = item.get('f3', 0)
                        break
            return result
    except Exception as e:
        print(f"获取全球市场摘要失败: {e}")
        return {}

def analyze_market(us_stocks, global_summary, zt_count):
    """分析市场情况"""
    analysis = {
        "us_market": {},
        "global_trend": "",
        "a股预期": "",
        "key_points": []
    }
    
    # 分析美股
    if us_stocks:
        nasdaq = next((s for s in us_stocks if '纳' in s['name'] or 'NDX' in s['code']), None)
        dow = next((s for s in us_stocks if '道' in s['name'] or 'DJI' in s['code']), None)
        sp500 = next((s for s in us_stocks if '标' in s['name'] or 'SPX' in s['code']), None)
        
        if nasdaq:
            analysis["us_market"]["纳斯达克"] = f"{nasdaq['change_pct']:+.2f}%"
        if dow:
            analysis["us_market"]["道琼斯"] = f"{dow['change_pct']:+.2f}%"
        if sp500:
            analysis["us_market"]["标普500"] = f"{sp500['change_pct']:+.2f}%"
    
    # 判断全球趋势
    positive_count = sum(1 for v in global_summary.values() if v > 0)
    negative_count = sum(1 for v in global_summary.values() if v < 0)
    
    if positive_count > negative_count:
        analysis["global_trend"] = "偏多"
    elif negative_count > positive_count:
        analysis["global_trend"] = "偏空"
    else:
        analysis["global_trend"] = "震荡"
    
    # A股开盘预期
    if nasdaq and nasdaq['change_pct'] > 1:
        analysis["a股预期"] = "高开概率大，关注科技股"
        analysis["key_points"].append("美股科技股大涨，A股科技板块可能跟随")
    elif nasdaq and nasdaq['change_pct'] < -1:
        analysis["a股预期"] = "低开概率大，注意风险"
        analysis["key_points"].append("美股科技股大跌，A股可能承压")
    else:
        analysis["a股预期"] = "平开或小幅波动"
    
    # 昨日涨停情况
    if zt_count > 80:
        analysis["key_points"].append(f"昨日涨停{zt_count}家，市场情绪活跃")
    elif zt_count < 40:
        analysis["key_points"].append(f"昨日涨停{zt_count}家，市场情绪低迷")
    
    return analysis

if __name__ == "__main__":
    print("=" * 50)
    print("全球市场盘前简报")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    print("\n【美股市场】")
    us_stocks = fetch_us_stocks()
    if us_stocks:
        for stock in us_stocks:
            print(f"  {stock['name']}: {stock['change_pct']:+.2f}%")
    else:
        print("  获取失败")
    
    print("\n【全球市场摘要】")
    global_summary = fetch_global_summary()
    for name, change in global_summary.items():
        print(f"  {name}: {change:+.2f}%")
    
    print("\n【昨日A股涨停】")
    zt_count = fetch_zt_pool()
    print(f"  涨停家数: {zt_count}")
    
    print("\n【盘前分析】")
    analysis = analyze_market(us_stocks, global_summary, zt_count)
    print(f"  全球趋势: {analysis['global_trend']}")
    print(f"  A股预期: {analysis['a股预期']}")
    
    if analysis['key_points']:
        print("\n【重点关注】")
        for point in analysis['key_points']:
            print(f"  • {point}")
    
    # 保存结果
    result = {
        "timestamp": datetime.now().isoformat(),
        "us_stocks": us_stocks,
        "global_summary": global_summary,
        "zt_count": zt_count,
        "analysis": analysis
    }
    
    with open("/Users/tuqibiao/.openclaw/workspace/market_brief.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n数据已保存到 market_brief.json")
