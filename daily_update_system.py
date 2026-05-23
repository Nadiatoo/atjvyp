#!/usr/bin/env python3
# 每日自动更新系统
# 设计原则：每日更新一次股票列表，按需获取实时数据

import sqlite3
import schedule
import time
import threading
from datetime import datetime, timedelta
import logging
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/daily_update_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailyUpdateSystem:
    """每日自动更新系统"""
    
    def __init__(self):
        self.db_path = "/Users/tuqibiao/.openclaw/workspace/a_stock_data.db"
        self.running = False
        self.update_thread = None
        
    def update_stock_list(self):
        """更新股票列表（每日执行）"""
        logger.info("开始执行每日股票列表更新")
        
        try:
            # 这里应该调用获取真实股票列表的函数
            # 暂时使用简化版本
            
            from get_real_a_stock_list import get_real_a_stock_list
            
            stocks = get_real_a_stock_list()
            
            if stocks:
                logger.info(f"股票列表更新完成: {len(stocks)} 只股票")
                
                # 记录更新日志
                self.record_update_log("stock_list", len(stocks), "success")
                
                return True
            else:
                logger.error("股票列表更新失败: 获取到空列表")
                self.record_update_log("stock_list", 0, "failed")
                return False
                
        except Exception as e:
            logger.error(f"股票列表更新异常: {e}")
            self.record_update_log("stock_list", 0, f"error: {str(e)}")
            return False
    
    def get_stock_realtime_data(self, stock_codes):
        """按需获取股票实时数据"""
        logger.info(f"按需获取实时数据: {len(stock_codes)} 只股票")
        
        try:
            from fix_sina_api import get_sina_stock_data
            
            results = []
            
            for stock_info in stock_codes:
                if isinstance(stock_info, dict):
                    code = stock_info.get("code")
                    market = stock_info.get("market", "sz")
                else:
                    # 假设是字符串格式 "code:market"
                    parts = str(stock_info).split(":")
                    code = parts[0]
                    market = parts[1] if len(parts) > 1 else "sz"
                
                data = get_sina_stock_data(code, market)
                
                if data:
                    # 保存到数据库
                    self.save_realtime_data(data)
                    results.append({
                        "code": code,
                        "status": "success",
                        "data": data
                    })
                else:
                    results.append({
                        "code": code,
                        "status": "failed",
                        "error": "数据获取失败"
                    })
            
            logger.info(f"实时数据获取完成: 成功 {len([r for r in results if r['status'] == 'success'])}/{len(stock_codes)}")
            
            return results
            
        except Exception as e:
            logger.error(f"实时数据获取异常: {e}")
            return []
    
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
                data.get("source", "sina")
            ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"保存实时数据: {data['code']} {price}")
            return True
            
        except Exception as e:
            logger.error(f"保存实时数据失败 {data.get('code', 'unknown')}: {e}")
            return False
    
    def record_update_log(self, update_type, count, status):
        """记录更新日志"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建更新日志表（如果不存在）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS update_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    update_type TEXT,
                    update_count INTEGER,
                    status TEXT,
                    update_time TEXT,
                    details TEXT
                )
            ''')
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('''
                INSERT INTO update_log 
                (update_type, update_count, status, update_time, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                update_type,
                count,
                status,
                current_time,
                f"自动更新于 {current_time}"
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"更新日志记录: {update_type} - {status}")
            
        except Exception as e:
            logger.error(f"记录更新日志失败: {e}")
    
    def setup_daily_schedule(self):
        """设置每日定时任务"""
        logger.info("设置每日定时任务")
        
        # 每日早上8:00更新股票列表
        schedule.every().day.at("08:00").do(self.update_stock_list)
        
        # 每日晚上20:00清理旧数据（保留7天）
        schedule.every().day.at("20:00").do(self.clean_old_data)
        
        logger.info("定时任务设置完成:")
        logger.info("  - 08:00: 更新股票列表")
        logger.info("  - 20:00: 清理旧数据")
    
    def clean_old_data(self):
        """清理旧数据（保留最近7天）"""
        logger.info("开始清理旧数据")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 计算7天前的时间
            seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
            
            # 删除7天前的实时数据
            cursor.execute('''
                DELETE FROM stock_realtime 
                WHERE time < ?
            ''', (seven_days_ago,))
            
            deleted_count = cursor.rowcount
            
            # 删除7天前的更新日志
            cursor.execute('''
                DELETE FROM update_log 
                WHERE update_time < ?
            ''', (seven_days_ago,))
            
            log_deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"数据清理完成: 删除 {deleted_count} 条实时数据, {log_deleted_count} 条日志")
            self.record_update_log("data_cleanup", deleted_count, "success")
            
        except Exception as e:
            logger.error(f"数据清理失败: {e}")
            self.record_update_log("data_cleanup", 0, f"error: {str(e)}")
    
    def run_scheduler(self):
        """运行调度器"""
        logger.info("启动每日更新调度器")
        self.running = True
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
            except KeyboardInterrupt:
                logger.info("收到停止信号")
                break
            except Exception as e:
                logger.error(f"调度器运行异常: {e}")
                time.sleep(60)
        
        logger.info("每日更新调度器已停止")
    
    def start(self):
        """启动系统"""
        logger.info("启动每日自动更新系统")
        
        # 设置定时任务
        self.setup_daily_schedule()
        
        # 立即执行一次股票列表更新（首次运行）
        self.update_stock_list()
        
        # 启动调度器线程
        self.update_thread = threading.Thread(target=self.run_scheduler)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        logger.info("每日自动更新系统已启动")
    
    def stop(self):
        """停止系统"""
        logger.info("停止每日自动更新系统")
        self.running = False
        
        if self.update_thread:
            self.update_thread.join(timeout=10)
        
        logger.info("每日自动更新系统已停止")
    
    def get_stock_info(self, stock_code):
        """获取股票信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取基本信息
            cursor.execute('''
                SELECT code, name, market, update_time 
                FROM stock_basic 
                WHERE code = ?
            ''', (stock_code,))
            
            basic_info = cursor.fetchone()
            
            # 获取最新实时数据
            cursor.execute('''
                SELECT price, change_percent, volume, time, source 
                FROM stock_realtime 
                WHERE code = ? 
                ORDER BY time DESC 
                LIMIT 1
            ''', (stock_code,))
            
            realtime_info = cursor.fetchone()
            
            conn.close()
            
            result = {}
            
            if basic_info:
                result["basic"] = {
                    "code": basic_info[0],
                    "name": basic_info[1],
                    "market": basic_info[2],
                    "update_time": basic_info[3]
                }
            
            if realtime_info:
                result["realtime"] = {
                    "price": realtime_info[0],
                    "change_percent": realtime_info[1],
                    "volume": realtime_info[2],
                    "time": realtime_info[3],
                    "source": realtime_info[4]
                }
            
            return result
            
        except Exception as e:
            logger.error(f"获取股票信息失败 {stock_code}: {e}")
            return None

