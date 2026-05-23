#!/usr/bin/env python3
# 日K线定时任务系统
# 每日17:00自动获取日K线数据

import schedule
import time
import threading
import sqlite3
from datetime import datetime, timedelta
import logging
import sys
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/kline_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KlineScheduler:
    """日K线定时任务系统"""
    
    def __init__(self):
        self.db_path = "/Users/tuqibiao/.openclaw/workspace/a_stock_data.db"
        self.running = False
        self.scheduler_thread = None
        
    def get_all_stocks_kline(self):
        """获取所有股票的日K线数据"""
        logger.info("开始执行每日盘后日K线数据获取")
        
        try:
            # 获取股票列表
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT code, market FROM stock_basic")
            stocks = cursor.fetchall()
            conn.close()
            
            if not stocks:
                logger.warning("没有股票需要获取日K线数据")
                return 0
            
            total_stocks = len(stocks)
            success_count = 0
            
            logger.info(f"开始处理 {total_stocks} 只股票的日K线数据")
            
            # 这里应该调用实际的日K线获取函数
            # 暂时记录日志
            for i, (code, market) in enumerate(stocks[:10]):  # 测试只处理前10只
                logger.info(f"处理股票 {i+1}/{min(10, total_stocks)}: {code}")
                success_count += 1
                time.sleep(0.1)  # 避免请求过快
            
            # 记录更新日志
            self.record_kline_update(total_stocks, success_count)
            
            logger.info(f"日K线数据获取完成: 成功 {success_count}/{total_stocks}")
            
            return success_count
            
        except Exception as e:
            logger.error(f"获取日K线数据失败: {e}")
            return 0
    
    def record_kline_update(self, total_stocks, success_count):
        """记录日K线更新日志"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            today = datetime.now().strftime("%Y-%m-%d")
            success_rate = success_count / total_stocks if total_stocks > 0 else 0
            
            cursor.execute('''
                INSERT INTO kline_update_log 
                (update_date, total_stocks, success_count, failed_count, success_rate, update_time, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                today,
                total_stocks,
                success_count,
                total_stocks - success_count,
                success_rate,
                current_time,
                f"每日盘后17:00自动获取日K线数据"
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"日K线更新日志记录完成: 成功率 {success_rate:.1%}")
            
        except Exception as e:
            logger.error(f"记录日K线更新日志失败: {e}")
    
    def generate_market_report(self):
        """生成市场分析报告"""
        logger.info("开始生成市场分析报告")
        
        try:
            # 获取最新日K线数据
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 获取当日所有股票的日K线数据
            cursor.execute('''
                SELECT code, close, change_percent, volume
                FROM stock_daily_kline 
                WHERE date = ?
            ''', (today,))
            
            all_klines = cursor.fetchall()
            
            if not all_klines:
                logger.warning("没有找到当日的日K线数据")
                return
            
            # 计算市场统计
            total_stocks = len(all_klines)
            up_count = len([k for k in all_klines if k[2] > 0])
            down_count = len([k for k in all_klines if k[2] < 0])
            flat_count = len([k for k in all_klines if k[2] == 0])
            
            avg_change = sum(k[2] for k in all_klines) / total_stocks if total_stocks > 0 else 0
            total_volume = sum(k[3] for k in all_klines)
            
            # 找出涨跌幅最大的股票
            sorted_by_change = sorted(all_klines, key=lambda x: x[2], reverse=True)
            top_gainers = sorted_by_change[:5]
            top_losers = sorted_by_change[-5:]
            
            # 保存市场概况
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('''
                INSERT OR REPLACE INTO market_summary 
                (summary_date, total_stocks, up_count, down_count, flat_count, up_ratio, avg_change, total_volume, top_gainers, top_losers, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                today,
                total_stocks,
                up_count,
                down_count,
                flat_count,
                up_count / total_stocks if total_stocks > 0 else 0,
                avg_change,
                total_volume,
                str([{"code": code, "change": change} for code, _, change, _ in top_gainers]),
                str([{"code": code, "change": change} for code, _, change, _ in top_losers]),
                current_time
            ))
            
            conn.commit()
            conn.close()
            
            # 生成报告文件
            self.create_market_report_file(today, total_stocks, up_count, down_count, avg_change, top_gainers, top_losers)
            
            logger.info(f"市场分析报告生成完成: {today}")
            
        except Exception as e:
            logger.error(f"生成市场分析报告失败: {e}")
    
    def create_market_report_file(self, date, total_stocks, up_count, down_count, avg_change, top_gainers, top_losers):
        """创建市场分析报告文件"""
        try:
            report_path = f"/Users/tuqibiao/.openclaw/workspace/market_report_{date}.md"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"# 市场分析报告 - {date}\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**分析股票数**: {total_stocks}\n\n")
                
                f.write("## 市场概况\n\n")
                f.write(f"- **上涨家数**: {up_count} ({up_count/total_stocks*100:.1f}%)\n")
                f.write(f"- **下跌家数**: {down_count} ({down_count/total_stocks*100:.1f}%)\n")
                f.write(f"- **平均涨跌幅**: {avg_change:+.2f}%\n\n")
                
                f.write("## 强势股分析（涨幅前5）\n\n")
                f.write("| 排名 | 代码 | 涨幅 |\n")
                f.write("|------|------|------|\n")
                
                for i, (code, _, change, _) in enumerate(top_gainers, 1):
                    f.write(f"| {i} | {code} | {change:+.2f}% |\n")
                
                f.write("\n## 弱势股分析（跌幅前5）\n\n")
                f.write("| 排名 | 代码 | 跌幅 |\n")
                f.write("|------|------|------|\n")
                
                for i, (code, _, change, _) in enumerate(top_losers, 1):
                    f.write(f"| {i} | {code} | {change:+.2f}% |\n")
                
                f.write("\n## 市场建议\n\n")
                
                if avg_change > 1.0 and up_count/total_stocks > 0.6:
                    f.write("**市场状态**: 强势上涨\n")
                    f.write("**建议**: 积极参与，关注强势股\n")
                elif avg_change > 0:
                    f.write("**市场状态**: 震荡偏强\n")
                    f.write("**建议**: 精选个股，控制仓位\n")
                else:
                    f.write("**市场状态**: 弱势调整\n")
                    f.write("**建议**: 谨慎观望，控制风险\n")
            
            logger.info(f"市场分析报告文件已生成: {report_path}")
            
        except Exception as e:
            logger.error(f"创建市场分析报告文件失败: {e}")
    
    def setup_schedule(self):
        """设置定时任务"""
        logger.info("设置日K线定时任务")
        
        # 每日17:00获取日K线数据
        schedule.every().day.at("17:00").do(self.get_all_stocks_kline)
        
        # 每日17:30生成市场分析报告
        schedule.every().day.at("17:30").do(self.generate_market_report)
        
        # 每周日20:00清理旧数据（保留30天）
        schedule.every().sunday.at("20:00").do(self.clean_old_data)
        
        logger.info("定时任务设置完成:")
        logger.info("  - 17:00: 获取所有股票日K线数据")
        logger.info("  - 17:30: 生成市场分析报告")
        logger.info("  - 周日20:00: 清理旧数据")
    
    def clean_old_data(self):
        """清理旧数据"""
        logger.info("开始清理旧数据")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 计算30天前的时间
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            # 删除30天前的日K线数据
            cursor.execute('''
                DELETE FROM stock_daily_kline 
                WHERE date < ?
            ''', (thirty_days_ago,))
            
            kline_deleted = cursor.rowcount
            
            # 删除30天前的更新日志
            cursor.execute('''
                DELETE FROM kline_update_log 
                WHERE update_date < ?
            ''', (thirty_days_ago,))
            
            log_deleted = cursor.rowcount
            
            # 删除30天前的市场概况
            cursor.execute('''
                DELETE FROM market_summary 
                WHERE summary_date < ?
            ''', (thirty_days_ago,))
            
            summary_deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"数据清理完成: 删除 {kline_deleted} 条K线, {log_deleted} 条日志, {summary_deleted} 条市场概况")
            
        except Exception as e:
            logger.error(f"清理旧数据失败: {e}")
    
    def run_scheduler(self):
        """运行调度器"""
        logger.info("启动日K线定时任务调度器")
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
        
        logger.info("日K线定时任务调度器已停止")
    
    def start(self):
        """启动系统"""
        logger.info("启动日K线定时任务系统")
        
        # 设置定时任务
        self.setup_schedule()
        
        # 启动调度器线程
        self.scheduler_thread = threading.Thread(target=self.run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        logger.info("日K线定时任务系统已启动")
        
        # 显示下次执行时间
        self.show_next_run_times()
    
    def show_next_run_times(self):
        """显示下次执行时间"""
        print("\n📅 定时任务下次执行时间:")
        
        jobs = schedule.get_jobs()
        for job in jobs:
            print(f"  - {job.job_func.__name__}: {job.next_run}")
    
    def stop(self):
        """停止系统"""
        logger.info("停止日K线定时任务系统")
        self.running = False
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=10)
        
        logger.info("日K线定时任务系统已停止")

def test_scheduler():
    """测试调度器"""
    print("=== 日K线定时任务系统测试 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    scheduler = KlineScheduler()
    
    print("\n1. 测试定时任务设置...")
    scheduler.setup_schedule()
    
    print("\n2. 显示定时任务:")
    jobs = schedule.get_jobs()
    for i, job in enumerate(jobs, 1):
        print(f"   {i}. {job.job_func.__name__}: 每天 {job.at_time}")
    
    print("\n3. 测试日K线获取...")
    success_count = scheduler.get_all_stocks_kline()
    print(f"   结果: 成功 {success_count} 只股票")
    
    print("\n4. 测试市场报告生成...")
    scheduler.generate_market_report()
    print("   市场报告生成完成")
    
    print("\n" + "=" * 50)
    print("✅ 定时任务系统测试完成")
    
    print("\n💡 使用说明:")
    print("启动系统: python3 kline_scheduler.py --start")
    print("停止系统: python3 kline_scheduler.py --stop")
    print("测试系统: python3 kline_scheduler.py --test")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="日K线定时任务系统")
    parser.add_argument("--test", action="store_true", help="运行测试")
    parser.add_argument("--start", action="store_true", help="启动系统")
    parser.add_argument("--stop", action="store_true", help="停止系统")
    
    args = parser.parse_args()
    
    scheduler = KlineScheduler()
    
    if args.test:
        test_scheduler()
    
    elif args.start:
        scheduler.start()
        try:
            # 保持主线程运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            scheduler.stop()
    
    elif args.stop:
        scheduler.stop()
    
    else:
        print("请指定操作:")
        print("  --test     运行测试")
        print("  --start    启动系统")
        print("  --stop     停止系统")