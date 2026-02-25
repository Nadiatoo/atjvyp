#!/usr/bin/env python3
"""
Tushare Pro API 数据采集与回测分析脚本
用于彪哥战法v4.0进化
"""

import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import time

class TushareDataCollector:
    """Tushare Pro 数据采集器"""
    
    def __init__(self, token=None, data_dir="tushare_data"):
        """
        初始化采集器
        
        Args:
            token: Tushare Pro API Token，如果为None则使用环境变量
            data_dir: 数据保存目录
        """
        if token:
            ts.set_token(token)
        self.pro = ts.pro_api()
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
    def get_trade_calendar(self, start_date="20210101", end_date="20251231"):
        """获取交易日历"""
        df = self.pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date)
        df = df[df['is_open'] == 1]
        df.to_csv(f"{self.data_dir}/trade_calendar.csv", index=False, encoding='utf-8-sig')
        print(f"✓ 获取交易日历: {len(df)}个交易日")
        return df
    
    def get_stock_basic(self):
        """获取股票基础信息（全市场）"""
        # 获取所有A股列表
        df = self.pro.stock_basic(exchange='', list_status='L')
        df.to_csv(f"{self.data_dir}/stock_basic.csv", index=False, encoding='utf-8-sig')
        print(f"✓ 获取股票基础信息: {len(df)}只股票")
        return df
    
    def get_index_daily(self, start_date="20210101", end_date="20250228"):
        """获取主要指数日线数据"""
        indices = {
            "上证指数": "000001.SH",
            "深证成指": "399001.SZ", 
            "创业板指": "399006.SZ",
            "沪深300": "000300.SH",
            "中证500": "000905.SH",
            "中证1000": "000852.SH",
            "科创50": "000688.SH",
            "上证50": "000016.SH",
        }
        
        result = {}
        for name, ts_code in indices.items():
            try:
                df = self.pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
                if df is not None and len(df) > 0:
                    df['trade_date'] = pd.to_datetime(df['trade_date'])
                    df = df.sort_values('trade_date')
                    result[name] = df
                    df.to_csv(f"{self.data_dir}/index_{name}.csv", index=False, encoding='utf-8-sig')
                    print(f"✓ 获取{name}数据: {len(df)}条")
                time.sleep(0.2)  # 避免请求过快
            except Exception as e:
                print(f"✗ 获取{name}失败: {e}")
                
        return result
    
    def get_daily_market_stats(self, start_date="20210101", end_date="20250228"):
        """
        获取每日市场情绪统计数据
        包含：涨跌家数、涨跌停家数等
        """
        # 获取每日涨跌停统计
        all_data = []
        
        # 获取交易日历
        cal_df = self.pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date)
        trade_dates = cal_df[cal_df['is_open'] == 1]['cal_date'].tolist()
        
        print(f"开始采集{len(trade_dates)}个交易日的市场统计...")
        
        for i, date in enumerate(trade_dates):
            try:
                # 获取每日指标（包含涨跌家数等）
                df = self.pro.daily_info(trade_date=date)
                if df is not None and len(df) > 0:
                    all_data.append(df)
                
                if (i + 1) % 50 == 0:
                    print(f"  进度: {i+1}/{len(trade_dates)}")
                time.sleep(0.1)
            except Exception as e:
                # 某些日期可能没有数据
                pass
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            combined.to_csv(f"{self.data_dir}/daily_market_stats.csv", index=False, encoding='utf-8-sig')
            print(f"✓ 获取每日市场统计: {len(combined)}条")
            return combined
        return None
    
    def get_limit_up_stats(self, start_date="20210101", end_date="20250228"):
        """获取涨跌停统计数据"""
        # 获取交易日历
        cal_df = self.pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date)
        trade_dates = cal_df[cal_df['is_open'] == 1]['cal_date'].tolist()
        
        all_data = []
        print(f"开始采集{len(trade_dates)}个交易日的涨跌停数据...")
        
        for i, date in enumerate(trade_dates):
            try:
                # 获取涨跌停数据
                df = self.pro.limit_list(trade_date=date)
                if df is not None and len(df) > 0:
                    df['trade_date'] = date
                    all_data.append(df)
                
                if (i + 1) % 100 == 0:
                    print(f"  进度: {i+1}/{len(trade_dates)}")
                time.sleep(0.05)
            except Exception as e:
                pass
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            combined.to_csv(f"{self.data_dir}/limit_up_stats.csv", index=False, encoding='utf-8-sig')
            print(f"✓ 获取涨跌停数据: {len(combined)}条")
            return combined
        return None
    
    def get_top_list(self, start_date="20210101", end_date="20250228"):
        """获取龙虎榜数据（量化席位监控）"""
        cal_df = self.pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date)
        trade_dates = cal_df[cal_df['is_open'] == 1]['cal_date'].tolist()
        
        all_data = []
        print(f"开始采集{len(trade_dates)}个交易日的龙虎榜数据...")
        
        for i, date in enumerate(trade_dates):
            try:
                df = self.pro.top_list(trade_date=date)
                if df is not None and len(df) > 0:
                    all_data.append(df)
                
                if (i + 1) % 100 == 0:
                    print(f"  进度: {i+1}/{len(trade_dates)}")
                time.sleep(0.05)
            except Exception as e:
                pass
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            combined.to_csv(f"{self.data_dir}/top_list.csv", index=False, encoding='utf-8-sig')
            print(f"✓ 获取龙虎榜数据: {len(combined)}条")
            return combined
        return None
    
    def get_top_inst(self, start_date="20210101", end_date="20250228"):
        """获取龙虎榜机构交易数据"""
        cal_df = self.pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date)
        trade_dates = cal_df[cal_df['is_open'] == 1]['cal_date'].tolist()
        
        all_data = []
        print(f"开始采集{len(trade_dates)}个交易日的机构交易数据...")
        
        for i, date in enumerate(trade_dates):
            try:
                df = self.pro.top_inst(trade_date=date)
                if df is not None and len(df) > 0:
                    all_data.append(df)
                
                if (i + 1) % 100 == 0:
                    print(f"  进度: {i+1}/{len(trade_dates)}")
                time.sleep(0.05)
            except Exception as e:
                pass
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            combined.to_csv(f"{self.data_dir}/top_inst.csv", index=False, encoding='utf-8-sig')
            print(f"✓ 获取机构交易数据: {len(combined)}条")
            return combined
        return None
    
    def get_concept_list(self):
        """获取概念板块列表"""
        df = self.pro.concept()
        df.to_csv(f"{self.data_dir}/concept_list.csv", index=False, encoding='utf-8-sig')
        print(f"✓ 获取概念板块列表: {len(df)}个")
        return df
    
    def get_industry_list(self):
        """获取行业分类"""
        df = self.pro.index_classify(level='L1', src='SW2021')
        df.to_csv(f"{self.data_dir}/industry_list.csv", index=False, encoding='utf-8-sig')
        print(f"✓ 获取行业分类: {len(df)}个")
        return df
    
    def get_macro_economy(self):
        """获取宏观经济数据"""
        macro_data = {}
        
        # GDP数据
        try:
            df = self.pro.gdp()
            macro_data['gdp'] = df
            df.to_csv(f"{self.data_dir}/macro_gdp.csv", index=False, encoding='utf-8-sig')
            print(f"✓ 获取GDP数据: {len(df)}条")
        except Exception as e:
            print(f"✗ 获取GDP数据失败: {e}")
        
        # CPI数据
        try:
            df = self.pro.cpi()
            macro_data['cpi'] = df
            df.to_csv(f"{self.data_dir}/macro_cpi.csv", index=False, encoding='utf-8-sig')
            print(f"✓ 获取CPI数据: {len(df)}条")
        except Exception as e:
            print(f"✗ 获取CPI数据失败: {e}")
        
        # 货币供应量
        try:
            df = self.pro.money_supply(start_m="202101", end_m="202512")
            macro_data['money_supply'] = df
            df.to_csv(f"{self.data_dir}/macro_money_supply.csv", index=False, encoding='utf-8-sig')
            print(f"✓ 获取货币供应量数据: {len(df)}条")
        except Exception as e:
            print(f"✗ 获取货币供应量数据失败: {e}")
        
        # 社会融资规模
        try:
            df = self.pro.sf_month(start_m="202101", end_m="202512")
            macro_data['social_finance'] = df
            df.to_csv(f"{self.data_dir}/macro_social_finance.csv", index=False, encoding='utf-8-sig')
            print(f"✓ 获取社融数据: {len(df)}条")
        except Exception as e:
            print(f"✗ 获取社融数据失败: {e}")
        
        return macro_data


