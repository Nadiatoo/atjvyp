"""
彪哥战法v5.0 - 配置文件
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 数据配置
class DataConfig:
    """数据配置"""
    # 数据存储路径
    DATA_DIR = BASE_DIR / "data"
    CACHE_DIR = DATA_DIR / "cache"
    LOGS_DIR = BASE_DIR / "logs"
    
    # 创建目录
    for dir_path in [DATA_DIR, CACHE_DIR, LOGS_DIR]:
        dir_path.mkdir(exist_ok=True, parents=True)
    
    # 数据库配置
    DATABASE_URL = "sqlite:///data/biaoge_v5.db"
    
    # 数据源配置
    DATA_SOURCES = {
        "akshare": {
            "enabled": True,
            "timeout": 30,
            "retry_times": 3
        },
        "tushare": {
            "enabled": False,  # 需要token，暂时禁用
            "token": "",
            "timeout": 30
        }
    }

# 分析配置
class AnalysisConfig:
    """分析配置"""
    # 技术面分析权重
    TECHNICAL_WEIGHTS = {
        "trend": 0.30,      # 趋势判断
        "pattern": 0.25,    # 形态识别
        "indicator": 0.25,  # 指标验证
        "key_level": 0.20   # 关键位置
    }
    
    # 资金面分析权重
    FUND_FLOW_WEIGHTS = {
        "quant": 0.35,      # 量化资金
        "institutional": 0.30,  # 机构资金
        "retail": 0.20,     # 散户资金
        "liquidity": 0.15   # 流动性
    }
    
    # 情绪面分析权重
    SENTIMENT_WEIGHTS = {
        "traditional": 0.40,  # 传统情绪指标
        "big_data": 0.35,     # 大数据情绪
        "behavioral": 0.25    # 行为金融
    }
    
    # 宏观面分析权重
    MACRO_WEIGHTS = {
        "geopolitical": 0.40,  # 地缘政治
        "policy": 0.35,        # 政策环境
        "international": 0.25  # 国际联动
    }

# 季节判断配置
class SeasonConfig:
    """季节判断配置"""
    # 基础权重
    BASE_WEIGHTS = {
        "technical": 0.30,
        "fund_flow": 0.30,
        "sentiment": 0.20,
        "macro": 0.20
    }
    
    # 动态权重调整规则
    DYNAMIC_ADJUSTMENTS = {
        "quant_dominant": {  # 量化主导
            "fund_flow": +0.10,
            "technical": -0.05,
            "sentiment": -0.05
        },
        "geopolitical_tension": {  # 地缘紧张
            "macro": +0.15,
            "technical": -0.05,
            "fund_flow": -0.05,
            "sentiment": -0.05
        },
        "policy_sensitive": {  # 政策敏感
            "macro": +0.10,
            "technical": -0.05,
            "sentiment": -0.05
        },
        "emotional_extreme": {  # 情绪极端
            "sentiment": +0.10,
            "technical": -0.05,
            "fund_flow": -0.05
        }
    }
    
    # 季节判断阈值
    SEASON_THRESHOLDS = {
        "spring": 70,   # 春播阈值
        "summer": 65,   # 夏长阈值
        "autumn": 60,   # 秋收阈值
        "winter": 75    # 冬藏阈值
    }
    
    # 季节倾向度阈值
    TENDENCY_THRESHOLDS = {
        "spring": 60,
        "summer": 55,
        "autumn": 50,
        "winter": 65
    }

# 风险预警配置
class RiskConfig:
    """风险预警配置"""
    # 预警级别阈值
    ALERT_THRESHOLDS = {
        "yellow": {  # 黄色预警
            "quant_crowding": 0.70,      # 量化策略拥挤度
            "geopolitical_risk": 60,     # 地缘风险指数
            "micro_deviation": 0.15      # 微盘股背离度
        },
        "orange": {  # 橙色预警
            "quant_multikill": True,     # 量化多杀多信号
            "limit_height": 3,           # 连板高度压缩
            "limit_down_count": 50       # 跌停家数
        },
        "red": {     # 红色预警
            "systemic_risk": True,       # 系统性风险确认
            "liquidity_crisis": True,    # 流动性危机
            "geopolitical_extreme": True # 地缘极端事件
        }
    }
    
    # 预警应对措施
    ALERT_ACTIONS = {
        "yellow": {
            "position": 0.50,  # 仓位降至50%
            "hedge": True,     # 增加对冲
            "defensive": True  # 转向防御
        },
        "orange": {
            "position": 0.30,  # 仓位降至30%
            "clear_weak": True, # 清仓跟风品种
            "keep_core": True  # 只保留核心仓位
        },
        "red": {
            "position": 0.10,  # 仓位降至10%
            "wait_signal": True, # 空仓观望
            "monitor": True    # 等待明确信号
        }
    }

# 仓位管理配置
class PositionConfig:
    """仓位管理配置"""
    # 基础仓位配置
    BASE_POSITIONS = {
        "spring": (0.30, 0.50),  # 春播期：30-50%
        "summer": (0.50, 0.80),  # 夏长期：50-80%
        "autumn": (0.20, 0.40),  # 秋收期：20-40%
        "winter": (0.10, 0.20)   # 冬藏期：10-20%
    }
    
    # 风险系数调整
    RISK_ADJUSTMENTS = {
        "geopolitical_high": 0.50,   # 地缘高风险
        "quant_crowding": 0.60,      # 量化策略拥挤
        "policy_sensitive": 0.70,    # 政策敏感期
        "emotional_extreme": 0.80    # 情绪极端期
    }
    
    # 机会系数调整
    OPPORTUNITY_ADJUSTMENTS = {
        "sector_resonance": 1.20,    # 板块共振
        "leader_clear": 1.30,        # 龙头明确
        "fund_inflow": 1.40,         # 资金持续流入
        "technical_breakthrough": 1.20  # 技术突破确认
    }

# 报告输出配置
class ReportConfig:
    """报告输出配置"""
    # 报告类型
    REPORT_TYPES = {
        "pre_market": {  # 盘前报告
            "time": "08:00",
            "enabled": True
        },
        "post_market": {  # 盘后报告
            "time": "17:00",
            "enabled": True
        },
        "weekly": {  # 周度报告
            "day": "friday",
            "enabled": True
        },
        "monthly": {  # 月度报告
            "day": "last",
            "enabled": True
        }
    }
    
    # 飞书配置
    FEISHU_CONFIG = {
        "enabled": True,
        "webhook_url": "",  # 需要配置
        "card_template": "green"  # 卡片模板
    }
    
    # 文件输出配置
    FILE_OUTPUT = {
        "enabled": True,
        "format": "markdown",  # markdown/json
        "directory": BASE_DIR / "reports"
    }

# 监控配置
class MonitorConfig:
    """监控配置"""
    # 性能监控
    PERFORMANCE_MONITOR = {
        "enabled": True,
        "interval": 60,  # 60秒
        "metrics": ["cpu", "memory", "disk", "network"]
    }
    
    # 业务监控
    BUSINESS_MONITOR = {
        "enabled": True,
        "interval": 300,  # 5分钟
        "metrics": ["data_freshness", "analysis_latency", "alert_count"]
    }
    
    # 错误监控
    ERROR_MONITOR = {
        "enabled": True,
        "log_level": "ERROR",
        "alert_threshold": 10  # 10个错误触发告警
    }

# 导出配置实例
data_config = DataConfig()
analysis_config = AnalysisConfig()
season_config = SeasonConfig()
risk_config = RiskConfig()
position_config = PositionConfig()
report_config = ReportConfig()
monitor_config = MonitorConfig()