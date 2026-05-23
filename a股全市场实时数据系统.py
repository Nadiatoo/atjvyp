#!/usr/bin/env python3
# A股全市场实时数据系统 v1.0
# 设计目标：覆盖5000+ A股股票，实时数据，准确性保障

import requests
import json
import time
import sqlite3
from datetime import datetime, timedelta
import threading
import queue
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/a_stock_data_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AStockRealTimeSystem:
    """A股全市场实时数据系统"""
    
    def __init__(self):
        self.data_sources = self._init_data_sources()
        self.db_path = "/Users/tuqibiao/.openclaw/workspace/a_stock_data.db"
        self.init_database()
        self.data_queue = queue.Queue()
        self.running = False
        
    def _init_data_sources(self):
        """初始化数据源配置"""
        return {
            "eastmoney": {
                "name": "东方财富",
                "base_url": "http://quote.eastmoney.com",
                "reliability": 4,  # 可靠性评分 1-5
                "update_interval": 60,  # 更新间隔(秒)
                "coverage": "全市场",
            },
            "sina": {
                "name": "新浪财经", 
                "base_url": "http://hq.sinajs.cn",
                "reliability": 4,
                "update_interval": 30,
                "coverage": "全市场",
            },
            "tencent": {
                "name": "腾讯财经",
                "base_url": "http://qt.gtimg.cn",
                "reliability": 3,
                "update_interval": 60,
                "coverage": "主要股票",
            }
        }
    
    def init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建股票基本信息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_basic (
                    code TEXT PRIMARY KEY,
                    name TEXT,
                    industry TEXT,
                    market TEXT,
                    listing_date TEXT,
                    total_shares REAL,
                    float_shares REAL,
                    update_time TEXT
                )
            ''')
            
            # 创建实时行情表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_realtime (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT,
                    price REAL,
                    change REAL,
                    change_percent REAL,
                    volume REAL,
                    amount REAL,
                    high REAL,
                    low REAL,
                    open REAL,
                    pre_close REAL,
                    time TEXT,
                    source TEXT,
                    FOREIGN KEY (code) REFERENCES stock_basic (code)
                )
            ''')
            
            # 创建日K线数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_daily (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT,
                    date TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL,
                    amount REAL,
                    change REAL,
                    change_percent REAL,
                    turnover_rate REAL,
                    FOREIGN KEY (code) REFERENCES stock_basic (code),
                    UNIQUE(code, date)
                )
            ''')
            
            # 创建数据质量监控表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_quality (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    check_time TEXT,
                    total_stocks INTEGER,
                    updated_stocks INTEGER,
                    update_rate REAL,
                    avg_delay REAL,
                    error_count INTEGER,
                    source_health TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("数据库初始化完成")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
    
    def get_stock_list(self):
        """获取A股股票列表"""
        # 这里应该从数据源获取完整的A股列表
        # 暂时使用示例数据
        sample_stocks = [
            {"code": "002675", "name": "东诚药业", "market": "SZ"},
            {"code": "600893", "name": "航发动力", "market": "SH"},
            {"code": "000881", "name": "中广核技", "market": "SZ"},
            {"code": "300114", "name": "中航电测", "market": "SZ"},
            {"code": "600391", "name": "航发科技", "market": "SH"},
            {"code": "000999", "name": "华润三九", "market": "SZ"},
            {"code": "01763", "name": "中国同辐", "market": "HK"},
        ]
        
        # 实际应该从数据源获取全市场股票
        # 这里先返回示例数据
        return sample_stocks
    
    def fetch_realtime_data(self, stock_code, market="SZ"):
        """获取股票实时数据"""
        data_sources = list(self.data_sources.keys())
        results = []
        
        for source_key in data_sources:
            source = self.data_sources[source_key]
            try:
                if source_key == "sina":
                    data = self._fetch_from_sina(stock_code, market)
                elif source_key == "tencent":
                    data = self._fetch_from_tencent(stock_code, market)
                else:
                    data = self._fetch_from_eastmoney(stock_code, market)
                
                if data and self._validate_realtime_data(data):
                    data["source"] = source["name"]
                    data["fetch_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    results.append(data)
                    
            except Exception as e:
                logger.warning(f"数据源 {source['name']} 获取失败: {e}")
                continue
        
        # 选择最可靠的数据
        if results:
            # 简单策略：选择第一个成功获取的数据
            best_data = results[0]
            
            # 如果有多个数据源，可以进行交叉验证
            if len(results) > 1:
                best_data = self._cross_validate(results)
            
            return best_data
        
        return None
    
    def _fetch_from_sina(self, stock_code, market):
        """从新浪财经获取数据"""
        # 新浪财经数据格式示例
        # var hq_str_sz002675="东诚药业,14.480,14.480,0.000,0.000,0.000,14.480,14.480,...";
        
        if market == "SZ":
            symbol = f"sz{stock_code}"
        elif market == "SH":
            symbol = f"sh{stock_code}"
        else:
            symbol = stock_code
        
        url = f"http://hq.sinajs.cn/list={symbol}"
        
        try:
            response = requests.get(url, timeout=5)
            response.encoding = 'gbk'
            
            if response.status_code == 200:
                content = response.text
                # 解析数据
                data_str = content.split('="')[1].split('"')[0]
                fields = data_str.split(',')
                
                if len(fields) >= 30:
                    return {
                        "code": stock_code,
                        "name": fields[0],
                        "price": float(fields[3]),  # 当前价格
                        "open": float(fields[1]),   # 开盘价
                        "pre_close": float(fields[2]),  # 昨收
                        "high": float(fields[4]),   # 最高
                        "low": float(fields[5]),    # 最低
                        "volume": float(fields[8]), # 成交量(手)
                        "amount": float(fields[9]), # 成交额(万)
                        "buy1": float(fields[10]),  # 买一
                        "sell1": float(fields[20]), # 卖一
                    }
        
        except Exception as e:
            logger.error(f"新浪数据获取失败 {stock_code}: {e}")
        
        return None
    
    def _fetch_from_tencent(self, stock_code, market):
        """从腾讯财经获取数据"""
        # 腾讯财经数据格式示例
        # v_sz002675="51~东诚药业~002675~14.48~14.48~0.00~0.00~123456~...";
        
        if market == "SZ":
            symbol = f"sz{stock_code}"
        elif market == "SH":
            symbol = f"sh{stock_code}"
        else:
            symbol = stock_code
        
        url = f"http://qt.gtimg.cn/q={symbol}"
        
        try:
            response = requests.get(url, timeout=5)
            response.encoding = 'gbk'
            
            if response.status_code == 200:
                content = response.text
                data_str = content.split('="')[1].split('"')[0]
                fields = data_str.split('~')
                
                if len(fields) >= 40:
                    return {
                        "code": stock_code,
                        "name": fields[1],
                        "price": float(fields[3]),  # 当前价格
                        "open": float(fields[5]),   # 开盘价
                        "pre_close": float(fields[4]),  # 昨收
                        "high": float(fields[33]),  # 最高
                        "low": float(fields[34]),   # 最低
                        "volume": float(fields[6]), # 成交量(手)
                        "amount": float(fields[37]), # 成交额(万)
                    }
        
        except Exception as e:
            logger.error(f"腾讯数据获取失败 {stock_code}: {e}")
        
        return None
    
    def _fetch_from_eastmoney(self, stock_code, market):
        """从东方财富获取数据"""
        # 东方财富API需要更复杂的处理
        # 这里简化实现
        try:
            # 实际应该调用东方财富API
            # 暂时返回None，由其他数据源提供
            return None
            
        except Exception as e:
            logger.error(f"东方财富数据获取失败 {stock_code}: {e}")
            return None
    
    def _validate_realtime_data(self, data):
        """验证实时数据合理性"""
        required_fields = ["code", "price", "volume", "open", "high", "low", "pre_close"]
        
        # 检查必要字段
        for field in required_fields:
            if field not in data:
                logger.warning(f"数据缺少必要字段: {field}")
                return False
        
        # 检查价格合理性
        price = data["price"]
        if price <= 0 or price > 10000:  # A股价格合理范围
            logger.warning(f"价格不合理: {price}")
            return False
        
        # 检查成交量合理性
        volume = data["volume"]
        if volume < 0:
            logger.warning(f"成交量为负: {volume}")
            return False
        
        # 检查价格关系
        if data["low"] > data["high"]:
            logger.warning(f"最低价高于最高价: {data['low']} > {data['high']}")
            return False
        
        if data["price"] < data["low"] or data["price"] > data["high"]:
            logger.warning(f"当前价不在高低价范围内")
            return False
        
        return True
    
    def _cross_validate(self, data_list):
        """交叉验证多个数据源的数据"""
        if len(data_list) == 1:
            return data_list[0]
        
        # 简单策略：选择价格最接近平均值的
        prices = [d["price"] for d in data_list]
        avg_price = sum(prices) / len(prices)
        
        # 找到最接近平均价格的数据
        best_idx = 0
        min_diff = abs(prices[0] - avg_price)
        
        for i in range(1, len(prices)):
            diff = abs(prices[i] - avg_price)
            if diff < min_diff:
                min_diff = diff
                best_idx = i
        
        best_data = data_list[best_idx]
        best_data["cross_validated"] = True
        best_data["source_count"] = len(data_list)
        best_data["price_variance"] = min_diff
        
        return best_data
    
    def save_realtime_data(self, data):
        """保存实时数据到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 计算涨跌幅
            change = data["price"] - data["pre_close"]
            change_percent = change / data["pre_close"] * 100 if data["pre_close"] > 0 else 0
            
            cursor.execute('''
                INSERT INTO stock_realtime 
                (code, price, change, change_percent, volume, amount, high, low, open, pre_close, time, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data["code"],
                data["price"],
                change,
                change_percent,
                data["volume"],
                data.get("amount", 0),
                data["high"],
                data["low"],
                data["open"],
                data["pre_close"],
                current_time,
                data["source"]
            ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"保存实时数据: {data['code']} {data['price']}")
            return True
            
        except Exception as e:
            logger.error(f"保存数据失败 {data['code']}: {e}")
            return False
    
    def start_realtime_monitoring(self, interval=60):
        """启动实时监控"""
        self.running = True
        logger.info(f"启动实时监控，间隔{interval}秒")
        
        def monitoring_loop():
            while self.running:
                try:
                    stocks = self.get_stock_list()
                    updated_count = 0
                    
                    for stock in stocks:
                        data = self.fetch_realtime_data(stock["code"], stock.get("market", "SZ"))
                        if data:
                            self.save_realtime_data(data)
                            updated_count += 1
                    
                    # 记录数据质量
                    self.record_data_quality(len(stocks), updated_count)
                    
                    logger.info(f"数据更新完成: {updated_count}/{len(stocks)}")
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"监控循环错误: {e}")
                    time.sleep(interval)
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=monitoring_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return monitor_thread
    
    def record_data_quality(self, total_stocks, updated_stocks):
        """记录数据质量"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            update_rate = updated_stocks / total_stocks if total_stocks > 0 else 0
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 简单评估数据源健康状态
            source_health = "良好" if update_rate > 0.8 else "警告" if update_rate > 0.5 else "异常"
            
            cursor.execute('''
                INSERT INTO data_quality 
                (check_time,