#!/usr/bin/env python3
"""
彪哥战法 - 增强版全市场分析器
支持：AKShare实时数据 + 本地缓存 + QVeris(待接入)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from biaoge_data_manager import BiaogeDataManager
from datetime import datetime
import pandas as pd


def analyze_market_with_cache():
    """
    使用缓存机制分析市场
    优先获取实时数据，失败时使用缓存
    """
    print("=" * 60)
    print("彪哥战法 - 全市场分析（增强版）")
    print("=" * 60)
    
    dm = BiaogeDataManager()
    
    # 获取数据（自动处理缓存）
    df = dm.get_full_market_data()
    
    if df is None:
        print("\n❌ 无法获取数据（AKShare连接失败且无缓存）")
        print("\n建议：")
        print("1. 检查网络连接")
        print("2. 等待QVeris数据源接入")
        print("3. 稍后重试")
        return None
    
    # 标准化列名（处理AKShare和缓存数据的差异）
    df = standardize_dataframe(df)
    
    # 市场统计
    analysis = calculate_market_stats(df)
    
    # 龙头候选
    dragon_candidates = find_dragon_candidates(df)
    
    # 中军候选
    zhongjun_candidates = find_zhongjun_candidates(df)
    
    # 输出报告
    print_report(analysis, dragon_candidates, zhongjun_candidates)
    
    return analysis


def standardize_dataframe(df):
    """标准化DataFrame列名"""
    # AKShare列名 -> 标准列名
    column_mapping = {
        '代码': 'code',
        '名称': 'name',
        '最新价': 'close',
        '涨跌幅': 'change_pct',
        '换手率': 'turnover',
        '成交额': 'amount',
        '总市值': 'market_cap',
        '流通市值': 'float_market_cap',
        '成交量': 'volume',
        '最高': 'high',
        '最低': 'low',
        '今开': 'open',
        '昨收': 'pre_close',
    }
    
    for old, new in column_mapping.items():
        if old in df.columns:
            df[new] = df[old]
    
    return df


def calculate_market_stats(df):
    """计算市场统计指标"""
    total = len(df)
    
    # 确定使用哪个涨跌幅列
    change_col = 'change_pct' if 'change_pct' in df.columns else '涨跌幅'
    
    up = len(df[df[change_col] > 0])
    down = len(df[df[change_col] < 0])
    zt = len(df[df[change_col] >= 9.5])
    dt = len(df[df[change_col] <= -9.5])
    
    # 换手率
    turnover_col = 'turnover' if 'turnover' in df.columns else '换手率'
    high_turnover = len(df[df[turnover_col] > 10]) if turnover_col in df.columns else 0
    avg_turnover = df[turnover_col].mean() if turnover_col in df.columns else 0
    
    analysis = {
        "统计时间": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "总股票数": total,
        "上涨家数": up,
        "下跌家数": down,
        "涨停家数": zt,
        "跌停家数": dt,
        "高换手家数": high_turnover,
        "平均换手率": f"{avg_turnover:.2f}%" if avg_turnover else "N/A",
        "涨跌比": f"{up/down:.2f}" if down > 0 else "N/A"
    }
    
    # 季节判断
    analysis["季节判断"] = judge_season(zt, dt, high_turnover)
    
    return analysis


def judge_season(zt, dt, high_turnover):
    """季节判断（量化战法v3.0）"""
    if dt > 30:
        return "冬藏→春播（恐慌盘）"
    elif zt > 80 and high_turnover > 200:
        return "夏长（活跃期）"
    elif zt < 40 and high_turnover < 100:
        return "冬藏（冰点）"
    elif 40 <= zt <= 80:
        return "秋收/震荡期"
    else:
        return "观察期"


def find_dragon_candidates(df, top_n=5):
    """识别龙头候选"""
    change_col = 'change_pct' if 'change_pct' in df.columns else '涨跌幅'
    turnover_col = 'turnover' if 'turnover' in df.columns else '换手率'
    
    # 条件：涨停 + 高换手
    candidates = df[
        (df[change_col] >= 9.5) & 
        (df[turnover_col] >= 5) & 
        (df[turnover_col] <= 20)
    ].copy()
    
    if len(candidates) == 0:
        return []
    
    # 排序：涨幅 > 换手
    candidates['score'] = candidates[change_col] * 0.6 + candidates[turnover_col] * 0.4
    candidates = candidates.sort_values('score', ascending=False)
    
    return candidates.head(top_n)


def find_zhongjun_candidates(df, top_n=5):
    """识别中军候选"""
    change_col = 'change_pct' if 'change_pct' in df.columns else '涨跌幅'
    turnover_col = 'turnover' if 'turnover' in df.columns else '换手率'
    market_cap_col = 'market_cap' if 'market_cap' in df.columns else '总市值'
    
    # 条件：大市值 + 稳健上涨 + 成交活跃
    candidates = df[
        (df[change_col] >= 3) & 
        (df[change_col] <= 7) &
        (df[turnover_col] >= 2)
    ].copy()
    
    if len(candidates) == 0:
        return []
    
    # 优先大市值
    candidates = candidates.sort_values(market_cap_col, ascending=False)
    
    return candidates.head(top_n)


def print_report(analysis, dragon_candidates, zhongjun_candidates):
    """打印分析报告"""
    print("\n" + "=" * 60)
    print("【市场概况】")
    print("=" * 60)
    for key, value in analysis.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 60)
    print("【🔥 龙头候选 TOP5】")
    print("=" * 60)
    if len(dragon_candidates) > 0:
        for i, (_, row) in enumerate(dragon_candidates.iterrows(), 1):
            code = row.get('code', row.get('代码', 'N/A'))
            name = row.get('name', row.get('名称', 'N/A'))
            change = row.get('change_pct', row.get('涨跌幅', 0))
            turnover = row.get('turnover', row.get('换手率', 0))
            print(f"{i}. {name} ({code})")
            print(f"   涨幅: {change:+.2f}% | 换手: {turnover:.2f}%")
    else:
        print("暂无符合条件的龙头候选")
    
    print("\n" + "=" * 60)
    print("【⚓ 中军候选 TOP5】")
    print("=" * 60)
    if len(zhongjun_candidates) > 0:
        for i, (_, row) in enumerate(zhongjun_candidates.iterrows(), 1):
            code = row.get('code', row.get('代码', 'N/A'))
            name = row.get('name', row.get('名称', 'N/A'))
            change = row.get('change_pct', row.get('涨跌幅', 0))
            market_cap = row.get('market_cap', row.get('总市值', 0))
            print(f"{i}. {name} ({code})")
            print(f"   涨幅: {change:+.2f}% | 市值: {market_cap/1e8:.0f}亿")
    else:
        print("暂无符合条件的中军候选")
    
    print("\n" + "=" * 60)
    print("【🎯 战法判断】")
    print("=" * 60)
    print(f"当前季节: {analysis['季节判断']}")
    print(f"策略: 根据季节执行相应操作")
    print(f"关注: 涨停{analysis['涨停家数']}家 / 跌停{analysis['跌停家数']}家")


if __name__ == "__main__":
    analyze_market_with_cache()
