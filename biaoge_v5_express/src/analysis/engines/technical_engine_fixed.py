"""
技术面分析引擎 - 修复版
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class TechnicalAnalysisEngine:
    """技术面分析引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.weights = config.get("weights", {
            "trend": 0.30,      # 趋势判断
            "pattern": 0.25,    # 形态识别
            "indicator": 0.25,  # 指标验证
            "key_level": 0.20   # 关键位置
        })
        
        logger.info("技术面分析引擎初始化完成")
    
    def analyze(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行技术面分析
        
        Args:
            stock_data: 股票数据
            
        Returns:
            技术面分析结果
        """
        logger.info("开始技术面分析")
        
        if not stock_data or "technical_data" not in stock_data:
            logger.warning("股票数据为空或格式不正确")
            return self.get_empty_result()
        
        try:
            # 提取数据
            df_stocks = pd.DataFrame(stock_data["technical_data"].get("stocks", []))
            
            if df_stocks.empty:
                logger.warning("股票数据为空")
                return self.get_empty_result()
            
            # 执行各项分析
            trend_analysis = self.analyze_trend(df_stocks)
            pattern_analysis = self.analyze_pattern(df_stocks)
            indicator_analysis = self.analyze_indicators(df_stocks)
            key_level_analysis = self.analyze_key_levels(df_stocks)
            
            # 计算综合评分
            technical_score = self.calculate_technical_score(
                trend_analysis,
                pattern_analysis,
                indicator_analysis,
                key_level_analysis
            )
            
            # 季节倾向度
            season_tendencies = self.calculate_season_tendencies(
                trend_analysis,
                pattern_analysis,
                indicator_analysis,
                key_level_analysis
            )
            
            result = {
                "timestamp": datetime.now(),
                "technical_score": technical_score,
                "season_tendencies": season_tendencies,
                "trend_analysis": trend_analysis,
                "pattern_analysis": pattern_analysis,
                "indicator_analysis": indicator_analysis,
                "key_level_analysis": key_level_analysis,
                "market_status": self.determine_market_status(technical_score, season_tendencies),
                "confidence": 70.0  # 简化实现
            }
            
            logger.info(f"技术面分析完成，评分: {technical_score:.1f}")
            return result
            
        except Exception as e:
            logger.error(f"技术面分析失败: {e}")
            return self.get_empty_result()
    
    def analyze_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析市场趋势"""
        if df.empty:
            return {"trend": "unknown", "strength": 0, "details": {}}
        
        # 计算涨跌比例
        rise_count = len(df[df["涨跌幅"] > 0])
        total_count = len(df)
        rise_ratio = rise_count / total_count if total_count > 0 else 0
        
        # 判断趋势
        trend = "neutral"
        if rise_ratio >= 0.7:
            trend = "strong_bull"
        elif rise_ratio >= 0.55:
            trend = "bull"
        elif rise_ratio >= 0.45:
            trend = "neutral"
        elif rise_ratio >= 0.3:
            trend = "bear"
        else:
            trend = "strong_bear"
        
        # 计算趋势强度
        trend_strength = min(100, max(0, (rise_ratio - 0.5) * 200))
        
        return {
            "trend": trend,
            "strength": trend_strength,
            "rise_ratio": rise_ratio,
            "rise_count": rise_count,
            "total_count": total_count
        }
    
    def analyze_pattern(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析K线形态"""
        if df.empty:
            return {"patterns": [], "score": 50, "details": {}}
        
        patterns = []
        pattern_score = 50
        
        # 检查涨停跌停情况
        limit_up = len(df[df["涨跌幅"] > 9])
        limit_down = len(df[df["涨跌幅"] < -9])
        
        if limit_up > 50:
            patterns.append({"name": "涨停潮", "type": "bullish", "score": 80})
            pattern_score = 80
        elif limit_down > 20:
            patterns.append({"name": "跌停潮", "type": "bearish", "score": 20})
            pattern_score = 20
        
        return {
            "patterns": patterns,
            "score": pattern_score,
            "pattern_count": len(patterns)
        }
    
    def analyze_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析技术指标"""
        if df.empty:
            return {"indicators": {}, "score": 50, "details": {}}
        
        indicator_score = 50
        
        # 简化实现：基于涨跌幅分布
        changes = df["涨跌幅"].dropna()
        if len(changes) > 0:
            avg_change = changes.mean()
            if avg_change > 2:
                indicator_score = 75
            elif avg_change < -2:
                indicator_score = 25
        
        return {
            "indicators": {"simplified": {"score": indicator_score}},
            "score": indicator_score
        }
    
    def analyze_key_levels(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析关键位置"""
        if df.empty:
            return {"key_levels": [], "score": 50, "details": {}}
        
        key_levels = []
        
        # 简化实现：识别价格分位数
        if "最新价" in df.columns:
            prices = df["最新价"].dropna()
            if len(prices) > 0:
                current_price = prices.iloc[-1]
                
                # 添加简单支撑阻力位
                for q in [0.25, 0.5, 0.75]:
                    level = prices.quantile(q)
                    level_type = "support" if level < current_price else "resistance"
                    key_levels.append({
                        "price": round(level, 2),
                        "type": level_type,
                        "strength": 60
                    })
        
        level_score = 60 if key_levels else 50
        
        return {
            "key_levels": key_levels,
            "score": level_score,
            "level_count": len(key_levels)
        }
    
    def calculate_technical_score(self, trend: Dict, pattern: Dict, indicator: Dict, key_level: Dict) -> float:
        """计算技术面综合评分"""
        scores = []
        weights = []
        
        # 趋势评分
        if "strength" in trend:
            scores.append(trend["strength"])
            weights.append(self.weights["trend"])
        
        # 形态评分
        if "score" in pattern:
            scores.append(pattern["score"])
            weights.append(self.weights["pattern"])
        
        # 指标评分
        if "score" in indicator:
            scores.append(indicator["score"])
            weights.append(self.weights["indicator"])
        
        # 关键位置评分
        if "score" in key_level:
            scores.append(key_level["score"])
            weights.append(self.weights["key_level"])
        
        if not scores:
            return 50.0
        
        # 计算加权平均
        total_score = sum(s * w for s, w in zip(scores, weights))
        total_weight = sum(weights)
        
        technical_score = total_score / total_weight if total_weight > 0 else 50.0
        
        return round(max(0, min(100, technical_score)), 1)
    
    def calculate_season_tendencies(self, trend: Dict, pattern: Dict, indicator: Dict, key_level: Dict) -> Dict[str, float]:
        """计算季节倾向度"""
        tendencies = {
            "spring": 50.0,  # 春播
            "summer": 50.0,  # 夏长
            "autumn": 50.0,  # 秋收
            "winter": 50.0   # 冬藏
        }
        
        # 基于趋势判断
        trend_type = trend.get("trend", "neutral")
        trend_strength = trend.get("strength", 50)
        
        if trend_type in ["strong_bear", "bear"]:
            tendencies["winter"] += trend_strength * 0.3
        elif trend_type in ["strong_bull", "bull"]:
            tendencies["summer"] += trend_strength * 0.3
        
        # 归一化到0-100
        for key in tendencies:
            tendencies[key] = round(max(0, min(100, tendencies[key])), 1)
        
        return tendencies
    
    def determine_market_status(self, technical_score: float, season_tendencies: Dict[str, float]) -> str:
        """确定市场状态"""
        if technical_score >= 70:
            return "强势"
        elif technical_score >= 60:
            return "偏强"
        elif technical_score >= 40:
            return "震荡"
        elif technical_score >= 30:
            return "偏弱"
        else:
            return "弱势"
    
    def get_empty_result(self) -> Dict[str, Any]:
        """获取空结果"""
        return {
            "timestamp": datetime.now(),
            "technical_score": 50.0,
            "season_tendencies": {
                "spring": 50.0,
                "summer": 50.0,
                "autumn": 50.0,
                "winter": 50.0
            },
            "trend_analysis": {
                "trend": "unknown",
                "strength": 0
            },
            "pattern_analysis": {
                "patterns": [],
                "score": 50
            },
            "indicator_analysis": {
                "indicators": {},
                "score": 50
            },
            "key_level_analysis": {
                "key_levels": [],
                "score": 50
            },
            "market_status": "unknown",
            "confidence": 0
        }