class BacktestAnalyzer:
    """回测分析器"""
    
    def __init__(self, data_dir="tushare_data"):
        self.data_dir = data_dir
        
    def load_data(self):
        """加载数据"""
        data = {}
        
        # 加载指数数据
        indices = ["上证指数", "深证成指", "创业板指", "沪深300", "中证1000"]
        for idx in indices:
            try:
                df = pd.read_csv(f"{self.data_dir}/index_{idx}.csv")
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                data[idx] = df
            except:
                pass
        
        # 加载市场统计数据
        try:
            data['market_stats'] = pd.read_csv(f"{self.data_dir}/daily_market_stats.csv")
        except:
            pass
        
        # 加载涨跌停数据
        try:
            data['limit_up'] = pd.read_csv(f"{self.data_dir}/limit_up_stats.csv")
        except:
            pass
            
        return data
    
    def calculate_four_seasons_signals(self, index_name="上证指数"):
        """
        计算四季战法信号
        
        春播信号：强势股补跌、跌停家数激增、恐慌情绪
        夏长信号：主线明确、涨停家数多、连板高度打开
        秋收信号：板块高潮、跟风补涨、放量滞涨
        冬藏信号：高位股杀跌、题材半日游、炸板率高
        """
        df = pd.read_csv(f"{self.data_dir}/index_{index_name}.csv")
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df.sort_values('trade_date')
        
        # 计算技术指标
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma60'] = df['close'].rolling(60).mean()
        df['vol_ma5'] = df['vol'].rolling(5).mean()
        df['vol_ratio'] = df['vol'] / df['vol_ma5']
        
        # 计算涨跌幅
        df['change_pct'] = df['close'].pct_change() * 100
        df['high_low_pct'] = (df['high'] - df['low']) / df['close'] * 100
        
        # 四季信号标记
        df['season'] = '冬藏'  # 默认冬藏
        
        # 春播信号识别
        # 1. 指数从高点回调超过5%
        df['high_20'] = df['high'].rolling(20).max()
        df['drawdown_from_high'] = (df['close'] - df['high_20']) / df['high_20'] * 100
        
        # 2. 放量下跌（成交量>1.5倍5日均量）
        df['volume_spike'] = df['vol_ratio'] > 1.5
        
        # 春播条件：深度回调+放量+超跌
        spring_condition = (
            (df['drawdown_from_high'] < -5) &  # 从高点回撤超5%
            (df['volume_spike']) &  # 放量
            (df['close'] < df['ma5']) &  # 跌破短期均线
            (df['change_pct'] < -1)  # 当日下跌
        )
        
        # 夏长条件：趋势向上+量价齐升
        summer_condition = (
            (df['close'] > df['ma5']) &
            (df['ma5'] > df['ma20']) &
            (df['vol_ratio'] > 1.2) &
            (df['change_pct'] > 0.5)
        )
        
        # 秋收条件：高位+放量滞涨
        autumn_condition = (
            (df['close'] > df['ma5'] * 1.05) &  # 偏离均线较大
            (df['vol_ratio'] > 1.5) &
            (df['change_pct'].abs() < 1)  # 波动小但放量
        )
        
        # 应用季节标记
        df.loc[spring_condition, 'season'] = '春播'
        df.loc[summer_condition, 'season'] = '夏长'
        df.loc[autumn_condition, 'season'] = '秋收'
        
        return df
    
    def calculate_win_rate(self, signals_df, holding_days=20):
        """计算各季节策略胜率"""
        results = {
            '春播': {'total': 0, 'win': 0, 'returns': []},
            '夏长': {'total': 0, 'win': 0, 'returns': []},
            '秋收': {'total': 0, 'win': 0, 'returns': []},
            '冬藏': {'total': 0, 'win': 0, 'returns': []}
        }
        
        df = signals_df.copy()
        
        for i in range(len(df) - holding_days):
            current_season = df.iloc[i]['season']
            entry_price = df.iloc[i]['close']
            exit_price = df.iloc[i + holding_days]['close']
            
            return_pct = (exit_price - entry_price) / entry_price * 100
            
            results[current_season]['total'] += 1
            results[current_season]['returns'].append(return_pct)
            if return_pct > 0:
                results[current_season]['win'] += 1
        
        # 计算胜率
        for season in results:
            if results[season]['total'] > 0:
                results[season]['win_rate'] = results[season]['win'] / results[season]['total'] * 100
                results[season]['avg_return'] = np.mean(results[season]['returns'])
                results[season]['max_return'] = max(results[season]['returns'])
                results[season]['min_return'] = min(results[season]['returns'])
        
        return results


