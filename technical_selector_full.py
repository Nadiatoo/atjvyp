#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术指标选股脚本 - 完整版
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
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class TechnicalStockSelector:
    def __init__(self):
        self.base_url = "https://push2.eastmoney.com/api"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.results = []
        self.hot_sectors = []
        
    def get_hot_sectors(self):
        """获取热门板块（按主力资金净流入排序）"""
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': 1,
                'pz': 30,
                'po': 1,
                'np': 1,
                'fltt': 2,
                'invt': 2,
                'fid': 'f20',  # 按主力净流入排序
                'fs': 'm:90+t:2',  # 行业板块
                'fields': 'f12,f14,f2,f3,f4,f5,f6,f7,f8,f9,f10,f18,f20,f21'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            data = response.json()
            
            sectors = []
            if data.get('data') and data['data'].get('diff'):
                for item in data['data']['diff']:
                    sectors.append({
                        'code': item.get('f12'),
                        'name': item.get('f14'),
                        'change_pct': item.get('f3', 0),
                        'main_inflow': item.get('f20', 0) / 10000,  # 万元转亿元
                    })
            self.hot_sectors = sectors
            return sectors
        except Exception as e:
            print(f"获取热门板块失败: {e}")
            return []
    
    def get_sector_stocks(self, sector_code):
        """获取板块内的股票列表"""
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': 1,
                'pz': 100,
                'po': 1,
                'np': 1,
                'fltt': 2,
                'invt': 2,
                'fid': 'f20',
                'fs': f'b:{sector_code}',
                'fields': 'f12,f14,f2,f3,f4,f5,f6,f7,f8,f9,f10,f18,f20,f21'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            data = response.json()
            
            stocks = []
            if data.get('data') and data['data'].get('diff'):
                for item in data['data']['diff']:
                    stocks.append({
                        'code': item.get('f12'),
                        'name': item.get('f14'),
                        'sector_code': sector_code,
                        'price': item.get('f2', 0),
                        'change_pct': item.get('f3', 0),
                        'volume': item.get('f5', 0),
                        'amount': item.get('f6', 0),
                        'turnover': item.get('f8', 0),
                        'main_inflow': item.get('f20', 0),
                    })
            return stocks
        except Exception as e:
            print(f"获取板块{sector_code}股票失败: {e}")
            return []
    
    def get_stock_kline(self, code, days=80):
        """获取股票K线数据"""
        try:
            # 判断市场
            if code.startswith('6'):
                market = '1'
            elif code.startswith('0') or code.startswith('3'):
                market = '0'
            elif code.startswith('8') or code.startswith('4'):
                market = '0'  # 北交所
            else:
                market = '0'
            
            url = f"https://push2.eastmoney.com/api/qt/stock/kline/get"
            params = {
                'secid': f'{market}.{code}',
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': '101',
                'fqt': '0',
                'end': '20500101',
                'lmt': days
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
    
    def calculate_ma(self, df):
        """计算移动平均线"""
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA8'] = df['close'].rolling(window=8).mean()
        df['MA13'] = df['close'].rolling(window=13).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA50'] = df['close'].rolling(window=50).mean()
        df['MA55'] = df['close'].rolling(window=55).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()
        return df
    
    def check_ma_bullish(self, df):
        """
        检查均线多头排列：
        1. 5/8/13日均线多头排列 (5>8>13)
        2. 三条均线都在50/55/60日均线上方
        """
        if len(df) < 60:
            return False, {}
        
        latest = df.iloc[-1]
        
        ma5 = latest['MA5']
        ma8 = latest['MA8']
        ma13 = latest['MA13']
        ma50 = latest['MA50']
        ma55 = latest['MA55']
        ma60 = latest['MA60']
        
        # 条件1: 5>8>13 多头排列
        condition1 = ma5 > ma8 > ma13
        
        # 条件2: 5/8/13都在50/55/60上方
        long_term_ma = max(ma50, ma55, ma60)
        condition2 = (ma5 > long_term_ma) and (ma8 > long_term_ma) and (ma13 > long_term_ma)
        
        return condition1 and condition2, {
            'MA5': round(ma5, 2),
            'MA8': round(ma8, 2),
            'MA13': round(ma13, 2),
            'MA50': round(ma50, 2),
            'MA55': round(ma55, 2),
            'MA60': round(ma60, 2),
            'bullish': condition1 and condition2
        }
    
    def check_volume_expansion(self, df):
        """
        检查成交量条件：
        1. 近3日成交量持续放大
        2. 有过倍量放量（当日成交量>前一日1.8倍）
        """
        if len(df) < 5:
            return False, {}
        
        recent = df.tail(5)
        volumes = recent['volume'].tolist()
        
        # 近3日持续放大
        vol_increasing = volumes[-1] > volumes[-2] > volumes[-3]
        
        # 有过倍量（近5日内，当日>前日1.8倍）
        has_double_volume = False
        double_volume_day = None
        for i in range(1, 5):
            if volumes[i] > volumes[i-1] * 1.8:
                has_double_volume = True
                double_volume_day = i
                break
        
        # 计算量比（近3日平均/前10日平均）
        recent_3_avg = np.mean(volumes[-3:])
        prev_10_avg = np.mean(df.tail(13)['volume'].tolist()[:10])
        volume_ratio = recent_3_avg / prev_10_avg if prev_10_avg > 0 else 0
        
        return (vol_increasing or has_double_volume) and volume_ratio > 1.2, {
            'vol_trend': '持续放大' if vol_increasing else '震荡',
            'has_double': '有倍量' if has_double_volume else '无倍量',
            'volume_ratio': round(volume_ratio, 2),
            'latest_vol': int(volumes[-1])
        }
    
    def check_new_high(self, df):
        """
        检查新高条件：
        1. 股价创近一年新高或历史新高
        2. 或近20个交易日内创近一年新高
        """
        if len(df) < 60:
            return False, {}
        
        latest_close = df.iloc[-1]['close']
        
        # 近一年最高（取最近250个交易日）
        high_250d = df.tail(min(250, len(df)))['high'].max()
        
        # 近20日最高
        high_20d = df.tail(20)['high'].max()
        
        # 当前价格接近一年新高（98%以上）
        near_250d_high = latest_close >= high_250d * 0.98
        
        # 近20日内创过一年新高
        recent_breakout = high_20d >= high_250d * 0.98
        
        # 距离新高的幅度
        breakout_pct = (latest_close / high_250d - 1) * 100 if high_250d > 0 else 0
        
        return near_250d_high or recent_breakout, {
            'current_price': round(latest_close, 2),
            'high_250d': round(high_250d, 2),
            'high_20d': round(high_20d, 2),
            'breakout_pct': round(breakout_pct, 2),
            'is_new_high': near_250d_high
        }
    
    def check_main_force_inflow(self, code, df):
        """
        检查主力资金连续净流入（简化版，用3日数据）
        """
        if len(df) < 5:
            return False, {}
        
        # 用成交额和涨跌幅估算主力资金
        recent_3d = df.tail(3)
        
        # 计算每日主力净流入估算（简化算法）
        inflow_days = 0
        total_inflow = 0
        
        for idx, row in recent_3d.iterrows():
            # 如果上涨且放量，估算为净流入
            if row['change_pct'] > 0 and row['volume'] > df['volume'].rolling(10).mean().iloc[idx]:
                estimated_inflow = row['amount'] * 0.3  # 估算30%为主力资金
                inflow_days += 1
                total_inflow += estimated_inflow
            elif row['change_pct'] > 0:
                estimated_inflow = row['amount'] * 0.1
                inflow_days += 1
                total_inflow += estimated_inflow
        
        # 连续2天以上净流入视为符合条件
        return inflow_days >= 2, {
            'inflow_days': inflow_days,
            'total_inflow': round(total_inflow / 10000, 2),  # 万元
            'avg_daily_inflow': round(total_inflow / 3 / 10000, 2)
        }
    
    def analyze_stock(self, stock_info):
        """分析单只股票"""
        code = stock_info['code']
        name = stock_info['name']
        sector_name = stock_info.get('sector_name', '未知')
        
        try:
            # 获取K线数据
            df = self.get_stock_kline(code, days=80)
            if df.empty or len(df) < 60:
                return None
            
            # 计算均线
            df = self.calculate_ma(df)
            
            # 条件1: 均线多头排列
            ma_pass, ma_info = self.check_ma_bullish(df)
            if not ma_pass:
                return None
            
            # 条件2: 成交量放大
            vol_pass, vol_info = self.check_volume_expansion(df)
            if not vol_pass:
                return None
            
            # 条件3: 新高
            high_pass, high_info = self.check_new_high(df)
            if not high_pass:
                return None
            
            # 条件4: 主力资金
            main_pass, main_info = self.check_main_force_inflow(code, df)
            
            # 计算综合评分
            score = self.calculate_score(ma_info, vol_info, high_info, main_info)
            
            result = {
                'code': code,
                'name': name,
                'sector': sector_name,
                'price': high_info['current_price'],
                'change_pct': stock_info.get('change_pct', 0),
                'ma_status': f"MA5:{ma_info['MA5']} > MA8:{ma_info['MA8']} > MA13:{ma_info['MA13']}",
                'ma_bullish': '✓' if ma_info['bullish'] else '✗',
                'volume_status': f"{vol_info['vol_trend']}, 量比{vol_info['volume_ratio']}",
                'volume_double': vol_info['has_double'],
                'high_status': f"{'新高' if high_info['is_new_high'] else '接近新高'} {high_info['breakout_pct']}%",
                'main_inflow': f"{main_info['inflow_days']}/3天流入, {main_info['total_inflow']}万",
                'main_pass': '✓' if main_pass else '△',
                'score': score,
                'turnover': stock_info.get('turnover', 0),
                'amount': round(stock_info.get('amount', 0) / 10000, 2)  # 万元
            }
            
            return result
            
        except Exception as e:
            return None
    
    def calculate_score(self, ma_info, vol_info, high_info, main_info):
        """计算综合评分（0-100）"""
        score = 0
        
        # 均线多头排列 (30分)
        if ma_info.get('bullish'):
            score += 30
        
        # 成交量 (25分)
        if vol_info.get('volume_ratio', 0) > 2:
            score += 25
        elif vol_info.get('volume_ratio', 0) > 1.5:
            score += 20
        elif vol_info.get('volume_ratio', 0) > 1.2:
            score += 15
        
        # 新高 (25分)
        if high_info.get('is_new_high'):
            score += 25
        elif high_info.get('breakout_pct', -100) > -5:
            score += 20
        elif high_info.get('breakout_pct', -100) > -10:
            score += 15
        
        # 主力资金 (20分)
        if main_info.get('inflow_days', 0) >= 3:
            score += 20
        elif main_info.get('inflow_days', 0) >= 2:
            score += 15
        elif main_info.get('inflow_days', 0) >= 1:
            score += 10
        
        return score
    
    def select_stocks(self, max_sectors=10, max_stocks_per_sector=20):
        """执行选股"""
        print("=" * 80)
        print("技术指标选股 - 强势股筛选器（完整版）")
        print("=" * 80)
        print(f"选股时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 获取热门板块
        print("步骤1: 获取热门板块...")
        hot_sectors = self.get_hot_sectors()
        if not hot_sectors:
            print("获取热门板块失败，使用默认板块")
            hot_sectors = [
                {'code': 'BK1238', 'name': 'IT服务'},
                {'code': 'BK0737', 'name': '软件开发'},
                {'code': 'BK0457', 'name': '电网设备'},
                {'code': 'BK0428', 'name': '电力'},
                {'code': 'BK1033', 'name': '电池'},
            ]
        
        print(f"热门板块数量: {len(hot_sectors)}")
        for i, sector in enumerate(hot_sectors[:5]):
            print(f"  {i+1}. {sector['name']} (主力净流入: {sector['main_inflow']:.2f}亿)")
        print()
        
        # 获取各板块股票并分析
        all_results = []
        
        for sector in hot_sectors[:max_sectors]:
            sector_code = sector['code']
            sector_name = sector['name']
            
            print(f"步骤2.{hot_sectors.index(sector)+1}: 分析板块 [{sector_name}]...")
            
            # 获取板块内股票
            stocks = self.get_sector_stocks(sector_code)
            if not stocks:
                continue
            
            print(f"  板块内共 {len(stocks)} 只股票，开始筛选...")
            
            # 添加板块名称
            for stock in stocks:
                stock['sector_name'] = sector_name
            
            # 多线程分析
            sector_results = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_stock = {executor.submit(self.analyze_stock, stock): stock for stock in stocks[:max_stocks_per_sector]}
                for future in as_completed(future_to_stock):
                    result = future.result()
                    if result:
                        sector_results.append(result)
            
            # 按评分排序
            sector_results = sorted(sector_results, key=lambda x: x['score'], reverse=True)
            all_results.extend(sector_results)
            
            print(f"  符合条件: {len(sector_results)} 只")
            print()
        
        # 按板块分组
        results_by_sector = {}
        for result in all_results:
            sector = result['sector']
            if sector not in results_by_sector:
                results_by_sector[sector] = []
            results_by_sector[sector].append(result)
        
        return results_by_sector, hot_sectors
    
    def print_results(self, results_by_sector, hot_sectors):
        """打印结果表格"""
        print()
        print("=" * 120)
        print("选股结果 - 按板块分类")
        print("=" * 120)
        print()
        
        if not results_by_sector:
            print("未找到符合条件的股票")
            return
        
        # 按板块输出
        for sector_name, stocks in sorted(results_by_sector.items(), key=lambda x: len(x[1]), reverse=True):
            print()
            print(f"【{sector_name}】 共 {len(stocks)} 只")
            print("-" * 120)
            print(f"{'代码':<10} {'名称':<12} {'现价':<8} {'涨幅%':<8} {'均线状态':<35} {'成交量':<20} {'新高状态':<15} {'主力流入':<20} {'评分':<6}")
            print("-" * 120)
            
            for stock in stocks[:10]:  # 每板块最多显示10只
                print(f"{stock['code']:<10} {stock['name']:<12} {stock['price']:<8} {stock['change_pct']:<8.2f} "
                      f"{stock['ma_status']:<35} {stock['volume_status']:<20} {stock['high_status']:<15} "
                      f"{stock['main_inflow']:<20} {stock['score']:<6}")
            
            if len(stocks) > 10:
                print(f"... 还有 {len(stocks) - 10} 只股票 ...")
            print()
        
        # 汇总统计
        total_stocks = sum(len(stocks) for stocks in results_by_sector.values())
        print()
        print("=" * 120)
        print(f"总计: {total_stocks} 只股票符合选股条件")
        print("=" * 120)
        
        # TOP 10 推荐
        all_stocks = []
        for stocks in results_by_sector.values():
            all_stocks.extend(stocks)
        all_stocks = sorted(all_stocks, key=lambda x: x['score'], reverse=True)
        
        print()
        print("🏆 TOP 10 重点推荐")
        print("-" * 120)
        print(f"{'排名':<6} {'代码':<10} {'名称':<12} {'板块':<15} {'现价':<8} {'涨幅%':<8} {'评分':<6} {'推荐理由':<40}")
        print("-" * 120)
        
        for i, stock in enumerate(all_stocks[:10], 1):
            reason = f"均线{stock['ma_bullish']}+量比{stock['volume_status'].split('量比')[1] if '量比' in stock['volume_status'] else '高'}+{stock['high_status'][:4]}"
            print(f"{i:<6} {stock['code']:<10} {stock['name']:<12} {stock['sector']:<15} {stock['price']:<8} "
                  f"{stock['change_pct']:<8.2f} {stock['score']:<6} {reason:<40}")
        
        print("-" * 120)
        
        return all_stocks
    
    def save_results(self, results_by_sector, hot_sectors, all_stocks):
        """保存结果到文件"""
        output = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'hot_sectors': hot_sectors,
            'results_by_sector': results_by_sector,
            'top10': all_stocks[:10] if all_stocks else []
        }
        
        # JSON格式
        json_file = f"/tmp/technical_selection_{datetime.now().strftime('%Y%m%d')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        # CSV格式
        csv_file = f"/tmp/technical_selection_{datetime.now().strftime('%Y%m%d')}.csv"
        if all_stocks:
            df = pd.DataFrame(all_stocks)
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        print()
        print(f"📁 结果已保存:")
        print(f"   JSON: {json_file}")
        print(f"   CSV: {csv_file}")

def main():
    selector = TechnicalStockSelector()
    
    # 执行选股
    results_by_sector, hot_sectors = selector.select_stocks(
        max_sectors=10,
        max_stocks_per_sector=20
    )
    
    # 打印结果
    all_stocks = selector.print_results(results_by_sector, hot_sectors)
    
    # 保存结果
    selector.save_results(results_by_sector, hot_sectors, all_stocks)
    
    print()
    print("✅ 选股完成!")

if __name__ == '__main__':
    main()
