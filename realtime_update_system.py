#!/usr/bin/env python3
# 实时数据更新系统

import sqlite3
import time
import threading
import queue
from datetime import datetime, timedelta
import logging
from fix_sina_api import get_sina_stock_data
from a_stock_realtime_test import get_from_tencent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/realtime_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealTimeUpdateSystem:
    """实时数据更新系统"""
    
    def __init__(self):
        self.db_path = "/Users/tuqibiao/.openclaw/workspace/a_stock_data.db"
        self.update_interval = 60  # 更新间隔(秒)
        self.max_workers = 5  # 最大工作线程数
        self.running = False
        self.data_queue = queue.Queue()
        self.worker_threads = []
        
    def get_stocks_to_update(self):
        """获取需要更新的股票列表"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取所有股票
            cursor.execute("SELECT code, market FROM stock_basic")
            stocks = cursor.fetchall()
            
            conn.close()
            
            # 转换为字典列表
            stock_list = []
            for code, market in stocks:
                stock_list.append({
                    "code": code,
                    "market": market.lower()  # 转换为小写
                })
            
            logger.info(f"获取到 {len(stock_list)} 只需要更新的股票")
            return stock_list
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return []
    
    def update_stock_data(self, stock):
        """更新单只股票数据"""
        code = stock["code"]
        market = stock["market"]
        
        try:
            # 从新浪获取数据
            sina_data = get_sina_stock_data(code, market)
            
            if sina_data:
                # 验证数据
                if self.validate_stock_data(sina_data):
                    # 保存数据
                    self.save_realtime_data(sina_data)
                    return {"status": "success", "code": code, "source": "sina"}
                else:
                    logger.warning(f"数据验证失败: {code}")
                    return {"status": "validation_failed", "code": code}
            else:
                # 尝试从腾讯获取
                tencent_data = get_from_tencent(code, market)
                if tencent_data:
                    if self.validate_stock_data(tencent_data):
                        self.save_realtime_data(tencent_data)
                        return {"status": "success", "code": code, "source": "tencent"}
                
                logger.warning(f"所有数据源获取失败: {code}")
                return {"status": "failed", "code": code}
                
        except Exception as e:
            logger.error(f"更新股票数据失败 {code}: {e}")
            return {"status": "error", "code": code, "error": str(e)}
    
    def validate_stock_data(self, data):
        """验证股票数据合理性"""
        required_fields = ["code", "price", "volume"]
        
        # 检查必要字段
        for field in required_fields:
            if field not in data:
                return False
        
        # 检查价格合理性
        price = data["price"]
        if price <= 0 or price > 10000:  # A股价格合理范围
            return False
        
        # 检查成交量合理性
        volume = data.get("volume", 0)
        if volume < 0:
            return False
        
        return True
    
    def save_realtime_data(self, data):
        """保存实时数据到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 计算涨跌幅
            prev_close = data.get("prev_close", data.get("pre_close", 0))
            price = data["price"]
            
            if prev_close > 0:
                change = price - prev_close
                change_percent = change / prev_close * 100
            else:
                change = 0
                change_percent = 0
            
            # 插入实时数据
            cursor.execute('''
                INSERT INTO stock_realtime 
                (code, price, change, change_percent, volume, amount, high, low, open, pre_close, time, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data["code"],
                price,
                change,
                change_percent,
                data.get("volume", 0),
                data.get("amount", 0),
                data.get("high", price),
                data.get("low", price),
                data.get("open", price),
                prev_close,
                current_time,
                data.get("source", "unknown")
            ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"保存实时数据: {data['code']} {price}")
            return True
            
        except Exception as e:
            logger.error(f"保存数据失败 {data.get('code', 'unknown')}: {e}")
            return False
    
    def worker(self, worker_id):
        """工作线程"""
        logger.info(f"工作线程 {worker_id} 启动")
        
        while self.running:
            try:
                # 从队列获取任务
                stock = self.data_queue.get(timeout=1)
                
                if stock is None:  # 结束信号
                    break
                
                # 更新股票数据
                result = self.update_stock_data(stock)
                
                # 记录结果
                if result["status"] == "success":
                    logger.debug(f"线程{worker_id}: {stock['code']} 更新成功")
                else:
                    logger.warning(f"线程{worker_id}: {stock['code']} 更新失败 - {result['status']}")
                
                self.data_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"工作线程 {worker_id} 错误: {e}")
        
        logger.info(f"工作线程 {worker_id} 结束")
    
    def start_update(self):
        """启动实时更新"""
        logger.info(f"启动实时更新系统，间隔{self.update_interval}秒")
        self.running = True
        
        # 创建工作线程
        for i in range(self.max_workers):
            thread = threading.Thread(target=self.worker, args=(i+1,))
            thread.daemon = True
            thread.start()
            self.worker_threads.append(thread)
        
        # 主更新循环
        update_count = 0
        
        while self.running:
            try:
                update_count += 1
                logger.info(f"开始第 {update_count} 轮更新")
                
                # 获取需要更新的股票
                stocks = self.get_stocks_to_update()
                
                if not stocks:
                    logger.warning("没有需要更新的股票")
                    time.sleep(self.update_interval)
                    continue
                
                # 将股票加入队列
                for stock in stocks:
                    self.data_queue.put(stock)
                
                # 等待所有任务完成
                self.data_queue.join()
                
                # 记录更新统计
                self.record_update_stats(len(stocks), update_count)
                
                logger.info(f"第 {update_count} 轮更新完成，更新 {len(stocks)} 只股票")
                
                # 等待下一次更新
                time.sleep(self.update_interval)
                
            except KeyboardInterrupt:
                logger.info("收到停止信号")
                break
            except Exception as e:
                logger.error(f"更新循环错误: {e}")
                time.sleep(self.update_interval)
        
        self.stop_update()
    
    def record_update_stats(self, total_stocks, update_round):
        """记录更新统计"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 获取最近更新的股票数量
            five_min_ago = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                SELECT COUNT(DISTINCT code) FROM stock_realtime 
                WHERE time > ?
            ''', (five_min_ago,))
            
            recent_updates = cursor.fetchone()[0]
            update_rate = recent_updates / total_stocks if total_stocks > 0 else 0
            
            # 插入统计记录
            cursor.execute('''
                INSERT INTO data_quality 
                (check_time, total_stocks, updated_stocks, update_rate, avg_delay, error_count, source_health)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                current_time,
                total_stocks,
                recent_updates,
                update_rate,
                0,  # 平均延迟，需要实际计算
                0,  # 错误计数，需要实际统计
                "良好" if update_rate > 0.8 else "警告" if update_rate > 0.5 else "异常"
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"更新统计: {recent_updates}/{total_stocks} ({update_rate:.1%})")
            
        except Exception as e:
            logger.error(f"记录统计失败: {e}")
    
    def stop_update(self):
        """停止实时更新"""
        logger.info("停止实时更新系统")
        self.running = False
        
        # 发送结束信号给工作线程
        for _ in range(self.max_workers):
            self.data_queue.put(None)
        
        # 等待工作线程结束
        for thread in self.worker_threads:
            thread.join(timeout=5)
        
        logger.info("实时更新系统已停止")
    
    def run_once(self):
        """运行一次更新（测试用）"""
        logger.info("运行单次更新")
        
        stocks = self.get_stocks_to_update()
        
        if not stocks:
            logger.warning("没有需要更新的股票")
            return
        
        success_count = 0
        failed_count = 0
        
        # 只更新前10只股票（测试）
        test_stocks = stocks[:10]
        
        for stock in test_stocks:
            result = self.update_stock_data(stock)
            if result["status"] == "success":
                success_count += 1
            else:
                failed_count += 1
        
        logger.info(f"单次更新完成: 成功 {success_count}, 失败 {failed_count}")
        
        # 显示更新结果
        self.show_update_results(test_stocks)

def show_update_results(stocks):
    """显示更新结果"""
    print("\n=== 实时数据更新测试结果 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 从数据库读取最新数据
    try:
        db_path = "/Users/tuqibiao/.openclaw/workspace/a_stock_data.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for stock in stocks[:5]:  # 显示前5只
            cursor.execute('''
                SELECT code, price, change_percent, volume, time, source 
                FROM stock_realtime 
                WHERE code = ? 
                ORDER BY time DESC 
                LIMIT 1
            ''', (stock["code"],))
            
            result = cursor.fetchone()
            
            if result:
                code, price, change_percent, volume, update_time, source = result
                print(f"{code}: {price}元 ({change_percent:+.2f}%), 成交量: {volume:,.0f}手")
                print(f"  更新时间: {update_time}, 数据源: {source}")
            else:
                print(f"{stock['code']}: 无数据")
        
        conn.close()
        
    except Exception as e:
        print(f"显示结果失败: {e}")

if __name__ == "__main__":
    # 创建更新系统
    update_system = RealTimeUpdateSystem()
    
    print("=== 实时数据更新系统测试 ===")
    print("1. 运行单次更新测试")
    print("2. 启动持续更新")
    print("3. 显示当前数据")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        # 运行单次更新
        update_system.run_once()
        
    elif choice == "2":
        # 启动持续更新
        try:
            update_system.start_update()
        except KeyboardInterrupt:
            update_system.stop_update()
            
    elif choice == "3":
        # 显示当前数据
        stocks = update_system.get_stocks_to_update()
        show_update_results(stocks[:10])
        
    else:
        print("无效选择")