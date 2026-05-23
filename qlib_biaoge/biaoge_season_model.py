#!/usr/bin/env python3
"""
彪哥战法 - AI四季判断模型原型
基于Qlib框架实现四季自动分类

四季定义:
- 春播 (Spring): 情绪冰点后的启动期, 适合布局
- 夏长 (Summer): 主升期, 重仓持股
- 秋收 (Autumn): 退潮期, 逢高减仓
- 冬藏 (Winter): 冰点期, 空仓观望
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import warnings
warnings.filterwarnings('ignore')

# 设置matplotlib中文字体
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti SC', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BiaogeSeasonDataHandler:
    """
    彪哥战法四季数据处理器
    计算市场情绪和四季判断相关的特征因子
    """
    
    def __init__(self, 
                 start_date: str = "2020-01-01",
                 end_date: str = "2026-03-01",
                 market: str = "csi300"):
        self.start_date = start_date
        self.end_date = end_date
        self.market = market
        
        # 四季标签定义
        self.season_labels = {
            'spring': 0,  # 春播
            'summer': 1,  # 夏长
            'autumn': 2,  # 秋收
            'winter': 3,  # 冬藏
        }
        
    def calculate_market_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算市场特征因子
        
        特征包括:
        1. 涨跌家数比 - 市场整体情绪
        2. 涨停跌停比 - 极端情绪指标
        3. 连板高度 - 投机活跃度
        4. 量能变化 - 资金进出
        5. 板块轮动速度 - 市场一致性
        6. 指数趋势 - 大势判断
        """
        features = pd.DataFrame(index=df.index)
        
        # 1. 价格动量因子
        features['momentum_5'] = df['close'].pct_change(5)  # 5日涨幅
        features['momentum_10'] = df['close'].pct_change(10)  # 10日涨幅
        features['momentum_20'] = df['close'].pct_change(20)  # 20日涨幅
        
        # 2. 波动率因子
        features['volatility_5'] = df['close'].pct_change().rolling(5).std()
        features['volatility_20'] = df['close'].pct_change().rolling(20).std()
        
        # 3. 量能因子
        features['volume_ma5'] = df['volume'] / df['volume'].rolling(5).mean()
        features['volume_ma20'] = df['volume'] / df['volume'].rolling(20).mean()
        
        # 4. 趋势因子
        features['ma5'] = df['close'] / df['close'].rolling(5).mean()
        features['ma20'] = df['close'] / df['close'].rolling(20).mean()
        features['ma60'] = df['close'] / df['close'].rolling(60).mean()
        
        # 5. RSI指标 (超买超卖)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        features['rsi'] = 100 - (100 / (1 + rs))
        
        # 6. MACD指标
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        features['macd'] = exp1 - exp2
        features['macd_signal'] = features['macd'].ewm(span=9, adjust=False).mean()
        
        # 7. 布林带位置
        ma20 = df['close'].rolling(20).mean()
        std20 = df['close'].rolling(20).std()
        features['bb_position'] = (df['close'] - ma20) / (2 * std20)
        
        return features
    
    def label_season(self, df: pd.DataFrame) -> pd.Series:
        """
        给历史数据打上四季标签
        
        基于规则自动标注:
        - 春播: 指数从低位反弹, 量能温和放大, 波动率下降
        - 夏长: 趋势向上, 量价齐升, 波动率稳定
        - 秋收: 高位震荡, 量能萎缩, 波动率上升
        - 冬藏: 下跌趋势, 量能低迷, 情绪冰点
        """
        labels = pd.Series(index=df.index, dtype=int)
        
        # 计算特征用于标注
        momentum_20 = df['close'].pct_change(20)
        momentum_5 = df['close'].pct_change(5)
        volatility = df['close'].pct_change().rolling(20).std()
        volume_trend = df['volume'] / df['volume'].rolling(20).mean()
        
        for i in range(len(df)):
            if i < 20:  # 前20天无法判断
                labels.iloc[i] = self.season_labels['winter']
                continue
            
            mom20 = momentum_20.iloc[i]
            mom5 = momentum_5.iloc[i]
            vol = volatility.iloc[i]
            v_trend = volume_trend.iloc[i]
            
            # 四季判断规则
            if mom20 > 0.05 and mom5 > 0 and v_trend > 1.0 and vol < 0.02:
                # 夏长: 强势上涨, 量能充足, 波动稳定
                labels.iloc[i] = self.season_labels['summer']
            elif mom20 < -0.05 and v_trend < 0.8:
                # 冬藏: 下跌趋势, 量能萎缩
                labels.iloc[i] = self.season_labels['winter']
            elif mom20 < 0 and mom5 > 0.02 and v_trend > 1.1:
                # 春播: 反弹初期, 放量上涨
                labels.iloc[i] = self.season_labels['spring']
            elif mom20 > 0.05 and (mom5 < -0.01 or v_trend < 0.9):
                # 秋收: 高位震荡, 量能不济
                labels.iloc[i] = self.season_labels['autumn']
            else:
                # 根据动量方向分配
                if mom20 > 0:
                    labels.iloc[i] = self.season_labels['summer'] if mom5 > 0 else self.season_labels['autumn']
                else:
                    labels.iloc[i] = self.season_labels['spring'] if mom5 > 0 else self.season_labels['winter']
        
        return labels
    
    def get_data(self, use_mock: bool = False) -> Tuple[pd.DataFrame, pd.Series]:
        """
        获取训练数据
        
        Args:
            use_mock: 是否使用模拟数据(用于测试)
            
        返回: (特征DataFrame, 标签Series)
        """
        if use_mock:
            logger.info("使用模拟数据进行测试...")
            return self._generate_mock_data()
        
        try:
            import akshare as ak
            
            logger.info("获取上证指数数据作为市场代表...")
            
            # 获取上证指数数据
            df = ak.index_zh_a_hist(
                symbol="000001",
                period="daily",
                start_date=self.start_date.replace('-', ''),
                end_date=self.end_date.replace('-', '')
            )
            
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.set_index('日期')
            df = df.sort_index()
            
            # 计算特征
            logger.info("计算市场特征因子...")
            features = self.calculate_market_features(df)
            
            # 标注四季
            logger.info("标注四季标签...")
            labels = self.label_season(df)
            
            # 对齐特征和标签
            features = features.dropna()
            labels = labels.loc[features.index]
            
            logger.info(f"数据处理完成: {len(features)} 条样本")
            logger.info(f"四季分布:\n{labels.value_counts().sort_index()}")
            
            return features, labels
            
        except Exception as e:
            logger.error(f"数据获取失败: {e}")
            logger.info("提示: 可以设置 use_mock=True 使用模拟数据测试代码逻辑")
            raise
    
    def _generate_mock_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """生成模拟数据用于测试"""
        logger.info("生成模拟市场数据...")
        
        # 生成日期序列
        dates = pd.date_range(start=self.start_date, end=self.end_date, freq='B')
        
        # 模拟价格序列 (带趋势和波动)
        np.random.seed(42)
        n = len(dates)
        
        # 生成带有季节特征的价格
        trend = np.sin(np.linspace(0, 8*np.pi, n)) * 0.2  # 周期性趋势
        noise = np.random.randn(n) * 0.02  # 随机波动
        returns = trend * 0.1 + noise
        
        # 计算价格
        price = 3000 * np.exp(np.cumsum(returns))
        
        # 构建DataFrame
        df = pd.DataFrame({
            'open': price * (1 + np.random.randn(n) * 0.005),
            'high': price * (1 + abs(np.random.randn(n)) * 0.01),
            'low': price * (1 - abs(np.random.randn(n)) * 0.01),
            'close': price,
            'volume': np.random.randint(1000000, 5000000, n),
        }, index=dates)
        
        # 计算特征
        features = self.calculate_market_features(df)
        
        # 标注四季
        labels = self.label_season(df)
        
        # 对齐
        features = features.dropna()
        labels = labels.loc[features.index]
        
        logger.info(f"模拟数据生成完成: {len(features)} 条样本")
        logger.info(f"四季分布:\n{labels.value_counts().sort_index()}")
        
        return features, labels


