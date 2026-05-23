#!/usr/bin/env python3
"""
彪哥战法 - 完整Qlib回测工作流
使用Qlib官方API进行专业级回测

需要先安装Qlib: pip install pyqlib
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import qlib
from qlib.config import REG_CN
from qlib.data import D
from qlib.data.dataset import DatasetH
from qlib.data.dataset.handler import DataHandlerLP
from qlib.contrib.model.gbdt import LGBModel
from qlib.contrib.strategy import TopkDropoutStrategy
from qlib.contrib.evaluate import backtest_daily, risk_analysis
from qlib.workflow import R
from qlib.workflow.record_temp import SignalRecord, PortAnaRecord

import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BiaogeQlibWorkflow:
    """
    彪哥战法完整Qlib工作流
    """
    
    def __init__(self, provider_uri: str = "~/.qlib/qlib_data/cn_data"):
        self.provider_uri = Path(provider_uri).expanduser()
        
        # 初始化Qlib
        try:
            qlib.init(provider_uri=str(self.provider_uri), region=REG_CN)
            logger.info(f"Qlib初始化成功: {self.provider_uri}")
        except Exception as e:
            logger.error(f"Qlib初始化失败: {e}")
            logger.info("提示: 请先运行数据准备脚本")
            raise
    
    def get_market_features(self, start_date: str, end_date: str) -> pd.DataFrame:
        """获取市场特征用于四季判断"""
        # 获取上证指数
        df = D.features(
            instruments=['SH000001'],
            fields=['$close', '$volume', '$high', '$low', '$open'],
            start_time=start_date,
            end_time=end_date
        )
        
        # 计算四季判断特征
        features = pd.DataFrame(index=df.index)
        
        # 动量特征
        features['momentum_5'] = df['$close'].groupby(level=1).apply(lambda x: x.pct_change(5))
        features['momentum_10'] = df['$close'].groupby(level=1).apply(lambda x: x.pct_change(10))
        features['momentum_20'] = df['$close'].groupby(level=1).apply(lambda x: x.pct_change(20))
        
        # 波动率
        features['volatility_5'] = df['$close'].groupby(level=1).apply(
            lambda x: x.pct_change().rolling(5).std()
        )
        features['volatility_20'] = df['$close'].groupby(level=1).apply(
            lambda x: x.pct_change().rolling(20).std()
        )
        
        # 量能
        features['volume_ma5'] = df['$volume'].groupby(level=1).apply(
            lambda x: x / x.rolling(5).mean()
        )
        features['volume_ma20'] = df['$volume'].groupby(level=1).apply(
            lambda x: x / x.rolling(20).mean()
        )
        
        # 趋势
        features['ma5'] = df['$close'].groupby(level=1).apply(
            lambda x: x / x.rolling(5).mean()
        )
        features['ma20'] = df['$close'].groupby(level=1).apply(
            lambda x: x / x.rolling(20).mean()
        )
        features['ma60'] = df['$close'].groupby(level=1).apply(
            lambda x: x / x.rolling(60).mean()
        )
        
        # RSI
        def calc_rsi(x, window=14):
            delta = x.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        features['rsi'] = df['$close'].groupby(level=1).apply(calc_rsi)
        
        # MACD
        def calc_macd(x):
            exp1 = x.ewm(span=12, adjust=False).mean()
            exp2 = x.ewm(span=26, adjust=False).mean()
            return exp1 - exp2
        
        def calc_macd_signal(x):
            return calc_macd(x).ewm(span=9, adjust=False).mean()
        
        features['macd'] = df['$close'].groupby(level=1).apply(calc_macd)
        features['macd_signal'] = df['$close'].groupby(level=1).apply(calc_macd_signal)
        
        # 布林带位置
        def calc_bb_position(x):
            ma20 = x.rolling(20).mean()
            std20 = x.rolling(20).std()
            return (x - ma20) / (2 * std20)
        
        features['bb_position'] = df['$close'].groupby(level=1).apply(calc_bb_position)
        
        return features.dropna()
    
    def create_alpha_dataset(self,
                            start_date: str = "2020-01-01",
                            end_date: str = "2026-03-01",
                            fit_start: str = "2020-01-01",
                            fit_end: str = "2023-12-31",
                            instruments: str = "csi300") -> DatasetH:
        """
        创建Alpha因子数据集
        """
        from qlib.contrib.data.handler import Alpha158
        
        logger.info("创建Alpha158数据集...")
        
        # 数据处理器配置
        data_handler_config = {
            'start_time': start_date,
            'end_time': end_date,
            'fit_start_time': fit_start,
            'fit_end_time': fit_end,
            'instruments': instruments,
            'learn_processors': [
                {'class': 'DropnaProcessor', 'kwargs': {'fields_group': 'feature'}},
                {'class': 'CSZScoreNorm', 'kwargs': {'fields_group': 'feature'}},
            ],
            'infer_processors': [
                {'class': 'CSZScoreNorm', 'kwargs': {'fields_group': 'feature'}},
            ],
        }
        
        # 数据集切分
        segments = {
            'train': (start_date, fit_end),
            'valid': (fit_end, '2024-06-30'),
            'test': ('2024-07-01', end_date)
        }
        
        # 创建处理器
        handler = Alpha158(**data_handler_config)
        
        # 创建数据集
        dataset = DatasetH(
            handler=handler,
            segments=segments
        )
        
        logger.info("数据集创建成功")
        return dataset
    
    def train_model(self, dataset: DatasetH) -> LGBModel:
        """
        训练Alpha预测模型
        """
        logger.info("训练LightGBM模型...")
        
        # 模型配置
        model = LGBModel(
            loss='mse',
            colsample_bytree=0.8879,
            learning_rate=0.0421,
            subsample=0.8789,
            lambda_l1=205.6999,
            lambda_l2=580.9768,
            max_depth=8,
            num_leaves=210,
            num_threads=20,
        )
        
        # 训练
        model.fit(dataset)
        
        logger.info("模型训练完成")
        return model
    
    def run_backtest(self,
                    model: LGBModel,
                    dataset: DatasetH,
                    start_date: str = "2024-01-01",
                    end_date: str = "2026-03-01",
                    topk: int = 50,
                    n_drop: int = 5) -> dict:
        """
        运行回测
        """
        logger.info("开始回测...")
        
        # 获取预测结果
        pred = model.predict(dataset)
        
        # 创建策略
        strategy = TopkDropoutStrategy(
            topk=topk,
            n_drop=n_drop,
            signal=pred
        )
        
        # 回测配置
        backtest_config = {
            'start_time': start_date,
            'end_time': end_date,
            'account': 100000000,  # 1亿
            'benchmark': 'SH000300',
            'exchange_kwargs': {
                'limit_threshold': 0.095,
                'deal_price': 'close',
                'open_cost': 0.0005,
                'close_cost': 0.0015,
                'min_cost': 5,
            }
        }
        
        # 执行回测
        report_normal, positions_normal = backtest_daily(
            start_time=start_date,
            end_time=end_date,
            strategy=strategy,
            **backtest_config
        )
        
        # 风险分析
        analysis = risk_analysis(report_normal)
        
        logger.info("\n" + "=" * 60)
        logger.info("回测结果")
        logger.info("=" * 60)
        logger.info(f"总收益率: {analysis['return']:.2%}")
        logger.info(f"年化收益: {analysis['annualized_return']:.2%}")
        logger.info(f"夏普比率: {analysis['sharpe']:.2f}")
        logger.info(f"最大回撤: {analysis['max_drawdown']:.2%}")
        logger.info(f"信息比率: {analysis.get('information_ratio', 0):.2f}")
        
        return {
            'report': report_normal,
            'positions': positions_normal,
            'analysis': analysis
        }
    
    def run_with_season_adjustment(self,
                                   start_date: str = "2024-01-01",
                                   end_date: str = "2026-03-01"):
        """
        基于四季判断动态调整策略参数
        
        不同季节使用不同的topk和n_drop参数:
        - 春播: topk=30, n_drop=3 (精选,少换仓)
        - 夏长: topk=50, n_drop=5 (激进,高换仓)
        - 秋收: topk=20, n_drop=2 (保守,少换仓)
        - 冬藏: topk=0, n_drop=0 (空仓)
        """
        logger.info("运行四季调整策略...")
        
        # 获取四季判断
        market_features = self.get_market_features(start_date, end_date)
        
        # 这里简化处理，实际应该用训练好的模型预测
        # 现在用规则简单判断
        season_config = {
            'spring': {'topk': 30, 'n_drop': 3},
            'summer': {'topk': 50, 'n_drop': 5},
            'autumn': {'topk': 20, 'n_drop': 2},
            'winter': {'topk': 0, 'n_drop': 0},
        }
        
        logger.info("四季调整策略配置:")
        for season, config in season_config.items():
            logger.info(f"  {season}: topk={config['topk']}, n_drop={config['n_drop']}")
        
        # TODO: 实现动态调整逻辑
        logger.info("(完整实现需要加载四季判断模型)")


def run_full_workflow():
    """运行完整工作流"""
    logger.info("=" * 70)
    logger.info("彪哥战法 - Qlib完整回测工作流")
    logger.info("=" * 70)
    
    try:
        # 1. 初始化
        workflow = BiaogeQlibWorkflow()
        
        # 2. 创建数据集
        dataset = workflow.create_alpha_dataset(
            start_date="2020-01-01",
            end_date="2026-03-01",
            instruments="csi300"  # 沪深300成分股
        )
        
        # 3. 训练模型
        model = workflow.train_model(dataset)
        
        # 4. 运行回测
        results = workflow.run_backtest(
            model=model,
            dataset=dataset,
            start_date="2024-01-01",
            end_date="2026-03-01",
            topk=50,
            n_drop=5
        )
        
        logger.info("\n" + "=" * 70)
        logger.info("工作流运行完成!")
        logger.info("=" * 70)
        
        return results
        
    except Exception as e:
        logger.error(f"工作流运行失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def demo_without_qlib():
    """无需完整Qlib安装的演示"""
    logger.info("=" * 70)
    logger.info("彪哥战法 - 简化版回测演示")
    logger.info("=" * 70)
    
    logger.info("\n【说明】")
    logger.info("此演示使用简化回测逻辑，无需完整Qlib安装")
    logger.info("如需使用完整Qlib功能，请先安装: pip install pyqlib")
    logger.info("\n【回测逻辑】")
    logger.info("1. 获取沪深300成分股")
    logger.info("2. 每月末选动量最强的topk只")
    logger.info("3. 计算等权持仓收益")
    logger.info("4. 输出回测绩效")
    
    # 这里可以调用 biaoge_backtest.py 的功能
    logger.info("\n【运行】")
    logger.info("请运行: python biaoge_backtest.py --action backtest")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='彪哥战法Qlib工作流')
    parser.add_argument('--mode', choices=['full', 'demo'], default='demo',
                       help='运行模式')
    
    args = parser.parse_args()
    
    if args.mode == 'full':
        run_full_workflow()
    else:
        demo_without_qlib()
