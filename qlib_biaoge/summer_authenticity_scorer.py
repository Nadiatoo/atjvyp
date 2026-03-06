#!/usr/bin/env python3
"""
彪哥战法 - 真夏长识别系统 v2.0
新增中军健康度分析维度
"""

from typing import Dict, List, Tuple
import pandas as pd
import numpy as np


class SummerAuthenticityScorer:
    """
    真夏长识别评分器 v2.0
    
    核心维度：
    1. 板块持续性 (20%) - 主线是否清晰持续
    2. 量能质量 (20%) - 成交量是否健康
    3. 龙头高度 (15%) - 连板高度和持续性
    4. 跟风生态 (15%) - 梯队是否完整
    5. 指数共振 (10%) - 与大盘是否共振
    6. 中军健康度 (20%) - 新增核心维度
    """
    
    def __init__(self):
        self.weights = {
            'sector_duration': 0.20,      # 板块持续性
            'volume_quality': 0.20,        # 量能质量
            'leader_height': 0.15,         # 龙头高度
            'follower_ecosystem': 0.15,    # 跟风生态
            'index_resonance': 0.10,       # 指数共振
            'zhongjun_health': 0.20,       # 中军健康度 (新增)
        }
    
    def calculate_score(self, market_data: dict) -> dict:
        """
        计算真夏长评分
        
        Args:
            market_data: 市场数据字典，包含以下关键字段：
                # 板块数据
                - main_sector_duration: 主线持续天数
                - sector_rotation_speed: 板块轮动速度
                
                # 量能数据
                - current_volume: 当前成交额
                - avg_volume_20d: 20日均成交额
                - volume_trend: 量能趋势
                
                # 龙头数据
                - max_limit_up: 最高连板数
                - leader_rebounce: 是否断板反包
                - a_shaped_kill: 是否A字杀
                
                # 跟风数据
                - follower_batch_count: 批量跟风家数
                - sector_ladder_complete: 梯队是否完整
                - sector_limit_up_ratio: 板块涨停占比
                
                # 指数数据
                - index_vs_ma5: 指数相对5日线位置
                - index_vs_ma20: 指数相对20日线位置
                - sector_index_correlation: 板块与指数相关性
                
                # 中军数据 (新增)
                - zhongjun_list: 中军股票列表
                - zhongjun_avg_change: 中军平均涨跌幅
                - zhongjun_recover_speed: 中军杀跌后收回速度
                - zhongjun_volume_active: 中军成交活跃度
                - zhongjun_loss_effect: 中军亏钱效应
        
        Returns:
            {
                'total_score': 总分,
                'is_real_summer': 是否真夏长,
                'confidence': 置信度,
                'details': 各维度得分,
                'suggestion': 操作建议,
                'zhongjun_analysis': 中军专项分析
            }
        """
        scores = {}
        
        # 1. 板块持续性评分 (0-20分)
        scores['sector_duration'] = self._score_sector_duration(
            market_data.get('main_sector_duration', 0),
            market_data.get('sector_rotation_speed', 0)
        )
        
        # 2. 量能质量评分 (0-20分)
        scores['volume_quality'] = self._score_volume_quality(
            market_data.get('current_volume', 0),
            market_data.get('avg_volume_20d', 0),
            market_data.get('volume_trend', 0)
        )
        
        # 3. 龙头高度评分 (0-15分)
        scores['leader_height'] = self._score_leader_height(
            market_data.get('max_limit_up', 0),
            market_data.get('leader_rebounce', False),
            market_data.get('a_shaped_kill', False)
        )
        
        # 4. 跟风生态评分 (0-15分)
        scores['follower_ecosystem'] = self._score_follower_ecosystem(
            market_data.get('follower_batch_count', 0),
            market_data.get('sector_ladder_complete', False),
            market_data.get('sector_limit_up_ratio', 0)
        )
        
        # 5. 指数共振评分 (0-10分)
        scores['index_resonance'] = self._score_index_resonance(
            market_data.get('index_vs_ma5', 0),
            market_data.get('index_vs_ma20', 0),
            market_data.get('sector_index_correlation', 0)
        )
        
        # 6. 中军健康度评分 (0-20分) - 新增核心维度
        scores['zhongjun_health'] = self._score_zhongjun_health(
            market_data.get('zhongjun_list', []),
            market_data.get('zhongjun_avg_change', 0),
            market_data.get('zhongjun_recover_speed', 0),
            market_data.get('zhongjun_volume_active', 0),
            market_data.get('zhongjun_loss_effect', 0)
        )
        
        # 计算加权总分
        total_score = sum(
            scores[key] * self.weights[key] 
            for key in scores
        )
        
        # 判断结果
        is_real_summer = total_score >= 70
        
        # 中军专项分析
        zhongjun_analysis = self._analyze_zhongjun_detail(market_data)
        
        return {
            'total_score': round(total_score, 1),
            'is_real_summer': is_real_summer,
            'confidence': '高' if total_score >= 80 else '中' if total_score >= 70 else '低',
            'details': scores,
            'suggestion': self._generate_suggestion(total_score, is_real_summer, scores),
            'zhongjun_analysis': zhongjun_analysis
        }
    
    def _score_sector_duration(self, duration: int, rotation_speed: float) -> float:
        """板块持续性评分 (0-20分)"""
        if duration >= 15 and rotation_speed < 0.3:
            return 20
        elif duration >= 10:
            return 16
        elif duration >= 5:
            return 12
        else:
            return max(4, duration * 2)
    
    def _score_volume_quality(self, current: float, avg_20d: float, trend: float) -> float:
        """量能质量评分 (0-20分)"""
        ratio = current / avg_20d if avg_20d > 0 else 1
        
        if 1.2 <= ratio <= 1.5 and trend > 0:
            return 20
        elif 0.9 <= ratio <= 1.2:
            return 16
        elif ratio < 0.9 or ratio > 2.0:
            return 10
        else:
            return 12
    
    def _score_leader_height(self, max_limit: int, rebounce: bool, a_kill: bool) -> float:
        """龙头高度评分 (0-15分)"""
        if a_kill:
            return 0
        
        rebounce_bonus = 3 if rebounce else 0
        
        if max_limit >= 8:
            return min(15, 12 + rebounce_bonus)
        elif max_limit >= 5:
            return min(15, 10 + rebounce_bonus)
        elif max_limit >= 3:
            return min(15, 7 + rebounce_bonus)
        else:
            return 4
    
    def _score_follower_ecosystem(self, batch_count: int, ladder: bool, ratio: float) -> float:
        """跟风生态评分 (0-15分)"""
        if batch_count >= 10 and ladder:
            return 15
        elif batch_count >= 5 and ladder:
            return 12
        elif batch_count >= 5:
            return 9
        elif batch_count < 3:
            return 3
        else:
            return 7
    
    def _score_index_resonance(self, vs_ma5: float, vs_ma20: float, correlation: float) -> float:
        """指数共振评分 (0-10分)"""
        if vs_ma5 > 0 and vs_ma20 > 0 and correlation > 0.6:
            return 10
        elif vs_ma5 > 0 and correlation > 0.4:
            return 7
        elif abs(vs_ma5) < 0.02:
            return 5
        else:
            return 2
    
    def _score_zhongjun_health(self, zhongjun_list: list, avg_change: float, 
                                recover_speed: float, volume_active: float, 
                                loss_effect: float) -> float:
        """
        中军健康度评分 (0-20分) - 核心新增维度
        
        评分标准：
        - 中军平均涨幅 > 3%：+5分
        - 杀跌后快速收回（<2天）：+5分
        - 成交活跃（>10亿/日）：+5分
        - 无亏钱效应（跌幅<5%家数<20%）：+5分
        """
        score = 0
        
        # 1. 中军平均涨幅 (0-5分)
        if avg_change >= 5:
            score += 5
        elif avg_change >= 3:
            score += 4
        elif avg_change >= 1:
            score += 3
        elif avg_change >= -2:
            score += 2
        else:
            score += 0  # 负收益=不健康
        
        # 2. 杀跌收回速度 (0-5分)
        # recover_speed: 平均收回天数，越小越好
        if recover_speed <= 1:
            score += 5
        elif recover_speed <= 2:
            score += 4
        elif recover_speed <= 3:
            score += 3
        elif recover_speed <= 5:
            score += 2
        else:
            score += 0  # 收回太慢=不健康
        
        # 3. 成交活跃度 (0-5分)
        # volume_active: 中军平均成交额（亿）
        if volume_active >= 20:
            score += 5
        elif volume_active >= 10:
            score += 4
        elif volume_active >= 5:
            score += 3
        elif volume_active >= 2:
            score += 2
        else:
            score += 1
        
        # 4. 亏钱效应 (0-5分)
        # loss_effect: 跌幅>5%的中军占比
        if loss_effect <= 0.1:  # <10%
            score += 5
        elif loss_effect <= 0.2:  # <20%
            score += 4
        elif loss_effect <= 0.3:  # <30%
            score += 3
        elif loss_effect <= 0.5:  # <50%
            score += 2
        else:
            score += 0  # 大面积亏钱=不健康
        
        return score
    
    def _analyze_zhongjun_detail(self, market_data: dict) -> dict:
        """
        中军专项详细分析
        """
        zhongjun_list = market_data.get('zhongjun_list', [])
        
        analysis = {
            '中军数量': len(zhongjun_list),
            '健康状态': '',
            '关键信号': [],
            '风险提示': []
        }
        
        # 分析中军健康状态
        avg_change = market_data.get('zhongjun_avg_change', 0)
        recover_speed = market_data.get('zhongjun_recover_speed', 0)
        loss_effect = market_data.get('zhongjun_loss_effect', 0)
        
        # 健康状态判定
        if avg_change >= 3 and recover_speed <= 2 and loss_effect <= 0.2:
            analysis['健康状态'] = '🟢 健康'
        elif avg_change >= 0 and recover_speed <= 3 and loss_effect <= 0.3:
            analysis['健康状态'] = '🟡 亚健康'
        else:
            analysis['健康状态'] = '🔴 不健康'
        
        # 关键信号
        if recover_speed <= 1:
            analysis['关键信号'].append('✅ 杀跌快速收回，资金承接强')
        if market_data.get('zhongjun_volume_active', 0) >= 10:
            analysis['关键信号'].append('✅ 大资金成交活跃')
        if avg_change >= 5:
            analysis['关键信号'].append('✅ 中军集体大涨，板块强势')
        
        # 风险提示
        if recover_speed > 3:
            analysis['风险提示'].append('⚠️ 杀跌收回慢，资金信心不足')
        if loss_effect > 0.3:
            analysis['风险提示'].append('⚠️ 中军亏钱效应明显')
        if avg_change < -2:
            analysis['风险提示'].append('⚠️ 中军集体下跌，板块退潮')
        
        return analysis
    
    def _generate_suggestion(self, score: float, is_real: bool, details: dict) -> str:
        """生成操作建议"""
        # 特别关注中军健康度
        zhongjun_score = details.get('zhongjun_health', 0)
        
        if score >= 80 and zhongjun_score >= 15:
            return "🟢 真夏长确认，中军健康，重仓持有"
        elif score >= 80 and zhongjun_score < 15:
            return "🟡 疑似真夏长，但中军偏弱，控制仓位"
        elif score >= 70:
            return "🟡 疑似真夏长，可重仓但需密切监控中军"
        elif score >= 50:
            return "🟠 假夏长概率大，中军不稳，准备撤退"
        else:
            return "🔴 假夏长确认，中军亏钱，减仓清仓"


