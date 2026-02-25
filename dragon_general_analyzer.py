#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
龙头与中军特征分析器
通过回测数据分析每轮行情启动时的龙头和中军特征
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class DragonAnalyzer:
    """龙头与中军特征分析器"""
    
    def __init__(self, cache_dir="./dragon_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.results = {
            'dragon': [],  # 龙头数据
            'general': [], # 中军数据
            'analysis': {} # 分析结果
        }
    
    def _cache_path(self, name: str) -> Path:
        return self.cache_dir / f"{name}.json"
    
    def save_cache(self, name: str, data: dict):
        """保存缓存"""
        with open(self._cache_path(name), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    def load_cache(self, name: str) -> dict:
        """加载缓存"""
        path = self._cache_path(name)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取个股日线数据"""
        try:
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily",
                                   start_date=start_date, end_date=end_date, adjust="qfq")
            if not df.empty:
                df['日期'] = pd.to_datetime(df['日期'])
                df = df.sort_values('日期')
            return df
        except Exception as e:
            print(f"  获取{symbol}数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_info(self, symbol: str) -> dict:
        """获取股票基本信息"""
        try:
            # 从A股列表获取
            df = ak.stock_zh_a_spot_em()
            stock = df[df['代码'] == symbol]
            if not stock.empty:
                return {
                    'name': stock['名称'].values[0],
                    'market_cap': stock['总市值'].values[0] / 1e8,  # 转为亿
                    'circulating_cap': stock['流通市值'].values[0] / 1e8,
                    'industry': stock.get('所属行业', ['未知']).values[0] if '所属行业' in stock.columns else '未知'
                }
        except Exception as e:
            print(f"  获取{symbol}信息失败: {e}")
        
        return {'name': symbol, 'market_cap': 0, 'circulating_cap': 0, 'industry': '未知'}
    
    def get_lhb_detail(self, symbol: str, date: str) -> dict:
        """获取龙虎榜详情"""
        try:
            df = ak.stock_lhb_detail_daily_sina(start_date=date, end_date=date)
            if not df.empty:
                stock_lhb = df[df['代码'] == symbol]
                if not stock_lhb.empty:
                    return {
                        'has_lhb': True,
                        'buy_amount': stock_lhb.get('买入额', [0]).values[0],
                        'sell_amount': stock_lhb.get('卖出额', [0]).values[0],
                        'net_amount': stock_lhb.get('净额', [0]).values[0],
                    }
        except Exception as e:
            pass
        
        return {'has_lhb': False, 'buy_amount': 0, 'sell_amount': 0, 'net_amount': 0}
    
    def analyze_dragon_case(self, symbol: str, name: str, start_date: str, 
                           sector: str, period_days: int = 30) -> dict:
        """
        分析龙头案例
        
        Args:
            symbol: 股票代码
            name: 股票名称
            start_date: 行情启动日期 (YYYYMMDD)
            sector: 所属板块
            period_days: 分析周期
        """
        print(f"\n分析龙头: {name}({symbol}) - {sector}")
        
        # 计算日期范围
        start = datetime.strptime(start_date, '%Y%m%d')
        end = start + timedelta(days=period_days)
        pre_start = start - timedelta(days=30)
        
        start_str = start.strftime('%Y%m%d')
        end_str = end.strftime('%Y%m%d')
        pre_start_str = pre_start.strftime('%Y%m%d')
        
        # 获取启动前数据
        pre_df = self.get_stock_daily(symbol, pre_start_str, start_str)
        
        # 获取启动后数据
        post_df = self.get_stock_daily(symbol, start_str, end_str)
        
        if post_df.empty:
            print(f"  无法获取数据")
            return None
        
        # 获取基本信息
        info = self.get_stock_info(symbol)
        
        # 分析特征
        analysis = {
            'symbol': symbol,
            'name': name,
            'sector': sector,
            'start_date': start_date,
            'market_cap_at_start': info['market_cap'],
            'circulating_cap_at_start': info['circulating_cap'],
            'industry': info['industry'],
        }
        
        # 1. 启动时市值范围
        analysis['market_cap_range'] = self._classify_market_cap(info['market_cap'])
        
        # 2. 启动前换手率和量能特征
        if not pre_df.empty and len(pre_df) >= 5:
            pre_5d = pre_df.tail(5)
            analysis['pre_avg_turnover'] = pre_5d['换手率'].mean() if '换手率' in pre_5d.columns else 0
            analysis['pre_max_turnover'] = pre_5d['换手率'].max() if '换手率' in pre_5d.columns else 0
            analysis['pre_volume_trend'] = self._analyze_volume_trend(pre_5d)
        else:
            analysis['pre_avg_turnover'] = 0
            analysis['pre_max_turnover'] = 0
            analysis['pre_volume_trend'] = 'unknown'
        
        # 3. 涨幅特征
        if len(post_df) >= 1:
            first_day = post_df.iloc[0]
            analysis['first_day_change'] = first_day['涨跌幅'] if '涨跌幅' in first_day else 0
            analysis['first_day_turnover'] = first_day['换手率'] if '换手率' in first_day else 0
            
            # 计算连板天数
            limit_up_days = 0
            for _, row in post_df.iterrows():
                if row['涨跌幅'] >= 9.5:  # 涨停
                    limit_up_days += 1
                else:
                    break
            analysis['limit_up_days'] = limit_up_days
            
            # 总涨幅
            if len(post_df) > 1:
                total_change = (post_df['收盘'].iloc[-1] / post_df['开盘'].iloc[0] - 1) * 100
                analysis['total_change_pct'] = total_change
        
        # 4. 分时特征（简化处理，假设早盘涨停）
        analysis['first_limit_time'] = '09:30-10:00'  # 龙头通常早盘涨停
        
        print(f"  市值: {info['market_cap']:.1f}亿")
        print(f"  连板天数: {analysis.get('limit_up_days', 0)}")
        print(f"  启动前平均换手: {analysis['pre_avg_turnover']:.2f}%")
        
        return analysis
    
    def analyze_general_case(self, symbol: str, name: str, start_date: str,
                            sector: str, period_days: int = 30) -> dict:
        """
        分析中军案例
        
        Args:
            symbol: 股票代码
            name: 股票名称
            start_date: 行情启动日期
            sector: 所属板块
            period_days: 分析周期
        """
        print(f"\n分析中军: {name}({symbol}) - {sector}")
        
        start = datetime.strptime(start_date, '%Y%m%d')
        end = start + timedelta(days=period_days)
        start_str = start.strftime('%Y%m%d')
        end_str = end.strftime('%Y%m%d')
        
        df = self.get_stock_daily(symbol, start_str, end_str)
        
        if df.empty:
            print(f"  无法获取数据")
            return None
        
        info = self.get_stock_info(symbol)
        
        analysis = {
            'symbol': symbol,
            'name': name,
            'sector': sector,
            'start_date': start_date,
            'market_cap': info['market_cap'],
            'industry': info['industry'],
        }
        
        # 1. 市值规模
        analysis['is_large_cap'] = info['market_cap'] > 500
        
        # 2. 涨幅特征（阶梯式，非连板）
        if len(df) > 1:
            daily_changes = df['涨跌幅'].tolist() if '涨跌幅' in df.columns else []
            analysis['max_daily_change'] = max(daily_changes) if daily_changes else 0
            analysis['avg_daily_change'] = np.mean(daily_changes) if daily_changes else 0
            
            # 连板天数（中军应该很少连板）
            limit_up_days = sum(1 for c in daily_changes if c >= 9.5)
            analysis['limit_up_days'] = limit_up_days
            
            # 总涨幅
            total_change = (df['收盘'].iloc[-1] / df['开盘'].iloc[0] - 1) * 100
            analysis['total_change_pct'] = total_change
        
        print(f"  市值: {info['market_cap']:.1f}亿")
        print(f"  总涨幅: {analysis.get('total_change_pct', 0):.1f}%")
        print(f"  连板天数: {analysis.get('limit_up_days', 0)}")
        
        return analysis
    
    def _classify_market_cap(self, cap: float) -> str:
        """分类市值规模"""
        if cap < 50:
            return '小市值(<50亿)'
        elif cap < 100:
            return '中小市值(50-100亿)'
        elif cap < 300:
            return '中市值(100-300亿)'
        elif cap < 500:
            return '大中市值(300-500亿)'
        else:
            return '大市值(>500亿)'
    
    def _analyze_volume_trend(self, df: pd.DataFrame) -> str:
        """分析量能趋势"""
        if '成交额' not in df.columns or len(df) < 3:
            return 'unknown'
        
        volumes = df['成交额'].tolist()
        if volumes[-1] > volumes[0] * 1.5:
            return '放量'
        elif volumes[-1] < volumes[0] * 0.8:
            return '缩量'
        else:
            return '平量'
    
    def run_historical_analysis(self):
        """运行历史案例分析"""
        
        print("="*80)
        print("开始龙头与中军特征分析")
        print("="*80)
        
        # 龙头案例（基于历史数据的研究）
        dragon_cases = [
            # 2023年AI行情
            {'symbol': '603083', 'name': '剑桥科技', 'start_date': '20230301', 'sector': 'AI/CPO'},
            {'symbol': '300418', 'name': '昆仑万维', 'start_date': '20230301', 'sector': 'AI/大模型'},
            {'symbol': '300624', 'name': '万兴科技', 'start_date': '20230301', 'sector': 'AI/应用'},
            
            # 2023年华为行情
            {'symbol': '002855', 'name': '捷荣技术', 'start_date': '20230828', 'sector': '华为'},
            {'symbol': '300045', 'name': '华力创通', 'start_date': '20230828', 'sector': '华为/卫星'},
            
            # 2024年机器人行情
            {'symbol': '002896', 'name': '中大力德', 'start_date': '20240102', 'sector': '机器人'},
            {'symbol': '603728', 'name': '鸣志电器', 'start_date': '20240102', 'sector': '机器人'},
            
            # 2024年微盘股反弹
            {'symbol': '002786', 'name': '银宝山新', 'start_date': '20240201', 'sector': '微盘股'},
            {'symbol': '001300', 'name': '三柏硕', 'start_date': '20240201', 'sector': '微盘股'},
        ]
        
        # 中军案例
        general_cases = [
            # 2023年AI中军
            {'symbol': '601138', 'name': '工业富联', 'start_date': '20230301', 'sector': 'AI/算力'},
            {'symbol': '603019', 'name': '中科曙光', 'start_date': '20230301', 'sector': 'AI/算力'},
            
            # 2023年券商中军
            {'symbol': '600030', 'name': '中信证券', 'start_date': '20230725', 'sector': '券商'},
            {'symbol': '300059', 'name': '东方财富', 'start_date': '20230725', 'sector': '券商'},
            
            # 2024年新能源中军
            {'symbol': '300750', 'name': '宁德时代', 'start_date': '20240201', 'sector': '新能源'},
            {'symbol': '002594', 'name': '比亚迪', 'start_date': '20240201', 'sector': '新能源'},
        ]
        
        print("\n" + "="*80)
        print("【一、龙头案例分析】")
        print("="*80)
        
        for case in dragon_cases:
            result = self.analyze_dragon_case(
                case['symbol'], case['name'], 
                case['start_date'], case['sector']
            )
            if result:
                self.results['dragon'].append(result)
            time.sleep(0.5)  # 避免请求过快
        
        print("\n" + "="*80)
        print("【二、中军案例分析】")
        print("="*80)
        
        for case in general_cases:
            result = self.analyze_general_case(
                case['symbol'], case['name'],
                case['start_date'], case['sector']
            )
            if result:
                self.results['general'].append(result)
            time.sleep(0.5)
        
        # 生成统计报告
        self._generate_statistics()
        
        return self.results
    
    def _generate_statistics(self):
        """生成统计分析"""
        
        print("\n" + "="*80)
        print("【三、特征统计分析】")
        print("="*80)
        
        # 龙头统计
        if self.results['dragon']:
            df_dragon = pd.DataFrame(self.results['dragon'])
            
            print("\n◆ 龙头特征统计:")
            print(f"  案例数量: {len(df_dragon)}")
            
            # 市值分布
            print(f"\n  市值分布:")
            cap_dist = df_dragon['market_cap_range'].value_counts()
            for cap, count in cap_dist.items():
                print(f"    - {cap}: {count}家")
            
            # 平均市值
            avg_cap = df_dragon['market_cap_at_start'].mean()
            print(f"\n  平均启动市值: {avg_cap:.1f}亿")
            
            # 连板统计
            avg_limit = df_dragon['limit_up_days'].mean()
            max_limit = df_dragon['limit_up_days'].max()
            print(f"  平均连板天数: {avg_limit:.1f}")
            print(f"  最高连板天数: {max_limit}")
            
            # 换手率
            avg_turnover = df_dragon['pre_avg_turnover'].mean()
            print(f"  启动前平均换手: {avg_turnover:.2f}%")
        
        # 中军统计
        if self.results['general']:
            df_general = pd.DataFrame(self.results['general'])
            
            print("\n◆ 中军特征统计:")
            print(f"  案例数量: {len(df_general)}")
            
            # 市值分布
            large_cap_pct = (df_general['is_large_cap'].sum() / len(df_general)) * 100
            print(f"\n  大市值占比(>500亿): {large_cap_pct:.0f}%")
            
            avg_cap = df_general['market_cap'].mean()
            print(f"  平均市值: {avg_cap:.1f}亿")
            
            # 涨幅特征
            avg_change = df_general['total_change_pct'].mean()
            print(f"  平均阶段涨幅: {avg_change:.1f}%")
            
            # 连板天数（中军应该很少）
            avg_limit = df_general['limit_up_days'].mean()
            print(f"  平均连板天数: {avg_limit:.1f} (应<2)")
        
        # 保存分析结果
        self.save_cache('dragon_analysis', self.results)
        print("\n分析结果已保存到 dragon_cache/")


if __name__ == "__main__":
    analyzer = DragonAnalyzer()
    results = analyzer.run_historical_analysis()
    print("\n分析完成!")