def test_system():
    """测试系统"""
    print("=== 每日自动更新系统测试 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    system = DailyUpdateSystem()
    
    print("\n1. 测试股票列表更新...")
    success = system.update_stock_list()
    print(f"   结果: {'成功' if success else '失败'}")
    
    print("\n2. 测试按需获取实时数据...")
    test_stocks = [
        {"code": "002675", "market": "sz"},
        {"code": "600893", "market": "sh"},
    ]
    
    results = system.get_stock_realtime_data(test_stocks)
    print(f"   获取 {len(results)} 只股票数据")
    
    for result in results:
        status = "✅" if result["status"] == "success" else "❌"
        print(f"   {status} {result['code']}: {result['status']}")
    
    print("\n3. 测试获取股票信息...")
    for code in ["002675", "600893"]:
        info = system.get_stock_info(code)
        if info and "realtime" in info:
            realtime = info["realtime"]
            print(f"   {code}: {realtime['price']}元 ({realtime['change_percent']:+.2f}%)")
    
    print("\n" + "=" * 50)
    print("✅ 系统测试完成")
    print("\n💡 使用说明:")
    print("1. 系统每日自动更新股票列表")
    print("2. 按需获取实时数据")
    print("3. 自动清理旧数据")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="每日自动更新系统")
    parser.add_argument("--test", action="store_true", help="运行测试")
    parser.add_argument("--start", action="store_true", help="启动系统")
    parser.add_argument("--stop", action="store_true", help="停止系统")
    parser.add_argument("--get", type=str, help="获取股票信息，格式: 代码[:市场]")
    parser.add_argument("--realtime", type=str, help="获取实时数据，格式: 代码1,代码2,...")
    
    args = parser.parse_args()
    
    system = DailyUpdateSystem()
    
    if args.test:
        test_system()
    
    elif args.start:
        system.start()
        try:
            # 保持主线程运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            system.stop()
    
    elif args.stop:
        system.stop()
    
    elif args.get:
        info = system.get_stock_info(args.get)
        if info:
            print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            print(f"未找到股票信息: {args.get}")
    
    elif args.realtime:
        stocks = args.realtime.split(",")
        results = system.get_stock_realtime_data(stocks)
        for result in results:
            print(f"{result['code']}: {result['status']}")
    
    else:
        print("请指定操作:")
        print("  --test     运行测试")
        print("  --start    启动系统")
        print("  --stop     停止系统")
        print("  --get CODE 获取股票信息")
        print("  --realtime CODE1,CODE2,... 获取实时数据")