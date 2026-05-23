"""
彪哥战法v5.0 - 第3步：优化状态匹配算法（续）
"""

import sys
import os
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketState(Enum):
    """市场状态枚举"""
    WINTER_HIDING = "winter_hiding"  # 冬藏期
    WINTER_SPRING_TRANSITION = "winter_spring_transition"  # 冬末春初过渡期
    SPRING_SOWING = "spring_sowing"  # 春播期
    SPRING_SUMMER_TRANSITION = "spring_summer_transition"  # 春入夏过渡期
    SUMMER_GROWING = "summer_growing"  # 夏长期
    SUMMER_AUTUMN_TRANSITION = "summer_autumn_transition"  # 夏末秋初过渡期
    AUTUMN_HARVEST = "autumn_harvest"  # 秋收期
    AUTUMN_WINTER_TRANSITION = "autumn_winter_transition"  # 秋入冬过渡期
    CHAOTIC_PERIOD = "chaotic_period"  # 混沌期


@dataclass
class MarketFeatures:
    """市场特征"""
    # 技术面特征
    technical_score: float  # 技术评分 (0-100)
    rise_ratio: float  # 上涨比例 (0-1)
    average_change: float  # 平均涨跌幅 (%)
    limit_up_count: int  # 涨停家数
    limit_down_count: int  # 跌停家数
    
    # 资金面特征
    northbound_flow: float = 0.0  # 北向资金净流入 (亿元)
    main_force_flow: float = 0.0  # 主力资金净流入 (亿元)
    volume_ratio: float = 1.0  # 量比
    
    # 情绪面特征
    market_sentiment: float = 0.5  # 市场情绪 (0-1)
    fear_greed_index: float = 50.0  # 恐慌贪婪指数 (0-100)
    news_sentiment: float = 0.5  # 新闻情绪 (0-1)
    
    # 宏观面特征
    policy_impact: float = 0.0  # 政策影响 (-1到1，负数为利空，正数为利好)
    economic_outlook: float = 0.5  # 经济展望 (0-1)
    geopolitical_risk: float = 0.5  # 地缘政治风险 (0-1)
    
    def to_vector(self) -> np.ndarray:
        """转换为特征向量"""
        return np.array([
            self.technical_score / 100.0,
            self.rise_ratio,
            self.average_change / 10.0,  # 归一化到[-1, 1]
            self.limit_up_count / 100.0,  # 归一化
            self.limit_down_count / 50.0,  # 归一化
            self.northbound_flow / 100.0,  # 归一化
            self.main_force_flow / 100.0,  # 归一化
            self.volume_ratio / 3.0,  # 归一化
            self.market_sentiment,
            self.fear_greed_index / 100.0,
            self.news_sentiment,
            (self.policy_impact + 1) / 2.0,  # 从[-1,1]映射到[0,1]
            self.economic_outlook,
            self.geopolitical_risk
        ])


@dataclass
class StatePrediction:
    """状态预测结果"""
    state: MarketState
    confidence: float  # 置信度 (0-1)
    features_match: Dict[str, float]  # 各维度匹配度
    recommended_position: Tuple[float, float]  # 建议仓位范围
    operation_strategy: str  # 操作策略
    risk_level: str  # 风险等级


