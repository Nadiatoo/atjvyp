"""
彪哥战法v5.0 - 主程序（简化版）
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
from datetime import datetime
from typing import Dict, Any

from config.settings import data_config, analysis_config
from src.data.collectors.stock_collector import StockCollector
from src.data.collectors.base_collector import DataCollectorManager
from src.analysis.engines.technical_engine_fixed import TechnicalAnalysisEngine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BiaogeStrategyV5:
    """彪哥战法v5.0主类（简化版）"""
    
    def __init__(self):
        logger.info("初始化彪哥战法v5.0系统（简化版）")
        
        # 初始化数据采集器
        self.data_manager = DataCollectorManager()
        self.init_data_collectors()
        
        # 初始化分析引擎
        self.init_analysis_engines()
        
        logger.info("彪哥战法v5.0系统初始化完成")
    
    def init_data_collectors(self):
        """初始化数据采集器"""
        try:
            # 股票数据采集器配置
            stock_config = {
                "enabled": True,
                "timeout": 30,
                "retry_times": 3,
                "cache_dir": "data/cache",
                "cache_ttl": 300,
                "data_sources": ["mock"],  # 使用模拟数据
                "max_retries": 3,
                "retry_delay": 5
            }
            
            stock_collector = StockCollector(stock_config)
            self.data_manager.register_collector("stock", stock_collector)
            
            logger.info("数据采集器初始化完成")
            
        except Exception as e:
            logger.error(f"数据采集器初始化失败: {e}")
    
    def init_analysis_engines(self):
        """初始化分析引擎"""
        try:
            # 技术面分析引擎配置
            technical_config = {
                "weights": {
                    "trend": 0.30,
                    "pattern": 0.25,
                    "indicator": 0.25,
                    "key_level": 0.20
                }
            }
            
            self.technical_engine = TechnicalAnalysisEngine(technical_config)
            
            logger.info("分析引擎初始化完成")
            
        except Exception as e:
            logger.error(f"分析引擎初始化失败: {e}")
    
    def run_daily_analysis(self, date: datetime = None):
        """运行每日分析"""
        logger.info("开始每日分析")
        
        try:
            # 1. 数据采集
            logger.info("步骤1: 数据采集")
            collected_data = self.data_manager.collect_all(date)
            
            if not collected_data:
                logger.error("数据采集失败")
                return None
            
            # 2. 技术面分析
            logger.info("步骤2: 技术面分析")
            stock_data = collected_data.get("stock", {})
            technical_result = self.technical_engine.analyze(stock_data)
            
            # 3. 生成分析报告
            logger.info("步骤3: 生成分析报告")
            analysis_report = self.generate_analysis_report(
                collected_data,
                technical_result
            )
            
            # 4. 输出报告
            logger.info("步骤4: 输出分析报告")
            self.output_analysis_report(analysis_report)
            
            logger.info("每日分析完成")
            return analysis_report
            
        except Exception as e:
            logger.error(f"每日分析失败: {e}")
            return None
    
    def generate_analysis_report(self, collected_data: Dict[str, Any], 
                                technical_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成分析报告"""
        stock_data = collected_data.get("stock", {})
        market_stats = stock_data.get("market_stats", {})
        
        # 季节判断
        season_tendencies = technical_result.get("season_tendencies", {})
        main_season = max(season_tendencies, key=season_tendencies.get) if season_tendencies else "transition"
        
        # 策略建议
        technical_score = technical_result.get("technical_score", 50)
        suggested_position = max(10, min(80, 30 + (technical_score - 50) * 0.5))
        
        report = {
            "timestamp": datetime.now(),
            "data_source": stock_data.get("source", "mock"),
            "market_summary": {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "rise_count": market_stats.get("rise_count", 0),
                "fall_count": market_stats.get("fall_count", 0),
                "limit_up_count": market_stats.get("limit_up_count", 0),
                "limit_down_count": market_stats.get("limit_down_count", 0),
                "rise_ratio": market_stats.get("rise_ratio", 0),
                "technical_score": technical_score,
                "market_status": technical_result.get("market_status", "unknown")
            },
            "season_judgment": {
                "season": main_season,
                "confidence": season_tendencies.get(main_season, 50) if season_tendencies else 50,
                "tendencies": season_tendencies
            },
            "strategy_suggestions": {
                "season": main_season,
                "suggested_position": round(suggested_position, 1),
                "operation_strategy": self.get_operation_strategy(main_season, technical_score),
                "risk_level": self.get_risk_level(main_season, technical_score)
            }
        }
        
        return report
    
    def get_operation_strategy(self, season: str, technical_score: float) -> str:
        """获取操作策略"""
        strategies = {
            "spring": "分批低吸，布局优质标的",
            "summer": "趋势持有，适度做T",
            "autumn": "分批减仓，锁定利润",
            "winter": "空仓观望，等待信号",
            "transition": "轻仓试错，控制风险"
        }
        
        base_strategy = strategies.get(season, "谨慎操作，控制风险")
        
        if technical_score >= 70:
            return f"积极{base_strategy}"
        elif technical_score >= 60:
            return f"适度{base_strategy}"
        elif technical_score >= 40:
            return base_strategy
        else:
            return f"谨慎{base_strategy}"
    
    def get_risk_level(self, season: str, technical_score: float) -> str:
        """获取风险等级"""
        if season == "winter" or technical_score < 30:
            return "高"
        elif season == "autumn" or technical_score < 50:
            return "中高"
        elif season == "transition" or technical_score < 60:
            return "中"
        elif season == "spring" or technical_score < 70:
            return "中低"
        else:
            return "低"
    
    def output_analysis_report(self, analysis_report: Dict[str, Any]):
        """输出分析报告"""
        try:
            market_summary = analysis_report.get("market_summary", {})
            season_judgment = analysis_report.get("season_judgment", {})
            strategy_suggestions = analysis_report.get("strategy_suggestions", {})
            
            print("\n" + "="*60)
            print("📊 彪哥战法v5.0 - 每日分析报告（简化版）")
            print("="*60)
            
            print(f"\n📅 分析时间: {analysis_report.get('timestamp', '未知')}")
            print(f"📈 数据来源: {analysis_report.get('data_source', '未知')}")
            
            print(f"\n🎯 市场概况:")
            print(f"   上涨家数: {market_summary.get('rise_count', 0)}")
            print(f"   下跌家数: {market_summary.get('fall_count', 0)}")
            print(f"   涨停家数: {market_summary.get('limit_up_count', 0)}")
            print(f"   跌停家数: {market_summary.get('limit_down_count', 0)}")
            print(f"   上涨比例: {market_summary.get('rise_ratio', 0)*100:.1f}%")
            print(f"   技术评分: {market_summary.get('technical_score', 50):.1f}")
            print(f"   市场状态: {market_summary.get('market_status', '未知')}")
            
            print(f"\n🌱 季节判断:")
            print(f"   当前季节: {season_judgment.get('season', '过渡期')}")
            print(f"   置信度: {season_judgment.get('confidence', 0):.1f}")
            
            print(f"\n💰 策略建议:")
            print(f"   建议仓位: {strategy_suggestions.get('suggested_position', 0)}%")
            print(f"   操作策略: {strategy_suggestions.get('operation_strategy', '')}")
            print(f"   风险等级: {strategy_suggestions.get('risk_level', '中')}")
            
            print("\n" + "="*60)
            print("📝 报告生成完成")
            print("="*60 + "\n")
            
        except Exception as e:
            logger.error(f"输出分析报告失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        logger.info("清理系统资源")
        self.data_manager.cleanup_all()
        logger.info("系统资源清理完成")


def main():
    """主函数"""
    try:
        logger.info("启动彪哥战法v5.0系统（简化版）")
        
        # 创建系统实例
        system = BiaogeStrategyV5()
        
        # 运行每日分析
        report = system.run_daily_analysis()
        
        if report:
            logger.info("每日分析成功完成")
        else:
            logger.warning("每日分析完成，但可能存在问题")
        
        # 清理资源
        system.cleanup()
        
        logger.info("彪哥战法v5.0系统运行完成")
        
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"系统运行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()