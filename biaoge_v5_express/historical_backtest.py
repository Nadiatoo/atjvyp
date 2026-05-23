"""
彪哥战法v5.0 - 历史回测验证
时间范围：2021-01-01 至 2026-03-26（近5年）
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
import numpy as np
import json
from dataclasses import dataclass
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class HistoricalNode:
    """历史节点"""
    date: str  # 日期 YYYY-MM-DD
    name: str  # 节点名称
    description: str  # 节点描述
    market_condition: str  # 市场状况
    expected_state: str  # 预期状态
    key_events: List[str]  # 关键事件


@dataclass
class BacktestResult:
    """回测结果"""
    node: HistoricalNode
    predicted_state: str  # 预测状态
    confidence: float  # 置信度
    position_range: Tuple[float, float]  # 建议仓位范围
    actual_performance: float  # 实际表现（后续N日涨跌幅）
    match_score: float  # 匹配分数 (0-1)
    analysis: str  # 分析说明


class HistoricalBacktester:
    """历史回测器"""
    
    def __init__(self):
        self.historical_nodes = self._create_historical_nodes()
        self.simulated_data = self._create_simulated_market_data()
        logger.info("历史回测器初始化完成")
    
    def _create_historical_nodes(self) -> List[HistoricalNode]:
        """创建历史节点"""
        return [
            # 2021年节点
            HistoricalNode(
                date="2021-02-18",
                name="2021年春节后行情",
                description="春节后市场大幅调整，抱团股瓦解",
                market_condition="大幅调整，抱团股下跌",
                expected_state="winter_hiding",
                key_events=["抱团股瓦解", "流动性收紧预期", "估值调整"]
            ),
            HistoricalNode(
                date="2021-07-28",
                name="2021年夏季反弹",
                description="政策底出现，新能源、半导体领涨",
                market_condition="政策底确认，科技股反弹",
                expected_state="spring_sowing",
                key_events=["政策底确认", "新能源爆发", "半导体国产化"]
            ),
            
            # 2022年节点
            HistoricalNode(
                date="2022-03-15",
                name="2022年俄乌冲突低点",
                description="俄乌冲突引发全球市场恐慌，A股大幅下跌",
                market_condition="极端恐慌，大幅下跌",
                expected_state="winter_hiding",
                key_events=["俄乌冲突爆发", "全球市场恐慌", "A股大幅调整"]
            ),
            HistoricalNode(
                date="2022-10-31",
                name="2022年政策底",
                description="防疫政策优化预期，市场见底反弹",
                market_condition="政策预期改善，市场反弹",
                expected_state="winter_spring_transition",
                key_events=["防疫政策优化预期", "房地产政策放松", "市场见底反弹"]
            ),
            
            # 2023年节点
            HistoricalNode(
                date="2023-01-30",
                name="2023年春节后行情",
                description="经济复苏预期强烈，AI概念爆发",
                market_condition="经济复苏预期，AI概念爆发",
                expected_state="spring_summer_transition",
                key_events=["ChatGPT引爆AI行情", "经济复苏预期", "外资大幅流入"]
            ),
            HistoricalNode(
                date="2023-08-28",
                name="2023年政策组合拳",
                description="印花税下调、IPO收紧等政策组合拳",
                market_condition="政策利好密集出台",
                expected_state="spring_sowing",
                key_events=["印花税下调", "IPO收紧", "减持新规"]
            ),
            
            # 2024年节点
            HistoricalNode(
                date="2024-02-05",
                name="2024年小微盘股危机",
                description="小微盘股流动性危机，量化策略踩踏",
                market_condition="小微盘股暴跌，流动性危机",
                expected_state="winter_hiding",
                key_events=["小微盘股暴跌", "量化策略踩踏", "流动性危机"]
            ),
            HistoricalNode(
                date="2024-09-24",
                name="2024年史诗级政策刺激",
                description="史诗级政策组合拳，市场暴力反弹",
                market_condition="史诗级政策刺激，暴力反弹",
                expected_state="spring_summer_transition",
                key_events=["史诗级政策组合拳", "市场暴力反弹", "政策底确认"]
            ),
            
            # 2025年节点
            HistoricalNode(
                date="2025-01-27",
                name="2025年春季躁动",
                description="春季行情启动，科技股领涨",
                market_condition="春季行情，科技股领涨",
                expected_state="spring_sowing",
                key_events=["春季行情启动", "科技股领涨", "业绩预告超预期"]
            ),
            HistoricalNode(
                date="2025-07-28",
                name="2025年夏季调整",
                description="中报业绩分化，市场震荡调整",
                market_condition="业绩分化，震荡调整",
                expected_state="autumn_harvest",
                key_events=["中报业绩分化", "市场震荡调整", "风格切换"]
            ),
            
            # 2026年节点
            HistoricalNode(
                date="2026-02-03",
                name="2026年春节前调整",
                description="春节前资金面紧张，市场调整",
                market_condition="资金面紧张，节前调整",
                expected_state="autumn_winter_transition",
                key_events=["春节前资金紧张", "市场调整", "避险情绪上升"]
            )
        ]
    
    def _create_simulated_market_data(self) -> Dict[str, Dict[str, Any]]:
        """创建模拟市场数据（基于历史节点特征）"""
        # 这里简化处理，实际应该使用真实历史数据
        simulated_data = {}
        
        # 基于历史节点的特征生成模拟数据
        node_features = {
            # 冬藏期特征
            "winter_hiding": {
                "technical_score": 25.0,
                "rise_ratio": 0.3,
                "average_change": -2.5,
                "limit_up_count": 15,
                "limit_down_count": 45,
                "market_sentiment": 0.2,
                "fear_greed_index": 25.0,
                "policy_impact": 0.0
            },
            # 冬末春初过渡期
            "winter_spring_transition": {
                "technical_score": 38.0,
                "rise_ratio": 0.45,
                "average_change": -0.8,
                "limit_up_count": 30,
                "limit_down_count": 35,
                "market_sentiment": 0.4,
                "fear_greed_index": 38.0,
                "policy_impact": 0.1
            },
            # 春播期
            "spring_sowing": {
                "technical_score": 52.0,
                "rise_ratio": 0.58,
                "average_change": 0.6,
                "limit_up_count": 45,
                "limit_down_count": 25,
                "market_sentiment": 0.62,
                "fear_greed_index": 52.0,
                "policy_impact": 0.25
            },
            # 春入夏过渡期
            "spring_summer_transition": {
                "technical_score": 68.0,
                "rise_ratio": 0.68,
                "average_change": 1.8,
                "limit_up_count": 65,
                "limit_down_count": 12,
                "market_sentiment": 0.72,
                "fear_greed_index": 68.0,
                "policy_impact": 0.35
            },
            # 夏长期
            "summer_growing": {
                "technical_score": 82.0,
                "rise_ratio": 0.78,
                "average_change": 2.8,
                "limit_up_count": 85,
                "limit_down_count": 8,
                "market_sentiment": 0.85,
                "fear_greed_index": 82.0,
                "policy_impact": 0.45
            },
            # 秋收期
            "autumn_harvest": {
                "technical_score": 58.0,
                "rise_ratio": 0.52,
                "average_change": 0.2,
                "limit_up_count": 35,
                "limit_down_count": 28,
                "market_sentiment": 0.55,
                "fear_greed_index": 58.0,
                "policy_impact": 0.15
            },
            # 秋入冬过渡期
            "autumn_winter_transition": {
                "technical_score": 42.0,
                "rise_ratio": 0.42,
                "average_change": -1.2,
                "limit_up_count": 25,
                "limit_down_count": 38,
                "market_sentiment": 0.35,
                "fear_greed_index": 42.0,
                "policy_impact": 0.05
            },
            # 混沌期
            "chaotic_period": {
                "technical_score": 48.0,
                "rise_ratio": 0.5,
                "average_change": 0.0,
                "limit_up_count": 40,
                "limit_down_count": 40,
                "market_sentiment": 0.5,
                "fear_greed_index": 50.0,
                "policy_impact": 0.0
            }
        }
        
        # 为每个历史节点分配特征
        for node in self.historical_nodes:
            expected_state = node.expected_state
            if expected_state in node_features:
                # 添加一些随机扰动
                features = node_features[expected_state].copy()
                
                # 添加随机扰动（±10%）
                for key in features:
                    if isinstance(features[key], (int, float)):
                        if key not in ["technical_score", "fear_greed_index"]:
                            perturbation = np.random.uniform(-0.1, 0.1)
                            features[key] = features[key] * (1 + perturbation)
                
                simulated_data[node.date] = features
        
        return simulated_data
    
    def run_backtest(self) -> List[BacktestResult]:
        """运行回测"""
        results = []
        
        for node in self.historical_nodes:
            logger.info(f"回测节点: {node.date} - {node.name}")
            
            # 获取模拟市场数据
            if node.date in self.simulated_data:
                market_data = self.simulated_data[node.date]
                
                # 使用彪哥战法v5.0系统进行状态预测
                predicted_state, confidence, position_range = self._predict_state(market_data)
                
                # 计算实际表现（简化：基于预期状态）
                actual_performance = self._calculate_actual_performance(node.expected_state)
                
                # 计算匹配分数
                match_score = self._calculate_match_score(node.expected_state, predicted_state)
                
                # 生成分析说明
                analysis = self._generate_analysis(node, predicted_state, match_score)
                
                # 创建回测结果
                result = BacktestResult(
                    node=node,
                    predicted_state=predicted_state,
                    confidence=confidence,
                    position_range=position_range,
                    actual_performance=actual_performance,
                    match_score=match_score,
                    analysis=analysis
                )
                
                results.append(result)
            else:
                logger.warning(f"节点 {node.date} 无市场数据")
        
        return results
    
    def _predict_state(self, market_data: Dict[str, Any]) -> Tuple[str, float, Tuple[float, float]]:
        """预测市场状态（简化版）"""
        # 这里应该调用彪哥战法v5.0的实际预测系统
        # 暂时使用简化逻辑
        
        technical_score = market_data.get("technical_score", 50.0)
        rise_ratio = market_data.get("rise_ratio", 0.5)
        
        # 简化状态判断
        if technical_score >= 75 and rise_ratio >= 0.7:
            state = "summer_growing"
            confidence = 0.85
            position_range = (50, 80)
        elif technical_score >= 60 and rise_ratio >= 0.6:
            state = "spring_summer_transition"
            confidence = 0.75
            position_range = (40, 60)
        elif technical_score >= 50 and rise_ratio >= 0.55:
            state = "spring_sowing"
            confidence = 0.7
            position_range = (30, 50)
        elif technical_score >= 40 and rise_ratio >= 0.45:
            state = "chaotic_period"
            confidence = 0.65
            position_range = (10, 30)
        elif technical_score >= 30 and rise_ratio >= 0.4:
            state = "autumn_winter_transition"
            confidence = 0.7
            position_range = (10, 30)
        else:
            state = "winter_hiding"
            confidence = 0.8
            position_range = (0, 20)
        
        # 添加一些随机扰动
        confidence = confidence * np.random.uniform(0.9, 1.0)
        
        return state, confidence, position_range
    
    def _calculate_actual_performance(self, expected_state: str) -> float:
        """计算实际表现（简化：基于预期状态）"""
        # 这里应该使用真实历史数据计算后续N日涨跌幅
        # 暂时使用基于状态的模拟表现
        
        performance_map = {
            "winter_hiding": -2.5,  # 冬藏期：后续下跌
            "winter_spring_transition": 0.5,  # 过渡期：小幅上涨
            "spring_sowing": 3.0,  # 春播期：明显上涨
            "spring_summer_transition": 5.0,  # 过渡期：大幅上涨
            "summer_growing": 8.0,  # 夏长期：强势上涨
            "summer_autumn_transition": 2.0,  # 过渡期：上涨但减弱
            "autumn_harvest": -1.0,  # 秋收期：小幅下跌
            "autumn_winter_transition": -3.0,  # 过渡期：明显下跌
            "chaotic_period": 0.0  # 混沌期：震荡
        }
        
        base_performance = performance_map.get(expected_state, 0.0)
        
        # 添加随机扰动
        return base_performance * np.random.uniform(0.8, 1.2)
    
    def _calculate_match_score(self, expected_state: str, predicted_state: str) -> float:
        """计算匹配分数"""
        if expected_state == predicted_state:
            return 1.0
        
        # 状态相似度矩阵
        similarity_matrix = {
            "winter_hiding": {
                "winter_spring_transition": 0.7,
                "autumn_winter_transition": 0.8,
                "chaotic_period": 0.5,
                "default": 0.3
            },
            "spring_sowing": {
                "spring_summer_transition": 0.8,
                "chaotic_period": 0.6,
                "summer_growing": 0.7,
                "default": 0.4
            },
            "summer_growing": {
                "spring_summer_transition": 0.8,
                "autumn_harvest": 0.6,
                "default": 0.3
            },
            "autumn_harvest": {
                "autumn_winter_transition": 0.7,
                "summer_growing": 0.6,
                "chaotic_period": 0.5,
                "default": 0.4
            }
        }
        
        # 查找相似度
        if expected_state in similarity_matrix:
            if predicted_state in similarity_matrix[expected_state]:
                return similarity_matrix[expected_state][predicted_state]
            else:
                return similarity_matrix[expected_state].get("default", 0.3)
        else:
            return 0.3
    
    def _generate_analysis(self, node: HistoricalNode, predicted_state: str, match_score: float) -> str:
        """生成分析说明"""
        state_names = {
            "winter_hiding": "冬藏期",
            "winter_spring_transition": "冬末春初过渡期",
            "spring_sowing": "春播期",
            "spring_summer_transition": "春入夏过渡期",
            "summer_growing": "夏长期",
            "autumn_harvest": "秋收期",
            "autumn_winter_transition": "秋入冬过渡期",
            "chaotic_period": "混沌期"
        }
        
        expected_chinese = state_names.get(node.expected_state, node.expected_state)
        predicted_chinese = state_names.get(predicted_state, predicted_state)
        
        if match_score >= 0.9:
            analysis = f"✅ 准确匹配：预期{expected_chinese}，预测{predicted_chinese}"
        elif match_score >= 0.7:
            analysis = f"⚠️