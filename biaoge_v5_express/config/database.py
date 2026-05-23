"""
数据库配置和模型定义
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

from .settings import data_config

# 创建数据库引擎
engine = create_engine(
    data_config.DATABASE_URL,
    echo=False,  # 设置为True可查看SQL语句
    connect_args={"check_same_thread": False}  # SQLite需要
)

# 创建基类
Base = declarative_base()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 数据模型定义

class StockDaily(Base):
    """股票日线数据"""
    __tablename__ = "stock_daily"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)  # 股票代码
    date = Column(DateTime, index=True)      # 日期
    open = Column(Float)                     # 开盘价
    high = Column(Float)                     # 最高价
    low = Column(Float)                      # 最低价
    close = Column(Float)                    # 收盘价
    volume = Column(Float)                   # 成交量
    amount = Column(Float)                   # 成交额
    change = Column(Float)                   # 涨跌幅
    change_pct = Column(Float)               # 涨跌百分比
    
    # 技术指标
    ma5 = Column(Float)                      # 5日均线
    ma10 = Column(Float)                     # 10日均线
    ma20 = Column(Float)                     # 20日均线
    ma60 = Column(Float)                     # 60日均线
    rsi = Column(Float)                      # RSI指标
    macd = Column(Float)                     # MACD
    macd_signal = Column(Float)              # MACD信号线
    macd_hist = Column(Float)                # MACD柱状图
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class IndexDaily(Base):
    """指数日线数据"""
    __tablename__ = "index_daily"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True)  # 指数代码
    date = Column(DateTime, index=True)      # 日期
    open = Column(Float)                     # 开盘价
    high = Column(Float)                     # 最高价
    low = Column(Float)                      # 最低价
    close = Column(Float)                    # 收盘价
    volume = Column(Float)                   # 成交量
    amount = Column(Float)                   # 成交额
    change = Column(Float)                   # 涨跌幅
    
    # 市场宽度
    advance_count = Column(Integer)          # 上涨家数
    decline_count = Column(Integer)          # 下跌家数
    unchanged_count = Column(Integer)        # 平盘家数
    
    # 极端数据
    limit_up_count = Column(Integer)         # 涨停家数
    limit_down_count = Column(Integer)       # 跌停家数
    limit_up_height = Column(Integer)        # 连板高度
    
    created_at = Column(DateTime, default=datetime.now)

class FundFlow(Base):
    """资金流向数据"""
    __tablename__ = "fund_flow"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)  # 股票代码
    date = Column(DateTime, index=True)      # 日期
    
    # 北向资金
    northbound_in = Column(Float)            # 北向流入
    northbound_out = Column(Float)           # 北向流出
    northbound_net = Column(Float)           # 北向净流入
    
    # 主力资金
    main_in = Column(Float)                  # 主力流入
    main_out = Column(Float)                 # 主力流出
    main_net = Column(Float)                 # 主力净流入
    
    # 散户资金
    retail_in = Column(Float)                # 散户流入
    retail_out = Column(Float)               # 散户流出
    retail_net = Column(Float)               # 散户净流入
    
    # 量化特征
    quant_ratio = Column(Float)              # 量化席位占比
    programmatic_score = Column(Float)       # 程序化特征评分
    crowding_degree = Column(Float)          # 策略拥挤度
    
    created_at = Column(DateTime, default=datetime.now)

class SentimentData(Base):
    """情绪数据"""
    __tablename__ = "sentiment_data"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True)      # 日期
    
    # 传统情绪指标
    fear_greed_index = Column(Float)         # 恐慌贪婪指数
    limit_up_ratio = Column(Float)           # 涨停跌停比
    advance_decline_ratio = Column(Float)    # 涨跌家数比
    
    # 大数据情绪
    social_heat = Column(Float)              # 社交媒体热度
    search_index = Column(Float)             # 搜索指数
    news_sentiment = Column(Float)           # 新闻情感得分
    
    # 行为金融指标
    overreaction_score = Column(Float)       # 过度反应系数
    herd_effect_score = Column(Float)        # 羊群效应强度
    anchoring_score = Column(Float)          # 锚定效应程度
    
    created_at = Column(DateTime, default=datetime.now)

class MacroData(Base):
    """宏观数据"""
    __tablename__ = "macro_data"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True)      # 日期
    
    # 地缘政治
    geopolitical_risk = Column(Float)        # 地缘风险指数
    oil_price = Column(Float)                # 原油价格
    usd_cny = Column(Float)                  # 美元兑人民币
    
    # 政策环境
    monetary_policy = Column(Float)          # 货币政策松紧度
    regulatory_policy = Column(Float)        # 监管政策强度
    industrial_policy = Column(Float)        # 产业政策支持度
    
    # 国际联动
    sp500_change = Column(Float)             # 标普500涨跌幅
    nasdaq_change = Column(Float)            # 纳斯达克涨跌幅
    hang_seng_change = Column(Float)         # 恒生指数涨跌幅
    
    created_at = Column(DateTime, default=datetime.now)

class AnalysisResult(Base):
    """分析结果"""
    __tablename__ = "analysis_result"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True)      # 日期
    
    # 各维度评分
    technical_score = Column(Float)          # 技术面评分
    fund_flow_score = Column(Float)          # 资金面评分
    sentiment_score = Column(Float)          # 情绪面评分
    macro_score = Column(Float)              # 宏观面评分
    
    # 动态权重
    technical_weight = Column(Float)         # 技术面权重
    fund_flow_weight = Column(Float)         # 资金面权重
    sentiment_weight = Column(Float)         # 情绪面权重
    macro_weight = Column(Float)             # 宏观面权重
    
    # 综合评分
    comprehensive_score = Column(Float)      # 综合评分
    
    # 季节判断
    season = Column(String(20))              # 季节判断
    season_confidence = Column(Float)        # 季节置信度
    
    # 板块季节
    tech_season = Column(String(20))         # 科技线季节
    energy_season = Column(String(20))       # 能源线季节
    defensive_season = Column(String(20))    # 防御线季节
    
    created_at = Column(DateTime, default=datetime.now)

class StrategyResult(Base):
    """策略结果"""
    __tablename__ = "strategy_result"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True)      # 日期
    
    # 仓位建议
    position_suggestion = Column(Float)      # 仓位建议
    position_reason = Column(Text)           # 仓位理由
    
    # 风险预警
    risk_level = Column(String(20))          # 风险级别
    risk_reason = Column(Text)               # 风险原因
    risk_action = Column(Text)               # 风险应对
    
    # 操作策略
    operation_strategy = Column(String(50))  # 操作策略
    strategy_details = Column(JSON)          # 策略详情
    
    # 板块建议
    sector_suggestions = Column(JSON)        # 板块建议
    
    created_at = Column(DateTime, default=datetime.now)

class AlertRecord(Base):
    """预警记录"""
    __tablename__ = "alert_record"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True)      # 日期
    alert_time = Column(DateTime)            # 预警时间
    
    alert_level = Column(String(20))         # 预警级别
    alert_type = Column(String(50))          # 预警类型
    alert_message = Column(Text)             # 预警信息
    
    trigger_condition = Column(JSON)         # 触发条件
    action_taken = Column(Text)              # 采取行动
    
    resolved = Column(Boolean, default=False)# 是否已解决
    resolved_at = Column(DateTime)           # 解决时间
    resolution = Column(Text)                # 解决方案
    
    created_at = Column(DateTime, default=datetime.now)

class PerformanceRecord(Base):
    """性能记录"""
    __tablename__ = "performance_record"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True)      # 日期
    
    # 系统性能
    cpu_usage = Column(Float)                # CPU使用率
    memory_usage = Column(Float)             # 内存使用率
    disk_usage = Column(Float)               # 磁盘使用率
    
    # 业务性能
    data_freshness = Column(Float)           # 数据新鲜度（分钟）
    analysis_latency = Column(Float)         # 分析延迟（秒）
    alert_count = Column(Integer)            # 预警数量
    
    # 分析性能
    technical_latency = Column(Float)        # 技术面分析延迟
    fund_flow_latency = Column(Float)        # 资金面分析延迟
    sentiment_latency = Column(Float)        # 情绪面分析延迟
    macro_latency = Column(Float)            # 宏观面分析延迟
    
    created_at = Column(DateTime, default=datetime.now)

# 数据库工具函数

def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def drop_db():
    """删除所有表（谨慎使用）"""
    Base.metadata.drop_all(bind=engine)
    print("数据库表已删除")

def reset_db():
    """重置数据库"""
    drop_db()
    init_db()

# 数据访问工具函数

def save_stock_daily(db, stock_data):
    """保存股票日线数据"""
    # 检查是否已存在
    existing = db.query(StockDaily).filter(
        StockDaily.symbol == stock_data["symbol"],
        StockDaily.date == stock_data["date"]
    ).first()
    
    if existing:
        # 更新现有记录
        for key, value in stock_data.items():
            setattr(existing, key, value)
        existing.updated_at = datetime.now()
    else:
        # 创建新记录
        stock = StockDaily(**stock_data)
        db.add(stock)
    
    db.commit()

def get_latest_analysis(db, days=30):
    """获取最近的分析结果"""
    return db.query(AnalysisResult).order_by(
        AnalysisResult.date.desc()
    ).limit(days).all()

def get_season_history(db, start_date, end_date):
    """获取季节历史"""
    return db.query(AnalysisResult).filter(
        AnalysisResult.date >= start_date,
        AnalysisResult.date <= end_date
    ).order_by(AnalysisResult.date).all()

# 初始化数据库
if __name__ == "__main__":
    init_db()
    print("数据库初始化完成")