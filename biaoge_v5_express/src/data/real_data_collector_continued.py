"""
真实数据采集系统 - 稳健版（续）
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
import json
import time
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class RealDataCollector:
    """真实数据采集器（稳健版）"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self.load_config(config_path)
        self.cache_dir = Path(self.config.get("cache_dir", "data/cache"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据源状态
        self.data_source_status = {
            "akshare": {"enabled": True, "last_success": None, "error_count": 0},
            "tushare": {"enabled": True, "last_success": None, "error_count": 0},
            "eastmoney": {"enabled": True, "last_success": None, "error_count": 0},
            "sina": {"enabled": True, "last_success": None, "error_count": 0}
        }
        
        # 缓存管理
        self.cache = {}
        self.cache_ttl = self.config.get("cache_ttl", 300)  # 5分钟
        
        logger.info("真实数据采集器初始化完成")
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "cache_dir": "data/cache",
            "cache_ttl": 300,  # 5分钟
            "max_retries": 3,
            "retry_delay": 5,  # 秒
            "timeout": 30,  # 秒
            "data_sources": {
                "market_data": {
                    "primary": "akshare",
                    "backup": ["tushare", "eastmoney", "sina"],
                    "enabled": True
                },
                "news_data": {
                    "sources": ["eastmoney", "sina"],
                    "enabled": True
                },
                "economic_data": {
                    "sources": ["akshare"],
                    "enabled": True
                }
            }
        }
        
        return default_config
    
    def get_market_data(self, use_cache: bool = True) -> Dict[str, Any]:
        """获取市场数据"""
        logger.info("开始获取市场数据")
        
        # 检查缓存
        cache_key = "market_data"
        if use_cache:
            cached_data = self.get_from_cache(cache_key)
            if cached_data:
                logger.info("使用缓存的市场数据")
                return cached_data
        
        # 尝试多个数据源
        data_sources = ["akshare", "tushare", "eastmoney", "sina"]
        
        for source in data_sources:
            if not self.data_source_status[source]["enabled"]:
                continue
                
            logger.info(f"尝试从 {source} 获取市场数据")
            
            try:
                if source == "akshare":
                    data = self._get_market_data_from_akshare()
                elif source == "tushare":
                    data = self._get_market_data_from_tushare()
                elif source == "eastmoney":
                    data = self._get_market_data_from_eastmoney()
                elif source == "sina":
                    data = self._get_market_data_from_sina()
                else:
                    continue
                
                if data is not None:
                    # 更新数据源状态
                    self.data_source_status[source]["last_success"] = datetime.now()
                    self.data_source_status[source]["error_count"] = 0
                    
                    # 保存到缓存
                    self.save_to_cache(cache_key, data)
                    
                    logger.info(f"成功从 {source} 获取市场数据")
                    return data
                    
            except Exception as e:
                logger.warning(f"从 {source} 获取市场数据失败: {e}")
                self.data_source_status[source]["error_count"] += 1
                
                # 如果错误次数过多，暂时禁用该数据源
                if self.data_source_status[source]["error_count"] >= 5:
                    self.data_source_status[source]["enabled"] = False
                    logger.warning(f"暂时禁用数据源 {source}")
        
        # 所有数据源都失败，使用模拟数据
        logger.warning("所有真实数据源失败，使用模拟数据")
        data = self._get_mock_market_data()
        
        # 保存模拟数据到缓存（较短TTL）
        self.save_to_cache(cache_key, data, ttl=60)  # 1分钟
        
        return data
    
    def _get_market_data_from_akshare(self) -> Optional[Dict[str, Any]]:
        """从AkShare获取市场数据"""
        try:
            import akshare as ak
            
            # 尝试获取数据
            df = ak.stock_zh_a_spot_em()
            
            if df is None or len(df) == 0:
                return None
            
            # 计算市场统计
            return self._process_market_data(df, "akshare")
            
        except Exception as e:
            logger.error(f"AkShare数据获取异常: {e}")
            return None
    
    def _get_market_data_from_tushare(self) -> Optional[Dict[str, Any]]:
        """从Tushare获取市场数据"""
        try:
            import tushare as ts
            
            # 检查token
            token = ts.get_token()
            if not token:
                logger.warning("Tushare token未配置")
                return None
            
            # 获取日线数据
            df = ts.get_today_all()
            
            if df is None or len(df) == 0:
                return None
            
            return self._process_market_data(df, "tushare")
            
        except Exception as e:
            logger.error(f"Tushare数据获取异常: {e}")
            return None
    
    def _get_market_data_from_eastmoney(self) -> Optional[Dict[str, Any]]:
        """从东方财富获取市场数据"""
        try:
            # 东方财富数据接口
            import requests
            
            # 使用东方财富的API
            url = "http://push2.eastmoney.com/api/qt/ulist.np/get"
            params = {
                "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20",
                "secids": "1.000001,0.399001,1.000300",
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": "2",
                "invt": "2"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # 简化处理，返回基础数据
            if data.get("data") and data["data"].get("diff"):
                stocks = data["data"]["diff"]
                
                # 计算简单统计
                changes = [s.get("f3", 0) for s in stocks if isinstance(s.get("f3"), (int, float))]
                
                if changes:
                    rise_count = sum(1 for c in changes if c > 0)
                    total_count = len(changes)
                    
                    market_data = {
                        "timestamp": datetime.now(),
                        "source": "eastmoney",
                        "total_stocks": total_count,
                        "rise_count": rise_count,
                        "fall_count": total_count - rise_count,
                        "rise_ratio": rise_count / total_count if total_count > 0 else 0,
                        "average_change": np.mean(changes) if changes else 0,
                        "data_quality": "partial",
                        "note": "从东方财富获取的简化数据"
                    }
                    
                    return market_data
            
            return None
            
        except Exception as e:
            logger.error(f"东方财富数据获取异常: {e}")
            return None
    
    def _get_market_data_from_sina(self) -> Optional[Dict[str, Any]]:
        """从新浪财经获取市场数据"""
        try:
            # 新浪财经数据接口
            import requests
            
            # 获取主要指数
            indices = ["sh000001", "sz399001", "sz399006"]
            all_data = []
            
            for index in indices:
                url = f"http://hq.sinajs.cn/list={index}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    content = response.text
                    # 解析新浪格式: var hq_str_sh000001="上证指数,3264.81,3270.39,...";
                    if "=" in content:
                        data_str = content.split("=")[1].strip('";')
                        parts = data_str.split(",")
                        
                        if len(parts) > 3:
                            name = parts[0]
                            current = float(parts[3]) if parts[3] else 0
                            previous = float(parts[2]) if parts[2] else current
                            
                            if previous > 0:
                                change_percent = (current - previous) / previous * 100
                                all_data.append({
                                    "code": index,
                                    "name": name,
                                    "price": current,
                                    "change_percent": change_percent
                                })
            
            if all_data:
                # 基于指数数据估算市场情况
                avg_change = np.mean([d["change_percent"] for d in all_data])
                
                # 简单估算：如果平均上涨，假设60%股票上涨
                if avg_change > 0:
                    rise_ratio = 0.6
                else:
                    rise_ratio = 0.4
                
                market_data = {
                    "timestamp": datetime.now(),
                    "source": "sina",
                    "total_stocks": 5000,  # 估计值
                    "rise_count": int(5000 * rise_ratio),
                    "fall_count": 5000 - int(5000 * rise_ratio),
                    "rise_ratio": rise_ratio,
                    "average_change": avg_change,
                    "data_quality": "estimated",
                    "note": "基于新浪指数数据估算",
                    "indices": all_data
                }
                
                return market_data
            
            return None
            
        except Exception as e:
            logger.error(f"新浪财经数据获取异常: {e}")
            return None
    
    def _process_market_data(self, df: pd.DataFrame, source: str) -> Dict[str, Any]:
        """处理市场数据"""
        try:
            # 重命名列以统一格式
            column_mapping = {
                "akshare": {
                    "代码": "code",
                    "名称": "name", 
                    "最新价": "price",
                    "涨跌幅": "change_percent"
                },
                "tushare": {
                    "code": "code",
                    "name": "name",
                    "trade": "price",
                    "changepercent": "change_percent"
                }
            }
            
            if source in column_mapping:
                df = df.rename(columns=column_mapping[source])
            
            # 确保change_percent是数值类型
            if "change_percent" in df.columns:
                df["change_percent"] = pd.to_numeric(df["change_percent"], errors='coerce')
                
                # 移除无效数据
                df = df.dropna(subset=["change_percent"])
                
                if len(df) == 0:
                    return None
                
                # 计算市场统计
                rise_count = len(df[df["change_percent"] > 0])
                fall_count = len(df[df["change_percent"] < 0])
                limit_up_count = len(df[df["change_percent"] > 9.5])
                limit_down_count = len(df[df["change_percent"] < -9.5])
                total_count = len(df)
                
                market_data = {
                    "timestamp": datetime.now(),
                    "source": source,
                    "total_stocks": total_count,
                    "rise_count": rise_count,
                    "fall_count": fall_count,
                    "limit_up_count": limit_up_count,
                    "limit_down_count": limit_down_count,
                    "rise_ratio": rise_count / total_count if total_count > 0 else 0,
                    "average_change": df["change_percent"].mean(),
                    "data_quality": "good",
                    "sample_stocks": self._get_sample_stocks(df)
                }
                
                return market_data
            else:
                # 数据列不完整
                return None
                
        except Exception as e:
            logger.error(f"处理市场数据异常: {e}")
            return None
    
    def _get_sample_stocks(self, df: pd.DataFrame, n: int = 10) -> List[Dict[str, Any]]:
        """获取样本股票数据"""
        try:
            if len(df) == 0:
                return []
            
            # 按涨跌幅排序
            if "change_percent" in df.columns:
                sorted_df = df.sort_values("change_percent", ascending=False)
                sample_df = pd.concat([sorted_df.head(n//2), sorted_df.tail(n//2)])
            else:
                sample_df = df.head(n)
            
            samples = []
            for _, row in sample_df.iterrows():
                sample = {
                    "code": str(row.get("code", "")),
                    "name": str(row.get("name", "")),
                    "price": float(row.get("price", 0)),
                    "change_percent": float(row.get("change_percent", 0))
                }
                samples.append(sample)
            
            return samples
            
        except Exception as e:
            logger.error(f"获取样本股票异常: {e}")
            return []
    
    def _get_mock_market_data(self) -> Dict[str, Any]:
        """获取模拟市场数据"""
        import random
        
        # 基于当前时间生成相对稳定的模拟数据
        current_hour = datetime.now().hour
        
        if 9 <= current_hour < 15:  # 交易时间
            # 交易时间模拟相对活跃的市场
            rise_ratio = random.uniform(0.45, 0.65)
            avg_change = random.uniform(-1, 2)
        else:
            # 非交易时间模拟相对平静的市场
            rise_ratio = random.uniform(0.48, 0.52)
            avg_change = random.uniform(-0.5, 0.5)
        
        total_stocks = 5000
        rise_count = int(total_stocks * rise_ratio)
        fall_count = total_stocks - rise_count
        
        return {
            "timestamp": datetime.now(),
            "source": "mock",
            "total_stocks": total_stocks,
            "rise_count": rise_count,
            "fall_count": fall_count,
            "limit_up_count": random.randint(20, 80),
            "limit_down_count": random.randint(5, 30),
            "rise_ratio": rise_ratio,
            "average_change": avg_change,
            "data_quality": "simulated",
            "note": "模拟数据，真实数据获取失败",
            "sample_stocks": [
                {"code": "000001", "name": "平安银行", "price": 10.5, "change_percent": 1.2},
                {"code": "000002", "name": "万科A", "price": 8.7, "change_percent": -0.5},
                {"code": "000858", "name": "五粮液", "price": 150.3, "change_percent": 2.1}
            ]
        }
    
    def get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        try:
            cache_file = self.cache_dir / f"{key}.json"
            
            if cache_file.exists():
                # 检查是否过期
                file_age = time.time() - cache_file.stat().st_mtime
                
                if file_age < self.cache_ttl:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 转换时间字符串回datetime
                    if "timestamp" in data and isinstance(data["timestamp"], str):
                        try:
                            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                        except:
                            data["timestamp"] = datetime.now()
                    
                    return data
            
            return None
            
        except Exception as e:
            logger.warning(f"读取缓存失败: {e}")
            return None
    
    def save_to_cache(self, key: str, data: Any, ttl: Optional[int] = None):
        """保存数据到缓存"""
        try:
            cache_file = self.cache_dir / f"{key}.json"
            
            # 准备数据用于JSON序列化
            cache_data = data.copy() if isinstance(data, dict) else data
            
            # 转换datetime为字符串
            if isinstance(cache_data, dict) and "timestamp" in cache_data:
                if isinstance(cache_data["timestamp"], datetime):
                    cache_data["timestamp"] = cache_data["timestamp"].isoformat()
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"数据已保存到缓存: {key}")
            
        except Exception as e:
            logger.warning(f"保存缓存失败: {e}")
    
    def get_data_source_status(self) -> Dict[str, Any]:
        """获取数据源状态"""
        status = {
            "timestamp": datetime.now(),
            "sources": {}
        }
        
        for source_name, source_info in self.data_source_status.items():
            status["sources"][source_name] = {
                "enabled": source_info["enabled"],
                "last_success": source_info["last_success"].isoformat() if source_info["last_success"] else None,
                "error_count": source_info["error_count"],
                "status": "healthy" if source_info["error_count"] == 0 else "degraded"
            }
        
