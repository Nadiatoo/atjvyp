#!/usr/bin/env python3
"""
庄稼人战法 - 核心回测引擎
基于四季轮回框架的逐日回测
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum

class Season(Enum):
    """四季枚举"""
    SPRING = "春播"      # 建仓期
    SUMMER = "夏长"      # 持仓期
    AUTUMN = "秋收"      # 兑现期
    WINTER = "冬藏"      # 空仓期
    UNKNOWN = "未知"

@dataclass
class SeasonSignal:
    """季节判断信号"""
    date: str
    season: Season
    confidence: float  # 置信度 0-1
    signals: Dict[str, any]  # 详细信号
    
@dataclass
class BacktestRecord:
    """回测记录"""
    date: str
    season_judgment: str
    judgment_basis: str
    confidence: float
    main_sector: Optional[str]
    
    # 后续涨跌
    return_5d: float
    return_10d: float
    return_20d: float
    
    # 评估
    is_correct: bool
    pnl_ratio: float

class ZhuangjiarenBacktester:
    """庄稼人战法回测引擎"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.records: List[BacktestRecord] = []
        self.index_data = {}
        self.key_dates = {}
        
    def load_data(self):
        """加载数据"""
        # 加载指数数据
        indices = ["上证指数", "深证成指", "创业板指", "沪深300", "中证1000"]
        for name in indices:
            try:
                df = pd.read_csv(f"{self.data_dir}/index_{name}.csv")
                df['日期'] = pd.to_datetime(df['日期'])
                self.index_data[name] = df
            except:
                pass
        
        # 加载关键日期
        try:
            with open(f"{self.data_dir}/key_dates.json", 'r') as f:
                self.key_dates = json.load(f)
        except:
            pass
            
        print(f"✓ 加载数据完成：{len(self.index_data)}个指数")
    
    def calculate_ma(self, df, days):
        """计算均线"""
        return df['收盘'].rolling(window=days).mean()
    
    def calculate_atr(self, df, days=14):
        """计算ATR（真实波动幅度）"""
        high_low = df['最高'] - df['最低']
        high_close = np.abs(df['最高'] - df['收盘'].shift())
        low_close = np.abs(df['最低'] - df['收盘'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(window=days).mean()
    
    def detect_panic(self, df, idx):
        """检测恐慌信号"""
        if idx < 5:
            return False, {}
        
        current = df.iloc[idx]
        prev = df.iloc[idx-1]
        
        signals = {}
        
        # 大阴线
        drop_pct = (prev['收盘'] - current['收盘']) / prev['收盘'] * 100
        signals['单日跌幅'] = round(drop_pct, 2)
        
        # 连续下跌
        returns_5d = (current['收盘'] - df.iloc[idx-5]['收盘']) / df.iloc[idx-5]['收盘'] * 100
        signals['5日跌幅'] = round(returns_5d, 2)
        
        # 成交量放大
        volume_ratio = current['成交量'] / df['成交量'].rolling(20).mean().iloc[idx]
        signals['量能比'] = round(volume_ratio, 2)
        
        # 恐慌条件
        is_panic = (drop_pct > 2 or returns_5d < -5) and volume_ratio > 1.2
        
        return is_panic, signals
    
    def detect_exhaustion(self, df, idx):
        """检测高潮/力竭信号"""
        if idx < 20:
            return False, {}
        
        current = df.iloc[idx]
        
        signals = {}
        
        # 短期涨幅过大
        returns_10d = (current['收盘'] - df.iloc[idx-10]['收盘']) / df.iloc[idx-10]['收盘'] * 100
        returns_20d = (current['收盘'] - df.iloc[idx-20]['收盘']) / df.iloc[idx-20]['收盘'] * 100
        
        signals['10日涨幅'] = round(returns_10d, 2)
        signals['20日涨幅'] = round(returns_20d, 2)
        
        # 偏离均线
        ma5 = self.calculate_ma(df, 5).iloc[idx]
        ma10 = self.calculate_ma(df, 10).iloc[idx]
        ma20 = self.calculate_ma(df, 20).iloc[idx]
        
        deviation = (current['收盘'] - ma20) / ma20 * 100
        signals['偏离20日线'] = round(deviation, 2)
        
        # 高潮条件
        is_exhaustion = returns_10d > 8 or deviation > 10
        
        return is_exhaustion, signals
    
    def judge_season(self, df, idx):
        """判断当前季节"""
        if idx < 30:
            return Season.UNKNOWN, 0, {"原因": "数据不足"}
        
        date_str = df.iloc[idx]['日期'].strftime('%Y%m%d')
        current = df.iloc[idx]
        
        # 计算各项指标
        ma5 = self.calculate_ma(df, 5).iloc[idx]
        ma10 = self.calculate_ma(df, 10).iloc[idx]
        ma20 = self.calculate_ma(df, 20).iloc[idx]
        ma60 = self.calculate_ma(df, 60).iloc[idx]
        
        # 趋势判断
        trend_up = ma5 > ma10 > ma20
        trend_down = ma5 < ma10 < ma20
        
        # 检测恐慌
        is_panic, panic_signals = self.detect_panic(df, idx)
        
        # 检测高潮
        is_exhaustion, exhaust_signals = self.detect_exhaustion(df, idx)
        
        signals = {
            "趋势向上": trend_up,
            "趋势向下": trend_down,
            "价格与60日线关系": "上方" if current['收盘'] > ma60 else "下方",
            "恐慌信号": is_panic,
            "恐慌详情": panic_signals,
            "高潮信号": is_exhaustion,
            "高潮详情": exhaust_signals,
        }
        
        # 季节判断逻辑
        # 冬藏 -> 春播：强势股补跌完成 + 恐慌盘杀出
        # 春播 -> 夏长：趋势确立 + 站上均线
        # 夏长 -> 秋收：高潮一致 + 大涨
        # 秋收 -> 冬藏：反包失败 + 趋势破坏
        
        season = Season.UNKNOWN
        confidence = 0.5
        
        if is_panic and not trend_up:
            season = Season.SPRING
            confidence = 0.7
            signals['判断逻辑'] = "恐慌杀跌后出现，春播信号"
        elif trend_up and not is_exhaustion:
            season = Season.SUMMER
            confidence = 0.6
            signals['判断逻辑'] = "趋势向上，夏长持股"
        elif is_exhaustion:
            season = Season.AUTUMN
            confidence = 0.6
            signals['判断逻辑'] = "短期涨幅过大，秋收兑现"
        elif trend_down:
            season = Season.WINTER
            confidence = 0.7
            signals['判断逻辑'] = "趋势向下，冬藏观望"
        
        return season, confidence, signals
    
    def calculate_forward_returns(self, df, idx, days_list=[5, 10, 20]):
        """计算未来N日收益"""
        returns = {}
        current_price = df.iloc[idx]['收盘']
        
        for days in days_list:
            if idx + days < len(df):
                future_price = df.iloc[idx + days]['收盘']
                ret = (future_price - current_price) / current_price * 100
                returns[f"{days}d"] = round(ret, 2)
            else:
                returns[f"{days}d"] = None
        
        return returns
    
    def run_backtest(self, index_name="上证指数"):
        """执行回测"""
        if index_name not in self.index_data:
            print(f"错误：没有{index_name}的数据")
            return
        
        df = self.index_data[index_name]
        print(f"\n开始回测 {index_name}，共{len(df)}个交易日")
        
        for idx in range(len(df)):
            date = df.iloc[idx]['日期']
            date_str = date.strftime('%Y%m%d')
            
            # 判断季节
            season, confidence, signals = self.judge_season(df, idx)
            
            # 计算未来收益
            fw_returns = self.calculate_forward_returns(df, idx)
            
            # 判断正确性（简化规则）
            is_correct = False
            if season == Season.SPRING and fw_returns.get('5d', 0) > 0:
                is_correct = True
            elif season == Season.AUTUMN and fw_returns.get('5d', 0) < 0:
                is_correct = True
            elif season in [Season.SUMMER, Season.WINTER]:
                # 夏长冬藏主要看不犯大错
                is_correct = True
            
            record = BacktestRecord(
                date=date_str,
                season_judgment=season.value,
                judgment_basis=json.dumps(signals, ensure_ascii=False),
                confidence=confidence,
                main_sector=None,
                return_5d=fw_returns.get('5d', 0) or 0,
                return_10d=fw_returns.get('10d', 0) or 0,
                return_20d=fw_returns.get('20d', 0) or 0,
                is_correct=is_correct,
                pnl_ratio=0
            )
            
            self.records.append(record)
            
            # 每100天输出进度
            if idx % 100 == 0:
                print(f"  处理进度: {idx}/{len(df)} ({idx/len(df)*100:.1f}%)")
        
        print(f"✓ 回测完成，共{len(self.records)}条记录")
    
    def calculate_statistics(self):
        """计算统计指标"""
        df = pd.DataFrame([asdict(r) for r in self.records])
        
        stats = {}
        
        # 整体胜率
        total_records = len(df)
        correct_records = len(df[df['is_correct'] == True])
        stats['总体胜率'] = round(correct_records / total_records * 100, 2) if total_records > 0 else 0
        
        # 各季节胜率
        for season in ['春播', '夏长', '秋收', '冬藏']:
            season_df = df[df['season_judgment'] == season]
            if len(season_df) > 0:
                season_correct = len(season_df[season_df['is_correct'] == True])
                stats[f'{season}胜率'] = round(season_correct / len(season_df) * 100, 2)
                stats[f'{season}次数'] = len(season_df)
                
                # 平均收益
                stats[f'{season}5日平均收益'] = round(season_df['return_5d'].mean(), 2)
        
        # 春播后上涨概率
        spring_df = df[df['season_judgment'] == '春播']
        if len(spring_df) > 0:
            spring_up = len(spring_df[spring_df['return_5d'] > 0])
            stats['春播后5日上涨概率'] = round(spring_up / len(spring_df) * 100, 2)
        
        # 秋收后下跌概率
        autumn_df = df[df['season_judgment'] == '秋收']
        if len(autumn_df) > 0:
            autumn_down = len(autumn_df[autumn_df['return_5d'] < 0])
            stats['秋收后5日下跌概率'] = round(autumn_down / len(autumn_df) * 100, 2)
        
        return stats
    
    def save_results(self, output_dir="reports"):
        """保存回测结果"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存详细记录
        df = pd.DataFrame([asdict(r) for r in self.records])
        df.to_csv(f"{output_dir}/backtest_records.csv", index=False, encoding='utf-8-sig')
        
        # 保存统计结果
        stats = self.calculate_statistics()
        with open(f"{output_dir}/backtest_stats.json", "w", encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 结果已保存到 {output_dir}/")
        return stats

if __name__ == "__main__":
    bt = ZhuangjiarenBacktester("zhuangjiaren_backtest/data")
    bt.load_data()
    bt.run_backtest("上证指数")
    stats = bt.save_results("zhuangjiaren_backtest/reports")
    
    print("\n" + "="*50)
    print("回测统计结果")
    print("="*50)
    for key, value in stats.items():
        print(f"{key}: {value}")
