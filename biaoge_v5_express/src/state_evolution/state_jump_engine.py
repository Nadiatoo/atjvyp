"""
状态跳跃引擎 - 第4步实施
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class JumpFactorType(Enum):
    """跳跃因素类型"""
    POLICY_STIMULUS = "policy_stimulus"  # 政策刺激
    WAR_OUTBREAK = "war_outbreak"  # 战争爆发
    INDUSTRY_BREAKTHROUGH = "industry_breakthrough"  # 行业突破
    ECONOMIC_SHOCK = "economic_shock"  # 经济冲击
    FINANCIAL_CRISIS = "financial_crisis"  # 金融危机
    NATURAL_DISASTER = "natural_disaster"  # 自然灾害
    TECH_REVOLUTION = "tech_revolution"  # 技术革命
    REGULATORY_CHANGE = "regulatory_change"  # 监管变化


class JumpIntensity(Enum):
    """跳跃强度"""
    MILD = "mild"  # 轻度
    MODERATE = "moderate"  # 中度
    STRONG = "strong"  # 强烈
    EXTREME = "extreme"  # 极端


@dataclass
class JumpFactor:
    """跳跃因素"""
    factor_type: JumpFactorType
    intensity: JumpIntensity
    description: str
    impact_duration: int  # 影响持续时间（小时）
    confidence: float  # 置信度 (0-1)
    source: str  # 数据来源
    timestamp: datetime
    affected_industries: List[str] = None  # 受影响行业
    geographic_scope: str = "global"  # 地理范围
    
    def __post_init__(self):
        if self.affected_industries is None:
            self.affected_industries = []


@dataclass
class StateJumpRule:
    """状态跳跃规则"""
    from_state: str  # 起始状态
    factor_type: JumpFactorType  # 触发因素类型
    intensity: JumpIntensity  # 触发强度
    to_state: str  # 目标状态
    probability: float  # 跳跃概率 (0-1)
    description: str  # 规则描述
    conditions: Dict[str, Any] = None  # 额外条件
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}


@dataclass
class StateJumpPrediction:
    """状态跳跃预测"""
    from_state: str
    to_state: str
    probability: float
    trigger_factor: JumpFactor
    expected_duration: int  # 预计持续时间（小时）
    confidence: float  # 预测置信度
    risk_level: str  # 风险等级
    recommended_action: str  # 建议行动


class StateJumpEngine:
    """状态跳跃引擎"""
    
    def __init__(self):
        self.jump_rules = self._create_jump_rules()
        self.factor_monitors = self._create_factor_monitors()
        self.risk_thresholds = self._create_risk_thresholds()
        self.jump_history = []  # 跳跃历史记录
        logger.info("状态跳跃引擎初始化完成")
    
    def _create_jump_rules(self) -> List[StateJumpRule]:
        """创建跳跃规则"""
        return [
            # 政策刺激相关规则
            StateJumpRule(
                from_state="winter_hiding",
                factor_type=JumpFactorType.POLICY_STIMULUS,
                intensity=JumpIntensity.STRONG,
                to_state="spring_summer_transition",
                probability=0.8,
                description="冬藏期 + 强政策刺激 → 春入夏过渡期",
                conditions={"policy_type": "monetary_easing"}
            ),
            StateJumpRule(
                from_state="spring_sowing",
                factor_type=JumpFactorType.POLICY_STIMULUS,
                intensity=JumpIntensity.MODERATE,
                to_state="summer_growing",
                probability=0.7,
                description="春播期 + 政策利好 → 夏长期"
            ),
            
            # 战争爆发相关规则
            StateJumpRule(
                from_state="summer_growing",
                factor_type=JumpFactorType.WAR_OUTBREAK,
                intensity=JumpIntensity.STRONG,
                to_state="autumn_winter_transition",
                probability=0.9,
                description="夏长期 + 战争爆发 → 秋入冬过渡期"
            ),
            StateJumpRule(
                from_state="spring_sowing",
                factor_type=JumpFactorType.WAR_OUTBREAK,
                intensity=JumpIntensity.EXTREME,
                to_state="winter_hiding",
                probability=0.85,
                description="春播期 + 极端战争 → 冬藏期"
            ),
            
            # 行业突破相关规则
            StateJumpRule(
                from_state="autumn_harvest",
                factor_type=JumpFactorType.INDUSTRY_BREAKTHROUGH,
                intensity=JumpIntensity.STRONG,
                to_state="summer_growing",
                probability=0.6,
                description="秋收期 + 行业突破 → 夏长期",
                conditions={"industry": "tech"}
            ),
            StateJumpRule(
                from_state="chaotic_period",
                factor_type=JumpFactorType.INDUSTRY_BREAKTHROUGH,
                intensity=JumpIntensity.MODERATE,
                to_state="spring_sowing",
                probability=0.65,
                description="混沌期 + 行业突破 → 春播期"
            ),
            
            # 经济冲击相关规则
            StateJumpRule(
                from_state="summer_growing",
                factor_type=JumpFactorType.ECONOMIC_SHOCK,
                intensity=JumpIntensity.STRONG,
                to_state="autumn_harvest",
                probability=0.75,
                description="夏长期 + 经济冲击 → 秋收期"
            ),
            StateJumpRule(
                from_state="spring_sowing",
                factor_type=JumpFactorType.FINANCIAL_CRISIS,
                intensity=JumpIntensity.EXTREME,
                to_state="winter_hiding",
                probability=0.95,
                description="春播期 + 金融危机 → 冬藏期"
            ),
            
            # 技术革命相关规则
            StateJumpRule(
                from_state="winter_hiding",
                factor_type=JumpFactorType.TECH_REVOLUTION,
                intensity=JumpIntensity.STRONG,
                to_state="spring_sowing",
                probability=0.7,
                description="冬藏期 + 技术革命 → 春播期",
                conditions={"tech_field": "ai"}
            ),
            
            # 监管变化相关规则
            StateJumpRule(
                from_state="summer_growing",
                factor_type=JumpFactorType.REGULATORY_CHANGE,
                intensity=JumpIntensity.STRONG,
                to_state="autumn_harvest",
                probability=0.8,
                description="夏长期 + 强监管变化 → 秋收期",
                conditions={"regulatory_type": "tightening"}
            )
        ]
    
    def _create_factor_monitors(self) -> Dict[JumpFactorType, Dict[str, Any]]:
        """创建因素监测器配置"""
        return {
            JumpFactorType.POLICY_STIMULUS: {
                "sources": ["central_bank", "government", "regulator"],
                "update_interval": 3600,  # 1小时
                "threshold": 0.7,
                "keywords": ["降准", "降息", "刺激", "利好", "支持"]
            },
            JumpFactorType.WAR_OUTBREAK: {
                "sources": ["news", "government", "intelligence"],
                "update_interval": 300,  # 5分钟
                "threshold": 0.8,
                "keywords": ["战争", "冲突", "军事", "袭击", "紧张"]
            },
            JumpFactorType.INDUSTRY_BREAKTHROUGH: {
                "sources": ["tech_news", "research", "patents"],
                "update_interval": 86400,  # 1天
                "threshold": 0.6,
                "keywords": ["突破", "创新", "革命", "颠覆", "专利"]
            },
            JumpFactorType.ECONOMIC_SHOCK: {
                "sources": ["economic_data", "news", "analysts"],
                "update_interval": 86400,
                "threshold": 0.75,
                "keywords": ["衰退", "危机", "下滑", "萎缩", "恶化"]
            }
        }
    
    def _create_risk_thresholds(self) -> Dict[str, Dict[str, float]]:
        """创建风险阈值"""
        return {
            "jump_probability": {
                "low": 0.3,
                "medium": 0.6,
                "high": 0.8
            },
            "factor_intensity": {
                "mild": 0.3,
                "moderate": 0.5,
                "strong": 0.7,
                "extreme": 0.9
            },
            "confidence": {
                "low": 0.5,
                "medium": 0.7,
                "high": 0.9
            }
        }
    
    def predict_state_jumps(self, current_state: str, active_factors: List[JumpFactor]) -> List[StateJumpPrediction]:
        """预测状态跳跃"""
        predictions = []
        
        for factor in active_factors:
            # 查找匹配的跳跃规则
            matching_rules = self._find_matching_rules(current_state, factor)
            
            for rule in matching_rules:
                # 计算跳跃概率
                jump_probability = self._calculate_jump_probability(rule, factor)
                
                # 计算预测置信度
                confidence = self._calculate_prediction_confidence(rule, factor, jump_probability)
                
                # 确定风险等级
                risk_level = self._determine_risk_level(jump_probability, confidence, factor.intensity)
                
                # 生成建议行动
                recommended_action = self._generate_recommended_action(
                    current_state, rule.to_state, risk_level, factor
                )
                
                # 创建预测
                prediction = StateJumpPrediction(
                    from_state=current_state,
                    to_state=rule.to_state,
                    probability=jump_probability,
                    trigger_factor=factor,
                    expected_duration=factor.impact_duration,
                    confidence=confidence,
                    risk_level=risk_level,
                    recommended_action=recommended_action
                )
                
                predictions.append(prediction)
        
        # 按概率排序
        predictions.sort(key=lambda x: x.probability, reverse=True)
        
        # 记录跳跃历史
        if predictions:
            self._record_jump_history(current_state, predictions[0], active_factors)
        
        return predictions
    
    def _find_matching_rules(self, current_state: str, factor: JumpFactor) -> List[StateJumpRule]:
        """查找匹配的跳跃规则"""
        matching_rules = []
        
        for rule in self.jump_rules:
            # 检查状态匹配
            if rule.from_state != current_state:
                continue
            
            # 检查因素类型匹配
            if rule.factor_type != factor.factor_type:
                continue
            
            # 检查强度匹配
            if rule.intensity != factor.intensity:
                # 允许强度升级（如中度→强烈）
                intensity_values = {
                    JumpIntensity.MILD: 1,
                    JumpIntensity.MODERATE: 2,
                    JumpIntensity.STRONG: 3,
                    JumpIntensity.EXTREME: 4
                }
                
                if intensity_values[factor.intensity] < intensity_values[rule.intensity]:
                    continue  # 实际强度低于规则要求
            
            # 检查额外条件
            if rule.conditions and not self._check_conditions(rule.conditions, factor):
                continue
            
            matching_rules.append(rule)
        
        return matching_rules
    
    def _check_conditions(self, conditions: Dict[str, Any], factor: JumpFactor) -> bool:
        """检查额外条件"""
        for key, value in conditions.items():
            if key == "industry" and value not in factor.affected_industries:
                return False
            if key == "policy_type" and getattr(factor, "policy_type", None) != value:
                return False
            if key == "tech_field" and getattr(factor, "tech_field", None) != value:
                return False
            if key == "regulatory_type" and getattr(factor, "regulatory_type", None) != value:
                return False
        
        return True
    
    def _calculate_jump_probability(self, rule: StateJumpRule, factor: JumpFactor) -> float:
        """计算跳跃概率"""
        base_probability = rule.probability
        
        # 根据因素置信度调整
        confidence_adjustment = factor.confidence * 0.2  # 最多调整20%
        
        # 根据影响持续时间调整
        duration_adjustment = min(1.0, factor.impact_duration / 24) * 0.1  # 最多调整10%
        
        # 综合计算
        adjusted_probability = base_probability * (1 + confidence_adjustment + duration_adjustment)
        
        return min(1.0, max(0.0, adjusted_probability))
    
    def _calculate_prediction_confidence(self, rule: StateJumpRule, factor: JumpFactor, jump_probability: float) -> float:
        """计算预测置信度"""
        # 规则置信度
        rule_confidence = rule.probability
        
        # 因素置信度
        factor_confidence = factor.confidence
        
        # 跳跃概率置信度
        probability_confidence = 1.0 - abs(jump_probability - 0.5) * 2  # 越接近0.5越不确定
        
        # 加权平均
        confidence = (rule_confidence * 0.4 + factor_confidence * 0.4 + probability_confidence * 0.2)
        
        return min(1.0, max(0.0, confidence))
    
    def _determine_risk_level(self, probability: float, confidence: float, intensity: JumpIntensity) -> str:
        """确定风险等级"""
        # 根据概率判断
        if probability >= self.risk_thresholds["jump_probability"]["high"]:
            prob_risk = "high"
        elif probability >= self.risk_thresholds["jump_probability"]["medium"]:
            prob_risk = "medium"
        else:
            prob_risk = "low"
        
        # 根据置信度调整
        if confidence < self.risk_thresholds["confidence"]["low"]:
            conf_risk = "high"
        elif confidence < self.risk_thresholds["confidence"]["medium"]:
            conf_risk = "medium"
        else:
            conf_risk = "low"
        
        # 根据强度判断
        intensity_values = {
            JumpIntensity.MILD: "low",
            JumpIntensity.MODERATE: "medium",
            JumpIntensity.STRONG: "high",
            JumpIntensity.EXTREME: "extreme"
        }
        intensity_risk = intensity_values.get(intensity, "medium")
        
        # 综合风险等级
        risk_scores = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "extreme": 4
        }
        
        total_score = risk_scores.get(prob_risk, 1) + risk_scores.get(conf_risk, 1) + risk_scores.get(intensity_risk, 1)
        
        if total_score >= 10:
            return "extreme"
        elif total_score >= 7:
            return "high"
        elif total_score >= 5:
            return "medium"
        else:
            return "low"
    
    def _generate_recommended_action(self, from_state: str, to_state: str, risk_level: str, factor: JumpFactor) -> str:
        """生成建议行动"""
        actions = {
            "low": {
                "general": "保持现有策略，密切关注因素发展",
                "winter_hiding_to_spring_sowing": "开始小仓位布局，试探性建仓",
                "spring_sowing_to_summer_growing": "适度加仓，持有趋势股"
            },
            "medium": {
                "general": "调整仓位，做好风险对冲",
                "summer_growing_to_autumn_harvest": "分批减仓，锁定部分利润",
                "autumn_harvest_to_winter_hiding": "大幅减仓，转向防御"
            },
            "high": {
                "general": "立即调整仓位，做好风险控制",
                "summer_growing_to_autumn_winter_transition": "快速减仓，转向现金或避险资产",
                "spring_sowing_to_winter_hiding": "停止建仓，转为观望"
            },
            "extreme": {
                "general": "紧急避险，大幅降低仓位",
                "any_to_winter_hiding": "清仓或大幅减仓，等待市场稳定",
                "war_outbreak": "立即避险，转向黄金、美元等避险资产"
            }
        }
        
        # 查找特定行动
        state_transition = f"{from_state}_to_{to_state}"
        
        if risk_level in actions:
            # 先检查特定状态转换
            if state_transition in actions[risk_level]:
                return actions[risk_level][state_transition]
            
            # 检查因素特定行动
            factor_key = factor.factor_type.value
            if factor_key in actions[risk_level]:
                return actions[risk_level][factor_key]
            
            # 使用通用行动
            return actions[risk_level]["general"]
        
        return "保持谨慎，根据市场变化调整策略"
    
    def _record_jump_history(self, current_state: str, prediction: StateJumpPrediction, active_factors: List[JumpFactor]):
        """记录跳跃历史"""
        history_entry = {
            "timestamp": datetime.now(),
            "from_state": current_state