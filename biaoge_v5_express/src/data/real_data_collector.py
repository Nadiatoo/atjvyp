"""
真实数据采集系统 - 稳健版
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
        
        # 这里可以添加从文件加载配置的逻辑
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
            
            # 设置超时和重试
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            session = requests.Session()
            retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            
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
            
            # 设置代理（如果需要）
            # ts.set_proxy('http://proxy.example.com:8080')
            
            # 获取交易日历
            trade_cal = ts.trade_cal()
            if trade_cal is None or len(trade_cal) == 0:
                return None
            
            # 获取最近交易日
            today = datetime.now().strftime('%Y%m%d')
            recent_trading = trade_cal[trade_cal['is_open'] == 1]
            if len(recent_trading) == 0:
                return None
            
            last_trade_date = recent_trading['cal_date'].iloc[-1]
            
            # 获取日线数据（简化版）
            # 这里需要根据实际需求调整
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
            # 这里可以使用requests直接调用API
            import requests
            
            url = "http://quote.eastmoney.com/center/api/sidemenu.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            # 解析数据
            data = response.json()
            
            # 这里需要根据实际API响应格式处理
            # 暂时返回None，需要具体实现
            
            return None
            
        except Exception as e:
            logger.error(f"东方财富数据获取异常: {e}")
            return None
    
    def _get_market_data_from_sina(self) -> Optional[Dict[str, Any]]:
        """从新浪财经获取市场数据"""
        try:
            # 新浪财经数据接口
            import requests
            
            url = "http://hq.sinajs.cn/list=sh000001"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            # 解析数据
            content = response.text
            # 新浪返回的是特定格式，需要解析
            
            # 这里需要根据实际API响应格式处理
            # 暂时返回None，需要具体实现
            
            return None
            
        except Exception as e:
            logger.error(f"新浪财经数据获取异常: {e}")
            return None
    
    def _process_market_data(self, df: pd.DataFrame, source: str) -> Dict[str, Any]:
        """处理市场数据"""
        try:
            # 确保必要的列存在
            required_columns = []
            if source == "akshare":
                required_columns = ["代码", "名称", "最新价", "涨跌幅"]
            elif source == "tushare":
                required_columns = ["code", "name", "trade", "changepercent"]
            
            # 重命名列以统一格式
            if source == "akshare":
                df = df.rename(columns={
                    "代码": "code",
                    "名称": "name", 
                    "最新价": "price",
                    "涨跌幅": "change_percent"
                })
            elif source == "tushare":
                df = df.rename(columns={
                    "code": "code",
                    "name": "name",
                    "trade": "price",
                    "changepercent": "change_percent"
                })
            
            # 计算市场统计
            if "change_percent" in df.columns:
                df["change_percent"] = pd.to_numeric(df["change_percent"], errors='coerce')
                
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
                    "average_change": df["change_percent"].mean() if total_count > 0 else 0,
                    "data_quality": "good",
                    "sample_stocks": self._get_sample_stocks(df)
                }
            else:
                # 数据列不完整，使用简化统计
                market_data = {
                    "timestamp": datetime.now(),
                    "source": source,
                    "total_stocks": len(df),
                    "rise_count": len(df) // 2,  # 估计值
                    "fall_count": len(df) // 2,  # 估计值
                    "rise_ratio": 0.5,
                    "average_change": 0,
                    "data_quality": "partial",
                    "note": f"从{source}获取的数据列不完整"
                }
            
            return market_data
            
        except Exception as e:
            logger.error(f"处理市场数据异常: {e}")
            return None
    
    def _get_sample_stocks(self, df: pd.DataFrame, n: int = 10) -> List[Dict[str, Any]]:
        """获取样本股票数据"""
        try:
            if len(df) == 0:
                return []
            
            # 获取涨跌幅最大的几只股票
            sample_df = df.nlargest(n, "change_percent")
            
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
    
    def get_news_data(self, category: str = "finance", limit: int = 10) -> List[Dict[str, Any]]:
        """获取新闻数据"""
        logger.info(f"开始获取新闻数据，类别: {category}")
        
        cache_key = f"news_{category}"
        cached_data = self.get_from_cache(cache_key)
        if cached_data:
            logger.info("使用缓存的新闻数据")
            return cached_data
        
        # 尝试获取真实新闻数据
        news_list = []
        
        try:
            # 这里可以集成多个新闻源
            # 暂时使用模拟数据
            
            news_list = self._get_mock_news_data(category, limit)
            
            # 保存到缓存
            self.save_to_cache(cache_key, news_list, ttl=600)  # 10分钟
            
            return news_list
            
        except Exception as e:
            logger.error(f"获取新闻数据异常: {e}")
            return self._get_mock_news_data(category, limit)
    
    def _get_mock_news_data(self, category: str, limit: int) -> List[Dict[str, Any]]:
        """获取模拟新闻数据"""
        news_templates = {
            "finance": [
                "央行宣布维持基准利率不变",
                "证监会发布新的上市公司监管指引",
                "A股市场今日震荡上行，科技股领涨",
                "外资连续三日净流入A股市场",
                "多家券商发布下半年投资策略报告"
            ],
            "policy": [
                "国务院常务会议研究部署稳经济政策措施",
                "发改委推动基础设施REITs健康发展",
                "财政部加大减税降费力度支持中小企业",
                "央行货币政策委员会召开季度例会"
            ],
            "industry": [
                "人工智能行业迎来政策利好",
                "新能源汽车销量持续增长",
                "半导体产业链国产化进程加速",
                "光伏行业技术突破推动成本下降"
            ]
        }
        
        templates = news_templates.get(category, news_templates["finance"])
        
        news_list = []
        for i in range(min(limit, len(templates))):
            news = {
                "id": f"news_{int(time.time())}_{i}",
                "title": templates[i],
                "content": f"{templates[i]}，相关分析认为这对市场将产生积极影响。",
                "category": category,
                "source": "simulated",
                "publish_time": (datetime.now() - timedelta(hours=i)).isoformat(),
                "sentiment": "positive" if i % 3 != 0 else "neutral",
                "relevance": 0.7 + i * 0.03
            }
            news_list.append(news)
        
        return news_list
    
    def get_economic_data(self, indicator: str = "cpi") -> Dict[str, Any]:
        """获取经济数据"""
        logger.info(f"开始获取经济数据，指标: {indicator}")
        
        cache_key = f"economic_{indicator}"
        cached_data = self.get_from_cache(cache_key)
        if cached_data:
            logger.info("使用缓存的经济数据")
            return cached_data
        
        # 尝试获取真实经济数据
        try:
            import akshare as ak
            
            if indicator == "cpi":
                df = ak.macro_china_cpi()
            elif indicator == "ppi":
                df = ak.macro_china_ppi()
            elif indicator == "gdp":
                df = ak.macro_china_gdp()
            else:
                df = ak.macro_china_cpi()  # 默认使用CPI
            
            if df is not None and len(df) > 0:
                # 处理经济数据
                economic_data = {
                    "indicator": indicator,
                    "source": "akshare",
                    "data_points": len(df),
                    "latest_value": float(df.iloc[-1].get("value", 0)) if "value