def main():
    """主函数"""
    print("="*70)
    print("Tushare Pro API 数据采集 - 彪哥战法v4.0进化")
    print("="*70)
    
    # 初始化采集器
    collector = TushareDataCollector(data_dir="tushare_backtest/data")
    
    # 获取数据
    print("\n【阶段1】采集基础数据...")
    print("-"*70)
    collector.get_trade_calendar("20210101", "20250228")
    collector.get_stock_basic()
    
    print("\n【阶段2】采集指数数据...")
    print("-"*70)
    collector.get_index_daily("20210101", "20250228")
    
    print("\n【阶段3】采集宏观经济数据...")
    print("-"*70)
    collector.get_macro_economy()
    
    print("\n【阶段4】采集概念和行业分类...")
    print("-"*70)
    collector.get_concept_list()
    collector.get_industry_list()
    
    # 注意：以下接口可能积分消耗较大，根据积分情况选择性调用
    # print("\n【阶段5】采集每日市场统计...")
    # print("-"*70)
    # collector.get_daily_market_stats("20210101", "20250228")
    
    # print("\n【阶段6】采集涨跌停数据...")
    # print("-"*70)
    # collector.get_limit_up_stats("20210101", "20250228")
    
    # print("\n【阶段7】采集龙虎榜数据...")
    # print("-"*70)
    # collector.get_top_list("20210101", "20250228")
    # collector.get_top_inst("20210101", "20250228")
    
    print("\n" + "="*70)
    print("✓ 数据采集完成！")
    print("="*70)
    print(f"数据保存位置: {collector.data_dir}/")


if __name__ == "__main__":
    main()
