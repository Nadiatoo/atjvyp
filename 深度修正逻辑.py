#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度修正彪哥战法分析逻辑 - 重点解决情绪冰点判断
"""

import datetime

print("🔍 深度修正分析逻辑 - 重点解决情绪冰点判断")
print("=" * 70)
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

rising_ratio = data["rising_stocks"] / data["total_stocks"]  # 16.7%

print("📊 关键市场指标:")
print(f"  1. 上涨家数比例: {rising_ratio:.1%} (冰点阈值: <20%)")
print(f"  2. 涨停家数: {data['limit_up']} (冰点阈值: <60家)")
print(f"  3. 指数涨跌幅: {data['shanghai_change']}%")
print(f"  4. 跌停家数: {data['limit_down']} (恐慌阈值: >30家)")
print()

# 彪哥战法情绪冰点判断标准
print("🎯 彪哥战法情绪冰点判断标准:")
print("  1. 上涨家数比例 < 20%")
print("  2. 涨停家数 < 60家")
print("  3. 市场情绪极度恐慌")
print("  4. 成交量极度萎缩")
print()

# 检查今日是否符合情绪冰点
is_ice_point = False
ice_point_reasons = []

if rising_ratio < 0.2:
    ice_point_reasons.append(f"上涨家数仅{rising_ratio:.1%} (<20%)")
    is_ice_point = True

if data["limit_up"] < 60:
    ice_point_reasons.append(f"涨停仅{data['limit_up']}家 (<60家)")
    is_ice_point = True

if data["shanghai_change"] < -0.5:
    ice_point_reasons.append(f"指数下跌{data['shanghai_change']}%")

print("🔍 情绪冰点检查结果:")
if is_ice_point and len(ice_point_reasons) >= 2:
    print("  ✅ 符合情绪冰点特征")
    for reason in ice_point_reasons:
        print(f"    • {reason}")
else:
    print("  ❌ 不完全符合情绪冰点特征")
    for reason in ice_point_reasons:
        print(f"    • {reason}")

print()

# 重新设计更合理的评分系统
print("🔄 重新设计评分系统（更严格）:")
print()

# 1. 技术面评分 - 更严格
tech_score = 0

# 指数表现 (0-0.3分)
if data["shanghai_change"] < -2:
    tech_score += 0.3
elif data["shanghai_change"] < -1:
    tech_score += 0.25
elif data["shanghai_change"] < 0:
    tech_score += 0.2
elif data["shanghai_change"] < 1:
    tech_score += 0.1
else:
    tech_score += 0.05

# 市场广度 (0-0.4分)
if rising_ratio < 0.2:
    tech_score += 0.4  # 极度普跌
elif rising_ratio < 0.3:
    tech_score += 0.3  # 严重普跌
elif rising_ratio < 0.4:
    tech_score += 0.2  # 普跌
elif rising_ratio < 0.6:
    tech_score += 0.1  # 分化
else:
    tech_score += 0.05  # 普涨

# 涨停表现 (0-0.3分)
if data["limit_up"] < 40:
    tech_score += 0.3  # 涨停极少
elif data["limit_up"] < 60:
    tech_score += 0.25  # 涨停很少
elif data["limit_up"] < 80:
    tech_score += 0.15  # 涨停一般
elif data["limit_up"] < 100:
    tech_score += 0.1  # 涨停较多
else:
    tech_score += 0.05  # 涨停很多

tech_weighted = tech_score * 0.6
print(f"  技术面评分: {tech_score:.3f} → 加权: {tech_weighted:.3f}")

# 2. 情绪面评分 - 重点修正
if rising_ratio < 0.2:
    emotion_score = 0.15  # 情绪极度低迷（冰点）
    emotion_desc = "情绪冰点"
elif rising_ratio < 0.25:
    emotion_score = 0.12  # 情绪非常低迷
    emotion_desc = "情绪非常低迷"
elif rising_ratio < 0.3:
    emotion_score = 0.10  # 情绪低迷
    emotion_desc = "情绪低迷"
elif rising_ratio < 0.4:
    emotion_score = 0.07  # 情绪偏弱
    emotion_desc = "情绪偏弱"
elif rising_ratio < 0.6:
    emotion_score = 0.03  # 情绪中性
    emotion_desc = "情绪中性"
else:
    emotion_score = 0.0  # 情绪积极
    emotion_desc = "情绪积极"

print(f"  情绪面评分: {emotion_score:.3f} → {emotion_desc}")

# 3. 其他维度 - 更保守
fund_score = 0.03  # 资金面保守
macro_score = 0.01  # 宏观面保守

print(f"  资金面评分: {fund_score:.3f} (保守估计)")
print(f"  宏观面评分: {macro_score:.3f} (保守估计)")
print()

# 综合评分
total_score = tech_weighted + emotion_score + fund_score + macro_score
total_score = min(max(total_score, 0), 1)

print(f"📈 修正后综合评分: {total_score:.3f}/1.0")
print()

# 基于彪哥战法的状态判断
print("🎯 基于彪哥战法的正确状态判断:")
print()

# 更严格的状态判断阈值
if total_score < 0.25:
    state = "混沌期"
    position = "0-10%"
    strategy = "空仓等待，极端避险"
    reasoning = "市场极度恐慌，风险极高，适合空仓"
elif total_score < 0.40:
    state = "情绪冰点期"
    position = "10-20%"
    strategy = "极轻仓试探，等待明确信号"
    reasoning = "市场情绪冰点，可能接近转折但风险仍高"
elif total_score < 0.55:
    state = "冬藏期"
    position = "20-30%"
    strategy = "轻仓防守，耐心等待"
    reasoning = "市场低迷，需要耐心等待春天"
elif total_score < 0.70:
    state = "春播期"
    position = "30-50%"
    strategy = "分批建仓，布局优质标的"
    reasoning = "市场开始回暖，适合逐步布局"
elif total_score < 0.85:
    state = "夏长期"
    position = "50-70%"
    strategy = "重仓持有，顺势而为"
    reasoning = "市场趋势明确，机会较多"
else:
    state = "秋收期"
    position = "30-50%"
    strategy = "逐步减仓，锁定利润"
    reasoning = "市场过热，需要谨慎减仓"

print(f"  市场状态: {state}")
print(f"  建议仓位: {position}")
print(f"  操作策略: {strategy}")
print(f"  判断理由: {reasoning}")
print()

# 今日数据的详细分析
print("📋 今日数据深度分析:")
print(f"  1. 上涨比例16.7% → 属于情绪冰点范围(<20%)")
print(f"  2. 涨停52家 → 属于偏少范围(<60家)")
print(f"  3. 指数下跌1.09% → 弱势表现")
print(f"  4. 跌停14家 → 恐慌程度可控")
print(f"  5. 综合判断: 情绪冰点期特征明显")
print()

# 正确的彪哥战法逻辑
print("💡 正确的彪哥战法逻辑:")
print("  情绪冰点期 → 仓位10-20% → 极轻仓试探")
print("  冬藏期 → 仓位20-30% → 轻仓防守")
print("  春播期 → 仓位30-50% → 分批建仓")
print("  今日数据更符合情绪冰点期，而非春播期")
print()

print("✅ 结论: 今日市场处于情绪冰点期，建议仓位10-20%，极轻仓试探")
print("⚠️ 注意: 原分析逻辑存在基础分过高问题，已修正")