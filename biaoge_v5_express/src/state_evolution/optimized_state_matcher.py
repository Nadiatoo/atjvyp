"""
优化状态匹配器 - 修复版
"""

import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from dataclasses import dataclass
from enum import Enum

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
        features = [
            self.technical_score / 100.0,
            self.rise_ratio,
            max(-1.0, min(1.0, self.average_change / 10.0)),  # 归一化到[-1, 1]
            min(1.0, self.limit_up_count / 100.0),  # 归一化
            min(1.0, self.limit_down_count / 50.0),  # 归一化
            max(-1.0, min(1.0, self.northbound_flow / 100.0)),  # 归一化
            max(-1.0, min(1.0, self.main_force_flow / 100.0)),  # 归一化
            min(2.0, self.volume_ratio / 1.5),  # 归一化
            max(0.0, min(1.0, self.market_sentiment)),
            self.fear_greed_index / 100.0,
            max(0.0, min(1.0, self.news_sentiment)),
            max(0.0, min(1.0, (self.policy_impact + 1) / 2.0)),  # 从[-1,1]映射到[0,1]
            max(0.0, min(1.0, self.economic_outlook)),
            max(0.0, min(1.0, self.geopolitical_risk))
        ]
        return np.array(features)


@dataclass
class StatePrediction:
    """状态预测结果"""
    state: MarketState
    confidence: float  # 置信度 (0-1)
    features_match: Dict[str, float]  # 各维度匹配度
    recommended_position: Tuple[float, float]  # 建议仓位范围
    operation_strategy: str  # 操作策略
    risk_level: str  # 风险等级


class OptimizedStateMatcher:
    """优化状态匹配器"""
    
    def __init__(self):
        self.state_prototypes = self._create_state_prototypes()
        self.state_info = self._create_state_info()
        logger.info("优化状态匹配器初始化完成")
    
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
    
    def _create_state_info(self) -> Dict[MarketState, Dict[str, Any]]:
        """创建状态信息"""
        return {
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
    
    def predict_state(self, features: MarketFeatures) -> List[StatePrediction]:
        """预测市场状态"""
        predictions = []
        
        for state, prototype in self.state_prototypes.items():
            # 计算相似度
            similarity = self._calculate_similarity(features, prototype)
            
            # 计算特征匹配度
            feature_match = self._calculate_feature_match(features, prototype)
            
            # 计算置信度
            confidence = self._calculate_confidence(similarity, feature_match)
            
            # 获取状态信息
            state_info = self.state_info[state]
            
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
    
    def _calculate_similarity(self, current: MarketFeatures, prototype: MarketFeatures) -> float:
        """计算相似度"""
        try:
            vec1 = current.to_vector()
            vec2 = prototype.to_vector()
            
            # 使用余弦相似度
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            
            # 映射到0-1范围
            return max(0.0, min(1.0, (similarity + 1) / 2.0))
            
        except Exception as e:
            logger.error(f"计算相似度失败: {e}")
            return 0.5  # 默认相似度
    
    def _calculate_feature_match(self, current: MarketFeatures, prototype: MarketFeatures) -> Dict[str, float]:
        """计算特征匹配度"""
        match_scores = {}
        
        try:
            # 技术面匹配
            tech_diff = abs(current.technical_score - prototype.technical_score) / 100.0
            match_scores["technical"] = max(0.0, min(1.0, 1.0 - tech_diff))
            
            rise_diff = abs(current.rise_ratio - prototype.rise_ratio)
            match_scores["rise_ratio"] = max(0.0, min(1.0, 1.0 - rise_diff))
            
            change_diff = abs(current.average_change - prototype.average_change) / 10.0
            match_scores["average_change"] = max(0.0, min(1.0, 1.0 - change_diff))
            
            # 情绪面匹配
            sentiment_diff = abs(current.market_sentiment - prototype.market_sentiment)
            match_scores["market_sentiment"] = max(0.0, min(1.0, 1.0 - sentiment_diff))
            
            # 宏观面匹配
            policy_diff = abs(current.policy_impact - prototype.policy_impact) / 2.0
            match_scores["policy_impact"] = max(0.0, min(1.0, 1.0 - policy_diff))
            
        except Exception as e:
            logger.error(f"计算特征匹配度失败: {e}")
        
        return match_scores
    
    def _calculate_confidence(self, similarity: float, feature_match: Dict[str, float]) -> float:
        """计算置信度"""
        try:
            if not feature_match:
                return similarity
            
            # 计算特征匹配度的加权平均
            weights = {
                "technical": 0.4,
                "rise_ratio": 0.3,
                "average_change": 0.2,
                "market_sentiment": 0.05,
                "policy_impact": 0.05
            }
            
            weighted_sum = 0.0
            total_weight = 0.0
            
            for feature, match_score in feature_match.items():
                if feature in weights:
                    weighted_sum += match_score * weights[feature]
                    total_weight += weights[feature]
            
            if total_weight > 0:
                feature_confidence = weighted_sum / total_weight
            else:
                feature_confidence = similarity
            
            # 综合相似度和特征匹配度
            confidence = 0.7 * feature_confidence + 0.3 * similarity
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"计算置信度失败: {e}")
            return 0.5  # 默认置信度
    
    def get_top_prediction(self, features: MarketFeatures) -> Optional[StatePrediction]:
        """获取最佳预测"""
        predictions = self.predict_state(features)
        if predictions:
            return predictions[0]
        return None
    
    def get_state_info(self, state: MarketState) -> Dict[str, Any]:
        """获取状态信息"""
        return self.state_info.get(state, {
            "chinese_name": "未知状态",
            "position_range": (0, 20),
            "operation_strategy": "谨慎观望",
            "risk_level": "高"
        })


# 快速测试函数
def quick_test():
    """快速测试"""
    print("🧪 快速测试优化状态匹配器")
    
    matcher = OptimizedStateMatcher()
    
    # 测试案例
    test_cases = [
        ("强势市场", MarketFeatures(
            technical_score=85.0,
            rise_ratio=0.78,
            average_change=2.8,
            limit_up_count=85,
            limit_down_count=3
        )),
        ("弱势市场", MarketFeatures(
            technical_score=25.0,
            rise_ratio=0.28,
            average_change=-2.5,
            limit_up_count=8,
            limit_down_count=48
        ))
    ]
    
    for name, features in test_cases:
        print(f"\n📊 {name}:")
        pred = matcher.get_top_prediction(features)
        if pred:
            state_info = matcher.get_state_info(pred.state)
            print(f"   预测状态: {state_info['chinese_name']}")
            print(f"   置信度: {pred.confidence*100:.1f}%")
            print(f"   建议仓位: {pred.recommended_position[0]}%-{pred.recommended_position[1]}%")
    
    print("\n✅ 快速测试完成")


if __name__ == "__main__":
    quick_test()
