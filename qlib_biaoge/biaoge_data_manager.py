#!/usr/bin/env python3
"""
彪哥战法 - 增强版数据获取模块
支持：AKShare实时获取 + SQLite本地缓存 + 失败自动回退
"""

import os
import sqlite3
import json
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List


class BiaogeDataManager:
    """
    彪哥战法数据管理器
    优先从AKShare获取实时数据，失败时使用本地缓存
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化数据管理器
        
        Args:
            db_path: SQLite数据库路径，默认存储在用户目录
        """
        if db_path is None:
            self.db_path = Path.home() / ".openclaw/workspace/qlib_biaoge/biaoge_data.db"
        else:
            self.db_path = Path(db_path)
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 股票日线数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_daily (
                code TEXT,
                name TEXT,
                date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                amount REAL,
                change_pct REAL,
                turnover REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (code, date)
            )
        ''')
        
        # 市场统计表（用于盘后分析）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_stats (
                date TEXT PRIMARY KEY,
                total_stocks INTEGER,
                up_stocks INTEGER,
                down_stocks INTEGER,
                limit_up INTEGER,
                limit_down INTEGER,
                avg_turnover REAL,
                market_data TEXT,  -- JSON格式存储完整数据
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 数据更新日志
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS update_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                source TEXT,
                status TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_update(self, date: str, source: str, status: str, message: str = ""):
        """记录数据更新日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO update_log (date, source, status, message) VALUES (?, ?, ?, ?)",
            (date, source, status, message)
        )
        conn.commit()
        conn.close()
    
    def get_full_market_data(self, force_refresh: bool = False) -> Optional[pd.DataFrame]:
        """
        获取全市场数据
        
        Args:
            force_refresh: 是否强制刷新，不从缓存读取
            
        Returns:
            包含全市场股票数据的DataFrame，失败返回None
        """
        today = datetime.now().strftime("%Y%m%d")
        
        # 如果不是强制刷新，先检查缓存
        if not force_refresh:
            cached_data = self._get_cached_market_data(today)
            if cached_data is not None:
                print(f"使用缓存数据 (日期: {today})")
                return cached_data
        
        # 尝试从AKShare获取
        print("尝试从AKShare获取实时数据...")
        try:
            df = ak.stock_zh_a_spot_em()
            print(f"成功获取 {len(df)} 只股票数据")
            
            # 标准化列名
            df = self._standardize_columns(df)
            
            # 保存到缓存
            self._save_market_data(today, df)
            self.log_update(today, "akshare", "success", f"获取{len(df)}只股票")
            
            return df
            
        except Exception as e:
            print(f"AKShare获取失败: {e}")
            self.log_update(today, "akshare", "failed", str(e))
            
            # 获取最近一次成功的缓存数据
            cached_data = self._get_latest_cached_data()
            if cached_data is not None:
                cached_date = cached_data['date'].iloc[0] if 'date' in cached_data.columns else "未知"
                print(f"使用历史缓存数据 (日期: {cached_date})")
                return cached_data
            
            return None
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化AKShare返回的列名"""
        # AKShare的列名映射
        column_map = {
            '代码': 'code',
            '名称': 'name',
            '最新价': 'close',
            '涨跌幅': 'change_pct',
            '涨跌额': 'change',
            '成交量': 'volume',
            '成交额': 'amount',
            '振幅': 'amplitude',
            '最高': 'high',
            '最低': 'low',
            '今开': 'open',
            '昨收': 'pre_close',
            '量比': 'volume_ratio',
            '换手率': 'turnover',
            '市盈率-动态': 'pe',
            '市净率': 'pb',
            '总市值': 'total_market_cap',
            '流通市值': 'float_market_cap',
            '涨速': 'rise_speed',
            '5分钟涨跌': 'change_5min',
            '60日涨跌幅': 'change_60d',
            '年初至今涨跌幅': 'change_ytd',
        }
        
        # 重命名存在的列
        for old_name, new_name in column_map.items():
            if old_name in df.columns:
                df[new_name] = df[old_name]
        
        # 添加日期列
        df['date'] = datetime.now().strftime("%Y-%m-%d")
        
        return df
    
    def _save_market_data(self, date: str, df: pd.DataFrame):
        """保存市场数据到数据库"""
        conn = sqlite3.connect(self.db_path)
        
        # 准备数据
        save_df = df.copy()
        save_df['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 选择关键列保存
        columns_to_save = ['code', 'name', 'date', 'open', 'high', 'low', 'close', 
                          'volume', 'amount', 'change_pct', 'turnover', 'updated_at']
        available_columns = [c for c in columns_to_save if c in save_df.columns]
        
        save_df = save_df[available_columns]
        
        # 保存到数据库
        save_df.to_sql('stock_daily', conn, if_exists='append', index=False)
        
        # 计算并保存市场统计
        stats = self._calculate_market_stats(df, date)
        self._save_market_stats(stats)
        
        conn.close()
        print(f"数据已缓存到数据库: {self.db_path}")
    
    def _calculate_market_stats(self, df: pd.DataFrame, date: str) -> Dict:
        """计算市场统计指标"""
        total = len(df)
        up = len(df[df['change_pct'] > 0]) if 'change_pct' in df.columns else 0
        down = len(df[df['change_pct'] < 0]) if 'change_pct' in df.columns else 0
        limit_up = len(df[df['change_pct'] >= 9.5]) if 'change_pct' in df.columns else 0
        limit_down = len(df[df['change_pct'] <= -9.5]) if 'change_pct' in df.columns else 0
        avg_turnover = df['turnover'].mean() if 'turnover' in df.columns else 0
        
        # 保存完整数据为JSON
        market_data_json = df.to_json(orient='records', force_ascii=False)
        
        return {
            'date': date,
            'total_stocks': total,
            'up_stocks': up,
            'down_stocks': down,
            'limit_up': limit_up,
            'limit_down': limit_down,
            'avg_turnover': avg_turnover,
            'market_data': market_data_json
        }
    
    def _save_market_stats(self, stats: Dict):
        """保存市场统计数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO market_stats 
            (date, total_stocks, up_stocks, down_stocks, limit_up, limit_down, avg_turnover, market_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            stats['date'],
            stats['total_stocks'],
            stats['up_stocks'],
            stats['down_stocks'],
            stats['limit_up'],
            stats['limit_down'],
            stats['avg_turnover'],
            stats['market_data']
        ))
        
        conn.commit()
        conn.close()
    
    def _get_cached_market_data(self, date: str) -> Optional[pd.DataFrame]:
        """获取指定日期的缓存数据"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM stock_daily WHERE date = ?"
        df = pd.read_sql_query(query, conn, params=(date,))
        
        conn.close()
        
        if len(df) > 0:
            return df
        return None
    
    def _get_latest_cached_data(self) -> Optional[pd.DataFrame]:
        """获取最近一次成功缓存的数据"""
        conn = sqlite3.connect(self.db_path)
        
        # 获取最新有数据的日期
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT date FROM stock_daily ORDER BY date DESC LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            latest_date = result[0]
            query = "SELECT * FROM stock_daily WHERE date = ?"
            df = pd.read_sql_query(query, conn, params=(latest_date,))
            conn.close()
            return df
        
        conn.close()
        return None
    
    def get_market_summary(self, date: Optional[str] = None) -> Optional[Dict]:
        """
        获取市场摘要统计
        
        Args:
            date: 指定日期，默认今天
            
        Returns:
            市场统计字典
        """
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM market_stats WHERE date = ?",
            (date,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'date': result[0],
                'total_stocks': result[1],
                'up_stocks': result[2],
                'down_stocks': result[3],
                'limit_up': result[4],
                'limit_down': result[5],
                'avg_turnover': result[6]
            }
        return None


def test_data_manager():
    """测试数据管理器"""
    print("=" * 60)
    print("彪哥战法数据管理器测试")
    print("=" * 60)
    
    dm = BiaogeDataManager()
    
    # 测试获取数据
    print("\n获取全市场数据...")
    df = dm.get_full_market_data()
    
    if df is not None:
        print(f"\n✅ 成功获取 {len(df)} 只股票数据")
        print("\n数据预览:")
        print(df[['code', 'name', 'close', 'change_pct', 'turnover']].head(10))
        
        # 获取市场摘要
        summary = dm.get_market_summary()
        if summary:
            print(f"\n市场统计:")
            print(f"  总股票数: {summary['total_stocks']}")
            print(f"  上涨: {summary['up_stocks']}")
            print(f"  下跌: {summary['down_stocks']}")
            print(f"  涨停: {summary['limit_up']}")
            print(f"  跌停: {summary['limit_down']}")
    else:
        print("\n❌ 获取数据失败")


if __name__ == "__main__":
    test_data_manager()
