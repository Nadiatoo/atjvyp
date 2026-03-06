#!/usr/bin/env python3
"""
彪哥战法 - 真夏长3日确认系统 v2.0
综合考虑政策催化、行业突破、技术形态、资金流向
"""

from typing import Dict, List, Tuple
from datetime import datetime


class SummerConfirmationSystem:
    """
    真夏长3日确认系统
    
    核心思想：
    - 真夏长需要3天观察期确认
    - 必须结合政策/行业/技术/资金多维度
    - 所有趋势题材都有核心催化事件
    """
    
    def __init__(self):
        # 3日确认期权重分配
        self.weights = {
            'catalyst_strength': 0.20,     # 催化强度（政策/行业突破）
            'sector_performance': 0.15,    # 板块表现（3日累计）
            'leader_trend': 0.20,          # 龙头走势（连板质量）
            'zhongjun_health': 0.25,       # 中军健康度（形态+资金）
            'volume_quality': 0.10,        # 量能质量
            'market_context': 0.10,        # 市场环境
        }
    
    def confirm_summer(self, day1: dict, day2: dict, day3: dict,
                      catalyst: dict) -> dict:
        """
        3日确认真夏长
        
        Args:
            day1/day2/day3: 连续3日市场数据
            catalyst: 催化事件信息
        
        Returns:
            {
                'is_confirmed_summer': 是否确认真夏长,
                'confidence': 置信度,
                'score': 总分,
                'catalyst_analysis': 催化分析,
                'technical_analysis': 技术分析,
                'suggestion': 操作建议,
                'position_size': 建议仓位
            }
        """
        scores = {}
        analysis = {}
        
        # 1. 催化强度分析（20%）- 核心
        scores['catalyst'], analysis['catalyst'] = self._analyze_catalyst(catalyst)
        
        # 2. 板块表现分析（15%）- 3日累计
        scores['sector'], analysis['sector'] = self._analyze_sector_3day(day1, day2, day3)
        
        # 3. 龙头走势分析（20%）- 连板质量
        scores['leader'], analysis['leader'] = self._analyze_leader_3day(day1, day2, day3)
        
        # 4. 中军健康度分析（25%）- 形态+资金
        scores['zhongjun'], analysis['zhongjun'] = self._analyze_zhongjun_3day(day1, day2, day3)
        
        # 5. 量能质量分析（10%）
        scores['volume'], analysis['volume'] = self._analyze_volume_3day(day1, day2, day3)
        
        # 6. 市场环境分析（10%）
        scores['market'], analysis['market'] = self._analyze_market_3day(day1, day2, day3)
        
        # 计算总分
        total_score = sum(scores.values())
        
        # 判定结果
        is_confirmed = total_score >= 75
        
        # 置信度
        if total_score >= 85:
            confidence = "极高"
            position = "70-80%"
        elif total_score >= 75:
            confidence = "高"
            position = "50-60%"
        elif total_score >= 65:
            confidence = "中"
            position = "30-40%"
        else:
            confidence = "低"
            position = "0-10%"
        
        return {
            'is_confirmed_summer': is_confirmed,
            'confidence': confidence,
            'score': round(total_score, 1),
            'scores': scores,
            'analysis': analysis,
            'catalyst_tier': analysis['catalyst']['tier'],
            'suggestion': self._generate_suggestion(total_score, analysis),
            'position_size': position,
            'entry_timing': self._suggest_timing(analysis),
            'risk_factors': self._identify_risks(analysis)
        }
    
    def _analyze_catalyst(self, catalyst: dict) -> Tuple[float, dict]:
        """
        催化强度分析 - 核心维度
        
        催化类型：
        - S级：国家级政策/行业重大突破/行业反转
        - A级：部委级政策/重要技术突破/业绩暴增
        - B级：地方政策/一般技术进展/事件驱动
        - C级：传闻/短期刺激/无实质利好
        """
        signal = {
            'tier': catalyst.get('tier', 'C'),
            'type': catalyst.get('type', ''),
            'description': catalyst.get('description', ''),
            'duration_estimate': '',
            'key_observations': []
        }
        
        tier = catalyst.get('tier', 'C')
        cat_type = catalyst.get('type', '')
        
        # 根据催化等级评分
        tier_scores = {'S': 20, 'A': 16, 'B': 10, 'C': 5}
        score = tier_scores.get(tier, 5)
        
        # 催化类型加分
        type_bonus = {
            '国家级政策': 5,
            '行业重大突破': 5,
            '行业反转': 5,
            '部委级政策': 3,
            '技术突破': 3,
            '业绩暴增': 3,
            '地方政策': 2,
            '事件驱动': 1,
        }
        score += type_bonus.get(cat_type, 0)
        
        # 分析催化持续性
        if tier == 'S':
            signal['duration_estimate'] = '1-3个月'
            signal['key_observations'].append("✅ S级催化，国家级战略，持续性强")
        elif tier == 'A':
            signal['duration_estimate'] = '2-6周'
            signal['key_observations'].append("🟡 A级催化，重要政策/突破，持续性较好")
        elif tier == 'B':
            signal['duration_estimate'] = '1-3周'
            signal['key_observations'].append("🟠 B级催化，一般性利好，持续性一般")
        else:
            signal['duration_estimate'] = '<1周'
            signal['key_observations'].append("❌ C级催化，短期刺激，难以持续")
        
        # 催化与板块匹配度
        if catalyst.get('sector_match', False):
            score += 5
            signal['key_observations'].append("✅ 催化与板块高度匹配")
        
        return min(score, 20), signal
    
    def _analyze_sector_3day(self, d1: dict, d2: dict, d3: dict) -> Tuple[float, dict]:
        """
        板块3日表现分析
        
        关键指标：
        - 3日累计涨幅
        - 每日涨停家数稳定性
        - 板块内个股持续性
        """
        signal = {
            'total_change_3d': 0,
            'avg_limit_up': 0,
            'consistency': '',
            'key_observations': []
        }
        
        # 3日累计涨幅
        total_change = (1 + d1.get('sector_change', 0)) * \
                       (1 + d2.get('sector_change', 0)) * \
                       (1 + d3.get('sector_change', 0)) - 1
        signal['total_change_3d'] = total_change
        
        score = 0
        
        # 累计涨幅评分
        if total_change >= 0.15:  # 15%+
            score += 8
            signal['key_observations'].append("✅ 3日累计涨幅>15%，强势")
        elif total_change >= 0.10:  # 10-15%
            score += 6
            signal['key_observations'].append("🟡 3日累计涨幅10-15%，正常")
        elif total_change >= 0.05:  # 5-10%
            score += 3
            signal['key_observations'].append("🟠 3日累计涨幅5-10%，偏弱")
        else:
            signal['key_observations'].append("❌ 3日累计涨幅<5%，弱势")
        
        # 涨停家数稳定性
        lu1 = d1.get('limit_up_count', 0)
        lu2 = d2.get('limit_up_count', 0)
        lu3 = d3.get('limit_up_count', 0)
        avg_lu = (lu1 + lu2 + lu3) / 3
        signal['avg_limit_up'] = avg_lu
        
        if avg_lu >= 5 and min(lu1, lu2, lu3) >= 3:
            score += 7
            signal['key_observations'].append("✅ 3日涨停家数稳定>=5家")
        elif avg_lu >= 3:
            score += 4
            signal['key_observations'].append("🟡 3日涨停家数平均>=3家")
        else:
            signal['key_observations'].append("❌ 涨停家数不足，资金不持续")
        
        # 一致性（每日上涨家数占比）
        up_ratios = [d1.get('up_ratio', 0), d2.get('up_ratio', 0), d3.get('up_ratio', 0)]
        if all(r >= 0.6 for r in up_ratios):
            score += 5
            signal['consistency'] = '高'
            signal['key_observations'].append("✅ 3日普涨，一致性高")
        elif all(r >= 0.4 for r in up_ratios):
            score += 3
            signal['consistency'] = '中'
            signal['key_observations'].append("🟡 3日多数上涨，一致性一般")
        else:
            signal['consistency'] = '低'
            signal['key_observations'].append("❌ 分化严重，一致性低")
        
        return min(score, 15), signal
    
    def _analyze_leader_3day(self, d1: dict, d2: dict, d3: dict) -> Tuple[float, dict]:
        """
        龙头3日走势分析
        
        关键指标：
        - 是否连板（3连板最佳）
        - 封板质量（封单、开板次数）
        - 带动性（每日跟风情况）
        """
        signal = {
            'leader_name': d1.get('leader_name', ''),
            'boards_3d': 0,
            'seal_quality': '',
            'follower_stability': '',
            'key_observations': []
        }
        
        score = 0
        
        # 连板情况
        boards = sum([
            1 if d1.get('leader_limit_up', False) else 0,
            1 if d2.get('leader_limit_up', False) else 0,
            1 if d3.get('leader_limit_up', False) else 0
        ])
        signal['boards_3d'] = boards
        
        if boards == 3:
            score += 10
            signal['key_observations'].append("✅ 龙头3连板，强势")
        elif boards == 2:
            score += 7
            signal['key_observations'].append("🟡 龙头2连板，正常")
        elif boards == 1:
            score += 3
            signal['key_observations'].append("🟠 龙头仅1板，偏弱")
        else:
            signal['key_observations'].append("❌ 龙头未连板，弱势")
        
        # 封板质量（3日平均封单）
        avg_seal = (d1.get('leader_seal', 0) + 
                   d2.get('leader_seal', 0) + 
                   d3.get('leader_seal', 0)) / 3
        
        if avg_seal >= 3:  # 3亿+
            score += 5
            signal['seal_quality'] = '优秀'
            signal['key_observations'].append("✅ 封单充足，资金坚决")
        elif avg_seal >= 1:
            score += 3
            signal['seal_quality'] = '良好'
            signal['key_observations'].append("🟡 封单一般")
        else:
            signal['seal_quality'] = '差'
            signal['key_observations'].append("❌ 封单不足，资金犹豫")
        
        # 带动性稳定性
        f1 = d1.get('follower_count', 0)
        f2 = d2.get('follower_count', 0)
        f3 = d3.get('follower_count', 0)
        
        if f1 >= 3 and f2 >= 3 and f3 >= 3:
            score += 5
            signal['follower_stability'] = '稳定'
            signal['key_observations'].append("✅ 3日均有跟风，带动性稳定")
        elif min(f1, f2, f3) >= 1:
            score += 2
            signal['follower_stability'] = '一般'
            signal['key_observations'].append("🟡 跟风不稳定")
        else:
            signal['follower_stability'] = '差'
            signal['key_observations'].append("❌ 无持续跟风，独龙难舞")
        
        return min(score, 20), signal
    
    def _analyze_zhongjun_3day(self, d1: dict, d2: dict, d3: dict) -> Tuple[float, dict]:
        """
        中军3日健康度分析 - 核心维度
        
        关键指标：
        - 3日累计涨幅（是否稳健上涨）
        - 技术形态（5日线支撑）
        - 成交活跃度（资金持续）
        - 亏钱效应（是否健康）
        """
        signal = {
            'zhongjun_list': d1.get('zhongjun_list', []),
            'total_change_3d': 0,
            'technical_health': '',
            'volume_trend': '',
            'key_observations': []
        }
        
        score = 0
        
        # 3日累计涨幅
        zj_changes = [
            d1.get('zhongjun_avg_change', 0),
            d2.get('zhongjun_avg_change', 0),
            d3.get('zhongjun_avg_change', 0)
        ]
        total_zj_change = sum(zj_changes)
        signal['total_change_3d'] = total_zj_change
        
        if total_zj_change >= 0.15:  # 15%+
            score += 8
            signal['key_observations'].append("✅ 中军3日累计>15%，强势")
        elif total_zj_change >= 0.10:
            score += 6
            signal['key_observations'].append("🟡 中军3日累计10-15%，正常")
        elif total_zj_change >= 0.05:
            score += 3
            signal['key_observations'].append("🟠 中军3日累计5-10%，偏弱")
        else:
            signal['key_observations'].append("❌ 中军3日累计<5%，弱势")
        
        # 技术形态（3日是否沿5日线上行）
        vs_ma5 = [d1.get('zhongjun_vs_ma5', 0), 
                  d2.get('zhongjun_vs_ma5', 0), 
                  d3.get('zhongjun_vs_ma5', 0)]
        
        if all(v > 0 for v in vs_ma5):
            score += 7
            signal['technical_health'] = '优秀'
            signal['key_observations'].append("✅ 3日均在5日线上，形态完美")
        elif sum(vs_ma5) > 0:
            score += 4
            signal['technical_health'] = '良好'
            signal['key_observations'].append("🟡 整体在5日线上，偶有跌破")
        else:
            signal['technical_health'] = '差'
            signal['key_observations'].append("❌ 跌破5日线，形态走坏")
        
        # 成交活跃度趋势
        turnovers = [d1.get('zhongjun_turnover', 0),
                    d2.get('zhongjun_turnover', 0),
                    d3.get('zhongjun_turnover', 0)]
        
        if all(t >= 10 for t in turnovers):  # 日均10亿+
            score += 5
            signal['volume_trend'] = '持续活跃'
            signal['key_observations'].append("✅ 3日成交均>10亿，资金持续")
        elif sum(turnovers) / 3 >= 8:
            score += 3
            signal['volume_trend'] = '较活跃'
            signal['key_observations'].append("🟡 成交尚可")
        else:
            signal['volume_trend'] = '萎缩'
            signal['key_observations'].append("❌ 成交萎缩，资金离场")
        
        # 亏钱效应（3日是否有大跌）
        loss_days = sum(1 for c in zj_changes if c < -0.03)
        if loss_days == 0:
            score += 5
            signal['key_observations'].append("✅ 3日无大跌，健康")
        elif loss_days == 1:
            score += 2
            signal['key_observations'].append("🟡 1日大跌，尚可接受")
        else:
            signal['key_observations'].append("❌ 多日大跌，不健康")
        
        return min(score, 25), signal
    
    def _analyze_volume_3day(self, d1: dict, d2: dict, d3: dict) -> Tuple[float, dict]:
        """量能3日质量分析"""
        signal = {'key_observations': []}
        
        v_ratios = [d1.get('volume_ratio', 1), 
                   d2.get('volume_ratio', 1), 
                   d3.get('volume_ratio', 1)]
        
        score = 0
        
        # 是否持续温和放大
        if all(1.2 <= v <= 2.0 for v in v_ratios):
            score = 10
            signal['key_observations'].append("✅ 3日量能持续温和放大")
        elif all(v >= 1.0 for v in v_ratios):
            score = 6
            signal['key_observations'].append("🟡 量能正常")
        elif any(v > 3.0 for v in v_ratios):
            signal['key_observations'].append("❌ 某日渐近暴量，警惕")
        else:
            signal['key_observations'].append("❌ 量能萎缩")
        
        return score, signal
    
    def _analyze_market_3day(self, d1: dict, d2: dict, d3: dict) -> Tuple[float, dict]:
        """市场环境3日分析"""
        signal = {'key_observations': []}
        
        index_changes = [d1.get('index_change', 0),
                        d2.get('index_change', 0),
                        d3.get('index_change', 0)]
        
        score = 0
        
        # 大盘是否配合
        if sum(index_changes) > 0:
            score += 5
            signal['key_observations'].append("✅ 3日大盘整体上涨，环境良好")
        elif min(index_changes) > -2:
            score += 3
            signal['key_observations'].append("🟡 大盘震荡，影响不大")
        else:
            signal['key_observations'].append("❌ 大盘大跌，环境恶劣")
        
        # 是否有系统性风险
        if all(c > -3 for c in index_changes):
            score += 5
            signal['key_observations'].append("✅ 无系统性风险")
        else:
            signal['key_observations'].append("⚠️ 存在系统性风险")
        
        return score, signal
    
    def _generate_suggestion(self, score: float, analysis: dict) -> str:
        """生成操作建议"""
        catalyst_tier = analysis['catalyst']['tier']
        
        if score >= 85:
            return f"🟢 {catalyst_tier}级催化+技术完美，确认真夏长，满仓干"
        elif score >= 75:
            return f"🟡 {catalyst_tier}级催化+技术良好，疑似真夏长，重仓参与"
        elif score >= 65:
            return f"🟠 {catalyst_tier}级催化，信号一般，轻仓试错或观望"
        else:
            return f"🔴 催化不足或技术走坏，假夏长概率大，放弃"
    
    def _suggest_timing(self, analysis: dict) -> str:
        """建议入场时机"""
        if analysis['catalyst']['tier'] in ['S', 'A'] and \
           analysis['zhongjun']['technical_health'] == '优秀':
            return "Day3收盘前或Day4早盘确认后入场"
        else:
            return "等待进一步确认，不急于入场"
    
    def _identify_risks(self, analysis: dict) -> List[str]:
        """识别风险因素"""
        risks = []
        
        if analysis['catalyst']['tier'] == 'C':
            risks.append("催化级别低，难以持续")
        
        if analysis['leader']['boards_3d'] < 2:
            risks.append("龙头未连板，带动性不足")
        
        if analysis['zhongjun']['technical_health'] == '差':
            risks.append("中军形态走坏，板块难持续")
        
        return risks