# ========== 实战使用示例 ==========

def example_usage():
    """使用示例"""
    
    scorer = SummerAuthenticityScorer()
    
    # 示例1: 真夏长场景（2024年2月AI行情）
    real_summer_data = {
        'main_sector_duration': 18,      # AI持续18天
        'sector_rotation_speed': 0.2,     # 轮动慢
        'current_volume': 22000,          # 2.2万亿
        'avg_volume_20d': 18000,
        'volume_trend': 1.2,
        'max_limit_up': 7,                # 7板龙头
        'leader_rebounce': True,          # 断板反包
        'a_shaped_kill': False,
        'follower_batch_count': 15,       # 15家跟风
        'sector_ladder_complete': True,   # 梯队完整
        'sector_limit_up_ratio': 0.15,
        'index_vs_ma5': 0.02,
        'index_vs_ma20': 0.05,
        'sector_index_correlation': 0.7,
        # 中军数据
        'zhongjun_list': ['中际旭创', '新易盛', '天孚通信', '工业富联'],
        'zhongjun_avg_change': 6.5,       # 中军平均涨6.5%
        'zhongjun_recover_speed': 1.2,    # 平均1.2天收回
        'zhongjun_volume_active': 15,     # 平均成交15亿
        'zhongjun_loss_effect': 0.05,     # 仅5%中军亏钱
    }
    
    result = scorer.calculate_score(real_summer_data)
    print("=== 真夏长案例 ===")
    print(f"总分: {result['total_score']}")
    print(f"是否真夏长: {result['is_real_summer']}")
    print(f"置信度: {result['confidence']}")
    print(f"建议: {result['suggestion']}")
    print(f"\n各维度得分:")
    for key, score in result['details'].items():
        print(f"  {key}: {score}")
    print(f"\n中军分析:")
    print(f"  健康状态: {result['zhongjun_analysis']['健康状态']}")
    print(f"  关键信号: {result['zhongjun_analysis']['关键信号']}")
    
    # 示例2: 假夏长场景（2024年9月金融行情）
    fake_summer_data = {
        'main_sector_duration': 5,        # 仅5天
        'sector_rotation_speed': 0.6,     # 轮动快
        'current_volume': 35000,          # 暴量3.5万亿
        'avg_volume_20d': 18000,
        'volume_trend': 1.8,
        'max_limit_up': 4,                # 仅4板
        'leader_rebounce': False,
        'a_shaped_kill': True,            # A字杀
        'follower_batch_count': 3,        # 仅3家跟风
        'sector_ladder_complete': False,
        'sector_limit_up_ratio': 0.08,
        'index_vs_ma5': 0.01,
        'index_vs_ma20': -0.02,
        'sector_index_correlation': 0.3,
        # 中军数据
        'zhongjun_list': ['中信证券', '东方财富'],
        'zhongjun_avg_change': -1.5,      # 中军平均跌1.5%
        'zhongjun_recover_speed': 4.5,    # 平均4.5天收回（慢）
        'zhongjun_volume_active': 25,     # 成交活跃但出货
        'zhongjun_loss_effect': 0.4,      # 40%中军亏钱
    }
    
    result2 = scorer.calculate_score(fake_summer_data)
    print("\n=== 假夏长案例 ===")
    print(f"总分: {result2['total_score']}")
    print(f"是否真夏长: {result2['is_real_summer']}")
    print(f"置信度: {result2['confidence']}")
    print(f"建议: {result2['suggestion']}")
    print(f"\n中军分析:")
    print(f"  健康状态: {result2['zhongjun_analysis']['健康状态']}")
    print(f"  风险提示: {result2['zhongjun_analysis']['风险提示']}")


if __name__ == '__main__':
    example_usage()
