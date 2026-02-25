#!/usr/bin/env python3
"""
庄稼人战法 - 完整回测引擎 v2.0
基于四季轮回框架的五年回测（2021-2025）
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

class Season(Enum):
    """四季枚举"""
    SPRING = "春播"      # 建仓期 - 恐慌后布局
    SUMMER = "夏长"      # 持仓期 - 主升浪
    AUTUMN = "秋收"      # 兑现期 - 高潮后减仓
    WINTER = "冬藏"      # 空仓期 - 规避风险
    UNKNOWN = "未知"

@dataclass
class SeasonSignal:
    """季节判断信号"""
    date: str
    season: Season
    confidence: float
    signals: Dict
    
@dataclass
class BacktestRecord:
    """回测记录"""
    date: str
    season_judgment: str
    judgment_basis: Dict
    confidence: float
    
    # 市场数据
    index_close: float
    index_change_pct: float
    volume: float
    
    # 后续涨跌
    return_5d: float
    return_10d: float
    return_20d: float
    
    # 评估
    is_correct: bool
    pnl_ratio: float
    max_drawdown_20d: float

@dataclass
class FailureCase:
    """失效案例"""
    date: str
    expected_season: str
    actual_outcome: str
    failure_type: str
    description: str
    lessons: str

class ZhuangjiarenBacktester:
    """庄稼人战法回测引擎 v2.0"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.records: List[BacktestRecord] = []
        self.failure_cases: List[FailureCase] = []
        self.index_data = {}
        self.key_dates = {}
        self.daily_stats = None
        
        # 优化后的参数阈值
        self.thresholds = {
            'panic_drop_pct': 2.0,          # 单日跌幅阈值
            'panic_5d_drop': 5.0,           # 5日累计跌幅阈值
            'panic_volume_ratio': 1.3,      # 恐慌时量能放大倍数
            'exhaustion_10d_rise': 8.0,     # 10日涨幅阈值（秋收）
            'exhaustion_20d_rise': 15.0,    # 20日涨幅阈值
            'exhaustion_deviation': 8.0,    # 偏离20日线阈值
            'winter_ma_alignment': True,    # 冬藏是否需要均线空头排列
            'spring_volume_confirm': 1.2,   # 春播确认量价比
        }
        
    def load_data(self):
        """加载数据"""
        print("="*60)
        print("【数据加载】")
        print("="*60)
        
        # 加载指数数据
        indices = ["上证指数", "深证成指", "创业板指", "沪深300", "中证1000"]
        for name in indices:
            try:
                df = pd.read_csv(f"{self.data_dir}/index_{name}.csv")
                df['日期'] = pd.to_datetime(df['日期'])
                self.index_data[name] = df
                print(f"✓ 加载{name}: {len(df)}条")
            except Exception as e:
                print(f"✗ 加载{name}失败: {e}")
        
        # 加载关键日期
        try:
            with open(f"{self.data_dir}/key_dates.json", 'r') as f:
                self.key_dates = json.load(f)
            print(f"✓ 加载关键日期: {len(self.key_dates)}个")
        except:
            print("✗ 关键日期加载失败")
        
        # 加载每日市场统计
        try:
            self.daily_stats = pd.read_csv(f"{self.data_dir}/daily_market_stats.csv")
            print(f"✓ 加载每日统计: {len(self.daily_stats)}条")
        except:
            print("✗ 每日统计加载失败")
            
        print(f"\n✓ 数据加载完成\n")
    
    def calculate_ma(self, df, days):
        """计算均线"""
        return df['收盘'].rolling(window=days).mean()
    
    def calculate_atr(self, df, days=14):
        """计算ATR（平均真实波幅）"""
        high_low = df['最高'] - df['最低']
        high_close = np.abs(df['最高'] - df['收盘'].shift())
        low_close = np.abs(df['最低'] - df['收盘'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(window=days).mean()
    
    def calculate_rsi(self, df, period=14):
        """计算RSI指标"""
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def detect_panic(self, df, idx):
        """
        检测恐慌信号 - 春播的关键判断
        返回: (是否恐慌, 恐慌信号详情)
        """
        if idx < 10:
            return False, {}
        
        current = df.iloc[idx]
        prev = df.iloc[idx-1]
        
        signals = {}
        
        # 1. 单日大阴线
        drop_pct = (prev['收盘'] - current['收盘']) / prev['收盘'] * 100
        signals['单日跌幅%'] = round(drop_pct, 2)
        signals['大阴线'] = drop_pct > self.thresholds['panic_drop_pct']
        
        # 2. 连续下跌天数和幅度
        returns_5d = (current['收盘'] - df.iloc[idx-5]['收盘']) / df.iloc[idx-5]['收盘'] * 100
        returns_10d = (current['收盘'] - df.iloc[idx-10]['收盘']) / df.iloc[idx-10]['收盘'] * 100
        signals['5日跌幅%'] = round(returns_5d, 2)
        signals['10日跌幅%'] = round(returns_10d, 2)
        signals['连续下跌'] = returns_5d < -self.thresholds['panic_5d_drop']
        
        # 3. 成交量分析
        avg_volume_20 = df['成交量'].rolling(20).mean().iloc[idx]
        volume_ratio = current['成交量'] / avg_volume_20 if avg_volume_20 > 0 else 1
        signals['量能比'] = round(volume_ratio, 2)
        signals['放量杀跌'] = volume_ratio > self.thresholds['panic_volume_ratio']
        
        # 4. 与均线关系
        ma20 = self.calculate_ma(df, 20).iloc[idx]
        ma60 = self.calculate_ma(df, 60).iloc[idx]
        signals['价格与60日线%'] = round((current['收盘'] - ma60) / ma60 * 100, 2)
        signals['跌破60日线'] = current['收盘'] < ma60
        
        # 5. RSI超卖
        rsi = self.calculate_rsi(df).iloc[idx]
        signals['RSI'] = round(rsi, 2)
        signals['RSI超卖'] = rsi < 30
        
        # 恐慌条件综合判断（满足3项以上为恐慌）
        panic_indicators = [
            signals['大阴线'],
            signals['连续下跌'],
            signals['放量杀跌'],
            signals['跌破60日线'],
            signals['RSI超卖']
        ]
        panic_score = sum(panic_indicators)
        is_panic = panic_score >= 3
        
        signals['恐慌评分'] = f"{panic_score}/5"
        signals['恐慌确认'] = is_panic
        
        return is_panic, signals
    
    def detect_exhaustion(self, df, idx):
        """
        检测高潮/力竭信号 - 秋收的关键判断
        返回: (是否高潮, 高潮信号详情)
        """
        if idx < 30:
            return False, {}
        
        current = df.iloc[idx]
        
        signals = {}
        
        # 1. 短期涨幅
        returns_5d = (current['收盘'] - df.iloc[idx-5]['收盘']) / df.iloc[idx-5]['收盘'] * 100
        returns_10d = (current['收盘'] - df.iloc[idx-10]['收盘']) / df.iloc[idx-10]['收盘'] * 100
        returns_20d = (current['收盘'] - df.iloc[idx-20]['收盘']) / df.iloc[idx-20]['收盘'] * 100
        
        signals['5日涨幅%'] = round(returns_5d, 2)
        signals['10日涨幅%'] = round(returns_10d, 2)
        signals['20日涨幅%'] = round(returns_20d, 2)
        signals['短期大涨'] = returns_10d > self.thresholds['exhaustion_10d_rise']
        signals['中期大涨'] = returns_20d > self.thresholds['exhaustion_20d_rise']
        
        # 2. 偏离均线
        ma5 = self.calculate_ma(df, 5).iloc[idx]
        ma10 = self.calculate_ma(df, 10).iloc[idx]
        ma20 = self.calculate_ma(df, 20).iloc[idx]
        
        deviation_5 = (current['收盘'] - ma5) / ma5 * 100
        deviation_20 = (current['收盘'] - ma20) / ma20 * 100
        
        signals['偏离5日线%'] = round(deviation_5, 2)
        signals['偏离20日线%'] = round(deviation_20, 2)
        signals['严重偏离均线'] = deviation_20 > self.thresholds['exhaustion_deviation']
        
        # 3. 量价背离（缩量上涨）
        avg_volume_5 = df['成交量'].iloc[idx-5:idx].mean()
        avg_volume_20 = df['成交量'].iloc[idx-20:idx].mean()
        current_volume = current['成交量']
        
        signals['5日均量'] = int(avg_volume_5)
        signals['20日均量'] = int(avg_volume_20)
        signals['缩量上涨'] = current_volume < avg_volume_5 * 0.9 and returns_5d > 3
        
        # 4. RSI超买
        rsi = self.calculate_rsi(df).iloc[idx]
        signals['RSI'] = round(rsi, 2)
        signals['RSI超买'] = rsi > 70
        
        # 高潮条件综合判断
        exhaustion_indicators = [
            signals['短期大涨'],
            signals['中期大涨'],
            signals['严重偏离均线'],
            signals['缩量上涨'],
            signals['RSI超买']
        ]
        exhaustion_score = sum(exhaustion_indicators)
        is_exhaustion = exhaustion_score >= 3
        
        signals['高潮评分'] = f"{exhaustion_score}/5"
        signals['高潮确认'] = is_exhaustion
        
        return is_exhaustion, signals
    
    def detect_strong_stocks_sell_off(self, df, idx):
        """
        检测强势股补跌 - 春播前的必要条件
        """
        if idx < 20:
            return False, {}
        
        # 这里简化处理，实际应该分析前期强势股
        current = df.iloc[idx]
        prev_high = df['最高'].rolling(20).max().iloc[idx-1]
        
        signals = {
            '前期高点': round(prev_high, 2),
            '当前价格': round(current['收盘'], 2),
            '高点回撤%': round((prev_high - current['收盘']) / prev_high * 100, 2),
            '强势股补跌': (prev_high - current['收盘']) / prev_high > 0.15
        }
        
        return signals['强势股补跌'], signals
    
    def judge_season(self, df, idx):
        """
        判断当前季节 - 核心逻辑
        """
        if idx < 60:
            return Season.UNKNOWN, 0.5, {"原因": "数据不足，需要60日数据"}
        
        date_str = df.iloc[idx]['日期'].strftime('%Y%m%d')
        current = df.iloc[idx]
        
        # 计算各项指标
        ma5 = self.calculate_ma(df, 5).iloc[idx]
        ma10 = self.calculate_ma(df, 10).iloc[idx]
        ma20 = self.calculate_ma(df, 20).iloc[idx]
        ma60 = self.calculate_ma(df, 60).iloc[idx]
        
        # 趋势判断
        trend_up = ma5 > ma10 > ma20 > ma60
        trend_down = ma5 < ma10 < ma20 < ma60
        trend_mixed = not trend_up and not trend_down
        
        # 检测恐慌（春播信号）
        is_panic, panic_signals = self.detect_panic(df, idx)
        
        # 检测高潮（秋收信号）
        is_exhaustion, exhaust_signals = self.detect_exhaustion(df, idx)
        
        # 检测强势股补跌
        is_sell_off, sell_off_signals = self.detect_strong_stocks_sell_off(df, idx)
        
        signals = {
            "日期": date_str,
            "收盘价": round(current['收盘'], 2),
            "涨跌幅%": round((current['收盘'] - df.iloc[idx-1]['收盘']) / df.iloc[idx-1]['收盘'] * 100, 2),
            "趋势向上": trend_up,
            "趋势向下": trend_down,
            "趋势震荡": trend_mixed,
            "均线多头排列": trend_up,
            "均线空头排列": trend_down,
            "恐慌信号": is_panic,
            "恐慌详情": panic_signals,
            "高潮信号": is_exhaustion,
            "高潮详情": exhaust_signals,
            "强势股补跌": is_sell_off,
            "补跌详情": sell_off_signals,
        }
        
        # ==================== 季节判断逻辑 ====================
        
        season = Season.UNKNOWN
        confidence = 0.5
        logic = ""
        
        # 1. 春播判断（最重要）
        # 条件：恐慌杀跌 + 强势股补跌完成 + 位于重要均线下方
        if is_panic and is_sell_off and current['收盘'] < ma60:
            season = Season.SPRING
            panic_score_str = panic_signals.get('恐慌评分', '0/5')
            panic_score = int(panic_score_str.split('/')[0]) if '/' in str(panic_score_str) else 3
            confidence = 0.70 + (panic_score / 20)
            logic = "恐慌杀跌+强势股补跌完成，春播信号强烈"
        elif is_panic and current['收盘'] < ma20:
            season = Season.SPRING
            confidence = 0.60
            logic = "恐慌杀跌出现，疑似春播"
        
        # 2. 秋收判断
        # 条件：高潮信号 + 趋势向上（在上涨后）
        elif is_exhaustion and trend_up:
            season = Season.AUTUMN
            exhaust_score_str = exhaust_signals.get('高潮评分', '0/5')
            exhaust_score = int(exhaust_score_str.split('/')[0]) if '/' in str(exhaust_score_str) else 3
            confidence = 0.65 + (exhaust_score / 20)
            logic = "高潮一致，秋收兑现"
        elif is_exhaustion:
            season = Season.AUTUMN
            confidence = 0.55
            logic = "疑似高潮，谨慎秋收"
        
        # 3. 夏长判断
        # 条件：趋势向上 + 无高潮信号 + 价格在均线上方
        elif trend_up and not is_exhaustion and current['收盘'] > ma20:
            season = Season.SUMMER
            confidence = 0.65
            logic = "趋势向上，夏长持股"
        elif trend_mixed and current['收盘'] > ma20 and not is_exhaustion:
            season = Season.SUMMER
            confidence = 0.55
            logic = "震荡上行，疑似夏长"
        
        # 4. 冬藏判断
        # 条件：趋势向下 + 无恐慌信号（还没跌透）
        elif trend_down and not is_panic:
            season = Season.WINTER
            confidence = 0.70
            logic = "趋势向下，冬藏观望"
        elif current['收盘'] < ma60 and not is_panic:
            season = Season.WINTER
            confidence = 0.55
            logic = "弱势震荡，疑似冬藏"
        
        else:
            logic = "信号混杂，季节不明"
        
        signals['判断逻辑'] = logic
        signals['置信度'] = round(confidence, 2)
        
        return season, confidence, signals
    
    def calculate_forward_returns(self, df, idx, days_list=[5, 10, 20]):
        """计算未来N日收益和最大回撤"""
        returns = {}
        max_dd = 0
        current_price = df.iloc[idx]['收盘']
        
        for days in days_list:
            if idx + days < len(df):
                future_price = df.iloc[idx + days]['收盘']
                ret = (future_price - current_price) / current_price * 100
                returns[f"{days}d"] = round(ret, 2)
                
                # 计算最大回撤
                if days == 20:
                    prices = df.iloc[idx:idx+days]['收盘'].values
                    peak = current_price
                    for p in prices:
                        if p > peak:
                            peak = p
                        dd = (peak - p) / peak * 100
                        if dd > max_dd:
                            max_dd = dd
            else:
                returns[f"{days}d"] = 0
        
        returns['max_dd_20d'] = round(max_dd, 2)
        return returns
    
    def evaluate_judgment(self, season, fw_returns):
        """
        评估季节判断是否正确
        """
        is_correct = False
        
        if season == Season.SPRING:
            # 春播正确：后续5日上涨或20日整体上涨
            if fw_returns.get('5d', 0) > 0 or fw_returns.get('20d', 0) > 3:
                is_correct = True
        elif season == Season.AUTUMN:
            # 秋收正确：后续5日下跌或开始震荡
            if fw_returns.get('5d', 0) < 2 or fw_returns.get('10d', 0) < 5:
                is_correct = True
        elif season == Season.SUMMER:
            # 夏长正确：后续继续上涨
            if fw_returns.get('10d', 0) > 0:
                is_correct = True
        elif season == Season.WINTER:
            # 冬藏正确：后续下跌或震荡
            if fw_returns.get('10d', 0) < 5:
                is_correct = True
        
        return is_correct
    
    def run_backtest(self, index_name="上证指数"):
        """执行回测"""
        if index_name not in self.index_data:
            print(f"错误：没有{index_name}的数据")
            return
        
        df = self.index_data[index_name]
        print(f"\n开始回测 {index_name}，共{len(df)}个交易日")
        print("="*60)
        
        for idx in range(len(df)):
            date = df.iloc[idx]['日期']
            date_str = date.strftime('%Y%m%d')
            
            # 判断季节
            season, confidence, signals = self.judge_season(df, idx)
            
            # 计算未来收益
            fw_returns = self.calculate_forward_returns(df, idx)
            
            # 评估判断正确性
            is_correct = self.evaluate_judgment(season, fw_returns)
            
            # 计算盈亏比（简化）
            if season == Season.SPRING:
                pnl = fw_returns.get('20d', 0)
            elif season == Season.AUTUMN:
                pnl = -fw_returns.get('5d', 0)  # 秋收后应该跌，跌越多表示逃顶越正确
            elif season == Season.SUMMER:
                pnl = fw_returns.get('10d', 0)
            else:
                pnl = 0
            
            current = df.iloc[idx]
            prev = df.iloc[idx-1] if idx > 0 else current
            change_pct = (current['收盘'] - prev['收盘']) / prev['收盘'] * 100 if idx > 0 else 0
            
            record = BacktestRecord(
                date=date_str,
                season_judgment=season.value,
                judgment_basis=signals,
                confidence=confidence,
                index_close=round(current['收盘'], 2),
                index_change_pct=round(change_pct, 2),
                volume=int(current['成交量']),
                return_5d=fw_returns.get('5d', 0),
                return_10d=fw_returns.get('10d', 0),
                return_20d=fw_returns.get('20d', 0),
                is_correct=is_correct,
                pnl_ratio=pnl,
                max_drawdown_20d=fw_returns.get('max_dd_20d', 0)
            )
            
            self.records.append(record)
            
            # 每200天输出进度
            if idx % 200 == 0:
                print(f"  处理进度: {idx}/{len(df)} ({idx/len(df)*100:.1f}%) - {date_str}")
        
        print(f"✓ 回测完成，共{len(self.records)}条记录")
    
    def analyze_failures(self):
        """分析失效案例"""
        print("\n" + "="*60)
        print("【失效案例分析】")
        print("="*60)
        
        df = pd.DataFrame([asdict(r) for r in self.records])
        
        # 1. 假春播案例（判断为春播，但后续大跌）
        spring_failures = df[(df['season_judgment'] == '春播') & (df['return_5d'] < -3)]
        for _, row in spring_failures.head(5).iterrows():
            case = FailureCase(
                date=row['date'],
                expected_season='春播',
                actual_outcome=f"5日跌幅{row['return_5d']}%",
                failure_type='假春播',
                description='恐慌后出现，但仅为下跌中继',
                lessons='强势股补跌可能未完成，或整体趋势仍向下'
            )
            self.failure_cases.append(case)
        
        # 2. 假秋收案例（判断为秋收，但后续继续大涨）
        autumn_failures = df[(df['season_judgment'] == '秋收') & (df['return_10d'] > 8)]
        for _, row in autumn_failures.head(5).iterrows():
            case = FailureCase(
                date=row['date'],
                expected_season='秋收',
                actual_outcome=f"10日涨幅{row['return_10d']}%",
                failure_type='假秋收',
                description='判断为高潮，但实际还有次高潮',
                lessons='主升浪中的调整被误判为秋收，需结合板块强度'
            )
            self.failure_cases.append(case)
        
        print(f"✓ 发现假春播案例: {len(spring_failures)}个")
        print(f"✓ 发现假秋收案例: {len(autumn_failures)}个")
        print(f"✓ 共分析失效案例: {len(self.failure_cases)}个")
    
    def calculate_statistics(self):
        """计算统计指标"""
        df = pd.DataFrame([asdict(r) for r in self.records])
        
        stats = {}
        
        # 基本统计
        total_records = len(df)
        correct_records = len(df[df['is_correct'] == True])
        stats['总体胜率'] = round(correct_records / total_records * 100, 2)
        stats['总交易天数'] = total_records
        
        # 各季节统计
        for season in ['春播', '夏长', '秋收', '冬藏', '未知']:
            season_df = df[df['season_judgment'] == season]
            if len(season_df) > 0:
                season_correct = len(season_df[season_df['is_correct'] == True])
                stats[f'{season}胜率'] = round(season_correct / len(season_df) * 100, 2)
                stats[f'{season}次数'] = len(season_df)
                stats[f'{season}占比%'] = round(len(season_df) / total_records * 100, 2)
                
                # 收益统计
                stats[f'{season}5日平均收益'] = round(season_df['return_5d'].mean(), 2)
                stats[f'{season}10日平均收益'] = round(season_df['return_10d'].mean(), 2)
                stats[f'{season}20日平均收益'] = round(season_df['return_20d'].mean(), 2)
                stats[f'{season}平均最大回撤'] = round(season_df['max_drawdown_20d'].mean(), 2)
        
        # 春播专项统计
        spring_df = df[df['season_judgment'] == '春播']
        if len(spring_df) > 0:
            spring_up = len(spring_df[spring_df['return_5d'] > 0])
            stats['春播后5日上涨概率'] = round(spring_up / len(spring_df) * 100, 2)
            
            spring_up_20d = len(spring_df[spring_df['return_20d'] > 5])
            stats['春播后20日大涨(>5%)概率'] = round(spring_up_20d / len(spring_df) * 100, 2)
            
            # 盈亏比
            wins = spring_df[spring_df['return_20d'] > 0]['return_20d'].mean()
            losses = abs(spring_df[spring_df['return_20d'] < 0]['return_20d'].mean())
            stats['春播盈亏比'] = round(wins / losses, 2) if losses > 0 else 999
        
        # 秋收专项统计
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
        
        # 保存失效案例
        if self.failure_cases:
            failure_df = pd.DataFrame([asdict(c) for c in self.failure_cases])
            failure_df.to_csv(f"{output_dir}/failure_cases.csv", index=False, encoding='utf-8-sig')
        
        print(f"\n✓ 结果已保存到 {output_dir}/")
        return stats
    
    def generate_report(self, output_dir="reports"):
        """生成回测报告"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        stats = self.calculate_statistics()
        
        report = f"""
# 庄稼人战法 - 五年回测报告（2021-2025）

## 一、回测概况

| 指标 | 数值 |
|------|------|
| 回测区间 | 2021-01-01 至 2025-02-23 |
| 总交易天数 | {stats.get('总交易天数', 0)} |
| 总体胜率 | {stats.get('总体胜率', 0)}% |

## 二、四季统计

| 季节 | 出现次数 | 占比 | 胜率 | 5日平均收益 | 10日平均收益 | 20日平均收益 | 平均最大回撤 |
|------|---------|------|------|------------|-------------|-------------|-------------|
| 春播 | {stats.get('春播次数', 0)} | {stats.get('春播占比%', 0)}% | {stats.get('春播胜率', 0)}% | {stats.get('春播5日平均收益', 0)}% | {stats.get('春播10日平均收益', 0)}% | {stats.get('春播20日平均收益', 0)}% | {stats.get('春播平均最大回撤', 0)}% |
| 夏长 | {stats.get('夏长次数', 0)} | {stats.get('夏长占比%', 0)}% | {stats.get('夏长胜率', 0)}% | {stats.get('夏长5日平均收益', 0)}% | {stats.get('夏长10日平均收益', 0)}% | {stats.get('夏长20日平均收益', 0)}% | {stats.get('夏长平均最大回撤', 0)}% |
| 秋收 | {stats.get('秋收次数', 0)} | {stats.get('秋收占比%', 0)}% | {stats.get('秋收胜率', 0)}% | {stats.get('秋收5日平均收益', 0)}% | {stats.get('秋收10日平均收益', 0)}% | {stats.get('秋收20日平均收益', 0)}% | {stats.get('秋收平均最大回撤', 0)}% |
| 冬藏 | {stats.get('冬藏次数', 0)} | {stats.get('冬藏占比%', 0)}% | {stats.get('冬藏胜率', 0)}% | {stats.get('冬藏5日平均收益', 0)}% | {stats.get('冬藏10日平均收益', 0)}% | {stats.get('冬藏20日平均收益', 0)}% | {stats.get('冬藏平均最大回撤', 0)}% |

## 三、关键指标

| 指标 | 数值 |
|------|------|
| 春播后5日上涨概率 | {stats.get('春播后5日上涨概率', 0)}% |
| 春播后20日大涨概率(>5%) | {stats.get('春播后20日大涨(>5%)概率', 0)}% |
| 春播盈亏比 | {stats.get('春播盈亏比', 0)} |
| 秋收后5日下跌概率 | {stats.get('秋收后5日下跌概率', 0)}% |

## 四、当前参数阈值

```json
{json.dumps(self.thresholds, ensure_ascii=False, indent=2)}
```

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        with open(f"{output_dir}/backtest_report.md", "w", encoding='utf-8') as f:
            f.write(report)
        
        print(f"✓ 报告已保存到 {output_dir}/backtest_report.md")
        return report

if __name__ == "__main__":
    bt = ZhuangjiarenBacktester("zhuangjiaren_backtest/data")
    bt.load_data()
    bt.run_backtest("上证指数")
    bt.analyze_failures()
    stats = bt.save_results("zhuangjiaren_backtest/reports")
    bt.generate_report("zhuangjiaren_backtest/reports")
    
    print("\n" + "="*60)
    print("回测统计结果")
    print("="*60)
    for key, value in stats.items():
        print(f"{key}: {value}")