# ========== 实战案例验证 ==========

def validate_cases():
    """验证历史案例"""
    
    system = SummerConfirmationSystem()
    
    print("=" * 80)
    print("真夏长3日确认系统 - 历史案例验证")
    print("=" * 80)
    
    # 案例1：2024-02 AI/CPO（真夏长）
    print("\n【案例1】2024-02 AI/CPO行情（真夏长）")
    print("-" * 80)
    
    catalyst1 = {
        'tier': 'S',
        'type': '行业重大突破',
        'description': 'Sora发布，AI视频生成突破',
        'sector_match': True
    }
    
    day1_1 = {
        'sector_change': 0.085,
        'limit_up_count': 8,
        'up_ratio': 0.85,
        'leader_name': '克来机电',
        'leader_limit_up': True,
        'leader_seal': 3,
        'follower_count': 5,
        'zhongjun_list': ['中际旭创', '新易盛'],
        'zhongjun_avg_change': 0.12,
        'zhongjun_vs_ma5': 0.05,
        'zhongjun_turnover': 20,
        'volume_ratio': 1.5,
        'index_change': 0.015
    }
    
    day2_1 = {
        'sector_change': 0.052,
        'limit_up_count': 6,
        'up_ratio': 0.75,
        'leader_limit_up': True,
        'leader_seal': 2,
        'follower_count': 4,
        'zhongjun_avg_change': 0.08,
        'zhongjun_vs_ma5': 0.06,
        'zhongjun_turnover': 18,
        'volume_ratio': 1.3,
        'index_change': 0.01
    }
    
    day3_1 = {
        'sector_change': 0.06,
        'limit_up_count': 7,
        'up_ratio': 0.80,
        'leader_limit_up': True,
        'leader_seal': 4,
        'follower_count': 5,
        'zhongjun_avg_change': 0.10,
        'zhongjun_vs_ma5': 0.08,
        'zhongjun_turnover': 22,
        'volume_ratio': 1.6,
        'index_change': 0.008
    }
    
    result1 = system.confirm_summer(day1_1, day2_1, day3_1, catalyst1)
    
    print(f"催化等级: {result1['catalyst_tier']}级")
    print(f"总分: {result1['score']}分")
    print(f"是否确认真夏长: {result1['is_confirmed_summer']}")
    print(f"置信度: {result1['confidence']}")
    print(f"建议仓位: {result1['position_size']}")
    print(f"操作建议: {result1['suggestion']}")
    print(f"入场时机: {result1['entry_timing']}")
    
    print("\n各维度得分:")
    for key, score in result1['scores'].items():
        print(f"  {key}: {score}分")
    
    # 案例2：2024-09 金融（假夏长）
    print("\n" + "=" * 80)
    print("【案例2】2024-09 金融行情（假夏长）")
    print("-" * 80)
    
    catalyst2 = {
        'tier': 'A',
        'type': '政策刺激',
        'description': '降准降息政策刺激',
        'sector_match': True
    }
    
    day1_2 = {
        'sector_change': 0.07,
        'limit_up_count': 6,
        'up_ratio': 0.90,
        'leader_name': '天风证券',
        'leader_limit_up': True,
        'leader_seal': 5,
        'follower_count': 4,
        'zhongjun_list': ['中信证券', '东方财富'],
        'zhongjun_avg_change': 0.02,  # 中军弱！
        'zhongjun_vs_ma5': -0.02,
        'zhongjun_turnover': 15,
        'volume_ratio': 2.5,  # 暴量
        'index_change': 0.04
    }
    
    day2_2 = {
        'sector_change': 0.02,
        'limit_up_count': 3,
        'up_ratio': 0.50,
        'leader_limit_up': True,
        'leader_seal': 1,
        'follower_count': 2,
        'zhongjun_avg_change': -0.01,
        'zhongjun_vs_ma5': -0.03,
        'zhongjun_turnover': 12,
        'volume_ratio': 1.8,
        'index_change': -0.01
    }
    
    day3_2 = {
        'sector_change': -0.03,
        'limit_up_count': 1,
        'up_ratio': 0.30,
        'leader_limit_up': False,
        'leader_seal': 0,
        'follower_count': 0,
        'zhongjun_avg_change': -0.04,
        'zhongjun_vs_ma5': -0.05,
        'zhongjun_turnover': 10,
        'volume_ratio': 1.2,
        'index_change': -0.02
    }
    
    result2 = system.confirm_summer(day1_2, day2_2, day3_2, catalyst2)
    
    print(f"催化等级: {result2['catalyst_tier']}级")
    print(f"总分: {result2['score']}分")
    print(f"是否确认真夏长: {result2['is_confirmed_summer']}")
    print(f"置信度: {result2['confidence']}")
    print(f"建议仓位: {result2['position_size']}")
    print(f"操作建议: {result2['suggestion']}")
    print(f"风险因素: {result2['risk_factors']}")


if __name__ == '__main__':
    validate_cases()