class StateMatchingOptimizer:
    """状态匹配优化器"""
    
    def __init__(self):
        self.state_prototypes = self._create_state_prototypes()
        self.feature_weights = self._create_feature_weights()
        logger.info("状态匹配优化器初始化完成")
    
    def _create_state_prototypes(self) -> Dict[MarketState, MarketFeatures]:
        """创建状态原型特征"""
        return {
            MarketState.WINTER_HIDING: MarketFeatures(
                technical_score=20.0,
                rise_ratio=0.3,
                average_change=-2.0,
                limit_up_count=10,
                limit_down_count=50,
                market_sentiment=0.2,
                fear_greed_index=20.0,
                news_sentiment=0.3,
                policy_impact=0.0,
                economic_outlook=0.4,
                geopolitical_risk=0.6
            ),
            MarketState.WINTER_SPRING_TRANSITION: MarketFeatures(
                technical_score=35.0,
                rise_ratio=0.45,
                average_change=-0.5,
                limit_up_count=25,
                limit_down_count=30,
                market_sentiment=0.4,
                fear_greed_index=35.0,
                news_sentiment=0.45,
                policy_impact=0.1,
                economic_outlook=0.5,
                geopolitical_risk=0.5
            ),
            MarketState.SPRING_SOWING: MarketFeatures(
                technical_score=50.0,
                rise_ratio=0.55,
                average_change=0.5,
                limit_up_count=40,
                limit_down_count=20,
                market_sentiment=0.6,
                fear_greed_index=50.0,
                news_sentiment=0.6,
                policy_impact=0.2,
                economic_outlook=0.6,
                geopolitical_risk=0.4
            ),
            MarketState.SPRING_SUMMER_TRANSITION: MarketFeatures(
                technical_score=65.0,
                rise_ratio=0.65,
                average_change=1.5,
                limit_up_count=60,
                limit_down_count=10,
                market_sentiment=0.7,
                fear_greed_index=65.0,
                news_sentiment=0.7,
                policy_impact=0.3,
                economic_outlook=0.7,
                geopolitical_risk=0.3
            ),
            MarketState.SUMMER_GROWING: MarketFeatures(
                technical_score=80.0,
                rise_ratio=0.75,
                average_change=2.5,
                limit_up_count=80,
                limit_down_count=5,
                market_sentiment=0.85,
                fear_greed_index=80.0,
                news_sentiment=0.8,
                policy_impact=0.4,
                economic_outlook=0.8,
                geopolitical_risk=0.2
            ),
            MarketState.SUMMER_AUTUMN_TRANSITION: MarketFeatures(
                technical_score=70.0,
                rise_ratio=0.65,
                average_change=1.0,
                limit_up_count=50,
                limit_down_count=15,
                market_sentiment=0.6,
                fear_greed_index=60.0,
                news_sentiment=0.6,
                policy_impact=0.2,
                economic_outlook=0.6,
                geopolitical_risk=0.4
            ),
            MarketState.AUTUMN_HARVEST: MarketFeatures(
                technical_score=55.0,
                rise_ratio=0.5,
                average_change=0.0,
                limit_up_count=30,
                limit_down_count=25,
                market_sentiment=0.5,
                fear_greed_index=45.0,
                news_sentiment=0.5,
                policy_impact=0.1,
                economic_outlook=0.5,
                geopolitical_risk=0.5
            ),
            MarketState.AUTUMN_WINTER_TRANSITION: MarketFeatures(
                technical_score=40.0,
                rise_ratio=0.4,
                average_change=-1.0,
                limit_up_count=20,
                limit_down_count=35,
                market_sentiment=0.3,
                fear_greed_index=30.0,
                news_sentiment=0.4,
                policy_impact=0.0,
                economic_outlook=0.4,
                geopolitical_risk=0.6
            ),
            MarketState.CHAOTIC_PERIOD: MarketFeatures(
                technical_score=45.0,
                rise_ratio=0.5,
                average_change=0.0,
                limit_up_count=35,
                limit_down_count=35,
                market_sentiment=0.5,
                fear_greed_index=50.0,
                news_sentiment=0.5,
                policy_impact=0.0,
                economic_outlook=0.5,
                geopolitical_risk=0.5
            )
        }
    
    def _create_feature_weights(self) -> Dict[str, float]:
        """创建特征权重"""
        return {
            "technical_score": 0.25,  # 技术面权重
            "rise_ratio": 0.15,
            "average_change": 0.10,
            "limit_up_count": 0.05,
            "limit_down_count": 0.05,
            "northbound_flow": 0.10,  # 资金面权重
            "main_force_flow": 0.08,
            "volume_ratio": 0.02,
            "market_sentiment": 0.06,  # 情绪面权重
            "fear_greed_index": 0.04,
            "news_sentiment": 0.03,
            "policy_impact": 0.04,  # 宏观面权重
            "economic_outlook": 0.02,
            "geopolitical_risk": 0.01
        }
    
    def _get_state_info(self, state: MarketState) -> Dict[str, Any]:
        """获取状态信息"""
        state_info = {
            MarketState.WINTER_HIDING: {
                "chinese_name": "冬藏期",
                "position_range": (0, 20),
                "operation_strategy": "空仓观望，等待明确信号",
                "risk_level": "高"
            },
            MarketState.WINTER_SPRING_TRANSITION: {
                "chinese_name": "冬末春初过渡期",
                "position_range": (10, 30),
                "operation_strategy": "小仓位试错，布局超跌反弹",
                "risk_level": "中高"
            },
            MarketState.SPRING_SOWING: {
                "chinese_name": "春播期",
                "position_range": (30, 50),
                "operation_strategy": "分批建仓，布局优质标的",
                "risk_level": "中"
            },
            MarketState.SPRING_SUMMER_TRANSITION: {
                "chinese_name": "春入夏过渡期",
                "position_range": (40, 60),
                "operation_strategy": "适度加仓，持有趋势股",
                "risk_level": "中低"
            },
            MarketState.SUMMER_GROWING: {
                "chinese_name": "夏长期",
                "position_range": (50, 80),
                "operation_strategy": "重仓持股，趋势持有",
                "risk_level": "低"
            },
            MarketState.SUMMER_AUTUMN_TRANSITION: {
                "chinese_name": "夏末秋初过渡期",
                "position_range": (40, 60),
                "operation_strategy": "分批减仓，锁定利润",
                "risk_level": "中低"
            },
            MarketState.AUTUMN_HARVEST: {
                "chinese_name": "秋收期",
                "position_range": (20, 40),
                "operation_strategy": "获利了结，转向防御",
                "risk_level": "中"
            },
            MarketState.AUTUMN_WINTER_TRANSITION: {
                "chinese_name": "秋入冬过渡期",
                "position_range": (10, 30),
                "operation_strategy": "控制仓位，防御为主",
                "risk_level": "中高"
            },
            MarketState.CHAOTIC_PERIOD: {
                "chinese_name": "混沌期",
                "position_range": (10, 30),
                "operation_strategy": "观望等待，小仓位试错",
                "risk_level": "中高"
            }
        }
        
        return state_info.get(state, {
            "chinese_name": "未知状态",
            "position_range": (0, 20),
            "operation_strategy": "谨慎观望",
            "risk_level": "高"
        })
    
    def predict_state(self, features: MarketFeatures) -> List[StatePrediction]:
        """预测市场状态"""
        current_vector = features.to_vector()
        
        predictions = []
        
        for state, prototype in self.state_prototypes.items():
            # 计算相似度
            prototype_vector = prototype.to_vector()
            similarity = self._calculate_similarity(current_vector, prototype_vector)
            
            # 计算各维度匹配度
            feature_match = self._calculate_feature_match(features, prototype)
            
            # 计算综合置信度
            confidence = self._calculate_confidence(similarity, feature_match)
            
            # 获取状态信息
            state_info = self._get_state_info(state)
            
            prediction = StatePrediction(
                state=state,
                confidence=confidence,
                features_match=feature_match,
                recommended_position=state_info["position_range"],
                operation_strategy=state_info["operation_strategy"],
                risk_level=state_info["risk_level"]
            )
            
            predictions.append(prediction)
        
        # 按置信度排序
        predictions.sort(key=lambda x: x.confidence, reverse=True)
        
        return predictions
    
    def _calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算向量相似度"""
        # 使用余弦相似度
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # 映射到0-1范围
        return (similarity + 1) / 2.0
    
    def _calculate_feature_match(self, current: MarketFeatures, prototype: MarketFeatures) -> Dict[str, float]:
        """计算各维度匹配度"""
        match_scores = {}
        
        # 技术面匹配
        tech_diff = abs(current.technical_score - prototype.technical_score) / 100.0
        match_scores["technical"] = 1.0 - tech_diff
        
        rise_diff = abs(current.rise_ratio - prototype.rise_ratio)
        match_scores["rise_ratio"] = 1.0 - rise_diff
        
        change_diff = abs(current.average_change - prototype.average_change) / 10.0
        match_scores["average_change"] = 1.0 - change_diff
        
        # 资金面匹配（如果有数据）
        if current.northbound_flow != 0 or prototype.northbound_flow != 0:
            flow_diff = abs(current.northbound_flow - prototype.northbound_flow) / 100.0
            match_scores["northbound_flow"] = 1.0 - min(flow_diff, 1.0)
        
        # 情绪面匹配
        sentiment_diff = abs(current.market_sentiment - prototype.market_sentiment)
        match_scores["market_sentiment"] = 1.0 - sentiment_diff
        
        # 宏观面匹配
        policy_diff = abs(current.policy_impact - prototype.policy_impact) / 2.0
        match_scores["policy_impact"] = 1.0 - policy_diff
        
        return match_scores
    
    def _calculate_confidence(self, similarity: float, feature_match: Dict[str, float]) -> float:
        """计算综合置信度"""
        if not feature_match:
            return similarity
        
        # 加权平均
        total_weight = 0.0
        weighted_sum = 0.0
        
        # 技术面权重
        tech_weights = {
            "technical": 0.4,
            "rise_ratio": 0.3,
            "average_change": 0.3
        }
        
        for feature, match_score in feature_match.items():
            if feature in tech_weights:
                weight = tech_weights[feature] * 0.6  # 技术面占总权重60%
            elif feature in ["northbound_flow", "main_force_flow"]:
                weight = 0.15  # 资金面权重
            elif feature in ["market_sentiment", "fear_greed_index"]:
                weight = 0.15  # 情绪面权重
            elif feature in ["policy_impact", "economic_outlook"]:
                weight = 0.10  # 宏观面权重
            else:
                weight = 0.05  # 其他特征
            
            weighted_sum += match_score * weight
            total_weight += weight
        
        if total_weight > 0:
            feature_confidence = weighted_sum / total_weight
        else:
            feature_confidence = similarity
        
        # 综合相似度和特征匹配度
        confidence = 0.7 * feature_confidence + 0.3