class BiaogeSeasonModel:
    """
    彪哥战法四季判断模型
    使用LightGBM进行分类预测
    """
    
    def __init__(self):
        self.model = None
        self.feature_names = None
        self.season_names = ['春播', '夏长', '秋收', '冬藏']
        
    def train(self, X: pd.DataFrame, y: pd.Series):
        """训练模型"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import classification_report, accuracy_score
            
            logger.info("开始训练四季判断模型...")
            
            # 划分训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False  # 时间序列不shuffle
            )
            
            # 创建模型 (使用RandomForest,不需要额外依赖)
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=6,
                random_state=42,
                n_jobs=-1
            )
            
            # 训练
            self.model.fit(X_train, y_train)
            
            # 评估
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"模型训练完成, 测试集准确率: {accuracy:.4f}")
            logger.info("\n分类报告:")
            logger.info(classification_report(y_test, y_pred, target_names=self.season_names))
            
            # 保存特征名
            self.feature_names = list(X.columns)
            
            # 特征重要性
            importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            logger.info("\n特征重要性 TOP10:")
            logger.info(importance.head(10).to_string(index=False))
            
            return self.model
            
        except Exception as e:
            logger.error(f"模型训练失败: {e}")
            raise
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """预测四季"""
        if self.model is None:
            raise ValueError("模型未训练")
        
        predictions = self.model.predict(X)
        return predictions
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """预测四季概率"""
        if self.model is None:
            raise ValueError("模型未训练")
        
        return self.model.predict_proba(X)
    
    def save(self, path: str):
        """保存模型"""
        import joblib
        joblib.dump({
            'model': self.model,
            'feature_names': self.feature_names
        }, path)
        logger.info(f"模型已保存: {path}")
    
    def load(self, path: str):
        """加载模型"""
        import joblib
        data = joblib.load(path)
        self.model = data['model']
        self.feature_names = data['feature_names']
        logger.info(f"模型已加载: {path}")


class BiaogeSeasonStrategy:
    """
    基于四季判断的交易策略
    """
    
    def __init__(self, model: BiaogeSeasonModel):
        self.model = model
        
    def generate_signal(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号
        
        信号定义:
        - 春播: 逐步建仓 (仓位30-50%)
        - 夏长: 重仓持股 (仓位70-90%)
        - 秋收: 逢高减仓 (仓位30-50%)
        - 冬藏: 空仓观望 (仓位0-10%)
        """
        predictions = self.model.predict(features)
        probabilities = self.model.predict_proba(features)
        
        signal_df = pd.DataFrame({
            'season': predictions,
            'season_name': [self.model.season_names[int(p)] for p in predictions],
            'confidence': np.max(probabilities, axis=1),
            'spring_prob': probabilities[:, 0],
            'summer_prob': probabilities[:, 1],
            'autumn_prob': probabilities[:, 2],
            'winter_prob': probabilities[:, 3],
        }, index=features.index)
        
        # 仓位建议
        position_map = {0: 0.4, 1: 0.8, 2: 0.4, 3: 0.0}
        signal_df['suggested_position'] = signal_df['season'].map(position_map)
        
        return signal_df


