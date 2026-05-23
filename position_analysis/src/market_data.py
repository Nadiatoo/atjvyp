#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行情数据获取模块
基础层：实时行情数据获取、缓存管理
"""

import requests
import pandas as pd
import numpy as np
import time
import json
import os
import logging
from datetime import datetime, timedelta
import sqlite3
from typing import Dict, List, Optional, Tuple

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MarketDataFetcher:
    """行情数据获取器"""
    
    def __init__(self, cache_enabled=True, cache_dir="../data/cache"):
        """
        初始化行情数据获取器
        
        Args:
            cache_enabled (bool): 是否启用缓存
            cache_dir (str): 缓存目录
        """
        self.cache_enabled = cache_enabled
        self.cache_dir = cache_dir
        self.cache_db = None
        
        # 东方财富API配置
        self.eastmoney_api_base = "http://push2.eastmoney.com/api/"
        
        # QVeris API配置（备用）
        self.qveris_api_key = os.environ.get("QVERIS_API_KEY", "")
        self.qveris_api_base = "https://api.qveris.io/v1/"
        
        # 初始化缓存
        if cache_enabled:
            self._init_cache()
    
    def _init_cache(self):
        """初始化缓存数据库"""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            cache_db_path = os.path.join(self.cache_dir, "market_data.db")
            self.cache_db = sqlite3.connect(cache_db_path)
            
            # 创建缓存表
            cursor = self.cache_db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_quotes (
                    stock_code TEXT PRIMARY KEY,
                    data_json TEXT,
                    timestamp DATETIME,
                    expires_at DATETIME
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS batch_quotes (
                    batch_id TEXT PRIMARY KEY,
                    stock_codes TEXT,
                    data_json TEXT,
                    timestamp DATETIME,
                    expires_at DATETIME
                )
            ''')
            
            self.cache_db.commit()
            logger.info(f"缓存数据库初始化完成: {cache_db_path}")
            
        except Exception as e:
            logger.error(f"初始化缓存失败: {str(e)}")
            self.cache_enabled = False
    
    def get_realtime_quotes(self, stock_codes: List[str]) -> pd.DataFrame:
        """
        获取实时行情数据（主数据源：东方财富API）
        
        Args:
            stock_codes (List[str]): 股票代码列表
            
        Returns:
            pandas.DataFrame: 实时行情数据
        """
        if not stock_codes:
            logger.warning("股票代码列表为空")
            return pd.DataFrame()
        
        # 检查缓存
        cached_data = self._get_cached_quotes(stock_codes)
        if cached_data is not None and len(cached_data) == len(stock_codes):
            logger.info(f"从缓存获取 {len(stock_codes)} 只股票的行情数据")
            return cached_data
        
        logger.info(f"从东方财富API获取 {len(stock_codes)} 只股票的实时行情")
        
        try:
            # 东方财富API获取实时行情
            df_eastmoney = self._fetch_from_eastmoney(stock_codes)
            
            if df_eastmoney is not None and len(df_eastmoney) > 0:
                # 更新缓存
                if self.cache_enabled:
                    self._update_cache(stock_codes, df_eastmoney)
                
                return df_eastmoney
            
            # 如果东方财富API失败，尝试QVeris API
            logger.warning("东方财富API获取失败，尝试QVeris API")
            df_qveris = self._fetch_from_qveris(stock_codes)
            
            if df_qveris is not None and len(df_qveris) > 0:
                # 更新缓存
                if self.cache_enabled:
                    self._update_cache(stock_codes, df_qveris)
                
                return df_qveris
            
            # 两个API都失败，返回空DataFrame
            logger.error("所有数据源获取失败")
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"获取实时行情数据失败: {str(e)}")
            return pd.DataFrame()
    
    def _fetch_from_eastmoney(self, stock_codes: List[str]) -> Optional[pd.DataFrame]:
        """
        从东方财富API获取实时行情
        
        Args:
            stock_codes (List[str]): 股票代码列表
            
        Returns:
            pandas.DataFrame or None: 行情数据
        """
        try:
            # 东方财富API参数
            # 注意：这里使用简化的API调用，实际可能需要更复杂的参数
            
            # 构建请求URL
            # 东方财富实时行情API格式: http://push2.eastmoney.com/api/qt/ulist.np/get?fields=f1,f2,f3,...&secids=1.000001,0.300750
            
            # 将股票代码转换为东方财富格式：沪市1.开头，深市0.开头
            secids = []
            for code in stock_codes:
                if code.startswith('6') or code.startswith('9'):
                    secids.append(f"1.{code}")  # 沪市
                elif code.startswith('0') or code.startswith('3'):
                    secids.append(f"0.{code}")  # 深市
                else:
                    secids.append(f"1.{code}")  # 默认沪市
            
            secids_str = ','.join(secids)
            
            # 字段映射：我们需要的关键字段
            # f2: 最新价, f3: 涨跌幅, f4: 涨跌额, f5: 成交量, f6: 成交额, f7: 振幅, f8: 换手率
            # f9: 市盈率, f10: 量比, f12: 股票代码, f14: 股票名称, f20: 总市值, f21: 流通市值
            
            fields = "f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f20,f21"
            
            url = f"{self.eastmoney_api_base}qt/ulist.np/get"
            params = {
                'fields': fields,
                'secids': secids_str,
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'invt': '2',
                'fltt': '2'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'http://quote.eastmoney.com/'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('data') and data['data'].get('diff'):
                    stocks_data = data['data']['diff']
                    
                    # 解析数据
                    records = []
                    for stock in stocks_data:
                        record = {
                            '股票代码': str(stock.get('f12', '')).zfill(6),
                            '股票名称': stock.get('f14', ''),
                            '最新价': stock.get('f2', 0),
                            '涨跌幅': stock.get('f3', 0),  # 百分比
                            '涨跌额': stock.get('f4', 0),
                            '成交量': stock.get('f5', 0),
                            '成交额': stock.get('f6', 0),
                            '振幅': stock.get('f7', 0),
                            '换手率': stock.get('f8', 0),
                            '市盈率': stock.get('f9', 0),
                            '量比': stock.get('f10', 0),
                            '总市值': stock.get('f20', 0),
                            '流通市值': stock.get('f21', 0),
                            '数据来源': '东方财富',
                            '更新时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        records.append(record)
                    
                    df = pd.DataFrame(records)
                    logger.info(f"从东方财富API成功获取 {len(df)} 条行情数据")
                    return df
                else:
                    logger.warning("东方财富API返回数据格式异常")
                    return None
            else:
                logger.error(f"东方财富API请求失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"东方财富API调用异常: {str(e)}")
            return None
    
    def _fetch_from_qveris(self, stock_codes: List[str]) -> Optional[pd.DataFrame]:
        """
        从QVeris API获取实时行情（备用数据源）
        
        Args:
            stock_codes (List[str]): 股票代码列表
            
        Returns:
            pandas.DataFrame or None: 行情数据
        """
        if not self.qveris_api_key:
            logger.warning("QVeris API密钥未配置")
            return None
        
        try:
            # QVeris API调用
            url = f"{self.qveris_api_base}stocks/real-time"
            
            # 构建请求参数
            params = {
                'symbols': ','.join([f"{code}.SS" if code.startswith('6') else f"{code}.SZ" for code in stock_codes]),
                'fields': 'symbol,name,price,change,change_percent,volume,amount,market_cap,pe_ratio,turnover_rate'
            }
            
            headers = {
                'Authorization': f'Bearer {self.qveris_api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('data'):
                    records = []
                    for stock in data['data']:
                        symbol = stock.get('symbol', '')
                        # 提取股票代码（去掉后缀）
                        code = symbol.split('.')[0] if '.' in symbol else symbol
                        
                        record = {
                            '股票代码': code.zfill(6),
                            '股票名称': stock.get('name', ''),
                            '最新价': stock.get('price', 0),
                            '涨跌幅': stock.get('change_percent', 0),
                            '涨跌额': stock.get('change', 0),
                            '成交量': stock.get('volume', 0),
                            '成交额': stock.get('amount', 0),
                            '换手率': stock.get('turnover_rate', 0),
                            '市盈率': stock.get('pe_ratio', 0),
                            '总市值': stock.get('market_cap', 0),
                            '流通市值': stock.get('market_cap', 0),  # QVeris可能不区分
                            '数据来源': 'QVeris',
                            '更新时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        records.append(record)
                    
                    df = pd.DataFrame(records)
                    logger.info(f"从QVeris API成功获取 {len(df)} 条行情数据")
                    return df
                else:
                    logger.warning("QVeris API返回数据格式异常")
                    return None
            else:
                logger.error(f"QVeris API请求失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"QVeris API调用异常: {str(e)}")
            return None
    
    def _get_cached_quotes(self, stock_codes: List[str]) -> Optional[pd.DataFrame]:
        """
        从缓存获取行情数据
        
        Args:
            stock_codes (List[str]): 股票代码列表
            
        Returns:
            pandas.DataFrame or None: 缓存的行情数据
        """
        if not self.cache_enabled or not self.cache_db:
            return None
        
        try:
            cursor = self.cache_db.cursor()
            
            # 检查缓存是否有效（5分钟内）
            cutoff_time = datetime.now() - timedelta(minutes=5)
            cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 查询缓存
            placeholders = ','.join(['?'] * len(stock_codes))
            query = f'''
                SELECT stock_code, data_json 
                FROM stock_quotes 
                WHERE stock_code IN ({placeholders}) 
                AND timestamp > ?
            '''
            
            cursor.execute(query, stock_codes + [cutoff_str])
            cached_rows = cursor.fetchall()
            
            if len(cached_rows) != len(stock_codes):
                logger.debug(f"缓存命中不足: {len(cached_rows)}/{len(stock_codes)}")
                return None
            
            # 解析缓存数据
            records = []
            for row in cached_rows:
                stock_code, data_json = row
                try:
                    data = json.loads(data_json)
                    records.append(data)
                except:
                    continue
            
            if len(records) == len(stock_codes):
                df = pd.DataFrame(records)
                logger.debug(f"从缓存获取 {len(df)} 条行情数据")
                return df
            else:
                return None
                
        except Exception as e:
            logger.error(f"读取缓存失败: {str(e)}")
            return None
    
    def _update_cache(self, stock_codes: List[str], df: pd.DataFrame):
        """
        更新缓存
        
        Args:
            stock_codes (List[str]): 股票代码列表
            df (pandas.DataFrame): 行情数据
        """
        if not self.cache_enabled or not self.cache_db:
            return
        
        try:
            cursor = self.cache_db.cursor()
            current_time = datetime.now()
            expire_time = current_time + timedelta(minutes=5)  # 5分钟后过期
            
            for _, row in df.iterrows():
                stock_code = row['股票代码']
                data_dict = row.to_dict()
                
                # 转换为JSON字符串
                data_json = json.dumps(data_dict, ensure_ascii=False, default=str)
                
                # 插入或更新缓存
                cursor.execute('''
                    INSERT OR REPLACE INTO stock_quotes 
                    (stock_code, data_json, timestamp, expires_at)
                    VALUES (?, ?, ?, ?)
                ''', (stock_code, data_json, current_time, expire_time))
            
            self.cache_db.commit()
            logger.debug(f"更新 {len(df)} 条行情数据缓存")
            
        except Exception as e:
            logger.error(f"更新缓存失败: {str(e)}")
    
    def get_stock_industry_mapping(self) -> Dict[str, str]:
        """
        获取股票代码到行业的映射关系
        
        Returns:
            Dict[str, str]: 股票代码->行业名称的映射
        """
        # 这里可以集成行业分类数据
        # 实际实现中应该从数据库或文件加载
        
        # 示例映射（实际应该从申万行业分类文件加载）
        industry_mapping = {
            '000001': '银行',
            '600036': '银行',
            '000858': '食品饮料',
            '002415': '电子',
            '600519': '食品饮料',
            '000333': '家用电器',
            '300750': '电气设备',
            '600887': '食品饮料',
            '601318': '非银金融',
            '000725': '电子'
        }
        
        return industry_mapping
    
    def calculate_portfolio_values(self, portfolio_df: pd.DataFrame) -> pd.DataFrame:
        """
        计算持仓组合的实时价值
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据，包含股票代码、持仓数量、成本价
            
        Returns:
            pandas.DataFrame: 包含实时价值的持仓数据
        """
        if portfolio_df is None or len(portfolio_df) == 0:
            return pd.DataFrame()
        
        # 提取股票代码
        stock_codes = portfolio_df['股票代码'].tolist()
        
        # 获取实时行情
        quotes_df = self.get_realtime_quotes(stock_codes)
        
        if quotes_df is None or len(quotes_df) == 0:
            logger.warning("无法获取实时行情，使用成本价计算")
            portfolio_df['最新价'] = portfolio_df['成本价']
            portfolio_df['涨跌幅'] = 0
            portfolio_df['持仓市值'] = portfolio_df['持仓数量'] * portfolio_df['成本价']
            portfolio_df['浮动盈亏'] = 0
            portfolio_df['盈亏比例'] = 0
            portfolio_df['数据来源'] = '本地缓存'
            return portfolio_df
        
        # 合并持仓数据和行情数据
        merged_df = portfolio_df.merge(
            quotes_df[['股票代码', '最新价', '涨跌幅', '总市值', '数据来源']],
            on='股票代码',
            how='left'
        )
        
        # 计算实时价值
        merged_df['持仓市值'] = merged_df['持仓数量'] * merged_df['最新价']
        merged_df['成本市值'] = merged_df['持仓数量'] * merged_df['成本价']
        merged_df['浮动盈亏'] = merged_df['持仓市值'] - merged_df['成本市值']
        merged_df['盈亏比例'] = (merged_df['浮动盈亏'] / merged_df['成本市值'] * 100).round(2)
        
        # 处理缺失值
        merged_df['最新价'] = merged_df['最新价'].fillna(merged_df['成本价'])
        merged_df['涨跌幅'] = merged_df['涨跌幅'].fillna(0)
        merged_df['持仓市值'] = merged_df['持仓市值'].fillna(merged_df['成本市值'])
        merged_df['浮动盈亏'] = merged_df['浮动盈亏'].fillna(0)
        merged_df['盈亏比例'] = merged_df['盈亏比例'].fillna(0)
        
        logger.info(f"成功计算 {len(merged_df)} 只股票的实时价值")
        return merged_df
    
    def close(self):
        """关闭连接"""
        if self.cache_db:
            self.cache_db.close()
            logger.info("缓存数据库连接已关闭")


# 示例使用
if __name__ == "__main__":
    # 示例：获取实时行情
    fetcher = MarketDataFetcher(cache_enabled=True)
    
    # 示例股票代码
    test_stocks = ['000001', '600036', '000858', '002415']
    
    try:
        # 获取实时行情
        quotes_df = fetcher.get_realtime_quotes(test_stocks)
        
        if not quotes_df.empty:
            print("实时行情数据:")
            print(quotes_df[['股票代码', '股票名称', '最新价', '涨跌幅', '总市值', '数据来源']])
            
            # 示例持仓数据
            portfolio_data = [
                {'股票代码': '000001', '股票名称': '平安银行', '持仓数量': 1000, '成本价': 15.20},
                {'股票代码': '600036', '股票名称': '招商银行', '持仓数量': 800, '成本价': 32.50},
                {'股票代码': '000858', '股票名称': '五粮液', '持仓数量': 500, '成本价': 180.30},
            ]
            
            portfolio_df = pd.DataFrame(portfolio_data)
            
            # 计算持仓实时价值
            valued_portfolio = fetcher.calculate_portfolio_values(portfolio_df)
            
            if not valued_portfolio.empty:
                print("\n持仓实时价值:")
                print(valued_portfolio[['股票代码', '股票名称', '持仓数量', '成本价', '最新价', '持仓市值', '浮动盈亏', '盈亏比例']])
        else:
            print("未能获取实时行情数据")
            
    finally:
        fetcher.close()