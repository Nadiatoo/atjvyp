"""
动态状态演化系统 - 因素监测
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


class FactorType(str, Enum):
    """因素类型"""
    POLICY_CHANGE = "policy_change"              # 政策变化
    GEOPOLITICAL_EVENT = "geopolitical_event"    # 地缘政治事件
    ECONOMIC_SHOCK = "economic_shock"            # 经济冲击
    INDUSTRY_BREAKTHROUGH = "industry_breakthrough"  # 行业突破
    MARKET_STRUCTURE_CHANGE = "market_structure_change"  # 市场结构变化
    LIQUIDITY_SHOCK = "liquidity_shock"          # 流动性冲击
    SENTIMENT_EXTREME = "sentiment_extreme"      # 情绪极端
    TECHNICAL_BREAKTHROUGH = "technical_breakthrough"  # 技术突破


class FactorImpactLevel(str, Enum):
    """因素影响级别"""
    VERY_HIGH = "very_high"      # 非常高（可能直接改变状态）
    HIGH = "high"                # 高（可能加速状态转换）
    MEDIUM = "medium"            # 中（可能影响状态持续时间）
    LOW = "low"                  # 低（可能微调状态特征）
    NEGLIGIBLE = "negligible"    # 可忽略


class FactorDirection(str, Enum):
    """因素方向"""
    BULLISH = "bullish"          # 看涨
    BEARISH = "bearish"          # 看跌
    NEUTRAL = "neutral"          # 中性
    MIXED = "mixed"              # 混合


@dataclass
class Factor:
    """因素"""
    factor_id: str
    factor_type: FactorType
    title: str
    description: str
    impact_level: FactorImpactLevel
    direction: FactorDirection
    intensity: float  # 强度 0-100
    confidence: float  # 置信度 0-100
    detected_time: datetime
    expected_duration_days: int
    affected_sectors: List[str]
    source: str
    raw_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "factor_id": self.factor_id,
            "factor_type": self.factor_type.value,
            "title": self.title,
            "description": self.description,
            "impact_level": self.impact_level.value,
            "direction": self.direction.value,
            "intensity": self.intensity,
            "confidence": self.confidence,
            "detected_time": self.detected_time.isoformat(),
            "expected_duration_days": self.expected_duration_days,
            "affected_sectors": self.affected_sectors,
            "source": self.source
        }


class FactorMonitor:
    """因素监测器"""
    
    def __init__(self):
        self.active_factors: Dict[str, Factor] = {}
        self.factor_history: List[Factor] = []
        self.factor_rules = self.load_factor_rules()
        
        logger.info("因素监测器初始化完成")
    
    def load_factor_rules(self) -> Dict[str, Any]:
        """加载因素规则"""
        # 这里可以从配置文件或数据库加载
        # 暂时使用硬编码规则
        return {
            "policy_change": {
                "impact_thresholds": {
                    "very_high": 80,  # 强度>80为非常高影响
                    "high": 60,
                    "medium": 40,
                    "low": 20
                },
                "duration_mapping": {
                    "very_high": 30,  # 非常高影响预计持续30天
                    "high": 20,
                    "medium": 10,
                    "low": 5
                }
            },
            "geopolitical_event": {
                "impact_thresholds": {
                    "very_high": 85,
                    "high": 65,
                    "medium": 45,
                    "low": 25
                },
                "duration_mapping": {
                    "very_high": 60,
                    "high": 30,
                    "medium": 15,
                    "low": 7
                }
            },
            # ... 其他因素类型的规则
        }
    
    def monitor_all_factors(self) -> Dict[str, List[Factor]]:
        """监测所有因素"""
        logger.info("开始监测所有因素")
        
        factors_by_type = {}
        
        try:
            # 1. 监测政策变化
            policy_factors = self.monitor_policy_changes()
            factors_by_type[FactorType.POLICY_CHANGE.value] = policy_factors
            
            # 2. 监测地缘政治事件
            geopolitical_factors = self.monitor_geopolitical_events()
            factors_by_type[FactorType.GEOPOLITICAL_EVENT.value] = geopolitical_factors
            
            # 3. 监测经济冲击
            economic_factors = self.monitor_economic_shocks()
            factors_by_type[FactorType.ECONOMIC_SHOCK.value] = economic_factors
            
            # 4. 监测行业突破
            industry_factors = self.monitor_industry_breakthroughs()
            factors_by_type[FactorType.INDUSTRY_BREAKTHROUGH.value] = industry_factors
            
            # 5. 更新活跃因素
            self.update_active_factors(factors_by_type)
            
            logger.info(f"因素监测完成，发现{sum(len(f) for f in factors_by_type.values())}个因素")
            
            return factors_by_type
            
        except Exception as e:
            logger.error(f"因素监测失败: {e}")
            return {}
    
    def monitor_policy_changes(self) -> List[Factor]:
        """监测政策变化"""
        factors = []
        
        # 这里应该连接政策数据源
        # 暂时使用模拟数据
        
        # 模拟：检测到降准政策
        if self.should_detect_policy_change():
            factor = Factor(
                factor_id=f"policy_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                factor_type=FactorType.POLICY_CHANGE,
                title="央行宣布降准0.5个百分点",
                description="中国人民银行宣布下调存款准备金率0.5个百分点，释放长期资金约1万亿元",
                impact_level=FactorImpactLevel.HIGH,
                direction=FactorDirection.BULLISH,
                intensity=75.0,
                confidence=85.0,
                detected_time=datetime.now(),
                expected_duration_days=30,
                affected_sectors=["银行", "房地产", "基建"],
                source="央行官网",
                raw_data={"policy_type": "降准", "幅度": "0.5%", "释放资金": "约1万亿元"}
            )
            factors.append(factor)
            logger.info(f"监测到政策变化: {factor.title}")
        
        return factors
    
    def monitor_geopolitical_events(self) -> List[Factor]:
        """监测地缘政治事件"""
        factors = []
        
        # 模拟：检测到地缘紧张
        if self.should_detect_geopolitical_event():
            factor = Factor(
                factor_id=f"geo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                factor_type=FactorType.GEOPOLITICAL_EVENT,
                title="中东地区紧张局势升级",
                description="中东地区紧张局势升级，可能影响全球能源供应和金融市场稳定",
                impact_level=FactorImpactLevel.VERY_HIGH,
                direction=FactorDirection.BEARISH,
                intensity=85.0,
                confidence=80.0,
                detected_time=datetime.now(),
                expected_duration_days=60,
                affected_sectors=["能源", "军工", "黄金"],
                source="国际新闻",
                raw_data={"region": "中东", "risk_level": "高", "可能影响": ["油价", "避险情绪"]}
            )
            factors.append(factor)
            logger.info(f"监测到地缘政治事件: {factor.title}")
        
        return factors
    
    def monitor_economic_shocks(self) -> List[Factor]:
        """监测经济冲击"""
        factors = []
        
        # 模拟：检测到经济数据超预期
        if self.should_detect_economic_shock():
            factor = Factor(
                factor_id=f"economic_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                factor_type=FactorType.ECONOMIC_SHOCK,
                title="CPI数据超预期上升",
                description="最新CPI数据显示通胀压力超预期上升，可能引发货币政策收紧预期",
                impact_level=FactorImpactLevel.MEDIUM,
                direction=FactorDirection.BEARISH,
                intensity=60.0,
                confidence=75.0,
                detected_time=datetime.now(),
                expected_duration_days=20,
                affected_sectors=["消费", "金融", "周期"],
                source="统计局",
                raw_data={"指标": "CPI", "实际值": "3.2%", "预期值": "2.8%", "影响": "通胀担忧"}
            )
            factors.append(factor)
            logger.info(f"监测到经济冲击: {factor.title}")
        
        return factors
    
    def monitor_industry_breakthroughs(self) -> List[Factor]:
        """监测行业突破"""
        factors = []
        
        # 模拟：检测到AI行业突破
        if self.should_detect_industry_breakthrough():
            factor = Factor(
                factor_id=f"industry_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                factor_type=FactorType.INDUSTRY_BREAKTHROUGH,
                title="AI大模型取得重大突破",
                description="某公司宣布AI大模型在多项基准测试中取得突破性进展，性能提升显著",
                impact_level=FactorImpactLevel.HIGH,
                direction=FactorDirection.BULLISH,
                intensity=70.0,
                confidence=80.0,
                detected_time=datetime.now(),
                expected_duration_days=90,
                affected_sectors=["人工智能", "半导体", "软件"],
                source="公司公告",
                raw_data={"领域": "AI大模型", "突破点": "性能提升", "影响范围": ["算力", "算法", "应用"]}
            )
            factors.append(factor)
            logger.info(f"监测到行业突破: {factor.title}")
        
        return factors
    
    def update_active_factors(self, new_factors_by_type: Dict[str, List[Factor]]):
        """更新活跃因素"""
        current_time = datetime.now()
        
        # 清理过期因素
        expired_factors = []
        for factor_id, factor in list(self.active_factors.items()):
            expiration_time = factor.detected_time + timedelta(days=factor.expected_duration_days)
            if current_time > expiration_time:
                expired_factors.append(factor_id)
                logger.info(f"因素过期: {factor.title}")
        
        for factor_id in expired_factors:
            del self.active_factors[factor_id]
        
        # 添加新因素
        for factor_list in new_factors_by_type.values():
            for factor in factor_list:
                if factor.factor_id not in self.active_factors:
                    self.active_factors[factor.factor_id] = factor
                    self.factor_history.append(factor)
    
    def get_active_factors(self) -> List[Factor]:
        """获取活跃因素"""
        return list(self.active_factors.values())
    
    def get_factors_by_impact(self, min_impact: FactorImpactLevel = FactorImpactLevel.MEDIUM) -> List[Factor]:
        """按影响级别获取因素"""
        impact_order = {
            FactorImpactLevel.VERY_HIGH: 4,
            FactorImpactLevel.HIGH: 3,
            FactorImpactLevel.MEDIUM: 2,
            FactorImpactLevel.LOW: 1,
            FactorImpactLevel.NEGLIGIBLE: 0
        }
        
        min_level = impact_order[min_impact]
        
        filtered_factors = []
        for factor in self.get_active_factors():
            if impact_order[factor.impact_level] >= min_level:
                filtered_factors.append(factor)
        
        # 按影响级别和强度排序
        filtered_factors.sort(
            key=lambda f: (impact_order[f.impact_level], f.intensity),
            reverse=True
        )
        
        return filtered_factors
    
    def evaluate_market_impact(self) -> Dict[str, Any]:
        """评估市场总体影响"""
        active_factors = self.get_active_factors()
        
        if not active_factors:
            return {
                "overall_impact": "neutral",
                "impact_score": 50.0,
                "bullish_factors": 0,
                "bearish_factors": 0,
                "key_factors": []
            }
        
        # 计算多空因素数量
        bullish_count = sum(1 for f in active_factors if f.direction == FactorDirection.BULLISH)
        bearish_count = sum(1 for f in active_factors if f.direction == FactorDirection.BEARISH)
        
        # 计算加权影响分数
        total_weighted_impact = 0.0
        total_weight = 0.0
        
        for factor in active_factors:
            # 影响权重 = 强度 × 置信度
            weight = factor.intensity * factor.confidence / 10000
            
            # 方向权重：看涨+1，看跌-1，中性0
            direction_weight = 1 if factor.direction == FactorDirection.BULLISH else \
                              -1 if factor.direction == FactorDirection.BEARISH else 0
            
            total_weighted_impact += weight * direction_weight
            total_weight += weight
        
        if total_weight > 0:
            impact_score = 50 + (total_weighted_impact / total_weight) * 50
        else:
            impact_score = 50.0
        
        # 确定总体影响
        if impact_score >= 70:
            overall_impact = "strongly_bullish"
        elif impact_score >= 60:
            overall_impact = "bullish"
        elif impact_score >= 40:
            overall_impact = "neutral"
        elif impact_score >= 30:
            overall_impact = "bearish"
        else:
            overall_impact = "strongly_bearish"
        
        # 获取关键因素（影响级别高且置信度高）
        key_factors = [
            f for f in active_factors 
            if f.impact_level in [FactorImpactLevel.VERY_HIGH, FactorImpactLevel.HIGH]
            and f.confidence >= 70
        ]
        
        return {
            "overall_impact": overall_impact,
            "impact_score": round(impact_score, 1),
            "bullish_factors": bullish_count,
            "bearish_factors": bearish_count,
            "total_factors": len(active_factors),
            "key_factors": [f.to_dict() for f in key_factors[:5]],  # 最多5个关键因素
            "evaluation_time": datetime.now().isoformat()
        }
    
    # 模拟检测函数（实际应该连接真实数据源）
    def should_detect_policy_change(self) -> bool:
        """模拟：是否检测到政策变化"""
        # 实际应该连接政策数据源
        # 这里随机返回True/False用于测试
        import random
        return random.random() < 0.3  # 30%概率检测到政策变化
    
    def should_detect_geopolitical_event(self) -> bool:
        """模拟：是否检测到地缘政治事件"""
        import random
        return random.random() < 0.2  # 20%概率
    
    def should_detect_economic_shock(self) -> bool:
        """模拟：是否检测到经济冲击"""
        import random
        return random.random() < 0.4  # 40%概率
    
    def should_detect_industry_breakthrough(self) -> bool:
        """模拟：是否检测到行业突破"""
        import random
        return random.random() < 0.25  # 25%概率


if __name__ == "__main__":
    # 测试因素监测器
    logging.basicConfig(level=logging.INFO)
    
    monitor = FactorMonitor()
    
    print("因素监测器测试")
    print("=" * 60)
    
    # 监测因素
    factors_by_type = monitor.monitor_all_factors()
    
    print(f"\n监测到的因素类型: {list(factors_by_type.keys())}")
    
    for factor_type, factors in factors_by_type.items():
        print(f"\n{factor_type}: {len(factors)}个因素")
        for factor in factors:
            print(f"  • {factor.title} (影响: {factor.impact_level.value}, 方向: {factor.direction.value})")
    
    # 评估市场影响
    impact_evaluation = monitor.evaluate_market_impact()
    print(f"\n市场影响评估:")
    print(f"  总体影响: {impact_evaluation['overall_impact']}")
    print(f"  影响分数: {impact_evaluation['impact_score']}")
    print(f"  看涨因素: {impact_evaluation['bullish_factors']}个")
    print(f"  看跌因素: {impact_evaluation['bearish_factors']}个")
    print(f"  总因素数: {impact_evaluation['total_factors']}个")
    
    if impact_evaluation['key_factors']:
        print(f"\n关键因素:")
        for factor in impact_evaluation['key_factors']:
            print(f"  • {factor['title']}")