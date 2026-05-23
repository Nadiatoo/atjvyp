"""
股票数据采集器 - 支持多数据源和本地缓存
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import time
import json
import os
from pathlib import Path
from .base_collector import BaseCollector

logger = logging.getLogger(__name__)


class StockCollector(BaseCollector):
    """股票数据采集器 - 支持多数据源和本地缓存"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("stock_collector", config)
        
        # 配置指数列表
        self.indices = config.get("indices", [
            {"symbol": "000001", "name": "上证指数"},
            {"symbol": "399001", "name": "深证成指"},
            {"symbol": "399006", "name": "创业板指"},
            {"symbol": "000688", "name": "科创50"}
        ])
        
        # 配置重点板块
        self.sectors = config.get("sectors", [
            {"name": "人工智能", "symbols": ["002230", "300496", "603019"]},
            {"name": "半导体", "symbols": ["603501", "002371", "300661"]},
            {"name": "新能源", "symbols": ["300750", "002594", "002460"]},
            {"name": "医药", "symbols": ["600276", "000538", "300347"]}
        ])
        
        # 缓存配置
        self.cache_dir = Path(config.get("cache_dir", "data/cache"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = config.get("cache_ttl", 300)  # 5分钟
        
        # 数据源优先级
        self.data_sources = config.get("data_sources", ["akshare", "local", "mock"])
        
        # 重试配置
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 5)
    
    def collect(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        采集股票数据
        
        Args:
            date: 采集日期，None表示最新
            
        Returns:
            股票数据字典
        """
        if date is None:
            date = self.get_trading_date()
        
        logger.info(f"开始采集股票数据，日期: {self.format_date(date)}")
        
        # 尝试从缓存读取
        cache_key = f"stock_data_{self.format_date(date)}"
        cached_data = self.load_from_cache(cache_key)
        if cached_data:
            logger.info(f"从缓存加载数据: {cache_key}")
            return cached_data
        
        # 按优先级尝试不同数据源
        data = None
        for source in self.data_sources:
            try:
                if source == "akshare":
                    data = self.collect_from_akshare(date)
                elif source == "local":
                    data = self.collect_from_local(date)
                elif source == "mock":
                    data = self.collect_mock_data(date)
                
                if data and self.validate_stock_data(data):
                    logger.info(f"从 {source} 数据源成功采集数据")
                    break
                    
            except Exception as e:
                logger.warning(f"数据源 {source} 采集失败: {e}")
                continue
        
        if data is None:
            logger.error("所有数据源采集失败")
            return {}
        
        # 处理和分析数据
        processed_data = self.process_stock_data(data, date)
        
        # 保存到缓存
        self.save_to_cache(cache_key, processed_data)
        
        # 记录采集日志
        self.log_collection(
            success=True,
            data_count=len(processed_data.get("stocks", []))
        )
        
        return processed_data
    
    def collect_from_akshare(self, date: datetime) -> Optional[pd.DataFrame]:
        """从AkShare采集数据"""
        logger.info("尝试从AkShare采集数据")
        
        for attempt in range(self.max_retries):
            try:
                # 获取实时行情
                df = ak.stock_zh_a_spot_em()
                
                if df is not None and len(df) > 0:
                    logger.info(f"AkShare采集成功，获取到 {len(df)} 条数据")
                    
                    # 获取涨停数据
                    try:
                        limit_up = ak.stock_zt_pool_em(date=self.format_date(date, "%Y%m%d"))
                        logger.info(f"涨停家数: {len(limit_up)}")
                    except:
                        limit_up = pd.DataFrame()
                    
                    # 获取跌停数据
                    try:
                        limit_down = ak.stock_dt_pool_em(date=self.format_date(date, "%Y%m%d"))
                        logger.info(f"跌停家数: {len(limit_down)}")
                    except:
                        limit_down = pd.DataFrame()
                    
                    return {
                        "stocks": df,
                        "limit_up": limit_up,
                        "limit_down": limit_down,
                        "source": "akshare",
                        "timestamp": datetime.now()
                    }
                
            except Exception as e:
                logger.warning(f"AkShare第{attempt + 1}次尝试失败: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"AkShare采集失败，已达到最大重试次数")
        
        return None
    
    def collect_from_local(self, date: datetime) -> Optional[Dict[str, Any]]:
        """从本地文件采集数据"""
        logger.info("尝试从本地文件采集数据")
        
        local_file = self.cache_dir / f"stock_data_{self.format_date(date)}.csv"
        if local_file.exists():
            try:
                df = pd.read_csv(local_file)
                logger.info(f"从本地文件加载 {len(df)} 条数据")
                return {
                    "stocks": df,
                    "source": "local",
                    "timestamp": datetime.now()
                }
            except Exception as e:
                logger.error(f"加载本地文件失败: {e}")
        
        return None
    
    def collect_mock_data(self, date: datetime) -> Dict[str, Any]:
        """生成模拟数据"""
        logger.info("生成模拟股票数据")
        
        # 生成模拟股票数据
        np.random.seed(int(date.timestamp()))
        n_stocks = 100
        
        symbols = [f"{i:06d}" for i in range(1, n_stocks + 1)]
        names = [f"股票{i}" for i in range(1, n_stocks + 1)]
        
        df = pd.DataFrame({
            "代码": symbols,
            "名称": names,
            "最新价": np.random.uniform(5, 100, n_stocks),
            "涨跌幅": np.random.uniform(-10, 10, n_stocks),
            "成交量(手)": np.random.randint(10000, 1000000, n_stocks),
            "成交额(万)": np.random.uniform(100, 10000, n_stocks),
            "换手率": np.random.uniform(0.1, 20, n_stocks),
            "振幅": np.random.uniform(1, 15, n_stocks),
            "量比": np.random.uniform(0.5, 5, n_stocks)
        })
        
        # 模拟涨停数据
        limit_up_count = np.random.randint(20, 80)
        limit_up_symbols = np.random.choice(symbols, limit_up_count, replace=False)
        
        limit_up = pd.DataFrame({
            "代码": limit_up_symbols,
            "名称": [f"涨停股{i}" for i in range(1, limit_up_count + 1)],
            "最新价": np.random.uniform(10, 50, limit_up_count),
            "涨跌幅": np.random.uniform(9.5, 10.5, limit_up_count)
        })
        
        # 模拟跌停数据
        limit_down_count = np.random.randint(5, 20)
        limit_down_symbols = np.random.choice(
            [s for s in symbols if s not in limit_up_symbols],
            limit_down_count,
            replace=False
        )
        
        limit_down = pd.DataFrame({
            "代码": limit_down_symbols,
            "名称": [f"跌停股{i}" for i in range(1, limit_down_count + 1)],
            "最新价": np.random.uniform(5, 30, limit_down_count),
            "涨跌幅": np.random.uniform(-10.5, -9.5, limit_down_count)
        })
        
        logger.info(f"生成模拟数据: {len(df)}只股票，{len(limit_up)}只涨停，{len(limit_down)}只跌停")
        
        return {
            "stocks": df,
            "limit_up": limit_up,
            "limit_down": limit_down,
            "source": "mock",
            "timestamp": datetime.now()
        }
    
    def process_stock_data(self, raw_data: Dict[str, Any], date: datetime) -> Dict[str, Any]:
        """处理股票数据"""
        logger.info("处理股票数据")
        
        df = raw_data.get("stocks", pd.DataFrame())
        
        if df.empty:
            return {}
        
        # 基础统计
        total_stocks = len(df)
        rise_count = len(df[df["涨跌幅"] > 0])
        fall_count = len(df[df["涨跌幅"] < 0])
        flat_count = total_stocks - rise_count - fall_count
        
        # 极端数据统计
        limit_up_count = len(raw_data.get("limit_up", pd.DataFrame()))
        limit_down_count = len(raw_data.get("limit_down", pd.DataFrame()))
        
        # 成交量统计
        total_volume = df["成交量(手)"].sum() if "成交量(手)" in df.columns else 0
        total_amount = df["成交额(万)"].sum() if "成交额(万)" in df.columns else 0
        
        # 技术指标计算（简化版）
        df_processed = df.copy()
        
        # 添加技术指标
        if "最新价" in df.columns:
            df_processed["ma5"] = df["最新价"].rolling(5, min_periods=1).mean()
            df_processed["ma10"] = df["最新价"].rolling(10, min_periods=1).mean()
            df_processed["ma20"] = df["最新价"].rolling(20, min_periods=1).mean()
        
        # 板块分析
        sector_analysis = self.analyze_sectors(df)
        
        # 龙头识别
        leaders = self.identify_leaders(df)
        
        processed_data = {
            "date": self.format_date(date),
            "timestamp": datetime.now(),
            "source": raw_data.get("source", "unknown"),
            
            # 市场统计
            "market_stats": {
                "total_stocks": total_stocks,
                "rise_count": rise_count,
                "fall_count": fall_count,
                "flat_count": flat_count,
                "rise_ratio": rise_count / total_stocks if total_stocks > 0 else 0,
                "limit_up_count": limit_up_count,
                "limit_down_count": limit_down_count,
                "total_volume": total_volume,
                "total_amount": total_amount
            },
            
            # 技术数据
            "technical_data": {
                "stocks": df_processed.to_dict(orient="records"),
                "limit_up": raw_data.get("limit_up", pd.DataFrame()).to_dict(orient="records"),
                "limit_down": raw_data.get("limit_down", pd.DataFrame()).to_dict(orient="records")
            },
            
            # 分析结果
            "analysis": {
                "sectors": sector_analysis,
                "leaders": leaders,
                "market_trend": self.analyze_market_trend(df),
                "risk_level": self.assess_risk_level(df, limit_up_count, limit_down_count)
            }
        }
        
        return processed_data
    
    def analyze_sectors(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析板块表现"""
        sector_performance = {}
        
        for sector in self.sectors:
            sector_symbols = sector["symbols"]
            sector_stocks = df[df["代码"].isin(sector_symbols)]
            
            if not sector_stocks.empty:
                avg_change = sector_stocks["涨跌幅"].mean()
                rise_ratio = len(sector_stocks[sector_stocks["涨跌幅"] > 0]) / len(sector_stocks)
                
                sector_performance[sector["name"]] = {
                    "stock_count": len(sector_stocks),
                    "avg_change": avg_change,
                    "rise_ratio": rise_ratio,
                    "stocks": sector_stocks[["代码", "名称", "最新价", "涨跌幅"]].to_dict(orient="records")
                }
        
        return sector_performance
    
    def identify_leaders(self, df: pd.DataFrame, top_n: int = 10) -> List[Dict[str, Any]]:
        """识别龙头股票"""
        if df.empty:
            return []
        
        # 按涨跌幅排序
        leaders = df.nlargest(top_n, "涨跌幅")
        
        leader_list = []
        for _, row in leaders.iterrows():
            leader_list.append({
                "symbol": row.get("代码", ""),
                "name": row.get("名称", ""),
                "price": row.get("最新价", 0),
                "change": row.get("涨跌幅", 0),
                "volume": row.get("成交量(手)", 0),
                "reason": self.get_leader_reason(row)
            })
        
        return leader_list
    
    def get_leader_reason(self, stock_data: pd.Series) -> str:
        """获取龙头股逻辑"""
        change = stock_data.get("涨跌幅", 0)
        volume = stock_data.get("成交量(手)", 0)
        
        reasons = []
        
        if change > 9:
            reasons.append("强势涨停")
        elif change > 5:
            reasons.append("大幅上涨")
        
        if volume > 1000000:  # 假设100万手为高成交量
            reasons.append("放量上涨")
        
        if len(reasons) == 0:
            reasons.append("技术突破")
        
        return "，".join(reasons)
    
    def analyze_market_trend(self, df: pd.DataFrame) -> str:
        """分析市场趋势"""
        if df.empty:
            return "unknown"
        
        rise_ratio = len(df[df["涨跌幅"] > 0]) / len(df)
        
        if rise_ratio > 0.7:
            return "strong_bull"
        elif rise_ratio > 0.55:
            return "bull"
        elif rise_ratio > 0.45:
            return "neutral"
        elif rise_ratio > 0.3:
            return "bear"
        else:
            return "strong_bear"
    
    def assess_risk_level(self, df: pd.DataFrame, limit_up: int, limit_down: int) -> str:
        """评估风险等级"""
        if df.empty:
            return "unknown"
        
        rise_ratio = len(df[df["涨跌幅"] > 0]) / len(df)
        
        if limit_down > 50:
            return "high"
        elif limit_down > 20:
            return "medium"
        elif rise_ratio < 0.3:
            return "medium"
        else:
            return "low"
    
    def validate_stock_data(self, data: Dict[str, Any]) -> bool:
        """验证股票数据"""
        required_fields = ["stocks", "source", "timestamp"]
        
        for field in required_fields:
            if field not in data:
                logger.warning(f"数据缺少必需字段: {field}")
                return False
        
        if not isinstance(data["stocks"], pd.DataFrame) or data["stocks"].empty:
            logger.warning("股票数据为空或不是DataFrame")
            return False
        
        return True
    
    def save_to_cache(self, key: str, data: Dict[str, Any]):
        """保存数据到缓存"""
        cache_file = self.cache_dir / f"{key}.json"
        
        try:
            # 转换DataFrame为可序列化格式
            cache_data = data.copy()
            
            if "technical_data" in cache_data:
                if "stocks" in cache_data["technical_data"]:
                    cache_data["technical_data"]["stocks"] = data["technical_data"]["stocks"]
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, default=str)
            
            logger.info(f"数据已保存到缓存: {cache_file}")
            
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    def load_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """从缓存加载数据"""
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        # 检查缓存是否过期
        file_age = time.time() - cache_file.stat().st_mtime
        if file_age > self.cache_ttl:
            logger.info(f"缓存已过期: {key} (年龄: {file_age:.0f}秒)")
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"从缓存加载数据: {key}")
            return data
            
        except Exception as e:
            logger.error(f"加载缓存失败: {e}")
            return None
    
    def cleanup(self):
        """清理缓存文件"""
        super().cleanup()
        
        # 清理过期缓存
        current_time = time.time()
        for cache_file in self.cache_dir.glob("*.json"):
            file_age = current_time - cache_file.stat().st_mtime
            if file_age > self.cache_ttl * 2:  # 两倍TTL
                try:
                    cache_file.unlink()
                    logger.info(f"清理过期缓存: {cache_file.name}")
                except Exception as e:
                    logger.warning(f"清理缓存失败: {e}")