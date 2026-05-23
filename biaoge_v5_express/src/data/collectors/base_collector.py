"""
基础数据采集器
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import requests
from abc import ABC, abstractmethod

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """基础数据采集器抽象类"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        初始化采集器
        
        Args:
            name: 采集器名称
            config: 配置字典
        """
        self.name = name
        self.config = config
        self.enabled = config.get("enabled", True)
        self.timeout = config.get("timeout", 30)
        self.retry_times = config.get("retry_times", 3)
        self.retry_delay = config.get("retry_delay", 5)
        
        # 请求会话
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
    
    @abstractmethod
    def collect(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        采集数据
        
        Args:
            date: 采集日期，None表示最新
            
        Returns:
            采集到的数据字典
        """
        pass
    
    def safe_request(self, url: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
        """
        安全的HTTP请求，包含重试机制
        
        Args:
            url: 请求URL
            method: 请求方法
            **kwargs: 其他请求参数
            
        Returns:
            响应对象或None
        """
        for attempt in range(self.retry_times):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"第{attempt + 1}次请求失败: {e}")
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"请求失败，已达到最大重试次数: {url}")
                    return None
        
        return None
    
    def parse_date(self, date_str: str, formats: List[str] = None) -> Optional[datetime]:
        """
        解析日期字符串
        
        Args:
            date_str: 日期字符串
            formats: 日期格式列表
            
        Returns:
            解析后的datetime对象
        """
        if formats is None:
            formats = [
                "%Y-%m-%d",
                "%Y%m%d",
                "%Y/%m/%d",
                "%Y-%m-%d %H:%M:%S"
            ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"无法解析日期字符串: {date_str}")
        return None
    
    def format_date(self, date: datetime, fmt: str = "%Y-%m-%d") -> str:
        """
        格式化日期
        
        Args:
            date: datetime对象
            fmt: 格式字符串
            
        Returns:
            格式化后的日期字符串
        """
        return date.strftime(fmt)
    
    def get_trading_date(self, date: Optional[datetime] = None) -> datetime:
        """
        获取交易日
        
        Args:
            date: 参考日期，None表示今天
            
        Returns:
            交易日datetime对象
        """
        if date is None:
            date = datetime.now()
        
        # 如果是周末，调整到最近的周五
        if date.weekday() >= 5:  # 5=周六, 6=周日
            days_to_friday = (date.weekday() - 4) % 7
            date = date - timedelta(days=days_to_friday)
        
        return date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def validate_data(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        验证数据完整性
        
        Args:
            data: 数据字典
            required_fields: 必需字段列表
            
        Returns:
            数据是否完整
        """
        if not data:
            logger.warning("数据为空")
            return False
        
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            logger.warning(f"数据缺少必需字段: {missing_fields}")
            return False
        
        return True
    
    def save_to_csv(self, data: pd.DataFrame, filename: str):
        """
        保存数据到CSV文件
        
        Args:
            data: pandas DataFrame
            filename: 文件名
        """
        try:
            data.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"数据已保存到: {filename}")
        except Exception as e:
            logger.error(f"保存CSV文件失败: {e}")
    
    def load_from_csv(self, filename: str) -> Optional[pd.DataFrame]:
        """
        从CSV文件加载数据
        
        Args:
            filename: 文件名
            
        Returns:
            pandas DataFrame或None
        """
        try:
            data = pd.read_csv(filename, encoding='utf-8-sig')
            logger.info(f"从CSV文件加载数据: {filename}, 行数: {len(data)}")
            return data
        except Exception as e:
            logger.error(f"加载CSV文件失败: {e}")
            return None
    
    def log_collection(self, success: bool, data_count: int = 0, error_msg: str = ""):
        """
        记录采集日志
        
        Args:
            success: 是否成功
            data_count: 数据数量
            error_msg: 错误信息
        """
        if success:
            logger.info(f"{self.name} 采集成功，采集到 {data_count} 条数据")
        else:
            logger.error(f"{self.name} 采集失败: {error_msg}")
    
    def cleanup(self):
        """清理资源"""
        self.session.close()
        logger.info(f"{self.name} 采集器资源已清理")


class DataCollectorManager:
    """数据采集器管理器"""
    
    def __init__(self):
        self.collectors = {}
        self.collection_history = []
    
    def register_collector(self, name: str, collector: BaseCollector):
        """注册采集器"""
        self.collectors[name] = collector
        logger.info(f"注册采集器: {name}")
    
    def unregister_collector(self, name: str):
        """注销采集器"""
        if name in self.collectors:
            self.collectors[name].cleanup()
            del self.collectors[name]
            logger.info(f"注销采集器: {name}")
    
    def collect_all(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        执行所有采集器的采集任务
        
        Args:
            date: 采集日期
            
        Returns:
            所有采集结果
        """
        results = {}
        
        for name, collector in self.collectors.items():
            if not collector.enabled:
                logger.info(f"采集器 {name} 已禁用，跳过")
                continue
            
            logger.info(f"开始采集: {name}")
            start_time = time.time()
            
            try:
                data = collector.collect(date)
                elapsed_time = time.time() - start_time
                
                if data is not None:
                    results[name] = data
                    self.collection_history.append({
                        "collector": name,
                        "timestamp": datetime.now(),
                        "success": True,
                        "elapsed_time": elapsed_time,
                        "data_count": len(data) if isinstance(data, (list, dict)) else 1
                    })
                    logger.info(f"采集器 {name} 完成，耗时: {elapsed_time:.2f}秒")
                else:
                    self.collection_history.append({
                        "collector": name,
                        "timestamp": datetime.now(),
                        "success": False,
                        "elapsed_time": elapsed_time,
                        "error": "采集返回None"
                    })
                    logger.warning(f"采集器 {name} 返回None")
                    
            except Exception as e:
                elapsed_time = time.time() - start_time
                self.collection_history.append({
                    "collector": name,
                    "timestamp": datetime.now(),
                    "success": False,
                    "elapsed_time": elapsed_time,
                    "error": str(e)
                })
                logger.error(f"采集器 {name} 发生错误: {e}")
        
        return results
    
    def get_collection_stats(self) -> pd.DataFrame:
        """获取采集统计信息"""
        if not self.collection_history:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.collection_history)
        return df
    
    def cleanup_all(self):
        """清理所有采集器"""
        for name, collector in self.collectors.items():
            try:
                collector.cleanup()
            except Exception as e:
                logger.error(f"清理采集器 {name} 失败: {e}")
        
        logger.info("所有采集器已清理")