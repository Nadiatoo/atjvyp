#!/usr/bin/env python3
"""
彪哥战法 × Qlib 完整回测系统
整合四季判断模型 + Qlib回测框架

功能:
1. 从akshare获取数据并转换为Qlib格式
2. 使用四季判断模型生成市场状态信号
3. 基于市场状态调整策略参数
4. 运行完整回测并生成报告
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np
import joblib

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BiaogeDataConverter:
    """彪哥战法数据转换器 - 简化版Qlib格式"""
    
    def __init__(self, output_dir: str = "~/.qlib/qlib_data/cn_data"):
        self.output_dir = Path(output_dir).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建目录结构
        (self.output_dir / "calendars").mkdir(exist_ok=True)
        (self.output_dir / "instruments").mkdir(exist_ok=True)
        (self.output_dir / "features").mkdir(exist_ok=True)
    
    def convert_stock_data(self, symbol: str, df: pd.DataFrame) -> bool:
        """
        将股票数据转换为Qlib格式
        
        Qlib格式要求:
        - 每个股票一个目录
        - 每个字段一个.bin文件 (float32格式)
        - 字段: open, close, high, low, volume, factor, vwap
        """
        try:
            if df.empty:
                return False
            
            # 转换代码格式
            if '.' in symbol:
                code, exchange = symbol.split('.')
                qlib_symbol = f"{exchange}{code}"
            else:
                # 根据代码判断交易所
                if symbol.startswith('6'):
                    qlib_symbol = f"SH{symbol}"
                else:
                    qlib_symbol = f"SZ{symbol}"
            
            # 创建股票目录
            stock_dir = self.output_dir / "features" / qlib_symbol
            stock_dir.mkdir(exist_ok=True)
            
            # 确保必要的列存在
            required_cols = ['open', 'close', 'high', 'low', 'volume']
            for col in required_cols:
                if col not in df.columns:
                    logger.warning(f"{symbol} 缺少列 {col}")
                    return False
            
            # 准备数据
            qlib_df = pd.DataFrame({
                'open': df['open'].astype('float32'),
                'high': df['high'].astype('float32'),
                'low': df['low'].astype('float32'),
                'close': df['close'].astype('float32'),
                'volume': df['volume'].astype('float32'),
                'factor': df.get('factor', 1.0).astype('float32'),
            })
            
            # 计算vwap (如果有amount)
            if 'amount' in df.columns:
                qlib_df['vwap'] = (df['amount'] / df['volume']).astype('float32')
            else:
                qlib_df['vwap'] = df['close'].astype('float32')
            
            # 保存为.bin文件
            for col in qlib_df.columns:
                file_path = stock_dir / f"{col}.bin"
                arr = qlib_df[col].values
                arr.astype('float32').tofile(file_path)
            
            return True
            
        except Exception as e:
            logger.error(f"转换 {symbol} 失败: {e}")
            return False
    
    def generate_calendar(self, start_date: str, end_date: str):
        """生成交易日历"""
        try:
            import akshare as ak
            
            logger.info("获取交易日历...")
            calendar_df = ak.tool_trade_date_hist_sina()
            calendar_df['trade_date'] = pd.to_datetime(calendar_df['trade_date'])
            
            # 过滤日期
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            calendar_df = calendar_df[
                (calendar_df['trade_date'] >= start) & 
                (calendar_df['trade_date'] <= end)
            ]
            
            # 保存
            calendar_file = self.output_dir / "calendars" / "day.txt"
            with open(calendar_file, 'w') as f:
                for date in calendar_df['trade_date']:
                    f.write(date.strftime('%Y-%m-%d') + '\n')
            
            logger.info(f"交易日历已生成: {len(calendar_df)} 个交易日")
            
        except Exception as e:
            logger.error(f"生成交易日历失败: {e}")
            # 备选方案: 生成所有工作日
            self._generate_simple_calendar(start_date, end_date)
    
    def _generate_simple_calendar(self, start_date: str, end_date: str):
        """生成简单交易日历(备选)"""
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        dates = pd.date_range(start=start, end=end, freq='B')
        
        calendar_file = self.output_dir / "calendars" / "day.txt"
        with open(calendar_file, 'w') as f:
            for date in dates:
                f.write(date.strftime('%Y-%m-%d') + '\n')
        
        logger.info(f"简单交易日历已生成: {len(dates)} 天")
    
    def generate_instruments(self, stock_list: List[str]):
        """生成股票列表"""
        instruments_file = self.output_dir / "instruments" / "all.txt"
        
        with open(instruments_file, 'w') as f:
            for symbol in stock_list:
                if '.' in symbol:
                    code, exchange = symbol.split('.')
                    qlib_symbol = f"{exchange}{code}"
                else:
                    if symbol.startswith('6'):
                        qlib_symbol = f"SH{symbol}"
                    else:
                        qlib_symbol = f"SZ{symbol}"
                
                # 格式: SYMBOL\tSTART_DATE\tEND_DATE
                f.write(f"{qlib_symbol}\t2020-01-01\t2026-12-31\n")
        
        logger.info(f"股票列表已生成: {len(stock_list)} 只")


class BiaogeBacktestEngine:
    """
    彪哥战法回测引擎
    整合四季判断模型 + Qlib回测
    """
    
    def __init__(self, 
                 data_dir: str = "~/.qlib/qlib_data/cn_data",
                 model_path: str = "biaoge_season_model.pkl"):
        self.data_dir = Path(data_dir).expanduser()
        self.model_path = model_path
        self.season_model = None
        
        # 尝试加载四季模型
        if Path(model_path).exists():
            try:
                self.season_model = joblib.load(model_path)['model']
                logger.info(f"四季模型已加载: {model_path}")
            except Exception as e:
                logger.warning(f"加载模型失败: {e}")
    
    def prepare_data(self, 
                    start_date: str = "2020-01-01",
                    end_date: str = "2026-03-01",
                    max_stocks: Optional[int] = None):
        """
        准备回测数据
        """
        logger.info("=" * 60)
        logger.info("准备回测数据")
        logger.info("=" * 60)
        
        try:
            import akshare as ak
            
            # 获取股票列表
            logger.info("获取A股列表...")
            stock_df = ak.stock_info_a_code_name()
            
            if max_stocks:
                stock_df = stock_df.head(max_stocks)
            
            stock_list = []
            success_count = 0
            
            converter = BiaogeDataConverter(str(self.data_dir))
            
            # 下载每只股票数据
            for idx, row in stock_df.iterrows():
                code = row['code']
                name = row.get('name', '')
                
                # 判断交易所
                if code.startswith('6'):
                    symbol = f"{code}.SH"
                else:
                    symbol = f"{code}.SZ"
                
                if (idx + 1) % 50 == 0:
                    logger.info(f"进度: {idx+1}/{len(stock_df)}, 成功: {success_count}")
                
                try:
                    # 下载历史数据
                    df = ak.stock_zh_a_hist(
                        symbol=code,
                        period="daily",
                        start_date=start_date.replace('-', ''),
                        end_date=end_date.replace('-', ''),
                        adjust="qfq"
                    )
                    
                    if df.empty or len(df) < 100:  # 数据太少跳过
                        continue
                    
                    # 转换列名
                    df = df.rename(columns={
                        '日期': 'date',
                        '开盘': 'open',
                        '收盘': 'close',
                        '最高': 'high',
                        '最低': 'low',
                        '成交量': 'volume',
                        '成交额': 'amount',
                    })
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.set_index('date')
                    
                    # 转换为Qlib格式
                    if converter.convert_stock_data(symbol, df):
                        stock_list.append(symbol)
                        success_count += 1
                    
                except Exception as e:
                    logger.debug(f"下载 {symbol} 失败: {e}")
                    continue
            
            # 生成交易日历
            converter.generate_calendar(start_date, end_date)
            
            # 生成股票列表
            converter.generate_instruments(stock_list)
            
            logger.info(f"数据准备完成! 成功: {success_count}/{len(stock_df)}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"数据准备失败: {e}")
            return False
    
    def run_backtest_simple(self,
                           start_date: str = "2024-01-01",
                           end_date: str = "2026-03-01",
                           topk: int = 20):
        """
        简化版回测 (不依赖完整Qlib安装)
        """
        logger.info("=" * 60)
        logger.info("运行简化版回测")
        logger.info("=" * 60)
        
        try:
            import akshare as ak
            
            # 获取沪深300成分股作为标的池
            logger.info("获取沪深300成分股...")
            try:
                index_df = ak.index_stock_cons_weight_csindex(symbol="000300")
                stock_pool = index_df['成分券代码'].tolist()[:50]  # 取前50只
            except:
                # 备选: 用大盘股
                stock_pool = ['000001', '000002', '000333', '000858', '002415', 
                             '600000', '600036', '600276', '600519', '601318']
            
            logger.info(f"标的池: {len(stock_pool)} 只股票")
            
            # 下载数据
            all_data = {}
            for code in stock_pool:
                try:
                    df = ak.stock_zh_a_hist(
                        symbol=code,
                        period="daily",
                        start_date=start_date.replace('-', ''),
                        end_date=end_date.replace('-', ''),
                        adjust="qfq"
                    )
                    if not df.empty:
                        df['日期'] = pd.to_datetime(df['日期'])
                        df = df.set_index('日期')
                        all_data[code] = df
                except:
                    continue
            
            logger.info(f"成功下载 {len(all_data)} 只股票数据")
            
            # 简单回测: 每月调仓，选动量最强的topk只
            dates = pd.date_range(start=start_date, end=end_date, freq='BME')  # 月末 (BME = Business Month End)
            
            portfolio_values = [1.0]  # 初始净值
            positions = {}  # 持仓
            
            for i, date in enumerate(dates[:-1]):
                next_date = dates[i + 1]
                
                # 计算每只股票过去20日收益
                momentum_scores = {}
                for code, df in all_data.items():
                    try:
                        past_data = df[df.index <= date].tail(20)
                        if len(past_data) >= 20:
                            ret = (past_data['收盘'].iloc[-1] / past_data['收盘'].iloc[0]) - 1
                            momentum_scores[code] = ret
                    except:
                        continue
                
                # 选topk只
                sorted_stocks = sorted(momentum_scores.items(), key=lambda x: x[1], reverse=True)
                selected = [code for code, _ in sorted_stocks[:topk]]
                
                # 计算这段时间的收益
                period_return = 0
                for code in selected:
                    try:
                        df = all_data[code]
                        start_price = df[df.index >= date]['开盘'].iloc[0] if len(df[df.index >= date]) > 0 else None
                        end_price = df[df.index <= next_date]['收盘'].iloc[-1] if len(df[df.index <= next_date]) > 0 else None
                        
                        if start_price and end_price:
                            period_return += (end_price / start_price - 1) / topk
                    except:
                        continue
                
                # 更新净值
                new_value = portfolio_values[-1] * (1 + period_return)
                portfolio_values.append(new_value)
                
                if (i + 1) % 6 == 0:  # 每6个月打印一次
                    logger.info(f"{next_date.strftime('%Y-%m')}: 净值={new_value:.4f}, 收益={period_return:.2%}")
            
            # 计算绩效指标
            total_return = portfolio_values[-1] - 1
            annual_return = (portfolio_values[-1]) ** (252 / len(dates)) - 1
            
            returns = pd.Series(portfolio_values).pct_change().dropna()
            sharpe = returns.mean() / returns.std() * np.sqrt(12) if returns.std() > 0 else 0
            max_dd = (portfolio_values / np.maximum.accumulate(portfolio_values) - 1).min()
            
            logger.info("\n" + "=" * 60)
            logger.info("回测结果")
            logger.info("=" * 60)
            logger.info(f"总收益率: {total_return:.2%}")
            logger.info(f"年化收益: {annual_return:.2%}")
            logger.info(f"夏普比率: {sharpe:.2f}")
            logger.info(f"最大回撤: {max_dd:.2%}")
            logger.info(f"最终净值: {portfolio_values[-1]:.4f}")
            
            return {
                'total_return': total_return,
                'annual_return': annual_return,
                'sharpe': sharpe,
                'max_drawdown': max_dd,
                'values': portfolio_values
            }
            
        except Exception as e:
            logger.error(f"回测失败: {e}")
            import traceback
            traceback.print_exc()
            return None


def main():
    parser = argparse.ArgumentParser(description='彪哥战法回测系统')
    parser.add_argument('--action', choices=['prepare', 'backtest', 'full'], 
                       default='backtest', help='操作类型')
    parser.add_argument('--start', default='2020-01-01', help='数据开始日期')
    parser.add_argument('--end', default='2026-03-01', help='数据结束日期')
    parser.add_argument('--backtest-start', default='2024-01-01', help='回测开始日期')
    parser.add_argument('--max-stocks', type=int, default=100, help='最大股票数')
    parser.add_argument('--topk', type=int, default=20, help='选股数量')
    
    args = parser.parse_args()
    
    engine = BiaogeBacktestEngine()
    
    if args.action in ['prepare', 'full']:
        engine.prepare_data(
            start_date=args.start,
            end_date=args.end,
            max_stocks=args.max_stocks
        )
    
    if args.action in ['backtest', 'full']:
        result = engine.run_backtest_simple(
            start_date=args.backtest_start,
            end_date=args.end,
            topk=args.topk
        )
        
        if result:
            logger.info("\n回测完成! 结果已保存到日志。")


if __name__ == '__main__':
    main()