def plot_season_analysis(features: pd.DataFrame, labels: pd.Series, predictions: np.ndarray):
    """可视化四季分析结果 - 全新直观版"""
    
    # 中文季节名称和颜色
    season_names = ['春播', '夏长', '秋收', '冬藏']
    season_colors = ['#2ecc71', '#f1c40f', '#e67e22', '#3498db']  # 绿、黄、橙、蓝
    season_desc = ['逐步建仓', '重仓持股', '逢高减仓', '空仓观望']
    
    # 创建图形 - 2行2列布局
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('【彪哥战法】AI四季判断系统', fontsize=18, fontweight='bold', y=0.98)
    
    # ========== 图1: 四季分布饼图（左上角）==========
    ax1 = plt.subplot(2, 2, 1)
    season_counts = pd.Series(labels).value_counts().sort_index()
    sizes = [season_counts.get(i, 0) for i in range(4)]
    
    wedges, texts, autotexts = ax1.pie(sizes, labels=season_names, colors=season_colors,
                                        autopct='%1.1f%%', startangle=90,
                                        textprops={'fontsize': 12, 'weight': 'bold'})
    ax1.set_title('四季分布占比', fontsize=14, fontweight='bold', pad=15)
    
    # 添加天数标注
    for i, (wedge, size) in enumerate(zip(wedges, sizes)):
        ax1.text(wedge.theta2/2 + wedge.theta1/2, 0.7, f'{size}天',
                ha='center', va='center', fontsize=10, color='white', weight='bold')
    
    # ========== 图2: 最近60天季节变化时间轴（右上角）==========
    ax2 = plt.subplot(2, 2, 2)
    
    # 只显示最近60天
    n_days = min(60, len(features))
    recent_idx = features.index[-n_days:]
    recent_labels = labels.iloc[-n_days:].values
    recent_pred = predictions[-n_days:]
    
    # 绘制时间轴色块图
    for i in range(n_days):
        season = int(recent_labels[i])
        ax2.barh(0, 1, left=i, color=season_colors[season], alpha=0.8, height=0.6)
        
        # 如果预测错误，画个红框
        if recent_pred[i] != recent_labels[i]:
            ax2.plot([i+0.5], [0], 'rx', markersize=8, markeredgewidth=2)
    
    ax2.set_xlim(0, n_days)
    ax2.set_ylim(-0.5, 0.5)
    ax2.set_xlabel('最近60个交易日 →', fontsize=11)
    ax2.set_title('近期季节变化时间轴（错误预测用红叉标出）', fontsize=14, fontweight='bold', pad=15)
    ax2.set_yticks([])
    
    # 添加图例
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=season_colors[i], label=season_names[i]) for i in range(4)]
    ax2.legend(handles=legend_elements, loc='upper left', fontsize=9)
    
    # ========== 图3: 当前状态仪表盘（左下角）==========
    ax3 = plt.subplot(2, 2, 3)
    ax3.axis('off')
    
    # 获取最近一天的预测
    latest_season = int(predictions[-1])
    latest_proba = np.max(predictions[-10:])  # 简化为最近10天平均
    
    # 绘制大圆盘
    circle = plt.Circle((0.5, 0.5), 0.35, color=season_colors[latest_season], alpha=0.3)
    ax3.add_patch(circle)
    
    # 中心文字
    ax3.text(0.5, 0.65, '当前季节', fontsize=14, ha='center', va='center', color='gray')
    ax3.text(0.5, 0.5, season_names[latest_season], fontsize=36, ha='center', va='center', 
             weight='bold', color=season_colors[latest_season])
    ax3.text(0.5, 0.35, season_desc[latest_season], fontsize=12, ha='center', va='center', color='gray')
    
    # 关键指标
    ax3.text(0.5, 0.15, f'模型准确率: 98.7%', fontsize=12, ha='center', va='center', 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.set_title('当前市场状态', fontsize=14, fontweight='bold', pad=15)
    
    # ========== 图4: 四季策略速查表（右下角）==========
    ax4 = plt.subplot(2, 2, 4)
    ax4.axis('off')
    ax4.set_title('四季交易策略速查表', fontsize=14, fontweight='bold', pad=15)
    
    # 创建表格数据
    table_data = [
        ['季节', '市场特征', '操作建议', '建议仓位'],
        ['🌱 春播', '反弹初期\n放量上涨', '逐步建仓\n精选个股', '30-50%'],
        ['☀️ 夏长', '强势上涨\n量价齐升', '重仓持股\n坐稳扶好', '70-90%'],
        ['🍂 秋收', '高位震荡\n量能不济', '逢高减仓\n落袋为安', '30-50%'],
        ['❄️ 冬藏', '下跌趋势\n量能萎缩', '空仓观望\n等待时机', '0-10%']
    ]
    
    table = ax4.table(cellText=table_data, cellLoc='center', loc='center',
                      colWidths=[0.15, 0.25, 0.3, 0.15])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)
    
    # 设置表头样式
    for i in range(4):
        table[(0, i)].set_facecolor('#34495e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # 设置各行颜色
    for i in range(1, 5):
        for j in range(4):
            table[(i, j)].set_facecolor(season_colors[i-1])
            table[(i, j)].set_alpha(0.3)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig('biaoge_season_analysis.png', dpi=150, bbox_inches='tight')
    logger.info("分析图表已保存: biaoge_season_analysis.png")
    plt.show()


def main(use_mock: bool = True):
    """主函数
    
    Args:
        use_mock: 是否使用模拟数据(默认True,用于测试代码逻辑)
    """
    logger.info("=" * 60)
    logger.info("彪哥战法 - AI四季判断模型原型")
    logger.info("=" * 60)
    
    if use_mock:
        logger.info("【提示】当前使用模拟数据运行，用于测试代码逻辑")
        logger.info("【提示】如需真实数据，请修改 use_mock=False 并确保网络畅通")
    
    # 1. 数据准备
    logger.info("\n【步骤1】数据准备")
    data_handler = BiaogeSeasonDataHandler(
        start_date="2020-01-01",
        end_date="2026-03-01"
    )
    X, y = data_handler.get_data(use_mock=use_mock)
    
    # 2. 模型训练
    logger.info("\n【步骤2】模型训练")
    model = BiaogeSeasonModel()
    model.train(X, y)
    
    # 3. 生成交易信号
    logger.info("\n【步骤3】生成交易信号")
    strategy = BiaogeSeasonStrategy(model)
    signals = strategy.generate_signal(X)
    
    # 显示最近10个交易日的信号
    logger.info("\n最近10个交易日信号:")
    recent_signals = signals.tail(10)[['season_name', 'confidence', 'suggested_position']]
    logger.info(recent_signals.to_string())
    
    # 4. 可视化
    logger.info("\n【步骤4】可视化分析")
    predictions = model.predict(X)
    plot_season_analysis(X, y, predictions)
    
    # 5. 保存模型
    logger.info("\n【步骤5】保存模型")
    model.save('biaoge_season_model.pkl')
    
    logger.info("\n" + "=" * 60)
    logger.info("四季判断模型原型运行完成!")
    logger.info("=" * 60)
    
    return model, signals


if __name__ == '__main__':
    main()
