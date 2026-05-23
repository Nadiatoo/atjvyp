#!/usr/bin/env python3
"""
彪哥战法 × Qlib 整合示例
展示如何将四季判断模型与Qlib完整工作流结合
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import qlib
from qlib.data import D
from qlib.config import REG_CN
import pandas as pd
import numpy as np
import logging

from biaoge_season_model import BiaogeSeasonModel, BiaogeSeasonDataHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BiaogeIntegratedStrategy:
    """
    整合策略: 结合Qlib的Alpha预测和彪哥四季判断
    """
    
    def __init__(self, season_model_path: str = 'biaoge_season_model.pkl'):
        # 初始化Qlib
        qlib.init(provider_uri='~/.qlib/qlib_data/cn_data', region=REG_CN)
        
        # 加载四季判断模型
        self.season_model = BiaogeSeasonModel()
        if Path(season_model_path).exists():
            self.season_model.load(season_model_path)
            logger.info(f"四季模型已加载: {season_model_path}")
        else:
            logger.warning(f"模型文件不存在: {season_model_path}, 请先训练模型")
            self.season_model = None
    
    def get_market_features(self) -> pd.DataFrame:
        """获取当前市场特征"""
        # 获取上证指数数据
        df = D.features(
            instruments=['SH000001'],
            fields=['$close', '$volume', '$high', '$low'],
            start_time='2024-01-01',
            end_time='2026-03-01'
        )
        
        # 计算特征 (与训练时一致)
        features = pd.DataFrame(index=df.index)
        
        # 价格动量
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
        def calc_rsi(x):
            delta = x.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
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
    
    def predict_current_season(self) -> dict:
        """预测当前市场季节"""
        if self.season_model is None:
            return {"error": "模型未加载"}
        
        # 获取最新特征
        features = self.get_market_features()
        
        if features.empty:
            return {"error": "无法获取市场特征"}
        
        # 取最新一天
        latest = features.iloc[-1:]
        
        # 预测
        season_idx = self.season_model.predict(latest)[0]
        season_proba = self.season_model.predict_proba(latest)[0]
        
        season_names = ['春播', '夏长', '秋收', '冬藏']
        position_map = {0: 0.4, 1: 0.8, 2: 0.4, 3: 0.0}
        
        result = {
            "season": season_names[int(season_idx)],
            "confidence": float(season_proba.max()),
            "probabilities": {
                "春播": float(season_proba[0]),
                "夏长": float(season_proba[1]),
                "秋收": float(season_proba[2]),
                "冬藏": float(season_proba[3]),
            },
            "suggested_position": position_map[int(season_idx)],
            "date": str(latest.index[-1][0].date()),
        }
        
        return result
    
    def get_stock_signals(self, pred_score: pd.Series, topk: int = 20) -> pd.DataFrame:
        """
        结合四季判断和Alpha预测生成个股信号
        
        策略:
        - 春播: 选反弹初期强势股, 仓位40%
        - 夏长: 选主升浪强势股, 仓位80%
        - 秋收: 减仓, 只留最强标的, 仓位40%
        - 冬藏: 空仓或极轻仓
        """
        # 预测当前季节
        season_info = self.predict_current_season()
        
        if "error" in season_info:
            logger.error(season_info["error"])
            return pd.DataFrame()
        
        season = season_info["season"]
        suggested_position = season_info["suggested_position"]
        
        logger.info(f"当前季节: {season}, 建议仓位: {suggested_position:.0%}")
        
        # 根据季节调整选股策略
        if season == "冬藏":
            logger.info("冬藏期: 建议空仓观望")
            return pd.DataFrame()
        
        elif season == "春播":
            # 春播期: 选超跌反弹 + Alpha信号
            logger.info("春播期: 布局反弹初期强势股")
            top_stocks = pred_score.sort_values(ascending=False).head(topk)
            
        elif season == "夏长":
            # 夏长期: 选最强Alpha
            logger.info("夏长期: 重仓主升浪强势股")
            top_stocks = pred_score.sort_values(ascending=False).head(topk)
            
        else:  # 秋收
            # 秋收期: 减仓, 只留最强的10只
            logger.info("秋收期: 逢高减仓, 只留最强标的")
            top_stocks = pred_score.sort_values(ascending=False).head(topk // 2)
        
        # 构建信号DataFrame
        signals = pd.DataFrame({
            'score': top_stocks,
            'season': season,
            'target_position': suggested_position / len(top_stocks) if len(top_stocks) > 0 else 0
        })
        
        return signals


def demo_run():
    """演示运行"""
    print("=" * 60)
    print("彪哥战法 × Qlib 整合演示")
    print("=" * 60)
    
    # 创建整合策略
    strategy = BiaogeIntegratedStrategy()
    
    # 预测当前季节
    print("\n【当前季节判断】")
    season_info = strategy.predict_current_season()
    
    if "error" in season_info:
        print(f"错误: {season_info['error']}")
        return
    
    print(f"日期: {season_info['date']}")
    print(f"季节: {season_info['season']}")
    print(f"置信度: {season_info['confidence']:.2%}")
    print(f"建议仓位: {season_info['suggested_position']:.0%}")
    
    print("\n【四季概率分布】")
    for season, prob in season_info['probabilities'].items():
        bar = "█" * int(prob * 20)
        print(f"  {season}: {prob:.2%} {bar}")
    
    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)


if __name__ == '__main__':
    demo_run()
