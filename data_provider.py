#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AKShare 数据获取模块 - 战法回测数据支持
获取真实的历史涨停数据、连板数据、指数数据
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
from pathlib import Path


class AKDataProvider:
    """AKShare数据提供者"""
    
    def __init__(self, cache_dir="./data_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache = {}
    
    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{key}.json"
    
    def _load_cache(self, key: str) -> pd.DataFrame:
        """从缓存加载数据"""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            return pd.read_json(cache_path)
        return None
    
    def _save_cache(self, key: str, df: pd.DataFrame):
        """保存数据到缓存"""
        cache_path = self._get_cache_path(key)
        df.to_json(cache_path, orient='records', force_ascii=False)
    
    def get_zt_pool(self, date: str) -> pd.DataFrame:
        """
        获取涨停股池数据
        date: 格式YYYYMMDD
        """
        cache_key = f"zt_pool_{date}"
        cached = self._load_cache(cache_key)
        if cached is not None:
            return cached
        
        try:
            df = ak.stock_zt_pool_em(date=date)
            self._save_cache(cache_key, df)
            time.sleep(0.3)  # 避免请求过快
            return df
        except Exception as e:
            print(f"  获取{date}涨停数据失败: {e}")
            return pd.DataFrame()
    
    def get_zt_pool_strong(self, date: str) -> pd.DataFrame:
        """获取强势涨停股池"""
        cache_key = f"zt_strong_{date}"
        cached = self._load_cache(cache_key)
        if cached is not None:
            return cached
        
        try:
            df = ak.stock_zt_pool_strong_em(date=date)
            self._save_cache(cache_key, df)
            time.sleep(0.3)
            return df
        except Exception as e:
            return pd.DataFrame()
    
    def get_zt_pool_sub_new(self, date: str) -> pd.DataFrame:
        """获取次新股涨停股池"""
        try:
            df = ak.stock_zt_pool_sub_new_em(date=date)
            time.sleep(0.3)
            return df
        except:
            return pd.DataFrame()
    
    def get_zt_pool_zbgc(self, date: str) -> pd.DataFrame:
        """获取炸板股池"""
        try:
            df = ak.stock_zt_pool_zbgc_em(date=date)
            time.sleep(0.3)
            return df
        except:
            return pd.DataFrame()
    
    def get_limit_up_statistics(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取涨停统计数据
        包括每日涨停家数、连板情况等
        """
        # 尝试从已有数据获取
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        stats_list = []
        
        print(f"获取涨停统计数据: {len(dates)} 个交易日")
        
        for i, date in enumerate(dates):
            date_str = date.strftime('%Y%m%d')
            
            if i % 50 == 0:
                print(f"  进度: {i}/{len(dates)} ({i/len(dates)*100:.1f}%)")
            
            zt_df = self.get_zt_pool(date_str)
            
            if not zt_df.empty:
                stat = {
                    'date': date_str,
                    'limit_up_count': len(zt_df),
                    'max_lianban': zt_df['连板数'].max() if '连板数' in zt_df.columns else 1,
                    'avg_lianban': zt_df['连板数'].mean() if '连板数' in zt_df.columns else 1,
                    'zt_amount': zt_df['成交额'].sum() if '成交额' in zt_df.columns else 0,
                }
                stats_list.append(stat)
        
        return pd.DataFrame(stats_list)
    
    def get_index_daily(self, symbol: str = "000001", start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取指数日线数据
        symbol: 指数代码 000001=上证指数, 399001=深证成指, 399006=创业板指
        """
        cache_key = f"index_{symbol}_{start_date}_{end_date}"
        cached = self._load_cache(cache_key)
        if cached is not None:
            return cached
        
        try:
            df = ak.index_zh_a_hist(symbol=symbol, period="daily", 
                                   start_date=start_date, end_date=end_date)
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.sort_values('日期')
            self._save_cache(cache_key, df)
            return df
        except Exception as e:
            print(f"获取指数{symbol}数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取个股日线数据"""
        cache_key = f"stock_{symbol}_{start_date}_{end_date}"
        cached = self._load_cache(cache_key)
        if cached is not None:
            return cached
        
        try:
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily",
                                   start_date=start_date, end_date=end_date, adjust="qfq")
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.sort_values('日期')
            self._save_cache(cache_key, df)
            return df
        except Exception as e:
            return pd.DataFrame()
    
    def get_a_stock_list(self) -> pd.DataFrame:
        """获取A股所有股票列表"""
        try:
            return ak.stock_zh_a_spot_em()
        except:
            return pd.DataFrame()
    
    def get_concept_boards(self) -> pd.DataFrame:
        """获取概念板块列表"""
        try:
            return ak.stock_board_concept_name_em()
        except:
            return pd.DataFrame()
    
    def get_industry_boards(self) -> pd.DataFrame:
        """获取行业板块列表"""
        try:
            return ak.stock_board_industry_name_em()
        except:
            return pd.DataFrame()


class MarketAnalyzer:
    """市场分析器"""
    
    def __init__(self):
        self.data_provider = AKDataProvider()
    
    def analyze_date(self, date_str: str) -> dict:
        """分析某日的市场状态"""
        
        # 获取涨停数据
        zt_df = self.data_provider.get_zt_pool(date_str)
        
        if zt_df.empty:
            return None
        
        analysis = {
            'date': date_str,
            'limit_up_count': len(zt_df),
            'max_lianban': 0,
            'lianban_4plus': 0,  # 4板及以上
            'lianban_3plus': 0,  # 3板及以上
            'sectors': {}
        }
        
        # 连板统计
        if '连板数' in zt_df.columns:
            analysis['max_lianban'] = zt_df['连板数'].max()
            analysis['lianban_4plus'] = len(zt_df[zt_df['连板数'] >= 4])
            analysis['lianban_3plus'] = len(zt_df[zt_df['连板数'] >= 3])
        
        # 板块统计
        if '所属行业' in zt_df.columns:
            sectors = zt_df['所属行业'].value_counts()
            analysis['top_sectors'] = sectors.head(5).to_dict()
        
        return analysis
    
    def analyze_period(self, start_date: str, end_date: str) -> pd.DataFrame:
        """分析一段时间的市场状态"""
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        analyses = []
        
        print(f"分析市场状态: {start_date} 至 {end_date}")
        print(f"共 {len(dates)} 个交易日")
        
        for i, date in enumerate(dates):
            date_str = date.strftime('%Y%m%d')
            
            if i % 30 == 0:
                print(f"  处理中: {date_str} ({i+1}/{len(dates)})")
            
            analysis = self.analyze_date(date_str)
            if analysis:
                analyses.append(analysis)
        
        df = pd.DataFrame(analyses)
        print(f"成功获取 {len(df)} 天数据")
        return df
    
    def get_historical_limit_up_series(self, start_date: str, end_date: str) -> pd.DataFrame:
        """获取历史涨停家数序列"""
        df = self.analyze_period(start_date, end_date)
        return df


def test_data_provider():
    """测试数据获取"""
    provider = AKDataProvider()
    
    # 测试获取涨停数据
    test_date = "20240219"
    print(f"测试获取 {test_date} 涨停数据...")
    
    zt_df = provider.get_zt_pool(test_date)
    if not zt_df.empty:
        print(f"  涨停家数: {len(zt_df)}")
        print(f"  最高连板: {zt_df['连板数'].max() if '连板数' in zt_df.columns else 'N/A'}")
        print(f"  前5条数据:")
        print(zt_df.head())
    
    # 测试获取指数数据
    print("\n测试获取上证指数数据...")
    index_df = provider.get_index_daily("000001", "20240101", "20240220")
    if not index_df.empty:
        print(f"  数据条数: {len(index_df)}")
        print(f"  最新日期: {index_df['日期'].iloc[-1]}")
        print(f"  最新收盘: {index_df['收盘'].iloc[-1]}")
    
    return zt_df, index_df


def generate_backtest_data():
    """生成回测所需的历史数据"""
    analyzer = MarketAnalyzer()
    
    # 2023-2025年数据
    periods = [
        ("20230101", "20231231", "2023年"),
        ("20240101", "20241231", "2024年"),
        ("20250101", "20250220", "2025年至今"),
    ]
    
    all_data = []
    
    for start, end, label in periods:
        print(f"\n{'='*60}")
        print(f"获取{label}数据...")
        print('='*60)
        
        df = analyzer.analyze_period(start, end)
        if not df.empty:
            df['year'] = label
            all_data.append(df)
            
            # 输出统计
            print(f"\n{label}统计:")
            print(f"  平均涨停家数: {df['limit_up_count'].mean():.1f}")
            print(f"  最高涨停家数: {df['limit_up_count'].max()}")
            print(f"  平均最高连板: {df['max_lianban'].mean():.1f}")
            print(f"  最高连板: {df['max_lianban'].max()}")
    
    # 合并所有数据
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        combined.to_csv("historical_market_data_2023_2025.csv", index=False, encoding='utf-8-sig')
        print(f"\n数据已保存到 historical_market_data_2023_2025.csv")
        return combined
    
    return pd.DataFrame()


if __name__ == "__main__":
    print("="*80)
    print("AKShare 数据获取模块")
    print("="*80)
    
    # 先测试数据获取
    print("\n[1/2] 测试数据获取...")
    test_data_provider()
    
    # 生成完整回测数据
    print("\n[2/2] 生成完整历史数据...")
    df = generate_backtest_data()
    
    print("\n数据准备完成!")
