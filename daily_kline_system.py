#!/usr/bin/env python3
# 每日盘后日K线数据系统
# 设计原则：每日17:00获取日K线数据，用于市场分析

import sqlite3
import schedule
import time
import threading
from datetime import datetime, timedelta
import logging
import sys
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/daily_kline_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailyKlineSystem:
    """每日盘后日K线数据系统"""
    
    def __init__(self):
        self.db_path = "/Users/tuqibiao/.openclaw/workspace/a_stock_data.db"
        self.running = False
        self.kline_thread = None
        
    def get_daily_kline_data(self, stock_code, market="sz"):
        """获取股票日K线数据"""
        logger.info(f"获取日K线数据: {stock_code}")
        
        try:
            # 这里应该调用获取日K线数据的API
            # 暂时使用简化版本，从实时数据生成日K线
            
            from fix_sina_api import get_sina_stock_data
            
            # 获取当日实时数据
            realtime_data = get_sina_stock_data(stock_code, market)
            
            if realtime_data:
                # 从实时数据生成日K线
                kline_data = {
                    "code": stock_code,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "open": realtime_data.get("open", 0),
                    "high": realtime_data.get("high", 0),
                    "low": realtime_data.get("low", 0),
                    "close": realtime_data.get("price", 0),
                    "volume": realtime_data.get("volume", 0),
                    "amount": realtime_data.get("amount", 0),
                    "change": realtime_data.get("change", 0),
                    "change_percent": realtime_data.get("change_percent", 0),
                    "pre_close": realtime_data.get("prev_close", 0),
                    "source": "sina_realtime"
                }
                
                # 保存日K线数据
                self.save_daily_kline(kline_data)
                
                return kline_data
            else:
                logger.warning(f"无法获取实时数据生成日K线: {stock_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取日K线数据失败 {stock_code}: {e}")
            return None
    
    def save_daily_kline(self, kline_data):
        """保存日K线数据到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建日K线数据表（如果不存在）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_daily_kline (
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
                    pre_close REAL,
                    turnover_rate REAL,
                    source TEXT,
                    update_time TEXT,
                    UNIQUE(code, date)
                )
            ''')
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 插入或更新日K线数据
            cursor.execute('''
                INSERT OR REPLACE INTO stock_daily_kline 
                (code, date, open, high, low, close, volume, amount, change, change_percent, pre_close, source, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                kline_data["code"],
                kline_data["date"],
                kline_data["open"],
                kline_data["high"],
                kline_data["low"],
                kline_data["close"],
                kline_data["volume"],
                kline_data["amount"],
                kline_data["change"],
                kline_data["change_percent"],
                kline_data.get("pre_close", 0),
                kline_data.get("source", "unknown"),
                current_time
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"保存日K线数据: {kline_data['code']} {kline_data['date']}")
            return True
            
        except Exception as e:
            logger.error(f"保存日K线数据失败 {kline_data.get('code', 'unknown')}: {e}")
            return False
    
    def get_all_stocks_daily_kline(self):
        """获取所有股票的日K线数据"""
        logger.info("开始获取所有股票的日K线数据")
        
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
            
            success_count = 0
            failed_count = 0
            
            for code, market in stocks:
                # 转换为小写
                market_lower = market.lower() if market else "sz"
                
                kline_data = self.get_daily_kline_data(code, market_lower)
                
                if kline_data:
                    success_count += 1
                    logger.debug(f"获取日K线成功: {code}")
                else:
                    failed_count += 1
                    logger.warning(f"获取日K线失败: {code}")
            
            logger.info(f"日K线数据获取完成: 成功 {success_count}, 失败 {failed_count}")
            
            # 记录更新日志
            self.record_kline_update_log(len(stocks), success_count, failed_count)
            
            return success_count
            
        except Exception as e:
            logger.error(f"获取所有股票日K线数据失败: {e}")
            return 0
    
    def record_kline_update_log(self, total_stocks, success_count, failed_count):
        """记录日K线更新日志"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建更新日志表（如果不存在）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kline_update_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    update_date TEXT,
                    total_stocks INTEGER,
                    success_count INTEGER,
                    failed_count INTEGER,
                    success_rate REAL,
                    update_time TEXT,
                    details TEXT
                )
            ''')
            
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
                failed_count,
                success_rate,
                current_time,
                f"每日盘后日K线数据更新"
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"日K线更新日志记录完成: 成功率 {success_rate:.1%}")
            
        except Exception as e:
            logger.error(f"记录日K线更新日志失败: {e}")
    
    def get_stock_kline_history(self, stock_code, days=30):
        """获取股票历史日K线数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取最近N天的日K线数据
            cursor.execute('''
                SELECT date, open, high, low, close, volume, amount, change_percent
                FROM stock_daily_kline 
                WHERE code = ? 
                ORDER BY date DESC 
                LIMIT ?
            ''', (stock_code, days))
            
            klines = cursor.fetchall()
            conn.close()
            
            result = []
            for kline in klines:
                result.append({
                    "date": kline[0],
                    "open": kline[1],
                    "high": kline[2],
                    "low": kline[3],
                    "close": kline[4],
                    "volume": kline[5],
                    "amount": kline[6],
                    "change_percent": kline[7]
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取股票历史K线失败 {stock_code}: {e}")
            return []
    
    def get_market_summary(self, date=None):
        """获取市场概况（基于日K线数据）"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取当日所有股票的日K线数据
            cursor.execute('''
                SELECT code, close, change_percent, volume
                FROM stock_daily_kline 
                WHERE date = ?
            ''', (date,))
            
            all_klines = cursor.fetchall()
            
            if not all_klines:
                logger.warning(f"没有找到 {date} 的日K线数据")
                return None
            
            # 计算市场统计
            total_stocks = len(all_klines)
            up_count = len([k for k in all_klines if k[2] > 0])
            down_count = len([k for k in all_klines if k[2] < 0])
            flat_count = len([k for k in all_klines if k[2] == 0])
            
            # 计算平均涨跌幅
            avg_change = sum(k[2] for k in all_klines) / total_stocks if total_stocks > 0 else 0
            
            # 计算总成交量
            total_volume = sum(k[3] for k in all_klines)
            
            # 找出涨跌幅最大的股票
            sorted_by_change = sorted(all_klines, key=lambda x: x[2], reverse=True)
            top_gainers = sorted_by_change[:5]  # 涨幅前5
            top_losers = sorted_by_change[-5:]  # 跌幅前5
            
            conn.close()
            
            market_summary = {
                "date": date,
                "total_stocks": total_stocks,
                "up_count": up_count,
                "down_count": down_count,
                "flat_count": flat_count,
                "up_ratio": up_count / total_stocks if total_stocks > 0 else 0,
                "avg_change": avg_change,
                "total_volume": total_volume,
                "top_gainers": [
                    {"code": code, "change_percent": change, "close": close}
                    for code, close, change, _ in top_gainers
                ],
                "top_losers": [
                    {"code": code, "change_percent": change, "close": close}
                    for code, close, change, _ in top_losers
                ]
            }
            
            return market_summary
            
        except Exception as e:
            logger.error(f"获取市场概况失败: {e}")
            return None
    
    def setup_daily_schedule(self):
        """设置每日定时任务"""
        logger.info("设置每日盘后定时任务")
        
        # 每日盘后17:00获取日K线数据
        schedule.every().day.at("17:00").do(self.get_all_stocks_daily_kline)
        
        # 每周日20:00生成市场分析报告
        schedule.every().sunday.at("20:00").do(self.generate_market_analysis_report)
        
        logger.info("定时任务设置完成:")
        logger.info("  - 17:00: 获取所有股票日K线数据")
        logger.info("  - 周日20:00: 生成市场分析报告")
    
    def generate_market_analysis_report(self):
        """生成市场分析报告"""
        logger.info("开始生成市场分析报告")
        
        try:
            # 获取最近5个交易日的市场概况
            recent_dates = []
            for i in range(5):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                recent_dates.append(date)
            
            market_summaries = []
            for date in recent_dates:
                summary = self.get_market_summary(date)
                if summary:
                    market_summaries.append(summary)
            
            if not market_summaries:
                logger.warning("没有足够的数据生成市场分析报告")
                return
            
            # 生成报告
            report_path = "/Users/tuqibiao/.openclaw/workspace/market_analysis_report.md"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("# 市场分析报告\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**分析周期**: 最近{len(market_summaries)}个交易日\n\n")
                
                # 市场趋势分析
                f.write("## 市场趋势分析\n\n")
                
                for summary in market_summaries:
                    f.write(f"### {summary['date']}\n")
                    f.write(f"- 上涨家数: {summary['up_count']} ({summary['up_ratio']:.1%})\n")
                    f.write(f"- 下跌家数: {summary['down_count']}\n")
                    f.write(f"- 平均涨跌幅: {summary['avg_change']:+.2f}%\n")
                    f.write(f"- 总成交量: {summary['total_volume']:,.0f}手\n\n")
                
                # 强势股分析
                latest_summary = market_summaries[0]
                f.write("## 强势股分析（最新交易日）\n\n")
                
                f.write("### 涨幅前5\n")
                f.write("| 代码 | 涨幅 | 收盘价 |\n")
                f.write("|------|------|--------|\n")
                for stock in latest_summary['top_gainers']:
                    f.write(f"| {stock['code']} | {stock['change_percent']:+.2f}% | {stock['close']}元 |\n")
                
                f.write("\n### 跌幅前5\n")
                f.write("| 代码 | 跌幅 | 收盘价 |\n")
                f.write("|------|------|--------|\n")
                for stock in latest_summary['top_losers']:
                    f.write(f"| {stock['code']} | {stock['change_percent']:+.2f}% | {stock['close']}元 |\n")
                
                # 市场建议
                f.write("\n## 市场建议\n\n")
                
                avg_up_ratio = sum(s['up_ratio'] for s in market_summaries) / len(market_summaries)
                avg_change = sum(s['avg_change'] for s in market_summaries) / len(market_summaries)
                
                if avg_up_ratio > 0.6 and avg_change > 0.5:
                    f.write("**市场状态**: 强势上涨\n")
                    f.write("**建议**: 积极参与，关注强势股\n")
                elif avg_up_ratio > 0.4:
                    f.write("**市场状态**: 震荡偏强\n")
                    f.write("**建议**: 精选个股，控制仓位\n")
                else:
                    f.write("**市场状态**: 弱势调整\n")
                    f.write("**建议**: 谨慎观望，控制风险\n")
            
            logger.info(f"市场分析报告已生成: {report_path}")
            
        except Exception as e:
            logger.error(f"生成市场分析报告失败: {e}")
    
    def run_scheduler(self):
        """运行调度器"""
        logger.info("启动每日盘后调度器")
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
        
        logger.info("每日盘后调度器已停止")
    
    def start(self):
        """启动系统"""
        logger.info("启动每日盘后日K线数据系统")
        
        # 设置定时任务
        self.setup_daily_schedule()
        
        # 立即执行一次日K线数据获取（测试用）
        # self.get_all_stocks_daily_kline()
        
        # 启动调度器线程
        self.kline_thread = threading.Thread(target=self.run_scheduler)
        self.kline_thread.daemon = True
        self.kline_thread.start()
        
        logger.info("每日盘后日K线数据系统已启动")
    
    def stop(self):
        """停止系统"""
        logger.info("停止每日盘后日K线数据系统")
        self.running = False
        
        if self.kline_thread:
            self.kline_thread.join(timeout=10)
        
        logger.info("每日盘后日K线数据系统已停止")

def test_system():
    """测试系统"""
    print("=== 每日盘后日K线数据系统测试 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    system = DailyKlineSystem()
    
    print("\n1. 测试获取单只股票日K线数据...")
    kline_data = system.get_daily_kline_data("002675", "sz")
    if kline_data:
        print(f"   东诚药业日K线: {kline_data['date']}")
        print(f"