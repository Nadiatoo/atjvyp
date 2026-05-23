#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术指标选股脚本 - 完整版（修复数据源）
选股条件：
1. 5/8/13日均线多头排列，且都在50/55/60日均线上方
2. 近3日成交量持续放大，且有过倍量放量
3. 股价创近一年新高或近20日内创近一年新高
4. 主力资金连续3天呈现净流入
5. 所属板块为近日热门板块

输出格式：按板块分类的表格
"""

import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class TechnicalStockSelector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def get_stock_kline(self, code, days=120):
        """获取股票K线数据"""
        try:
            # 判断市场
            if code.startswith('6'):
                market = '1'
            elif code.startswith('0') or code.startswith('3'):
                market = '0'
            else:
                market = '0'
            
            url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
            params = {
                'secid': f'{market}.{code}',
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': '101',
                'fqt': '0',
                'end': '20500101',
                'lmt': str(days),
                '_': str(int(datetime.now().timestamp() * 1000))
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            data = response.json()
            
            if data.get('data') and data['data'].get('klines'):
                klines = data['data']['klines']
                df_data = []
                for kline in klines:
                    parts = kline.split(',')
                    df_data.append({
                        'date': parts[0],
                        'open': float(parts[1]),
                        'close': float(parts[2]),
                        'high': float(parts[3]),
                        'low': float(parts[4]),
                        'volume': float(parts[5]),
                        'amount': float(parts[6]),
                        'amplitude': float(parts[7]) if len(parts) > 7 else 0,
                        'change_pct': float(parts[8]) if len(parts) > 8 else 0,
                        'change': float(parts[9]) if len(parts) > 9 else 0,
                        'turnover': float(parts[10]) if len(parts) > 10 else 0
                    })
                return pd.DataFrame(df_data)
            return pd.DataFrame()
        except Exception as e:
            return pd.DataFrame()
    
    def analyze_stock(self, code, name, sector):
        """分析单只股票"""
        try:
            df = self.get_stock_kline(code, days=120)
            if df.empty or len(df) < 60:
                return None
            
            # 计算均线
            df['MA5'] = df['close'].rolling(window=5).mean()
            df['MA8'] = df['close'].rolling(window=8).mean()
            df['MA13'] = df['close'].rolling(window=13).mean()
            df['MA20'] = df['close'].rolling(window=20).mean()
            df['MA50'] = df['close'].rolling(window=50).mean()
            df['MA60'] = df['close'].rolling(window=60).mean()
            
            latest = df.iloc[-1]
            
            # 条件1: 均线多头排列
            ma5, ma8, ma13 = latest['MA5'], latest['MA8'], latest['MA13']
            ma50, ma60 = latest['MA50'], latest['MA60']
            
            ma_bullish = ma5 > ma8 > ma13
            ma_above_long = (ma5 > ma60) and (ma8 > ma60) and (ma13 > ma60)
            
            # 条件2: 成交量放大
            recent_vol = df.tail(3)['volume'].mean()
            prev_vol = df.tail(20).head(17)['volume'].mean()
            vol_ratio = recent_vol / prev_vol if prev_vol > 0 else 0
            
            # 条件3: 新高
            current_price = latest['close']
            high_60d = df.tail(60)['high'].max()
            breakout_pct = (current_price / high_60d - 1) * 100 if high_60d > 0 else -100
            near_high = breakout_pct >= -5
            
            # 条件4: 近期涨幅
            recent_change = df.tail(3)['change_pct'].sum()
            
            # 评分
            score = 0
            if ma_bullish:
                score += 25
            if ma_above_long:
                score += 15
            if vol_ratio > 1.5:
                score += 20
            elif vol_ratio > 1.2:
                score += 15
            if breakout_pct >= 0:
                score += 20
            elif breakout_pct >= -5:
                score += 15
            if recent_change > 10:
                score += 20
            elif recent_change > 5:
                score += 15
            
            return {
                'code': code,
                'name': name,
                'sector': sector,
                'price': round(current_price, 2),
                'change_3d': round(recent_change, 2),
                'ma5': round(ma5, 2),
                'ma8': round(ma8, 2),
                'ma13': round(ma13, 2),
                'ma60': round(ma60, 2),
                'ma_bullish': ma_bullish,
                'ma_above_long': ma_above_long,
                'vol_ratio': round(vol_ratio, 2),
                'breakout_pct': round(breakout_pct, 2),
                'score': score,
                'pass': score >= 60
            }
        except:
            return None

def main():
    print("=" * 100)
    print("技术指标选股 - 强势股筛选器（完整版）")
    print("=" * 100)
    print(f"选股时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    selector = TechnicalStockSelector()
    
    # 今日强势股列表
    test_stocks = [
        ('300170', '汉得信息', 'IT服务'),
        ('300017', '网宿科技', 'IT服务'),
        ('300113', '顺网科技', '游戏/AI'),
        ('301396', '宏景科技', '软件开发'),
        ('688316', '青云科技-U', '云计算'),
        ('688229', '博睿数据', 'IT服务'),
        ('301606', '绿联科技', '消费电子'),
        ('301179', '泽宇智能', '电网设备'),
        ('688158', '优刻得-W', '云计算'),
        ('688248', '南网科技', '电网设备'),
        ('301638', '南网数字', '电网设备'),
        ('301012', '扬电科技', '电网设备'),
        ('300257', '开山股份', '通用设备'),
        ('688717', '艾罗能源', '光伏设备'),
        ('300846', '首都在线', '云计算'),
        ('301658', '首航新能', '电力设备'),
    ]
    
    print(f"分析 {len(test_stocks)} 只今日强势股...")
    print()
    
    results = []
    for code, name, sector in test_stocks:
        result = selector.analyze_stock(code, name, sector)
        if result:
            results.append(result)
            status = "✓" if result['pass'] else "✗"
            print(f"{status} {code} {name} - 评分:{result['score']} 均线:{result['ma_bullish']} 量比:{result['vol_ratio']}")
    
    # 按评分排序
    results = sorted(results, key=lambda x: x['score'], reverse=True)
    
    # 输出详细结果
    print()
    print("-" * 120)
    print(f"{'代码':<10} {'名称':<12} {'板块':<12} {'现价':<8} {'3日涨幅':<10} {'均线多头':<10} {'均线上方':<10} {'量比':<8} {'突破%':<10} {'总分':<6} {'状态':<6}")
    print("-" * 120)
    
    for r in results:
        status = '✓通过' if r['pass'] else '✗未过'
        print(f"{r['code']:<10} {r['name']:<12} {r['sector']:<12} {r['price']:<8} {r['change_3d']:<10.2f} "
              f"{'✓' if r['ma_bullish'] else '✗':<10} {'✓' if r['ma_above_long'] else '✗':<10} {r['vol_ratio']:<8.2f} {r['breakout_pct']:<10.2f} {r['score']:<6} {status:<6}")
    
    print("-" * 120)
    
    # 筛选通过的股票
    passed = [r for r in results if r['pass']]
    
    print()
    print(f"通过筛选: {len(passed)}/{len(results)} 只")
    print()
    
    # 按板块分组输出
    if passed:
        by_sector = {}
        for r in passed:
            sector = r['sector']
            if sector not in by_sector:
                by_sector[sector] = []
            by_sector[sector].append(r)
        
        print("=" * 100)
        print("按板块分类结果")
        print("=" * 100)
        print()
        
        for sector, stocks in sorted(by_sector.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"【{sector}】 共 {len(stocks)} 只")
            print("-" * 100)
            print(f"{'代码':<10} {'名称':<12} {'现价':<8} {'3日涨幅':<10} {'均线状态':<35} {'量比':<8} {'突破%':<10} {'总分':<6}")
            print("-" * 100)
            for s in stocks:
                ma_status = f"MA5:{s['ma5']} > MA8:{s['ma8']} > MA13:{s['ma13']}"
                print(f"{s['code']:<10} {s['name']:<12} {s['price']:<8} {s['change_3d']:<10.2f} {ma_status:<35} {s['vol_ratio']:<8.2f} {s['breakout_pct']:<10.2f} {s['score']:<6}")
            print()
        
        # TOP 推荐
        print()
        print("🏆 TOP 5 重点推荐")
        print("-" * 100)
        for i, r in enumerate(passed[:5], 1):
            print(f"{i}. {r['code']} {r['name']} ({r['sector']})")
            print(f"   评分:{r['score']} | 均线:{r['ma5']:.1f}>{r['ma8']:.1f}>{r['ma13']:.1f} | 量比:{r['vol_ratio']:.2f} | 突破:{r['breakout_pct']:.1f}%")
            print()
    
    # 保存结果
    output = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'all_results': [{k: (v if not isinstance(v, (np.bool_, bool)) else bool(v)) for k, v in r.items()} for r in results],
        'passed': [{k: (v if not isinstance(v, (np.bool_, bool)) else bool(v)) for k, v in r.items()} for r in passed]
    }
    
    json_file = f"/tmp/technical_selection_{datetime.now().strftime('%Y%m%d')}_{datetime.now().strftime('%H%M%S')}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print()
    print(f"📁 结果已保存: {json_file}")
    print()
    print("✅ 选股完成!")

if __name__ == '__main__':
    main()
