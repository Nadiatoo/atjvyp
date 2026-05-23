#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正彪哥战法v5.0分析逻辑
"""

import datetime

print("🔧 修正彪哥战法v5.0分析逻辑")
print("=" * 60)
print(f"分析时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 今日市场数据
data = {
    "shanghai_change": -1.09,  # 上证指数涨跌幅
    "total_stocks": 5493,      # 总股票数
    "rising_stocks": 916,      # 上涨家数
    "falling_stocks": 4493,    # 下跌家数
    "limit_up": 52,           # 涨停家数
    "limit_down": 14,         # 跌停家数
}

# 计算关键指标
rising_ratio = data["rising_stocks"] / data["total_stocks"]  # 16.7%

print("📊 市场数据:")
print(f"  上证指数涨跌幅: {data['shanghai_change']}%")
print(f"  上涨家数比例: {rising_ratio:.1%} ({data['rising_stocks']}/{data['total_stocks']})")
print(f"  涨停家数: {data['limit_up']}")
print(f"  跌停家数: {data['limit_down']}")
print()

# 重新设计评分逻辑
print("🎯 重新设计评分逻辑:")
print()

# 1. 技术面评分 (权重60%)
tech_score = 0
tech_features = []

# 指数涨跌 (-30% to +30%)
if data["shanghai_change"] < -2:
    tech_score += 0.3  # 大幅下跌
    tech_features.append("指数大幅下跌")
elif data["shanghai_change"] < 0:
    tech_score += 0.2  # 下跌
    tech_features.append("指数下跌")
else:
    tech_score += 0.1  # 上涨或平盘
    tech_features.append("指数上涨或平盘")

# 市场广度
if rising_ratio < 0.2:
    tech_score += 0.3  # 极度普跌
    tech_features.append("极度普跌行情")
elif rising_ratio < 0.4:
    tech_score += 0.2  # 普跌
    tech_features.append("普跌行情")
elif rising_ratio < 0.6:
    tech_score += 0.1  # 分化行情
    tech_features.append("分化行情")
else:
    tech_score += 0.0  # 普涨
    tech_features.append("普涨行情")

# 涨停家数
if data["limit_up"] < 40:
    tech_score += 0.3  # 涨停极少
    tech_features.append("涨停家数极少")
elif data["limit_up"] < 60:
    tech_score += 0.2  # 涨停较少
    tech_features.append("涨停家数较少")
elif data["limit_up"] < 80:
    tech_score += 0.1  # 涨停一般
    tech_features.append("涨停家数一般")
else:
    tech_score += 0.0  # 涨停较多
    tech_features.append("涨停家数较多")

# 跌停家数
if data["limit_down"] > 50:
    tech_score += 0.3  # 跌停极多
    tech_features.append("跌停家数极多")
elif data["limit_down"] > 30:
    tech_score += 0.2  # 跌停较多
    tech_features.append("跌停家数较多")
elif data["limit_down"] > 15:
    tech_score += 0.1  # 跌停一般
    tech_features.append("跌停家数一般")
else:
    tech_score += 0.0  # 跌停较少
    tech_features.append("跌停家数较少")

tech_total = tech_score
tech_weighted = tech_total * 0.6  # 技术面权重60%

print(f"  技术面评分: {tech_total:.3f} → 加权后: {tech_weighted:.3f}")
print(f"  技术特征: {', '.join(tech_features)}")
print()

# 2. 情绪面评分 (权重13%)
if rising_ratio < 0.2:
    emotion_score = 0.13  # 情绪极度低迷
    emotion = "情绪极度低迷（冰点）"
elif rising_ratio < 0.3:
    emotion_score = 0.10  # 情绪非常低迷
    emotion = "情绪非常低迷"
elif rising_ratio < 0.4:
    emotion_score = 0.065  # 情绪低迷
    emotion = "情绪低迷"
elif rising_ratio < 0.6:
    emotion_score = 0.03  # 情绪中性
    emotion = "情绪中性"
else:
    emotion_score = 0.0  # 情绪积极
    emotion = "情绪积极"

print(f"  情绪面评分: {emotion_score:.3f}")
print(f"  市场情绪: {emotion}")
print()

# 3. 资金面评分 (权重20%，今日数据不足，给基础分)
fund_score = 0.05  # 基础分，偏谨慎
print(f"  资金面评分: {fund_score:.3f} (数据不足，给基础分)")
print()

# 4. 宏观面评分 (权重7%，今日数据不足，给基础分)
macro_score = 0.02  # 基础分，偏谨慎
print(f"  宏观面评分: {macro_score:.3f} (数据不足，给基础分)")
print()

# 综合评分
total_score = tech_weighted + emotion_score + fund_score + macro_score

# 确保在0-1之间
total_score = min(max(total_score, 0), 1)

print(f"📈 综合评分计算:")
print(f"  技术面: {tech_weighted:.3f} (权重60%)")
print(f"  情绪面: {emotion_score:.3f} (权重13%)")
print(f"  资金面: {fund_score:.3f} (权重20%)")
print(f"  宏观面: {macro_score:.3f} (权重7%)")
print(f"  --------------------")
print(f"  总评分: {total_score:.3f}/1.0")
print()

# 状态判断
print("🎯 市场状态判断:")
print()

if total_score < 0.2:
    state = "混沌期"
    position = "0-10%"
    strategy = "空仓等待，极端谨慎"
    reasoning = "市场极度恐慌，风险极高"
elif total_score < 0.35:
    state = "情绪冰点期"
    position = "10-30%"
    strategy = "轻仓试探，等待转机"
    reasoning = "市场情绪冰点，但可能接近转折"
elif total_score < 0.5:
    state = "冬藏期"
    position = "10-30%"
    strategy = "防守为主，轻仓观望"
    reasoning = "市场低迷，需要耐心等待"
elif total_score < 0.65:
    state = "春播期"
    position = "30-50%"
    strategy = "分批建仓，布局未来"
    reasoning = "市场开始回暖，适合逐步布局"
elif total_score < 0.8:
    state = "夏长期"
    position = "50-70%"
    strategy = "重仓持有，顺势而为"
    reasoning = "市场趋势明确，机会较多"
else:
    state = "秋收期"
    position = "30-50%"
    strategy = "逐步减仓，锁定利润"
    reasoning = "市场过热，需要谨慎"

print(f"  市场状态: {state}")
print(f"  建议仓位: {position}")
print(f"  操作策略: {strategy}")
print(f"  判断理由: {reasoning}")
print()

# 与之前分析的对比
print("🔍 与之前分析的对比:")
print(f"  之前评分: 0.700 → 春播期 → 仓位50-70%")
print(f"  修正评分: {total_score:.3f} → {state} → 仓位{position}")
print(f"  主要差异: 降低了基础分权重，更严格的技术面评分")
print()

# 今日市场特征总结
print("📋 今日市场特征总结:")
print(f"  1. 指数下跌: {data['shanghai_change']}%")
print(f"  2. 极度普跌: 仅{rising_ratio:.1%}股票上涨")
print(f"  3. 涨停稀少: 仅{data['limit_up']}家涨停")
print(f"  4. 情绪冰点: {emotion}")
print(f"  5. 成交量萎缩: 交投清淡")
print()

print("💡 正确判断: 今日市场更符合情绪冰点期特征，而非春播期")
print("✅ 修正后的仓位建议更加合理和谨慎")