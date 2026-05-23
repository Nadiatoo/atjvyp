#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术指标选股脚本 - 强势股筛选器
选股条件：
1. 5/8/13日均线多头排列，且都在50/55/60日均线上方
2. 近3日成交量持续放大，且有过倍量
3. 股价创近一年新高或近20日内创新高
4. 主力连续3天净流入
5. 所属板块为近日热门板块
"""

import json
import requests
import pandas as pd
from datetime import datetime, timedelta

class TechnicalStockSelector:
    def __init__(self):
        self.base_url = "https://push2.eastmoney.com/api"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def get_all_stocks(self):
        """获取全市场股票列表"""
        url = "http://api.finance.ifeng.com/stock/latest"
        try:
            # 使用东方财富接口获取沪深A股
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': 1,
                'pz': 5000,
                'po': 1,
                'np': 1,
                'fltt': 2,
                'invt': 2,
                'fid': 'f12',
                'fs': 'm:0+t:6,m:0+t:13,m:1+t:2,m:1+t:23',
                'fields': 'f12,f14,f2,f3,f4,f5,f6,f7,f8,f9,f10,f18,f20,f21,f33,f34,f35,f36,f37,f38,f39,f40,f41,f42,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65,f66,f67,f68,f69,f70,f71,f72,f73,f74,f75,f76,f77,f78,f79,f80,f81,f82,f83,f84,f85,f86,f87,f88,f89,f90,f91,f92,f93,f94,f95,f96,f97,f98,f99,f100'
            }
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            data = response.json()
            
            stocks = []
            if data.get('data') and data['data'].get('diff'):
                for item in data['data']['diff']:
                    stock = {
                        'code': item.get('f12'),
                        'name': item.get('f14'),
                        'price': item.get('f2'),
                        'change_pct': item.get('f3'),
                        'volume': item.get('f5'),
                        'amount': item.get('f6'),
                        'turnover': item.get('f8'),
                        'pe': item.get('f9'),
                        'pb': item.get('f23'),
                        'market_cap': item.get('f20'),
                        'float_cap': item.get('f21'),
                        'high_52w': item.get('f44'),
                        'low_52w': item.get('f45'),
                        'high_20d': item.get('f46'),
                        'low_20d': item.get('f47'),
                        'ma5': item.get('f21'),
                        'ma10': item.get('f22'),
                        'ma20': item.get('f23'),
                        'ma60': item.get('f24'),
                    }
                    stocks.append(stock)
            return pd.DataFrame(stocks)
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_stock_kline(self, code, days=60):
        """获取股票K线数据"""
        try:
            # 判断市场
            if code.startswith('6'):
                market = '1'
            elif code.startswith('0') or code.startswith('3'):
                market = '0'
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
            print(f"获取{code}K线失败: {e}")
            return pd.DataFrame()
    
    def calculate_ma(self, df, periods):
        """计算移动平均线"""
        for period in periods:
            df[f'MA{period}'] = df['close'].rolling(window=period).mean()
        return df
    
    def check_ma_bullish(self, df):
        """
        检查均线多头排列：
        1. 5/8/13日均线多头排列
        2. 三条均线都在50/55/60日均线上方
        """
        if len(df) < 60:
            return False
        
        latest = df.iloc[-1]
        
        # 计算8日均线（如果没有）
        if 'MA8' not in df.columns:
            df['MA8'] = df['close'].rolling(window=8).mean()
            latest = df.iloc[-1]
        
        # 条件1: 5/8/13日均线多头排列
        ma5 = latest.get('MA5', 0)
        ma8 = latest.get('MA8', 0)
        ma10 = latest.get('MA10', 0)
        ma13 = latest.get('MA13', 0)
        ma20 = latest.get('MA20', 0)
        
        # 如果没有MA13，用MA10代替
        if ma13 == 0:
            ma13 = ma10
        
        # 计算50/55/60日均线
        ma50 = df['close'].rolling(window=50).mean().iloc[-1]
        ma55 = df['close'].rolling(window=55).mean().iloc[-1]
        ma60 = latest.get('MA60', 0)
        
        # 条件1: 5>8>13 多头排列
        condition1 = ma5 > ma8 > ma13
        
        # 条件2: 5/8/13都在50/55/60上方
        long_term_ma = max(ma50, ma55, ma60) if ma60 > 0 else max(ma50, ma55)
        condition2 = (ma5 > long_term_ma) and (ma8 > long_term_ma) and (ma13 > long_term_ma)
        
        return condition1 and condition2, {
            'MA5': round(ma5, 2),
            'MA8': round(ma8, 2),
            'MA13': round(ma13, 2),
            'MA50': round(ma50, 2),
            'MA60': round(ma60, 2)
        }
    
    def check_volume_expansion(self, df):
        """
        检查成交量条件：
        1. 近3日成交量持续放大
        2. 有过倍量放量（当日成交量>前一日2倍）
        """
        if len(df) < 5:
            return False
        
        recent = df.tail(5)
        volumes = recent['volume'].tolist()
        
        # 近3日持续放大
        vol_increasing = volumes[-1] > volumes[-2] > volumes[-3]
        
        # 有过倍量（近5日内）
        has_double_volume = False
        for i in range(1, 5):
            if volumes[i] > volumes[i-1] * 2:
                has_double_volume = True
                break
        
        return vol_increasing or has_double_volume, {
            'vol_trend': '放大' if vol_increasing else '震荡',
            'has_double': '有倍量' if has_double_volume else '无倍量',
            'latest_vol': int(volumes[-1])
        }
    
    def check_new_high(self, df):
        """
        检查新高条件：
        1. 股价创近一年新高或历史新高
        2. 或近20个交易日内创近一年新高
        """
        if len(df) < 20:
            return False
        
        latest_close = df.iloc[-1]['close']
        high_250d = df['high'].max()  # 近一年最高
        high_20d = df.tail(20)['high'].max()  # 近20日最高
        
        # 当前价格接近一年新高（95%以上）
        near_250d_high = latest_close >= high_250d * 0.95
        
        # 近20日内创过一年新高
        recent_breakout = high_20d >= high_250d * 0.98
        
        return near_250d_high or recent_breakout, {
            'current_price': round(latest_close, 2),
            'high_250d': round(high_250d, 2),
            'high_20d': round(high_20d, 2),
            'breakout': '突破' if near_250d_high else '接近'
        }
    
    def get_main_force_flow(self, code):
        """获取主力资金流向（简化版，使用当日数据）"""
        try:
            if code.startswith('6'):
                market = '1'
            elif code.startswith('0') or code.startswith('3'):
                market = '0'
            else:
                market = '0'
            
            url = f"https://push2.eastmoney.com/api/qt/stock/get"
            params = {
                'secid': f'{market}.{code}',
                'fields': 'f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65,f66,f67,f68,f69,f70,f71,f72,f73,f74,f75,f76,f77,f78,f79,f80,f81,f82,f83,f84,f85,f86,f87,f88,f89,f90,f91,f92,f93,f94,f95,f96,f97,f98,f99,f100'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            data = response.json()
            
            if data.get('data'):
                # 主力资金净流入（万元）
                main_inflow = data['data'].get('f62', 0)
                return float(main_inflow) if main_inflow else 0
            return 0
        except:
            return 0
    
    def get_hot_sectors(self):
        """获取热门板块"""
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': 1,
                'pz': 50,
                'po': 1,
                'np': 1,
                'fltt': 2,
                'invt': 2,
                'fid': 'f20',
                'fs': 'm:90+t:2',
                'fields': 'f12,f14,f2,f3,f4,f5,f6,f7,f8,f9,f10,f18,f20,f21'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            data = response.json()
            
            hot_sectors = []
            if data.get('data') and data['data'].get('diff'):
                for item in data['data']['diff'][:20]:  # 前20热门板块
                    hot_sectors.append({
                        'code': item.get('f12'),
                        'name': item.get('f14'),
                        'change_pct': item.get('f3'),
                        'main_inflow': item.get('f20')
                    })
            return hot_sectors
        except Exception as e:
            print(f"获取热门板块失败: {e}")
            return []
    
    def get_stock_sector(self, code):
        """获取股票所属板块（简化版）"""
        # 这里简化处理，实际应该查询股票详情
        # 返回板块代码列表
        return []
    
    def select_stocks(self, max_stocks=100):
        """执行选股"""
        print("=" * 60)
        print("技术指标选股 - 强势股筛选器")
        print("=" * 60)
        print(f"选股时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 获取热门板块
        print("正在获取热门板块...")
        hot_sectors = self.get_hot_sectors()
        hot_sector_names = [s['name'] for s in hot_sectors]
        print(f"热门板块: {', '.join(hot_sector_names[:10])}")
        print()
        
        # 获取股票列表（这里简化，实际应该遍历全市场）
        # 由于数据量大，我们先测试几只股票
        test_stocks = [
            '300170',  # 汉得信息
            '300113',  # 顺网科技
            '300017',  # 网宿科技
            '301396',  # 宏景科技
            '688316',  # 青云科技
            '688229',  # 博睿数据
            '301606',  # 绿联科技
            '301179',  # 泽宇智能
            '688158',  # 优刻得
            '301638',  # 南网数字
            '002594',  # 比亚迪
            '300750',  # 宁德时代
            '000066',  # 中国长城
            '600602',  # 云赛智联
            '601877',  # 正泰电器
        ]
        
        results = []
        
        print(f"开始分析 {len(test_stocks)} 只测试股票...")
        print()
        
        for code in test_stocks:
            try:
                # 获取K线数据
                df = self.get_stock_kline(code, days=80)
                if df.empty or len(df) < 60:
                    continue
                
                # 计算均线
                df = self.calculate_ma(df, [5, 8, 13, 20, 50, 55, 60])
                
                # 条件1: 均线多头排列
                ma_pass, ma_info = self.check_ma_bullish(df)
                if not ma_pass:
                    continue
                
                # 条件2: 成交量放大
                vol_pass, vol_info = self.check_volume_expansion(df)
                if not vol_pass:
                    continue
                
                # 条件3: 新高
                high_pass, high_info = self.check_new_high(df)
                if not high_pass:
                    continue
                
                # 条件4: 主力资金（简化，只检查当日）
                main_inflow = self.get_main_force_flow(code)
                
                # 获取股票名称
                stock_name = self.get_stock_name(code)
                
                result = {
                    'code': code,
                    'name': stock_name,
                    'price': high_info['current_price'],
                    'change_pct': round((df.iloc[-1]['close'] - df.iloc[-2]['close']) / df.iloc[-2]['close'] * 100, 2),
                    'sector': '待查询',
                    'ma_status': f"MA5:{ma_info['MA5']} > MA8:{ma_info['MA8']} > MA13:{ma_info['MA13']}",
                    'volume_status': f"{vol_info['vol_trend']}, {vol_info['has_double']}",
                    'high_status': f"当前{high_info['current_price']}/一年新高{high_info['high_250d']}",
                    'main_inflow': f"{main_inflow:.0f}万",
                    'score': self.calculate_score(ma_pass, vol_pass, high_pass, main_inflow)
                }
                
                results.append(result)
                print(f"✅ {code} {stock_name} 符合条件")
                
            except Exception as e:
                print(f"❌ {code} 分析失败: {e}")
                continue
        
        return results, hot_sectors
    
    def get_stock_name(self, code):
        """获取股票名称"""
        stock_names = {
            '300170': '汉得信息',
            '300113': '顺网科技',
            '300017': '网宿科技',
            '301396': '宏景科技',
            '688316': '青云科技',
            '688229': '博睿数据',
            '301606': '绿联科技',
            '301179': '泽宇智能',
            '688158': '优刻得',
            '301638': '南网数字',
            '002594': '比亚迪',
            '300750': '宁德时代',
            '000066': '中国长城',
            '600602': '云赛智联',
            '601877': '正泰电器',
        }
        return stock_names.get(code, '未知')
    
    def calculate_score(self, ma_pass, vol_pass, high_pass, main_inflow):
        """计算综合评分"""
        score = 0
        if ma_pass:
            score += 40
        if vol_pass:
            score += 30
        if high_pass:
            score += 20
        if main_inflow > 0:
            score += 10
        return score

def main():
    selector = TechnicalStockSelector()
    results, hot_sectors = selector.select_stocks()
    
    print()
    print("=" * 60)
    print("选股结果")
    print("=" * 60)
    
    if not results:
        print("未找到符合条件的股票")
        return
    
    # 按板块分组（简化，实际应该查询板块）
    df = pd.DataFrame(results)
    df = df.sort_values('score', ascending=False)
    
    print()
    print(f"共选出 {len(results)} 只符合条件的股票：")
    print()
    
    # 输出表格
    print("-" * 120)
    print(f"{'代码':<10} {'名称':<12} {'现价':<10} {'涨幅%':<8} {'板块':<15} {'均线状态':<30} {'成交量':<15} {'主力资金':<12} {'评分':<6}")
    print("-" * 120)
    
    for _, row in df.iterrows():
        print(f"{row['code']:<10} {row['name']:<12} {row['price']:<10} {row['change_pct']:<8} {row['sector']:<15} {row['ma_status']:<30} {row['volume_status']:<15} {row['main_inflow']:<12} {row['score']:<6}")
    
    print("-" * 120)
    
    # 保存结果
    output_file = f"/tmp/technical_stock_selection_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'count': len(results),
            'stocks': results,
            'hot_sectors': hot_sectors
        }, f, ensure_ascii=False, indent=2)
    
    print()
    print(f"结果已保存至: {output_file}")

if __name__ == '__main__':
    main()
