        return {
            "status": status,
            "score": score,
            "avg_volatility": round(avg_volatility, 2),
            "signal": "控制风险" if score < 40 else ("稳定" if score > 60 else "正常")
        }
    
    def analyze_key_levels(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析关键位置"""
        logger.info("分析关键位置")
        
        if df.empty:
            return {"key_levels": [], "score": 50, "details": {}}
        
        key_levels = []
        level_score = 50
        
        # 分析支撑阻力位（简化版）
        if "最新价" in df.columns:
            price_levels = self.identify_price_levels(df["最新价"])
            key_levels.extend(price_levels)
            
            # 计算关键位置评分
            if price_levels:
                level_scores = [p.get("strength", 50) for p in price_levels]
                level_score = np.mean(level_scores)
        
        # 分析整数关口
        integer_levels = self.identify_integer_levels(df)
        key_levels.extend(integer_levels)
        
        return {
            "key_levels": key_levels,
            "score": round(level_score, 1),
            "level_count": len(key_levels),
            "nearest_level": key_levels[0] if key_levels else None,
            "details": {
                "breakthrough_risk": self.assess_breakthrough_risk(key_levels, df),
                "support_resistance": self.classify_levels(key_levels)
            }
        }
    
    def identify_price_levels(self, prices: pd.Series) -> List[Dict[str, Any]]:
        """识别价格关键位"""
        if len(prices) < 20:
            return []
        
        # 使用分位数识别关键位置
        levels = []
        current_price = prices.iloc[-1] if len(prices) > 0 else 0
        
        # 重要分位数
        quantiles = [0.1, 0.25, 0.5, 0.75, 0.9]
        
        for q in quantiles:
            level = prices.quantile(q)
            level_type = "support" if level < current_price else "resistance"
            
            # 计算强度（基于价格聚集程度）
            nearby_prices = prices[(prices >= level * 0.99) & (prices <= level * 1.01)]
            strength = min(100, len(nearby_prices) / len(prices) * 1000)
            
            levels.append({
                "price": round(level, 2),
                "type": level_type,
                "strength": round(strength, 1),
                "distance_pct": round(abs(level - current_price) / current_price * 100, 2),
                "description": f"{q*100:.0f}%分位数{level_type}"
            })
        
        # 按强度排序
        levels.sort(key=lambda x: x["strength"], reverse=True)
        
        return levels[:5]  # 返回前5个最强关键位
    
    def identify_integer_levels(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """识别整数关口"""
        if df.empty or "最新价" not in df.columns:
            return []
        
        current_price = df["最新价"].iloc[-1] if len(df) > 0 else 0
        
        if current_price <= 0:
            return []
        
        # 识别附近的整数关口
        integer_levels = []
        base = int(current_price)
        
        for i in range(-2, 3):
            level = base + i
            if level > 0:
                level_type = "support" if level < current_price else "resistance"
                
                integer_levels.append({
                    "price": level,
                    "type": level_type,
                    "strength": 60,  # 整数关口通常有中等强度
                    "distance_pct": round(abs(level - current_price) / current_price * 100, 2),
                    "description": f"整数关口{level}"
                })
        
        return integer_levels
    
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
            # 下跌趋势倾向于冬藏或春播
            tendencies["winter"] += trend_strength * 0.3
            tendencies["spring"] += (100 - trend_strength) * 0.2
        elif trend_type in ["strong_bull", "bull"]:
            # 上涨趋势倾向于夏长或秋收
            tendencies["summer"] += trend_strength * 0.3
            tendencies["autumn"] += trend_strength * 0.2
        
        # 基于形态判断
        pattern_score = pattern.get("score", 50)
        dominant_pattern = pattern.get("dominant_pattern", "")
        
        if "涨停潮" in dominant_pattern or "普涨" in dominant_pattern:
            tendencies["summer"] += 20
        elif "跌停潮" in dominant_pattern or "普跌" in dominant_pattern:
            tendencies["winter"] += 20
        elif "震荡" in dominant_pattern:
            tendencies["spring"] += 10
            tendencies["autumn"] += 10
        
        # 基于指标判断
        indicator_score = indicator.get("score", 50)
        
        if indicator_score > 70:
            tendencies["summer"] += 15
        elif indicator_score < 30:
            tendencies["winter"] += 15
        else:
            tendencies["spring"] += 5
            tendencies["autumn"] += 5
        
        # 基于关键位置判断
        key_level_score = key_level.get("score", 50)
        nearest_level = key_level.get("nearest_level")
        
        if nearest_level:
            level_type = nearest_level.get("type", "")
            distance_pct = nearest_level.get("distance_pct", 0)
            
            if level_type == "support" and distance_pct < 2:
                # 接近支撑位，可能反弹（春播）
                tendencies["spring"] += 10
            elif level_type == "resistance" and distance_pct < 2:
                # 接近阻力位，可能回落（秋收）
                tendencies["autumn"] += 10
        
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
    
    def calculate_confidence(self, trend: Dict, pattern: Dict, indicator: Dict, key_level: Dict) -> float:
        """计算分析置信度"""
        confidence_scores = []
        
        # 趋势置信度
        trend_persistence = trend.get("persistence", {}).get("persistence_score", 50)
        confidence_scores.append(trend_persistence)
        
        # 形态置信度
        pattern_reliability = pattern.get("details", {}).get("reliability", 50)
        confidence_scores.append(pattern_reliability)
        
        # 指标置信度
        indicator_consistency = indicator.get("details", {}).get("consistency", 50)
        confidence_scores.append(indicator_consistency)
        
        # 数据充分性
        data_sufficiency = 70  # 假设数据基本充分
        
        confidence_scores.append(data_sufficiency)
        
        # 计算平均置信度
        avg_confidence = np.mean(confidence_scores)
        
        return round(avg_confidence, 1)
    
    def assess_breakthrough_risk(self, key_levels: List[Dict], df: pd.DataFrame) -> str:
        """评估突破风险"""
        if not key_levels or df.empty:
            return "unknown"
        
        nearest_level = key_levels[0]
        distance_pct = nearest_level.get("distance_pct", 100)
        strength = nearest_level.get("strength", 0)
        
        if distance_pct < 1 and strength > 70:
            return "high"
        elif distance_pct < 2 and strength > 60:
            return "medium"
        else:
            return "low"
    
    def classify_levels(self, key_levels: List[Dict]) -> Dict[str, List]:
        """分类关键位置"""
        supports = [l for l in key_levels if l.get("type") == "support"]
        resistances = [l for l in key_levels if l.get("type") == "resistance"]
        
        return {
            "supports": supports[:3],  # 前3个支撑位
            "resistances": resistances[:3]  # 前3个阻力位
        }
    
    def assess_pattern_reliability(self, patterns: List[Dict]) -> float:
        """评估形态可靠性"""
        if not patterns:
            return 50.0
        
        reliabilities = []
        for pattern in patterns:
            confidence = pattern.get("confidence", 50)
            reliabilities.append(confidence)
        
        return round(np.mean(reliabilities), 1)
    
    def assess_signal_strength(self, indicators: Dict[str, Any]) -> str:
        """评估信号强度"""
        if not indicators:
            return "weak"
        
        scores = []
        for indicator_name, indicator_data in indicators.items():
            if isinstance(indicator_data, dict) and "score" in indicator_data:
                scores.append(indicator_data["score"])
        
        if not scores:
            return "weak"
        
        avg_score = np.mean(scores)
        
        if avg_score >= 70:
            return "strong"
        elif avg_score >= 60:
            return "moderate"
        elif avg_score >= 40:
            return "neutral"
        else:
            return "weak"
    
    def assess_indicator_consistency(self, indicators: Dict[str, Any]) -> float:
        """评估指标一致性"""
        if not indicators:
            return 50.0
        
        signals = []
        for indicator_name, indicator_data in indicators.items():
            if isinstance(indicator_data, dict) and "signal" in indicator_data:
                signal = indicator_data["signal"]
                # 将信号转换为数值
                if signal in ["看多", "积极"]:
                    signals.append(75)
                elif signal in ["看空", "谨慎"]:
                    signals.append(25)
                else:
                    signals.append(50)
        
        if not signals:
            return 50.0
        
        # 计算一致性（标准差越小越一致）
        if len(signals) >= 2:
            consistency = 100 - min(50, np.std(signals) * 10)
        else:
            consistency = 50.0
        
        return round(consistency, 1)
    
    def get_trend_description(self, trend: str, rise_ratio: float) -> str:
        """获取趋势描述"""
        descriptions = {
            "strong_bull": f"强势上涨（上涨比例{rise_ratio*100:.1f}%）",
            "bull": f"温和上涨（上涨比例{rise_ratio*100:.1f}%）",
            "neutral": f"震荡整理（上涨比例{rise_ratio*100:.1f}%）",
            "bear": f"温和下跌（上涨比例{rise_ratio*100:.1f}%）",
            "strong_bear": f"强势下跌（上涨比例{rise_ratio*100:.1f}%）",
            "unknown": "趋势不明"
        }
        return descriptions.get(trend, "趋势不明")
    
    def get_trend_signal(self, trend: str, strength: float) -> str:
        """获取趋势信号"""
        if trend in ["strong_bull", "bull"]:
            if strength > 80:
                return "强烈看多"
            elif strength > 60:
                return "看多"
            else:
                return "谨慎看多"
        elif trend in ["strong_bear", "bear"]:
            if strength > 80:
                return "强烈看空"
            elif strength > 60:
                return "看空"
            else:
                return "谨慎看空"
        else:
            if strength > 60:
                return "震荡偏强"
            elif strength < 40:
                return "震荡偏弱"
            else:
                return "震荡中性"
    
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
                "strength": 0,
                "details": {}
            },
            "pattern_analysis": {
                "patterns": [],
                "score": 50,
                "details": {}
            },
            "indicator_analysis": {
                "indicators": {},
                "score": 50,
                "details": {}
            },
            "key_level_analysis": {
                "key_levels": [],
                "score": 50,
                "details": {}
            },
            "market_status": "unknown",
            "confidence": 0
        }