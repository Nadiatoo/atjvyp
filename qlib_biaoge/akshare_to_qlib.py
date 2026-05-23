#!/usr/bin/env python3
"""
Qlib + Akshare 数据对接脚本
将akshare获取的A股数据转换为Qlib格式

使用方法:
    python akshare_to_qlib.py --start 2020-01-01 --end 2026-03-01 --output ~/.qlib/qlib_data/cn_data
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import pandas as pd
import numpy as np

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AkshareToQlibConverter:
    """Akshare数据转Qlib格式转换器"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Qlib格式要求的目录结构
        self.qlib_dir = self.output_dir / "qlib_data" / "cn_data"
        self.qlib_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        (self.qlib_dir / "calendars").mkdir(exist_ok=True)
        (self.qlib_dir / "instruments").mkdir(exist_ok=True)
        (self.qlib_dir / "features").mkdir(exist_ok=True)
        
    def download_stock_list(self) -> pd.DataFrame:
        """获取A股股票列表"""
        try:
            import akshare as ak
            logger.info("正在获取A股股票列表...")
            
            # 获取所有A股代码
            stock_list = ak.stock_info_a_code_name()
            logger.info(f"获取到 {len(stock_list)} 只股票")
            
            return stock_list
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            raise
    
    def download_stock_data(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """下载单只股票历史数据"""
        try:
            import akshare as ak
            
            # 转换代码格式 (如: 000001.SZ -> sz000001)
            if '.' in symbol:
                code, exchange = symbol.split('.')
                if exchange == 'SZ':
                    ak_symbol = f"sz{code}"
                else:
                    ak_symbol = f"sh{code}"
            else:
                ak_symbol = symbol
            
            # 获取历史数据
            df = ak.stock_zh_a_hist(
                symbol=ak_symbol.replace('sz', '').replace('sh', ''),
                period="daily",
                start_date=start_date.replace('-', ''),
                end_date=end_date.replace('-', ''),
                adjust="qfq"  # 前复权
            )
            
            if df.empty:
                return None
                
            # 重命名列以匹配Qlib格式
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'change_pct',
                '涨跌额': 'change',
                '换手率': 'turnover'
            })
            
            # 转换日期格式
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            
            # 添加factor列 (复权因子)
            df['factor'] = 1.0
            
            # 添加vwap列 (成交均价)
            df['vwap'] = df['amount'] / df['volume'] if 'amount' in df.columns else df['close']
            
            return df
            
        except Exception as e:
            logger.warning(f"下载 {symbol} 数据失败: {e}")
            return None
    
    def convert_to_qlib_format(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """转换为Qlib格式"""
        # Qlib需要的列: open, close, high, low, volume, amount, factor, vwap
        qlib_df = pd.DataFrame({
            'open': df['open'].astype('float32'),
            'high': df['high'].astype('float32'),
            'low': df['low'].astype('float32'),
            'close': df['close'].astype('float32'),
            'volume': df['volume'].astype('float32'),
            'factor': df.get('factor', 1.0).astype('float32'),
            'vwap': df.get('vwap', df['close']).astype('float32'),
        })
        
        return qlib_df
    
    def save_to_bin(self, df: pd.DataFrame, symbol: str):
        """保存为Qlib二进制格式"""
        # 转换代码格式 (如: 000001.SZ -> SH000001)
        if '.' in symbol:
            code, exchange = symbol.split('.')
            qlib_symbol = f"{exchange}{code}"
        else:
            qlib_symbol = symbol.upper()
        
        # 创建股票目录
        stock_dir = self.qlib_dir / "features" / qlib_symbol
        stock_dir.mkdir(exist_ok=True)
        
        # 保存每个字段为.bin文件
        for col in df.columns:
            file_path = stock_dir / f"{col}.bin"
            
            # 使用numpy保存为二进制
            arr = df[col].values
            arr.astype('float32').tofile(file_path)
        
        logger.debug(f"已保存 {qlib_symbol}")
    
    def generate_calendar(self, start_date: str, end_date: str):
        """生成交易日历"""
        try:
            import akshare as ak
            
            logger.info("生成交易日历...")
            
            # 获取交易日历
            calendar_df = ak.tool_trade_date_hist_sina()
            calendar_df['trade_date'] = pd.to_datetime(calendar_df['trade_date'])
            
            # 过滤日期范围
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            calendar_df = calendar_df[
                (calendar_df['trade_date'] >= start) & 
                (calendar_df['trade_date'] <= end)
            ]
            
            # 保存交易日历
            calendar_file = self.qlib_dir / "calendars" / "day.txt"
            with open(calendar_file, 'w') as f:
                for date in calendar_df['trade_date']:
                    f.write(date.strftime('%Y-%m-%d') + '\n')
            
            logger.info(f"交易日历已保存: {len(calendar_df)} 个交易日")
            
        except Exception as e:
            logger.error(f"生成交易日历失败: {e}")
            # 创建简单的交易日历作为备选
            self._generate_simple_calendar(start_date, end_date)
    
    def _generate_simple_calendar(self, start_date: str, end_date: str):
        """生成简单的交易日历(备选)"""
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        # 生成所有工作日 (周一到周五)
        dates = pd.date_range(start=start, end=end, freq='B')
        
        calendar_file = self.qlib_dir / "calendars" / "day.txt"
        with open(calendar_file, 'w') as f:
            for date in dates:
                f.write(date.strftime('%Y-%m-%d') + '\n')
        
        logger.info(f"简单交易日历已保存: {len(dates)} 天")
    
    def generate_instruments(self, stock_list: pd.DataFrame):
        """生成股票列表文件"""
        logger.info("生成股票列表...")
        
        instruments_file = self.qlib_dir / "instruments" / "all.txt"
        
        with open(instruments_file, 'w') as f:
            for _, row in stock_list.iterrows():
                code = row['code']
                # 判断交易所
                if code.startswith('6'):
                    exchange = 'SH'
                else:
                    exchange = 'SZ'
                
                qlib_symbol = f"{exchange}{code}"
                # 格式: SYMBOL\tSTART_DATE\tEND_DATE
                f.write(f"{qlib_symbol}\t2020-01-01\t2026-12-31\n")
        
        logger.info(f"股票列表已保存: {len(stock_list)} 只")
    
    def run(self, start_date: str, end_date: str, max_stocks: Optional[int] = None):
        """执行完整转换流程"""
        logger.info(f"开始转换数据: {start_date} ~ {end_date}")
        
        # 1. 获取股票列表
        stock_list = self.download_stock_list()
        if max_stocks:
            stock_list = stock_list.head(max_stocks)
        
        # 2. 生成交易日历
        self.generate_calendar(start_date, end_date)
        
        # 3. 生成股票列表
        self.generate_instruments(stock_list)
        
        # 4. 下载并转换每只股票数据
        success_count = 0
        failed_count = 0
        
        for idx, row in stock_list.iterrows():
            code = row['code']
            name = row.get('name', '')
            
            # 判断交易所
            if code.startswith('6'):
                symbol = f"{code}.SH"
            else:
                symbol = f"{code}.SZ"
            
            logger.info(f"[{idx+1}/{len(stock_list)}] 处理 {symbol} {name}")
            
            # 下载数据
            df = self.download_stock_data(symbol, start_date, end_date)
            if df is None or df.empty:
                failed_count += 1
                continue
            
            # 转换格式
            qlib_df = self.convert_to_qlib_format(df, symbol)
            
            # 保存
            self.save_to_bin(qlib_df, symbol)
            success_count += 1
            
            # 每10只打印进度
            if (idx + 1) % 10 == 0:
                logger.info(f"进度: {idx+1}/{len(stock_list)}, 成功: {success_count}, 失败: {failed_count}")
        
        logger.info(f"转换完成! 成功: {success_count}, 失败: {failed_count}")
        logger.info(f"数据保存在: {self.qlib_dir}")


def main():
    parser = argparse.ArgumentParser(description='Akshare to Qlib Data Converter')
    parser.add_argument('--start', default='2020-01-01', help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end', default='2026-03-01', help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--output', default='~/.qlib/qlib_data/cn_data', help='输出目录')
    parser.add_argument('--max-stocks', type=int, default=None, help='最多处理股票数(用于测试)')
    
    args = parser.parse_args()
    
    # 展开用户目录
    output_dir = os.path.expanduser(args.output)
    
    # 创建转换器并运行
    converter = AkshareToQlibConverter(output_dir)
    converter.run(args.start, args.end, args.max_stocks)


if __name__ == '__main__':
    main()
