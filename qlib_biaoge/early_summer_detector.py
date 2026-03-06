#!/usr/bin/env python3
"""
彪哥战法 - 真夏长早期识别系统 v1.0
目标：在夏长启动初期（1-3天内）识别真夏长，避免追高
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta


class EarlySummerDetector:
    """
    真夏长早期识别器
    
    核心思想：
    - 真夏长在启动初期就有迹可循
    - 通过多维度早期信号，在1-3天内识别
    - 避免等涨了十几天才追高
    """
    
    def __init__(self):
        # 早期信号权重（启动期1-3天）
        self.weights = {
            'sector_strength': 0.25,      # 板块强度（25%）
            'leader_quality': 0.20,        # 龙头质量（20%）
            'zhongjun_response': 0.25,     # 中军响应（25%）- 核心
            'volume_structure': 0.15,      # 量能结构（15%）
            'market_environment': 0.15,    # 市场环境（15%）
        }
    
    def detect_early_summer(self, day1_data: dict, day2_data: dict = None, 
                           day3_data: dict = None) -> dict:
        """
        检测是否为真夏长启动
        
        Args:
            day1_data: 启动第1天数据
            day2_data: 启动第2天数据（可选）
            day3_data: 启动第3天数据（可选）
        
        Returns:
            {
                'is_early_summer': 是否真夏长启动,
                'confidence': 置信度,
                'score': 总分,
                'signals': 各维度信号,
                'suggestion': 操作建议,
                'risk_level': 风险等级
            }
        """
        scores = {}
        signals = {}
        
        # 1. 板块强度评分 (0-25分)
        scores['sector_strength'], signals['sector'] = self._analyze_sector_strength(
            day1_data, day2_data, day3_data
        )
        
        # 2. 龙头质量评分 (0-20分)
        scores['leader_quality'], signals['leader'] = self._analyze_leader_quality(
            day1_data, day2_data, day3_data
        )
        
        # 3. 中军响应评分 (0-25分) - 核心
        scores['zhongjun_response'], signals['zhongjun'] = self._analyze_zhongjun_response(
            day1_data, day2_data, day3_data
        )
        
        # 4. 量能结构评分 (0-15分)
        scores['volume_structure'], signals['volume'] = self._analyze_volume_structure(
            day1_data, day2_data, day3_data
        )
        
        # 5. 市场环境评分 (0-15分)
        scores['market_environment'], signals['market'] = self._analyze_market_environment(
            day1_data, day2_data, day3_data
        )
        
        # 计算总分（注意：scores已经是0-100分制，weights是百分比）
        total_score = sum(
            scores[key]  # 直接相加，因为每个维度已经按权重计算了满分
            for key in scores
        )
        
        # 判定结果
        is_early_summer = total_score >= 70
        
        # 风险等级
        if total_score >= 80:
            risk_level = "低风险"
            confidence = "高"
        elif total_score >= 70:
            risk_level = "中低风险"
            confidence = "中高"
        elif total_score >= 60:
            risk_level = "中风险"
            confidence = "中"
        else:
            risk_level = "高风险"
            confidence = "低"
        
        return {
            'is_early_summer': is_early_summer,
            'confidence': confidence,
            'score': round(total_score, 1),
            'scores': scores,
            'signals': signals,
            'risk_level': risk_level,
            'suggestion': self._generate_suggestion(total_score, signals),
            'entry_timing': self._suggest_entry_timing(signals)
        }
    
    def _analyze_sector_strength(self, d1: dict, d2: dict, d3: dict) -> Tuple[float, dict]:
        """
        板块强度分析（启动期）
        
        关键信号：
        - Day1: 板块涨幅 >3%
        - Day2: 板块继续上涨或强势震荡
        - 涨停家数 >=3家
        - 板块内个股普涨（>70%上涨）
        """
        signal = {
            'day1_sector_change': d1.get('sector_change', 0),
            'day1_limit_up_count': d1.get('limit_up_count', 0),
            'day1_up_ratio': d1.get('up_ratio', 0),
            'key_observations': []
        }
        
        score = 0
        
        # Day1板块涨幅
        if d1.get('sector_change', 0) >= 5:
            score += 10
            signal['key_observations'].append("✅ Day1板块大涨>5%，启动强劲")
        elif d1.get('sector_change', 0) >= 3:
            score += 7
            signal['key_observations'].append("🟡 Day1板块涨3-5%，启动正常")
        else:
            signal['key_observations'].append("❌ Day1板块涨幅<3%，启动偏弱")
        
        # 涨停家数
        if d1.get('limit_up_count', 0) >= 5:
            score += 8
            signal['key_observations'].append("✅ 涨停家数>=5，资金积极")
        elif d1.get('limit_up_count', 0) >= 3:
            score += 5
            signal['key_observations'].append("🟡 涨停家数3-4，资金一般")
        else:
            signal['key_observations'].append("❌ 涨停家数<3，资金犹豫")
        
        # 普涨程度
        if d1.get('up_ratio', 0) >= 0.7:
            score += 7
            signal['key_observations'].append("✅ 板块内>70%个股上涨，一致性强")
        elif d1.get('up_ratio', 0) >= 0.5:
            score += 4
            signal['key_observations'].append("🟡 板块内50-70%个股上涨")
        else:
            signal['key_observations'].append("❌ 板块内<50%个股上涨，分化严重")
        
        # Day2验证（如果有数据）
        if d2:
            if d2.get('sector_change', 0) > 0:
                score += 5
                signal['key_observations'].append("✅ Day2继续上涨，趋势确认")
            elif d2.get('sector_change', 0) > -2:
                score += 2
                signal['key_observations'].append("🟡 Day2强势震荡，趋势尚可")
            else:
                signal['key_observations'].append("❌ Day2大幅下跌，趋势存疑")
        
        return min(score, 25), signal
    
    def _analyze_leader_quality(self, d1: dict, d2: dict, d3: dict) -> Tuple[float, dict]:
        """
        龙头质量分析（启动期）
        
        关键信号：
        - 龙头封板坚决（一字或快速板）
        - 龙头带动性强（跟风迅速）
        - 龙头盘子适中（30-100亿）
        - 龙头股性活跃（历史连板基因）
        """
        signal = {
            'leader_name': d1.get('leader_name', ''),
            'leader_boards': 1,  # Day1是首板
            'leader_market_cap': d1.get('leader_market_cap', 0),
            'leader_seal_amount': d1.get('leader_seal_amount', 0),  # 封单金额
            'key_observations': []
        }
        
        score = 0
        
        # 封板质量
        if d1.get('leader_seal_amount', 0) >= 5:  # 封单>=5亿
            score += 8
            signal['key_observations'].append("✅ 龙头封单>5亿，资金抢筹")
        elif d1.get('leader_seal_amount', 0) >= 2:
            score += 5
            signal['key_observations'].append("🟡 龙头封单2-5亿，资金一般")
        else:
            signal['key_observations'].append("❌ 龙头封单<2亿，资金犹豫")
        
        # 盘子大小
        cap = d1.get('leader_market_cap', 0)
        if 30 <= cap <= 100:
            score += 6
            signal['key_observations'].append("✅ 龙头盘子30-100亿，最佳区间")
        elif 20 <= cap <= 150:
            score += 3
            signal['key_observations'].append("🟡 龙头盘子略大或略小")
        else:
            signal['key_observations'].append("❌ 龙头盘子不合适，难持续")
        
        # 带动性（Day1跟风情况）
        if d1.get('follower_count', 0) >= 3:
            score += 6
            signal['key_observations'].append("✅ Day1即有3+跟风，带动性强")
        else:
            signal['key_observations'].append("🟡 Day1跟风不足，带动性待观察")
        
        # Day2验证
        if d2:
            if d2.get('leader_boards', 0) >= 2:
                score += 5
                signal['key_observations'].append("✅ 龙头Day2连板，质量优秀")
            elif d2.get('leader_change', 0) > 0:
                score += 2
                signal['key_observations'].append("🟡 龙头Day2断板但收涨")
            else:
                signal['key_observations'].append("❌ 龙头Day2大跌，质量差")
        
        return min(score, 20), signal
    
    def _analyze_zhongjun_response(self, d1: dict, d2: dict, d3: dict) -> Tuple[float, dict]:
        """
        中军响应分析（启动期）- 核心维度
        
        关键信号（最重要）：
        - Day1中军即跟涨（不能缺席）
        - 中军涨幅 >板块平均（主动而非被动）
        - 中军成交放大（大资金入场）
        - 中军技术位置健康（沿5日线上行）
        """
        signal = {
            'zhongjun_list': d1.get('zhongjun_list', []),
            'day1_zhongjun_avg_change': d1.get('zhongjun_avg_change', 0),
            'day1_zhongjun_turnover': d1.get('zhongjun_avg_turnover', 0),
            'day1_zhongjun_vs_sector': 0,  # 中军vs板块涨幅
            'key_observations': []
        }
        
        score = 0
        
        # 中军Day1是否跟涨（最关键）
        zj_change = d1.get('zhongjun_avg_change', 0)
        sector_change = d1.get('sector_change', 0)
        
        if zj_change >= 5:
            score += 10
            signal['key_observations'].append("✅ 中军Day1大涨>5%，积极响应")
        elif zj_change >= 3:
            score += 7
            signal['key_observations'].append("🟡 中军Day1涨3-5%，响应正常")
        elif zj_change > 0:
            score += 3
            signal['key_observations'].append("⚠️ 中军Day1微涨，响应偏弱")
        else:
            signal['key_observations'].append("❌ 中军Day1下跌，无响应！危险信号！")
        
        # 中军vs板块（是否主动）
        if zj_change > sector_change:
            score += 5
            signal['key_observations'].append("✅ 中军涨幅>板块，主动性强")
        elif zj_change >= sector_change * 0.7:
            score += 2
            signal['key_observations'].append("🟡 中军涨幅接近板块")
        else:
            signal['key_observations'].append("❌ 中军涨幅明显落后，被动跟涨")
        
        # 成交放大
        turnover_ratio = d1.get('zhongjun_turnover_ratio', 1)
        if turnover_ratio >= 1.5:
            score += 5
            signal['key_observations'].append("✅ 中军成交放大>50%，大资金入场")
        elif turnover_ratio >= 1.2:
            score += 3
            signal['key_observations'].append("🟡 中军成交放大20-50%")
        else:
            signal['key_observations'].append("⚠️ 中军成交未放大，资金观望")
        
        # 技术位置
        if d1.get('zhongjun_vs_ma5', 0) > 0:
            score += 5
            signal['key_observations'].append("✅ 中军在5日线上，趋势健康")
        elif d1.get('zhongjun_vs_ma20', 0) > 0:
            score += 2
            signal['key_observations'].append("🟡 中军在20日线上")
        else:
            signal['key_observations'].append("⚠️ 中军跌破20日线，位置不佳")
        
        # Day2验证（关键）
        if d2:
            d2_zj_change = d2.get('zhongjun_avg_change', 0)
            if d2_zj_change > 0:
                score += 5
                signal['key_observations'].append("✅ 中军Day2继续上涨，趋势确认")
            elif d2_zj_change > -3:
                score += 2
                signal['key_observations'].append("🟡 中军Day2小幅调整，正常")
            else:
                signal['key_observations'].append("❌ 中军Day2大跌，趋势存疑！")
        
        return min(score, 25), signal
    
    def _analyze_volume_structure(self, d1: dict, d2: dict, d3: dict) -> Tuple[float, dict]:
        """
        量能结构分析（启动期）
        
        关键信号：
        - 板块量能温和放大（1.2-2倍）
        - 非暴量（排除对倒出货）
        - 量价配合良好（价涨量增）
        """
        signal = {
            'day1_volume_ratio': d1.get('volume_ratio', 1),
            'day2_volume_ratio': d2.get('volume_ratio', 1) if d2 else 1,
            'key_observations': []
        }
        
        score = 0
        
        # Day1量能
        v1 = d1.get('volume_ratio', 1)
        if 1.2 <= v1 <= 2.0:
            score += 8
            signal['key_observations'].append("✅ Day1量能温和放大，健康")
        elif 1.0 <= v1 < 1.2:
            score += 4
            signal['key_observations'].append("🟡 Day1量能略增")
        elif v1 > 3.0:
            signal['key_observations'].append("⚠️ Day1暴量，需警惕对倒")
        else:
            signal['key_observations'].append("❌ Day1量能萎缩，资金不积极")
        
        # Day2量能（如果有）
        if d2:
            v2 = d2.get('volume_ratio', 1)
            if 1.0 <= v2 <= 2.0:
                score += 7
                signal['key_observations'].append("✅ Day2量能持续，趋势确认")
            elif v2 > 3.0:
                signal['key_observations'].append("⚠️ Day2暴量，可能出货")
        
        return min(score, 15), signal
    
    def _analyze_market_environment(self, d1: dict, d2: dict, d3: dict) -> Tuple[float, dict]:
        """
        市场环境分析（启动期）
        
        关键信号：
        - 大盘非单边下跌
        - 市场情绪非冰点
        - 无重大利空
        """
        signal = {
            'index_change': d1.get('index_change', 0),
            'market_sentiment': d1.get('market_sentiment', 'neutral'),
            'key_observations': []
        }
        
        score = 0
        
        # 大盘环境
        index_change = d1.get('index_change', 0)
        if index_change >= -1:
            score += 8
            signal['key_observations'].append("✅ 大盘环境良好，支持板块启动")
        elif index_change >= -2:
            score += 4
            signal['key_observations'].append("🟡 大盘小幅调整，影响不大")
        else:
            signal['key_observations'].append("❌ 大盘大跌，板块难独善其身")
        
        # 市场情绪
        sentiment = d1.get('market_sentiment', 'neutral')
        if sentiment == 'warm':
            score += 7
            signal['key_observations'].append("✅ 市场情绪回暖，利于发酵")
        elif sentiment == 'neutral':
            score += 4
            signal['key_observations'].append("🟡 市场情绪中性")
        else:
            signal['key_observations'].append("⚠️ 市场情绪冰点，启动难度大")
        
        return min(score, 15), signal
    
    def _generate_suggestion(self, score: float, signals: dict) -> str:
        """生成操作建议"""
        
        # 特别关注中军响应
        zj_score = signals.get('zhongjun', {}).get('day1_zhongjun_avg_change', 0)
        
        if score >= 80:
            return "🟢 真夏长启动确认，Day1即可建仓10%，Day2确认后加满"
        elif score >= 70:
            return "🟡 疑似真夏长启动，Day1建仓5%，Day2验证后加仓"
        elif score >= 60:
            return "🟠 启动信号不足，观望或极轻仓试错，等待Day2验证"
        else:
            return "🔴 假启动概率大，不参与，等待下次机会"
    
    def _suggest_entry_timing(self, signals: dict) -> str:
        """建议入场时机"""
        
        zj_signals = signals.get('zhongjun', {}).get('key_observations', [])
        
        # 如果中军Day1就大涨，可以Day1尾盘或Day2早盘入场
        if any("中军Day1大涨" in s for s in zj_signals):
            return "Day1尾盘或Day2早盘（中军响应积极）"
        
        # 如果中军Day1一般，必须等Day2验证
        if any("中军Day1微涨" in s for s in zj_signals):
            return "必须等Day2验证（中军响应偏弱）"
        
        return "观望，等待信号明确"


# ========== 实战案例验证 ==========

def validate_with_historical_cases():
    """用历史案例验证早期识别系统"""
    
    detector = EarlySummerDetector()
    
    # 案例1：2024-02 AI/CPO（真夏长）
    case1_day1 = {
        'date': '2024-02-19',
        'sector_change': 8.5,
        'limit_up_count': 8,
        'up_ratio': 0.85,
        'leader_name': '克来机电',
        'leader_seal_amount': 3,
        'leader_market_cap': 50,
        'follower_count': 5,
        'zhongjun_list': ['中际旭创', '新易盛', '天孚通信'],
        'zhongjun_avg_change': 12,
        'zhongjun_turnover_ratio': 1.8,
        'zhongjun_vs_ma5': 0.05,
        'volume_ratio': 1.5,
        'index_change': 1.5,
        'market_sentiment': 'warm'
    }
    
    case1_day2 = {
        'sector_change': 5.2,
        'leader_boards': 2,
        'zhongjun_avg_change': 8,
        'volume_ratio': 1.3
    }
    
    result1 = detector.detect_early_summer(case1_day1, case1_day2)
    
    print("=" * 80)
    print("案例1：2024-02 AI/CPO（真夏长）")
    print("=" * 80)
    print(f"Day1日期: {case1_day1['date']}")
    print(f"总分: {result1['score']}分")
    print(f"是否真夏长启动: {result1['is_early_summer']}")
    print(f"置信度: {result1['confidence']}")
    print(f"风险等级: {result1['risk_level']}")
    print(f"建议: {result1['suggestion']}")
    print(f"入场时机: {result1['entry_timing']}")
    print("\n各维度得分:")
    for key, score in result1['scores'].items():
        print(f"  {key}: {score}分")
    print("\n关键信号:")
    for category, signal in result1['signals'].items():
        print(f"\n  {category}:")
        for obs in signal.get('key_observations', []):
            print(f"    {obs}")
    
    # 案例2：2024-09 金融（假夏长）
    case2_day1 = {
        'date': '2024-09-24',
        'sector_change': 7.0,
        'limit_up_count': 6,
        'up_ratio': 0.9,
        'leader_name': '天风证券',
        'leader_seal_amount': 5,
        'leader_market_cap': 200,
        'follower_count': 4,
        'zhongjun_list': ['中信证券', '东方财富'],
        'zhongjun_avg_change': 2,  # 中军响应弱！
        'zhongjun_turnover_ratio': 1.2,
        'zhongjun_vs_ma5': -0.02,
        'volume_ratio': 2.5,  # 暴量！
        'index_change': 4.0,
        'market_sentiment': 'warm'
    }
    
    result2 = detector.detect_early_summer(case2_day1)
    
    print("\n" + "=" * 80)
    print("案例2：2024-09 金融（假夏长）")
    print("=" * 80)
    print(f"Day1日期: {case2_day1['date']}")
    print(f"总分: {result2['score']}分")
    print(f"是否真夏长启动: {result2['is_early_summer']}")
    print(f"置信度: {result2['confidence']}")
    print(f"风险等级: {result2['risk_level']}")
    print(f"建议: {result2['suggestion']}")
    print("\n关键信号:")
    for category, signal in result2['signals'].items():
        print(f"\n  {category}:")
        for obs in signal.get('key_observations', []):
            print(f"    {obs}")


# ========== 主函数 ==========

def main():
    """主函数"""
    validate_with_historical_cases()


if __name__ == '__main__':
    main()
