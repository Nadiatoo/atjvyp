"""
动态状态演化系统 - 简化版演化引擎
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from .state_definitions import MarketState, get_state_definition

logger = logging.getLogger(__name__)


@dataclass
class StateTransition:
    """状态转换"""
    from_state: MarketState
    to_state: MarketState
    probability: float  # 转换概率 0-100
    transition_type: str  # 转换类型: normal, jump, revert, stay
    description: str


class SimpleStateEvolutionEngine:
    """简化版状态演化引擎"""
    
    def __init__(self):
        self.current_state: Optional[MarketState] = None
        self.state_history: List[Dict[str, Any]] = []
        
        logger.info("简化版状态演化引擎初始化完成")
    
    def set_current_state(self, state: MarketState, confidence: float = 80.0):
        """设置当前状态"""
        self.current_state = state
        
        state_record = {
            "state": state.value,
            "chinese_name": get_state_definition(state).chinese_name,
            "timestamp": datetime.now(),
            "confidence": confidence
        }
        
        self.state_history.append(state_record)
        logger.info(f"设置当前状态: {get_state_definition(state).chinese_name} (置信度: {confidence}%)")
    
    def analyze_current_market(self, technical_score: float, rise_ratio: float) -> MarketState:
        """分析当前市场状态"""
        logger.info("开始分析当前市场状态")
        
        try:
            # 基于技术评分和上涨比例的简单匹配
            if technical_score >= 70 and rise_ratio >= 0.7:
                matched_state = MarketState.SUMMER
            elif technical_score >= 60 and rise_ratio >= 0.6:
                matched_state = MarketState.SPRING_SUMMER_TRANSITION
            elif technical_score >= 50 and rise_ratio >= 0.55:
                matched_state = MarketState.SPRING
            elif technical_score >= 45 and rise_ratio >= 0.5:
                matched_state = MarketState.WINTER_SPRING_TRANSITION
            elif technical_score >= 40 and rise_ratio >= 0.45:
                matched_state = MarketState.CHAOS
            elif technical_score >= 30 and rise_ratio >= 0.3:
                matched_state = MarketState.AUTUMN
            elif technical_score >= 20 and rise_ratio >= 0.2:
                matched_state = MarketState.AUTUMN_WINTER_TRANSITION
            else:
                matched_state = MarketState.WINTER
            
            # 计算置信度
            confidence = self.calculate_state_confidence(technical_score, rise_ratio, matched_state)
            
            # 设置当前状态
            self.set_current_state(matched_state, confidence)
            
            logger.info(f"市场状态分析完成: {get_state_definition(matched_state).chinese_name} (置信度: {confidence}%)")
            
            return matched_state
            
        except Exception as e:
            logger.error(f"市场状态分析失败: {e}")
            # 返回默认状态
            return MarketState.CHAOS
    
    def calculate_state_confidence(self, technical_score: float, rise_ratio: float, matched_state: MarketState) -> float:
        """计算状态置信度"""
        # 基于技术评分与状态特征的匹配度
        if matched_state == MarketState.SUMMER:
            # 夏季要求技术评分高、上涨比例高
            confidence = min(100, (technical_score + rise_ratio * 100) / 2)
        elif matched_state == MarketState.WINTER:
            # 冬季要求技术评分低、上涨比例低
            confidence = min(100, ((100 - technical_score) + (1 - rise_ratio) * 100) / 2)
        else:
            # 其他状态
            tech_deviation = abs(technical_score - 50)
            rise_deviation = abs(rise_ratio - 0.5) * 100
            confidence = 100 - (tech_deviation + rise_deviation) / 2
        
        return round(max(0, min(100, confidence)), 1)
    
    def predict_next_state(self, current_state: Optional[MarketState] = None) -> List[StateTransition]:
        """预测下一状态"""
        if current_state is None:
            current_state = self.current_state
        
        if current_state is None:
            logger.warning("当前状态未设置，无法预测")
            return []
        
        logger.info(f"开始预测下一状态，当前状态: {get_state_definition(current_state).chinese_name}")
        
        try:
            transitions = []
            
            # 正常演进预测
            normal_transitions = self.predict_normal_evolution(current_state)
            transitions.extend(normal_transitions)
            
            # 状态跳跃预测（如果有重大因素）
            jump_transitions = self.predict_state_jumps(current_state)
            transitions.extend(jump_transitions)
            
            # 排序（按概率降序）
            transitions.sort(key=lambda t: t.probability, reverse=True)
            
            logger.info(f"状态预测完成，生成{len(transitions)}个可能的转换")
            
            return transitions[:5]  # 返回前5个最可能的转换
            
        except Exception as e:
            logger.error(f"状态预测失败: {e}")
            return []
    
    def predict_normal_evolution(self, current_state: MarketState) -> List[StateTransition]:
        """预测正常演进"""
        transitions = []
        
        # 正常演进规则
        normal_rules = {
            MarketState.WINTER: [
                (MarketState.WINTER_SPRING_TRANSITION, 70, "正常演进: 冬藏 → 冬末春初"),
                (MarketState.WINTER, 25, "状态保持: 继续冬藏"),
                (MarketState.CHAOS, 5, "异常转换: 进入混沌期")
            ],
            MarketState.WINTER_SPRING_TRANSITION: [
                (MarketState.SPRING, 60, "正常演进: 冬末春初 → 春播"),
                (MarketState.WINTER, 30, "状态回退: 回到冬藏"),
                (MarketState.CHAOS, 10, "异常转换: 进入混沌期")
            ],
            MarketState.SPRING: [
                (MarketState.SPRING_SUMMER_TRANSITION, 65, "正常演进: 春播 → 春入夏过渡"),
                (MarketState.AUTUMN, 25, "异常转换: 直接进入秋收"),
                (MarketState.CHAOS, 10, "异常转换: 进入混沌期")
            ],
            MarketState.SPRING_SUMMER_TRANSITION: [
                (MarketState.SUMMER, 70, "正常演进: 春入夏过渡 → 夏长"),
                (MarketState.SPRING, 20, "状态回退: 回到春播"),
                (MarketState.CHAOS, 10, "异常转换: 进入混沌期")
            ],
            MarketState.SUMMER: [
                (MarketState.SUMMER_AUTUMN_TRANSITION, 65, "正常演进: 夏长 → 夏末秋初过渡"),
                (MarketState.SUMMER, 30, "状态保持: 继续夏长"),
                (MarketState.CHAOS, 5, "异常转换: 进入混沌期")
            ],
            MarketState.SUMMER_AUTUMN_TRANSITION: [
                (MarketState.AUTUMN, 70, "正常演进: 夏末秋初过渡 → 秋收"),
                (MarketState.SUMMER, 20, "状态回退: 回到夏长"),
                (MarketState.CHAOS, 10, "异常转换: 进入混沌期")
            ],
            MarketState.AUTUMN: [
                (MarketState.AUTUMN_WINTER_TRANSITION, 65, "正常演进: 秋收 → 秋入冬过渡"),
                (MarketState.AUTUMN, 25, "状态保持: 继续秋收"),
                (MarketState.CHAOS, 10, "异常转换: 进入混沌期")
            ],
            MarketState.AUTUMN_WINTER_TRANSITION: [
                (MarketState.WINTER, 70, "正常演进: 秋入冬过渡 → 冬藏"),
                (MarketState.AUTUMN, 20, "状态回退: 回到秋收"),
                (MarketState.CHAOS, 10, "异常转换: 进入混沌期")
            ],
            MarketState.CHAOS: [
                (MarketState.WINTER_SPRING_TRANSITION, 30, "正常演进: 混沌 → 冬末春初"),
                (MarketState.SPRING, 25, "正常演进: 混沌 → 春播"),
                (MarketState.AUTUMN, 25, "正常演进: 混沌 → 秋收"),
                (MarketState.CHAOS, 20, "状态保持: 继续混沌")
            ]
        }
        
        if current_state in normal_rules:
            for to_state, probability, description in normal_rules[current_state]:
                transition = StateTransition(
                    from_state=current_state,
                    to_state=to_state,
                    probability=probability,
                    transition_type="normal",
                    description=description
                )
                transitions.append(transition)
        
        return transitions
    
    def predict_state_jumps(self, current_state: MarketState) -> List[StateTransition]:
        """预测状态跳跃"""
        transitions = []
        
        # 状态跳跃规则（重大因素导致）
        jump_rules = [
            # 冬藏期 + 强政策刺激 → 春入夏过渡期
            {
                "from_state": MarketState.WINTER,
                "to_state": MarketState.SPRING_SUMMER_TRANSITION,
                "probability": 80,
                "description": "状态跳跃: 强政策刺激可能让市场从冬藏直接进入春入夏过渡期"
            },
            # 夏长期 + 战争爆发 → 秋入冬过渡期
            {
                "from_state": MarketState.SUMMER,
                "to_state": MarketState.AUTUMN_WINTER_TRANSITION,
                "probability": 90,
                "description": "状态跳跃: 高强度战争可能让市场从夏长直接跳入秋入冬过渡期"
            },
            # 秋收期 + 行业突破 → 夏长期
            {
                "from_state": MarketState.AUTUMN,
                "to_state": MarketState.SUMMER,
                "probability": 60,
                "description": "状态跳跃: 重大行业突破可能让市场从秋收回退到夏长"
            }
        ]
        
        # 检查是否匹配跳跃规则
        for rule in jump_rules:
            if rule["from_state"] == current_state:
                transition = StateTransition(
                    from_state=current_state,
                    to_state=rule["to_state"],
                    probability=rule["probability"],
                    transition_type="jump",
                    description=rule["description"]
                )
                transitions.append(transition)
        
        return transitions
    
    def get_state_analysis_report(self, technical_score: float, rise_ratio: float) -> Dict[str, Any]:
        """获取状态分析报告"""
        # 分析当前状态
        current_state = self.analyze_current_market(technical_score, rise_ratio)
        state_def = get_state_definition(current_state)
        
        # 预测下一状态
        next_transitions = self.predict_next_state(current_state)
        
        # 生成报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "technical_score": technical_score,
            "rise_ratio": rise_ratio,
            "current_state": {
                "state": current_state.value,
                "chinese_name": state_def.chinese_name,
                "description": state_def.description,
                "position_range": state_def.position_range,
                "operation_strategy": state_def.operation_strategy,
                "risk_level": state_def.risk_level
            },
            "state_transitions": [
                {
                    "to_state": t.to_state.value,
                    "to_chinese_name": get_state_definition(t.to_state).chinese_name,
                    "probability": t.probability,
                    "transition_type": t.transition_type,
                    "description": t.description
                }
                for t in next_transitions
            ],
            "most_likely_next_state": None,
            "jump_risk": any(t.transition_type == "jump" for t in next_transitions)
        }
        
        if next_transitions:
            most_likely = next_transitions[0]
            report["most_likely_next_state"] = {
                "state": most_likely.to_state.value,
                "chinese_name": get_state_definition(most_likely.to_state).chinese_name,
                "probability": most_likely.probability,
                "transition_type": most_likely.transition_type
            }
        
        return report


if __name__ == "__main__":
    # 测试简化版演化引擎
    logging.basicConfig(level=logging.INFO)
    
    print("简化版状态演化引擎测试")
    print("=" * 60)
    
    engine = SimpleStateEvolutionEngine()
    
    # 测试案例
    test_cases = [
        (75.0, 0.72, "强势市场"),
        (35.0, 0.28, "弱势市场"),
        (52.0, 0.48, "震荡市场")
    ]
    
    for technical_score, rise_ratio, case_name in test_cases:
        print(f"\n🔍 测试案例: {case_name}")
        print(f"  技术评分: {technical_score}")
        print(f"  上涨比例: {rise_ratio*100:.1f}%")
        
        # 获取分析报告
        report = engine.get_state_analysis_report(technical_score, rise_ratio)
        
        current_state = report["current_state"]
        print(f"  当前状态: {current_state['chinese_name']}")
        print(f"  状态描述: {current_state['description']}")
        print(f"  仓位范围: {current_state['position_range'][0]}%-{current_state['position_range'][1]}%")
        print(f"  操作策略: {current_state['operation_strategy']}")
        print(f"  风险等级: {current_state['risk_level']}")
        
        if report["state_transitions"]:
            print(f"  状态演化预测:")
            for i, transition in enumerate(report["state_transitions"][:3]):
                print(f"    {i+1}. {transition['to_chinese_name']} (概率: {transition['probability']}%)")
                print(f"        类型: {transition['transition_type']}, 描述: {transition['description']}")
        
        if report["jump_risk"]:
            print(f"  ⚠️  检测到状态跳跃风险")
        
        print()