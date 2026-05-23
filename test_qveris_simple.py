#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版QVeris数据采集测试
"""

import os
import requests
import json
import datetime

# QVeris API配置
QVERIS_API_KEY = os.getenv("QVERIS_API_KEY", "sk-PYDj7ulDpbYUtxeXnKeUzKLzMjS2IndTZ6N-2uYbX5bo")
BASE_URL = "https://qveris.ai/api/v1"

def execute_tool(tool_id, parameters):
    """执行QVeris工具"""
    
    headers = {
        "Authorization": f"Bearer {QVERIS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/tools/execute"
    payload = {
        "tool_id": tool_id,
        "parameters": parameters
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 异常: {e}")
        return None

def get_today_market_data():
    """获取今日市场数据"""
    
    print("🚀 QVeris实时市场数据采集")
    print("=" * 60)
    print(f"时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    market_data = {}
    
    # 1. 获取上证指数
    print("1. 获取上证指数数据...")
    result = execute_tool("ths_ifind.real_time_quotation.v1", {
        "codes": "000001.SH",
        "indicators": "common"
    })
    
    if result and 'result' in result and 'data' in result['result']:
        data = result['result']['data']
        if isinstance(data, list) and len(data) > 0:
            sh_data = data[0][0]  # 嵌套列表结构
            market_data['shanghai_index'] = {
                'price': sh_data.get('latest'),
                'change': sh_data.get('change'),
                'change_pct': sh_data.get('changeRatio'),
                'volume': sh_data.get('volume'),
                'amount': sh_data.get('amount'),
                'high': sh_data.get('high'),
                'low': sh_data.get('low'),
                'open': sh_data.get('open')
            }
            print(f"  上证指数: {sh_data.get('latest')} ({sh_data.get('changeRatio'):+.2f}%)")
    
    # 2. 获取市场统计数据
    print("2. 获取市场统计数据...")
    result = execute_tool("mcp_gildata.marketlimitupdowncount.v1", {
        "query": "获取今日市场涨跌停家数"
    })
    
    if result and 'result' in result and 'data' in result['result']:
        data = result['result']['data']
        if 'table_markdown' in data:
            table = data['table_markdown']
            lines = table.strip().split('\n')
            if len(lines) >= 3:
                today_data = lines[2].split('|')
                if len(today_data) >= 9:
                    market_data['market_stats'] = {
                        'total': int(today_data[2].strip()),
                        'rising': int(today_data[3].strip()),
                        'falling': int(today_data[4].strip()),
                        'unchanged': int(today_data[5].strip()),
                        'limit_up': int(today_data[6].strip()),
                        'limit_down': int(today_data[7].strip())
                    }
                    stats = market_data['market_stats']
                    print(f"  上涨: {stats['rising']}/{stats['total']} ({stats['rising']/stats['total']:.1%})")
                    print(f"  涨停: {stats['limit_up']}, 跌停: {stats['limit_down']}")
    
    # 3. 获取创业板指
    print("3. 获取创业板指数据...")
    result = execute_tool("ths_ifind.real_time_quotation.v1", {
        "codes": "399006.SZ",
        "indicators": "common"
    })
    
    if result and 'result' in result and 'data' in result['result']:
        data = result['result']['data']
        if isinstance(data, list) and len(data) > 0:
            cyb_data = data[0][0]
            market_data['cyb_index'] = {
                'price': cyb_data.get('latest'),
                'change_pct': cyb_data.get('changeRatio')
            }
            print(f"  创业板指: {cyb_data.get('latest')} ({cyb_data.get('changeRatio'):+.2f}%)")
    
    # 保存数据
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"qveris_market_data_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.datetime.now().isoformat(),
            'data': market_data
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 数据已保存: {filename}")
    
    return market_data

def analyze_for_biage_strategy(market_data):
    """为彪哥战法v5.0分析数据"""
    
    print("\n" + "="*60)
    print("🎯 彪哥战法v5.0 市场分析")
    print("="*60)
    
    # 提取数据
    sh_index = market_data.get('shanghai_index', {})
    stats = market_data.get('market_stats', {})
    cyb_index = market_data.get('cyb_index', {})
    
    # 技术面分析（权重60%）
    tech_score = 0
    tech_features = []
    
    if sh_index.get('change_pct', 0) < 0:
        tech_score += 0.2
        tech_features.append("指数下跌")
    
    if stats.get('rising', 0) < stats.get('falling', 0):
        tech_score += 0.2
        tech_features.append("普跌行情")
    
    if stats.get('limit_up', 0) < 80:  # 涨停少于80家
        tech_score += 0.1
        tech_features.append("涨停家数少")
    
    if stats.get('limit_down', 0) > 20:  # 跌停多于20家
        tech_score += 0.1
        tech_features.append("跌停家数多")
    
    # 情绪面分析（权重13%）
    emotion_score = 0
    if stats.get('total', 0) > 0:
        rising_ratio = stats['rising'] / stats['total']
        if rising_ratio < 0.3:
            emotion_score = 0.13  # 情绪低迷
            emotion_status = "情绪低迷"
        elif rising_ratio < 0.5:
            emotion_score = 0.065
            emotion_status = "情绪中性"
        else:
            emotion_score = 0
            emotion_status = "情绪积极"
    else:
        emotion_status = "数据不足"
    
    # 综合评分
    total_score = tech_score * 0.6 + emotion_score
    
    # 状态判断
    if total_score < 0.3:
        market_state = "混沌期"
        position = "0-10%"
        strategy = "空仓等待"
    elif total_score < 0.5:
        market_state = "冬藏期"
        position = "10-30%"
        strategy = "防守为主"
    elif total_score < 0.7:
        market_state = "秋收期"
        position = "30-50%"
        strategy = "逐步减仓"
    elif total_score < 0.85:
        market_state = "春播期"
        position = "50-70%"
        strategy = "分批建仓"
    else:
        market_state = "夏长期"
        position = "70-90%"
        strategy = "重仓持有"
    
    # 输出分析结果
    print(f"📊 综合评分: {total_score:.3f}/1.0")
    print(f"🎯 市场状态: {market_state}")
    print(f"💰 建议仓位: {position}")
    print(f"📈 操作策略: {strategy}")
    print()
    
    print("🔍 特征分析:")
    print(f"  技术面: {', '.join(tech_features)}")
    print(f"  情绪面: {emotion_status}")
    print()
    
    print("💡 明日策略:")
    if market_state == "冬藏期":
        print("  1. 控制仓位，10-30%为宜")
        print("  2. 关注防御性板块")
        print("  3. 等待市场情绪回暖")
        print("  4. 避免追涨杀跌")
    elif market_state == "混沌期":
        print("  1. 保持极低仓位")
        print("  2. 等待明确方向信号")
        print("  3. 关注政策面变化")
        print("  4. 准备春播期布局")
    
    return {
        'market_state': market_state,
        'total_score': total_score,
        'position': position,
        'strategy': strategy,
        'tech_features': tech_features,
        'emotion_status': emotion_status
    }

def main():
    """主函数"""
    
    print("🚀 彪哥战法v5.0 - QVeris数据源集成测试")
    print()
    
    # 获取市场数据
    market_data = get_today_market_data()
    
    if market_data:
        # 分析数据
        analysis = analyze_for_biage_strategy(market_data)
        
        # 保存分析结果
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"biage_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.datetime.now().isoformat(),
                'market_data': market_data,
                'analysis': analysis
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 分析结果已保存: {filename}")
        
        print("\n✅ QVeris数据源集成成功！")
        print("💡 建议: 立即将QVeris作为彪哥战法v5.0的主要数据源")
    else:
        print("\n❌ 数据获取失败")

if __name__ == "__main__":
    main()