"""
动态状态演化系统 - 演化引擎
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from dataclasses import dataclass

from .state_definitions import MarketState, StateDefinition, get_state_definition
from .factor_monitor import FactorMonitor, Factor, FactorImpactLevel, FactorDirection

logger = logging.getLogger(__name__)


@dataclass
class StateTransition:
    """状态转换"""
    from_state: MarketState
    to_state: MarketState
    probability: float  # 转换概率 0-100
    confidence: float   # 置信度 0-100
    expected_duration_days: int  # 预计持续时间
    transition_type: str  # 转换类型: normal, jump, revert, stay
    influencing_factors: List[Dict[str, Any]]  # 影响因素
    description: str


class StateEvolutionEngine:
    """状态演化引擎"""
    
    def __init__(self, factor_monitor: FactorMonitor):
        self.factor_monitor = factor_monitor
        self.current_state: Optional[MarketState] = None
        self.state_history: List[Dict[str, Any]] = []
        self.transition_rules = self.load_transition_rules()
        
        logger.info("状态演化引擎初始化完成")
    
    def load_transition_rules(self) -> Dict[str, Any]:
        """加载转换规则"""
        # 这里可以从配置文件或数据库加载
        # 暂时使用硬编码规则
        
        rules = {
            "normal_evolution": {
                # 正常演进规则（无重大因素影响）
                MarketState.WINTER: {
                    "next_states": [
                        {"state": MarketState.WINTER_SPRING_TRANSITION, "probability": 70},
                        {"state": MarketState.WINTER, "probability": 25},
                        {"state": MarketState.CHAOS, "probability": 5}
                    ]
                },
                MarketState.WINTER_SPRING_TRANSITION: {
                    "next_states": [
                        {"state": MarketState.SPRING, "probability": 60},
                        {"state": MarketState.WINTER, "probability": 30},
                        {"state": MarketState.CHAOS, "probability": 10}
                    ]
                },
                MarketState.SPRING: {
                    "next_states": [
                        {"state": MarketState.SPRING_SUMMER_TRANSITION, "probability": 65},
                        {"state": MarketState.AUTUMN, "probability": 25},
                        {"state": MarketState.CHAOS, "probability": 10}
                    ]
                },
                # ... 其他状态的正常演进规则
            },
            "jump_rules": [
                # 跳跃规则（重大因素导致状态跳跃）
                {
                    "rule_id": "JUMP_001",
                    "condition": "current_state == 'WINTER' and has_factor('policy_change', 'very_high', 'bullish')",
                    "action": "jump_to('SPRING_SUMMER_TRANSITION')",
                    "probability": 80,
                    "description": "强政策刺激可能让市场从冬藏直接进入春入夏过渡期"
                },
                {
                    "rule_id": "JUMP_002",
                    "condition": "current_state == 'SUMMER' and has_factor('geopolitical_event', 'very_high', 'bearish')",
                    "action": "jump_to('AUTUMN_WINTER_TRANSITION')",
                    "probability": 90,
                    "description": "高强度战争可能让市场从夏长直接跳入秋入冬过渡期"
                },
                {
                    "rule_id": "JUMP_003",
                    "condition": "current_state == 'AUTUMN' and has_factor('industry_breakthrough', 'high', 'bullish')",
                    "action": "revert_to('SUMMER')",
                    "probability": 60,
                    "description": "重大行业突破可能让市场从秋收回退到夏长"
                },
                {
                    "rule_id": "JUMP_004",
                    "condition": "technical_score < 40 and volatility > 70 for 10_days",
                    "action": "enter_state('CHAOS')",
                    "probability": 70,
                    "description": "长期技术弱势高波动可能进入混沌期"
                }
            ],
            "stay_rules": [
                # 停滞规则（状态保持）
                {
                    "rule_id": "STAY_001",
                    "condition": "no_major_factors and technical_score between 45 and 55",
                    "action": "stay_in_current_state()",
                    "probability": 80,
                    "description": "无重大因素且技术面中性可能状态停滞"
                }
            ]
        }
        
        return rules
    
    def set_current_state(self, state: MarketState, confidence: float = 80.0):
        """设置当前状态"""
        self.current_state = state
        
        state_record = {
            "state": state.value,
            "chinese_name": get_state_definition(state).chinese_name,
            "timestamp": datetime.now(),
            "confidence": confidence,
            "factors_at_time": [f.to_dict() for f in self.factor_monitor.get_active_factors()]
        }
        
        self.state_history.append(state_record)
        logger.info(f"设置当前状态: {get_state_definition(state).chinese_name} (置信度: {confidence}%)")
    
    def analyze_current_market(self, technical_score: float, market_data: Dict[str, Any]) -> MarketState:
        """分析当前市场状态"""
        logger.info("开始分析当前市场状态")
        
        try:
            # 1. 获取技术面特征
            technical_features = self.extract_technical_features(technical_score, market_data)
            
            # 2. 获取资金面特征
            fund_features = self.extract_fund_features(market_data)
            
            # 3. 获取情绪面特征
            sentiment_features = self.extract_sentiment_features(market_data)
            
            # 4. 获取宏观面特征
            macro_features = self.extract_macro_features(market_data)
            
            # 5. 综合特征向量
            feature_vector = self.create_feature_vector(
                technical_features, fund_features, sentiment_features, macro_features
            )
            
            # 6. 状态匹配
            matched_state = self.match_state(feature_vector)
            
            # 7. 计算置信度
            confidence = self.calculate_state_confidence(feature_vector, matched_state)
            
            # 8. 设置当前状态
            self.set_current_state(matched_state, confidence)
            
            logger.info(f"市场状态分析完成: {get_state_definition(matched_state).chinese_name} (置信度: {confidence}%)")
            
            return matched_state
            
        except Exception as e:
            logger.error(f"市场状态分析失败: {e}")
            # 返回默认状态
            return MarketState.CHAOS
    
    def extract_technical_features(self, technical_score: float, market_data: Dict[str, Any]) -> Dict[str, float]:
        """提取技术面特征"""
        features = {
            "technical_score": technical_score,
            "rise_ratio": market_data.get("rise_ratio", 0.5),  # 上涨比例
            "limit_up_ratio": market_data.get("limit_up_ratio", 0.05),  # 涨停比例
            "limit_down_ratio": market_data.get("limit_down_ratio", 0.05),  # 跌停比例
            "volatility": market_data.get("volatility", 50.0),  # 波动率
            "trend_strength": market_data.get("trend_strength", 50.0),  # 趋势强度
            "market_breadth": market_data.get("market_breadth", 50.0)  # 市场宽度
        }
        
        return features
    
    def extract_fund_features(self, market_data: Dict[str, Any]) -> Dict[str, float]:
        """提取资金面特征"""
        # 这里应该连接资金数据源
        # 暂时使用模拟数据
        
        features = {
            "fund_inflow_ratio": market_data.get("fund_inflow_ratio", 50.0),  # 资金流入比例
            "main_fund_activity": market_data.get("main_fund_activity", 50.0),  # 主力资金活跃度
            "retail_sentiment": market_data.get("retail_sentiment", 50.0),  # 散户情绪
            "foreign_inflow": market_data.get("foreign_inflow", 50.0),  # 外资流入
            "leverage_level": market_data.get("leverage_level", 50.0)  # 杠杆水平
        }
        
        return features
    
    def extract_sentiment_features(self, market_data: Dict[str, Any]) -> Dict[str, float]:
        """提取情绪面特征"""
        # 这里应该连接情绪数据源
        # 暂时使用模拟数据
        
        features = {
            "sentiment_index": market_data.get("sentiment_index", 50.0),  # 情绪指数
            "news_sentiment": market_data.get("news_sentiment", 50.0),  # 新闻情绪
            "social_media_sentiment": market_data.get("social_media_sentiment", 50.0),  # 社交媒体情绪
            "investor_confidence": market_data.get("investor_confidence", 50.0),  # 投资者信心
            "fear_greed_index": market_data.get("fear_greed_index", 50.0)  # 恐慌贪婪指数
        }
        
        return features
    
    def extract_macro_features(self, market_data: Dict[str, Any]) -> Dict[str, float]:
        """提取宏观面特征"""
        # 这里应该连接宏观数据源
        # 暂时使用模拟数据
        
        features = {
            "policy_environment": market_data.get("policy_environment", 50.0),  # 政策环境
            "economic_outlook": market_data.get("economic_outlook", 50.0),  # 经济展望
            "geopolitical_risk": market_data.get("geopolitical_risk", 50.0),  # 地缘政治风险
            "liquidity_condition": market_data.get("liquidity_condition", 50.0),  # 流动性状况
            "inflation_expectation": market_data.get("inflation_expectation", 50.0)  # 通胀预期
        }
        
        return features
    
    def create_feature_vector(self, technical: Dict, fund: Dict, sentiment: Dict, macro: Dict) -> Dict[str, float]:
        """创建综合特征向量"""
        feature_vector = {}
        
        # 合并所有特征
        feature_vector.update({f"tech_{k}": v for k, v in technical.items()})
        feature_vector.update({f"fund_{k}": v for k, v in fund.items()})
        feature_vector.update({f"sent_{k}": v for k, v in sentiment.items()})
        feature_vector.update({f"macro_{k}": v for k, v in macro.items()})
        
        return feature_vector
    
    def match_state(self, feature_vector: Dict[str, float]) -> MarketState:
        """匹配最相似的状态"""
        # 这里应该使用更复杂的匹配算法
        # 暂时使用基于技术评分的简单匹配
        
        technical_score = feature_vector.get("tech_technical_score", 50.0)
        rise_ratio = feature_vector.get("tech_rise_ratio", 0.5)
        
        # 基于技术评分和上涨比例的简单匹配
        if technical_score >= 70 and rise_ratio >= 0.7:
            return MarketState.SUMMER
        elif technical_score >= 60 and rise_ratio >= 0.6:
            return MarketState.SPRING_SUMMER_TRANSITION
        elif technical_score >= 50 and rise_ratio >= 0.55:
            return MarketState.SPRING
        elif technical_score >= 45 and rise_ratio >= 0.5:
            return MarketState.WINTER_SPRING_TRANSITION
        elif technical_score >= 40 and rise_ratio >= 0.45:
            return MarketState.CHAOS
        elif technical_score >= 30 and rise_ratio >= 0.3:
            return MarketState.AUTUMN
        elif technical_score >= 20 and rise_ratio >= 0.2:
            return MarketState.AUTUMN_WINTER_TRANSITION
        else:
            return MarketState.WINTER
    
    def calculate_state_confidence(self, feature_vector: Dict[str, float], matched_state: MarketState) -> float:
        """计算状态置信度"""
        # 这里应该使用更复杂的置信度计算
        # 暂时使用基于特征一致性的简单计算
        
        technical_score = feature_vector.get("tech_technical_score", 50.0)
        
        # 获取状态定义
        state_def = get_state_definition(matched_state)
        
        # 基于技术评分与状态特征的匹配度
        if matched_state == MarketState.SUMMER:
            # 夏季要求技术评分高
            confidence = min(100, technical_score * 1.2)
        elif matched_state == MarketState.WINTER:
            # 冬季要求技术评分低
            confidence = min(100, (100 - technical_score) * 1.2)
        else:
            # 其他状态
            confidence = 80.0
        
        # 考虑特征一致性
        feature_consistency = self.calculate_feature_consistency(feature_vector, matched_state)
        confidence = confidence * 0.7 + feature_consistency * 0.3
        
        return round(max(0, min(100, confidence)), 1)
    
    def calculate_feature_consistency(self, feature_vector: Dict[str, float], state: MarketState) -> float:
        """计算特征一致性"""
        # 简化实现：检查关键特征是否符合状态特征
        state_def = get_state_definition(state)
        
        consistency_scores = []
        
        # 检查技术特征
        technical_score = feature_vector.get("tech_technical_score", 50.0)
        rise_ratio = feature_vector.get("tech_rise_ratio", 0.5)
        
        if state == MarketState.SUMMER:
            # 夏季应该技术评分高、上涨比例高
            tech_consistency = (technical_score / 100 + rise_ratio) / 2
            consistency_scores.append(tech_consistency * 100)
        elif state == MarketState.WINTER:
            # 冬季应该技术评分低、上涨比例低
            tech_consistency = ((100 - technical_score) / 100 + (1 - rise_ratio)) / 2
            consistency_scores.append(tech_consistency * 100)
        else:
            # 其他状态
            tech_consistency = 1 - abs(technical_score - 50) / 50
            consistency_scores.append(tech_consistency * 100)
        
        if consistency_scores:
            return np.mean(consistency_scores)
        else:
            return 50.0
    
    def predict_next_state(self, current_state: Optional[MarketState] = None) -> List[StateTransition]:
        """预测下一状态"""
        if current_state is None:
            current_state = self.current_state
        
        if current_state is None:
            logger.warning("当前状态未设置，无法预测")
            return []
        
        logger.info(f"开始预测下一状态，当前状态: {get_state_definition(current_state).chinese_name}")
        
        try:
            # 1. 获取活跃因素
            active_factors = self.factor_monitor.get_active_factors()
            
            # 2. 评估因素影响
            factor_impact = self.evaluate_factor_impact(active_factors, current_state)
            
            # 3. 匹配转换规则
            matched_transitions = self.match_transition_rules(current_state, active_factors, factor_impact)
            
            # 4. 生成转换预测
            transitions = self.generate_transition_predictions(current_state, matched_transitions, active_factors)
            
            # 5. 排序（按概率降序）
            transitions.sort(key=lambda t: t.probability, reverse=True)
            
            logger.info(f"状态预测完成，生成{len(transitions)}个可能的转换")
            
            return transitions
            
        except Exception as e:
            logger.error(f"状态预测失败: {e}")
            return []
    
    def evaluate_factor_impact(self, factors: List[Factor], current_state: MarketState) -> Dict[str, Any]:
        """评估因素影响"""
        impact_summary = {
            "has_major_factors": False,
            "bullish_impact": 0.0,
            "bearish_impact": 0.0,
            "jump_risk": 0.0,
            "stay_probability": 0.0,
            "key_factors": []
        }
        
        for factor in factors:
            # 计算因素影响分数
            factor_score = factor.intensity * factor.confidence / 100
            
            # 记录关键因素
            if factor.impact_level in [FactorImpactLevel.VERY_HIGH, FactorImpactLevel.HIGH]:
                impact_summary["has_major_factors"] = True
                impact_summary["key_factors"].append({
                    "factor": factor.to_dict(),
                    "score": factor_score
                })
            
            # 累计多空影响
            if factor.direction == FactorDirection.BULLISH:
                impact_summary["bullish_impact"] += factor_score
            elif factor.direction == FactorDirection.BEARISH:
                impact_summary["bearish_impact"] += factor_score
            
            # 评估跳跃风险
            if factor.impact_level == FactorImpactLevel.VERY_HIGH:
                impact_summary["jump_risk"] += factor_score * 0.01
        
        # 计算停滞概率（无重大因素时较高）
        if not impact_summary["has_major_factors"]:
            impact_summary["stay_probability"] = 80.0  # 无重大因素时80%概率保持状态
        
        return impact_summary
    
    def match_transition_rules(self, current_state: MarketState, factors: List[Factor], 
                              factor_impact