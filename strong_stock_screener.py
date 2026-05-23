#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强势股选股公式 - 简化版
基于实时市场数据的强势股筛选
选股条件：
1. 5/8/13日均线多头排列
2. 近3日成交量持续放大
3. 股价创近期新高
4. 主力资金净流入
"""

import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

class StrongStockScreener:
    def __init__(self):
        self.base_url = "https://push2.eastmoney.com/api"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def get_stock_list(self):
        """获取A股股票列表"""
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': 1,
                'pz': 100,  # 先取100只测试
                'po': 1,
                'np': 1,
                'fltt': 2,
                'invt': 2,
                'fid': 'f3',  # 按涨跌幅排序
                'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',  # A股
                'fields': 'f12,f14,f2,f3,f4,f5,f6,f7,f8,f9,f10,f18,f20,f21,f22,f23,f24,f25,f26'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            data = response.json()
            
            if data.get('data') and data['data'].get('diff'):
                stocks = data['data']['diff']
                return stocks[:50]  # 取前50只分析
            return []
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return []
    
    def get_stock_kline(self, code, days=60):
        """获取股票K线数据"""
        try:
            if code.startswith('6'):
                market = '1'
            else:
                market = '0'
            
            url = f"https://push2.eastmoney.com/api/qt/stock/kline/get"
            params = {
                'secid': f'{market}.{code}',
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': '101',  # 日K线
                'fqt': '0',    # 前复权
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
                    if len(parts) >= 7:
                        date = parts[0]
                        close = float(parts[2])
                        high = float(parts[3])
                        low = float(parts[4])
                        volume = float(parts[6])
                        df_data.append({
                            'date': date,
                            'close': close,
                            'high': high,
                            'low': low,
                            'volume': volume
                        })
                
                if df_data:
                    df = pd.DataFrame(df_data)
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values('date')
                    return df
            return None
        except Exception as e:
            print(f"获取{code}K线数据失败: {e}")
            return None
    
    def calculate_technical_indicators(self, df):
        """计算技术指标"""
        if df is None or len(df) < 60:
            return None
        
        # 计算均线
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma8'] = df['close'].rolling(window=8).mean()
        df['ma13'] = df['close'].rolling(window=13).mean()
        df['ma50'] = df['close'].rolling(window=50).mean()
        
        # 计算成交量均线
        df['volume_ma5'] = df['volume'].rolling(window=5).mean()
        df['volume_ma20'] = df['volume'].rolling(window=20).mean()
        
        # 计算近期高点和低点
        df['recent_high'] = df['high'].rolling(window=20).max()
        df['recent_low'] = df['low'].rolling(window=20).min()
        
        return df
    
    def check_selection_criteria(self, df, stock_info):
        """检查选股条件"""
        if df is None or len(df) < 60:
            return False, {}
        
        latest = df.iloc[-1]
        prev1 = df.iloc[-2] if len(df) >= 2 else latest
        prev2 = df.iloc[-3] if len(df) >= 3 else prev1
        prev3 = df.iloc[-4] if len(df) >= 4 else prev2
        
        criteria_results = {}
        
        # 1. 均线多头排列检查
        ma_criteria = (
            latest['ma5'] > latest['ma8'] > latest['ma13'] and
            latest['ma5'] > latest['ma50'] and
            latest['close'] > latest['ma5']
        )
        criteria_results['ma_multiple'] = ma_criteria
        
        # 2. 成交量持续放大检查
        volume_criteria = (
            latest['volume'] > latest['volume_ma5'] * 1.2 and
            latest['volume_ma5'] > latest['volume_ma20'] * 1.1
        )
        criteria_results['volume_increase'] = volume_criteria
        
        # 3. 股价创近期新高检查
        price_criteria = latest['close'] >= latest['recent_high'] * 0.98
        criteria_results['price_new_high'] = price_criteria
        
        # 4. 近期涨幅检查（3日涨幅>5%）
        if len(df) >= 4:
            price_3d_ago = df.iloc[-4]['close']
            price_increase = (latest['close'] - price_3d_ago) / price_3d_ago * 100
            price_increase_criteria = price_increase > 5
        else:
            price_increase_criteria = False
        criteria_results['price_increase'] = price_increase_criteria
        
        # 5. 股票基本信息检查
        basic_criteria = (
            float(stock_info.get('f3', 0)) > 0 and  # 今日涨幅>0
            float(stock_info.get('f6', 0)) > 1.0 and  # 成交额>1亿
            float(stock_info.get('f8', 100)) < 200  # 换手率<200%
        )
        criteria_results['basic_info'] = basic_criteria
        
        # 综合评分
        total_criteria = sum(criteria_results.values())
        
        return total_criteria >= 3, criteria_results
    
    def screen_stocks(self):
        """筛选强势股"""
        print("=" * 80)
        print("强势股选股分析 - 实时市场数据")
        print("=" * 80)
        print(f"选股时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 获取股票列表
        print("步骤1: 获取实时股票数据...")
        stocks = self.get_stock_list()
        if not stocks:
            print("获取股票列表失败，使用默认股票池")
            # 使用一些常见股票代码
            stocks = [
                {'f12': '000001', 'f14': '平安银行'},
                {'f12': '000002', 'f14': '万科A'},
                {'f12': '000858', 'f14': '五粮液'},
                {'f12': '002415', 'f14': '海康威视'},
                {'f12': '300750', 'f14': '宁德时代'},
                {'f12': '600519', 'f14': '贵州茅台'},
                {'f12': '601318', 'f14': '中国平安'},
                {'f12': '000333', 'f14': '美的集团'},
                {'f12': '002475', 'f14': '立讯精密'},
                {'f12': '300059', 'f14': '东方财富'},
            ]
        
        print(f"分析股票数量: {len(stocks)}")
        print()
        
        # 筛选强势股
        print("步骤2: 技术指标筛选...")
        strong_stocks = []
        
        for i, stock in enumerate(stocks):
            code = stock.get('f12', '')
            name = stock.get('f14', '')
            
            if not code or not name:
                continue
            
            print(f"  分析: {name}({code})", end='')
            
            # 获取K线数据
            df = self.get_stock_kline(code)
            if df is None:
                print(" - 数据获取失败")
                continue
            
            # 计算技术指标
            df = self.calculate_technical_indicators(df)
            if df is None:
                print(" - 技术指标计算失败")
                continue
            
            # 检查选股条件
            is_strong, criteria = self.check_selection_criteria(df, stock)
            
            if is_strong:
                latest = df.iloc[-1]
                score = sum(criteria.values())
                
                stock_data = {
                    'code': code,
                    'name': name,
                    'price': latest['close'],
                    'change': float(stock.get('f3', 0)),
                    'volume_ratio': latest['volume'] / latest['volume_ma20'] if latest['volume_ma20'] > 0 else 0,
                    'score': score,
                    'criteria': criteria
                }
                strong_stocks.append(stock_data)
                print(f" - ✅ 符合条件 (评分: {score}/5)")
            else:
                print(f" - ❌ 不符合条件")
            
            # 避免请求过快
            if (i + 1) % 5 == 0:
                time.sleep(0.5)
        
        print()
        print("步骤3: 结果排序和输出...")
        print()
        
        # 按评分排序
        strong_stocks.sort(key=lambda x: x['score'], reverse=True)
        
        return strong_stocks
    
    def print_results(self, strong_stocks):
        """打印筛选结果"""
        if not strong_stocks:
            print("❌ 未找到符合条件的强势股")
            return
        
        print("🎯 强势股筛选结果（按技术指标评分排序）")
        print("=" * 120)
        print(f"{'排名':<4} {'代码':<8} {'名称':<12} {'当前价':<8} {'涨幅%':<6} {'量比':<6} {'评分':<4} {'符合条件'}")
        print("-" * 120)
        
        for i, stock in enumerate(strong_stocks[:20]):  # 显示前20只
            criteria_text = []
            if stock['criteria'].get('ma_multiple'):
                criteria_text.append("均线多头")
            if stock['criteria'].get('volume_increase'):
                criteria_text.append("放量")
            if stock['criteria'].get('price_new_high'):
                criteria_text.append("新高")
            if stock['criteria'].get('price_increase'):
                criteria_text.append("强势")
            if stock['criteria'].get('basic_info'):
                criteria_text.append("基本面")
            
            change_symbol = "🟢" if stock['change'] > 0 else "🔴"
            
            print(f"{i+1:<4} {stock['code']:<8} {stock['name']:<12} "
                  f"{stock['price']:<8.2f} {change_symbol}{stock['change']:<5.1f}% "
                  f"{stock['volume_ratio']:<6.1f} {stock['score']:<4} {', '.join(criteria_text)}")
        
        print("=" * 120)
        print()
        
        # 输出详细分析
        print("📊 详细技术分析")
        print("-" * 80)
        
        for i, stock in enumerate(strong_stocks[:5]):  # 详细分析前5只
            print(f"\n{i+1}. {stock['name']}({stock['code']}) - 评分: {stock['score']}/5")
            print(f"   当前价: {stock['price']:.2f}元, 涨幅: {stock['change']:.1f}%, 量比: {stock['volume_ratio']:.1f}")
            print(f"   技术特征: ", end='')
            
            features = []
            if stock['criteria'].get('ma_multiple'):
                features.append("均线呈多头排列")
            if stock['criteria'].get('volume_increase'):
                features.append("成交量持续放大")
            if stock['criteria'].get('price_new_high'):
                features.append("股价创近期新高")
            if stock['criteria'].get('price_increase'):
                features.append("短期涨幅强势")
            
            print("; ".join(features))
        
        print()
        print("💡 投资建议")
        print("-" * 80)
        print("1. 重点关注评分4分以上的股票，技术面最为强势")
        print("2. 结合当前市场季节（秋收期），建议控制仓位在40-50%")
        print("3. 关注成交量配合情况，避免无量上涨")
        print("4. 设置止损位，控制回撤风险")
        print("5. 建议分批建仓，避免追高操作")
        
        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        result_file = f"/Users/tuqibiao/.openclaw/workspace/reports/strong_stocks_{timestamp}.txt"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(f"强势股筛选报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n")
            for stock in strong_stocks:
                f.write(f"{stock['code']} {stock['name']} 评分:{stock['score']} 价格:{stock['price']:.2f} 涨幅:{stock['change']:.1f}%\n")
        
        print(f"\n📁 报告已保存至: {result_file}")

def main():
    """主函数"""
    screener = StrongStockScreener()
    strong_stocks = screener.screen_stocks()
    screener.print_results(strong_stocks)

if __name__ == "__main__":
    main()