#!/usr/bin/env python3
# 优化市场分析报告内容

import sqlite3
from datetime import datetime, timedelta
import json

class OptimizedMarketReport:
    """优化市场分析报告"""
    
    def __init__(self):
        self.db_path = "/Users/tuqibiao/.openclaw/workspace/a_stock_data.db"
    
    def generate_detailed_report(self, date=None):
        """生成详细市场分析报告"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"=== 生成优化市场分析报告 ===")
        print(f"报告日期: {date}")
        print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 1. 获取当日市场概况
            print("\n📊 1. 获取当日市场数据...")
            
            cursor.execute('''
                SELECT code, close, change_percent, volume, amount
                FROM stock_daily_kline 
                WHERE date = ?
            ''', (date,))
            
            all_klines = cursor.fetchall()
            
            if not all_klines:
                print("  未找到当日日K线数据")
                return None
            
            total_stocks = len(all_klines)
            print(f"  分析股票数量: {total_stocks}")
            
            # 2. 计算市场统计
            print("\n📈 2. 计算市场统计指标...")
            
            # 基础统计
            up_stocks = [k for k in all_klines if k[2] > 0]
            down_stocks = [k for k in all_klines if k[2] < 0]
            flat_stocks = [k for k in all_klines if k[2] == 0]
            
            up_count = len(up_stocks)
            down_count = len(down_stocks)
            flat_count = len(flat_stocks)
            
            # 涨跌幅统计
            changes = [k[2] for k in all_klines]
            avg_change = sum(changes) / total_stocks if total_stocks > 0 else 0
            max_gain = max(changes) if changes else 0
            max_loss = min(changes) if changes else 0
            
            # 成交量统计
            volumes = [k[3] for k in all_klines]
            total_volume = sum(volumes)
            avg_volume = total_volume / total_stocks if total_stocks > 0 else 0
            
            # 成交额统计
            amounts = [k[4] for k in all_klines]
            total_amount = sum(amounts)
            
            print(f"  上涨家数: {up_count} ({up_count/total_stocks*100:.1f}%)")
            print(f"  下跌家数: