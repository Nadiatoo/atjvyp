"""
彪哥战法v5.0系统测试
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_data_collection():
    """测试数据采集"""
    logger.info("测试数据采集模块")
    
    try:
        from src.data.collectors.stock_collector import StockCollector
        from src.data.collectors.base_collector import DataCollectorManager
        
        # 创建采集器配置
        config = {
            "enabled": True,
            "timeout": 30,
            "retry_times": 3,
            "cache_dir": "data/cache",
            "cache_ttl": 300,
            "data_sources": ["mock"],  # 使用模拟数据测试
            "max_retries": 3,
            "retry_delay": 5
        }
        
        # 创建采集器
        collector = StockCollector(config)
        
        # 测试采集
        data = collector.collect()
        
        if data and "market_stats" in data:
            logger.info(f"✅ 数据采集测试成功")
            logger.info(f"   股票数量: {data['market_stats'].get('total_stocks', 0)}")
            logger.info(f"   上涨家数: {data['market_stats'].get('rise_count', 0)}")
            logger.info(f"   涨停家数: {data['market_stats'].get('limit_up_count', 0)}")
            return True
        else:
            logger.error("❌ 数据采集测试失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 数据采集测试异常: {e}")
        return False


def test_technical_analysis():
    """测试技术面分析"""
    logger.info("测试技术面分析模块")
    
    try:
        from src.analysis.engines.technical_engine import TechnicalAnalysisEngine
        
        # 创建分析引擎配置
        config = {
            "weights": {
                "trend": 0.30,
                "pattern": 0.25,
                "indicator": 0.25,
                "key_level": 0.20
            }
        }
        
        # 创建分析引擎
        engine = TechnicalAnalysisEngine(config)
        
        # 创建测试数据
        import pandas as pd
        import numpy as np
        
        np.random.seed(42)
        n_stocks = 100
        
        test_data = {
            "technical_data": {
                "stocks": [
                    {
                        "代码": f"{i:06d}",
                        "名称": f"测试股票{i}",
                        "最新价": np.random.uniform(10, 100),
                        "涨跌幅": np.random.uniform(-10, 10),
                        "成交量(手)": np.random.randint(10000, 1000000),
                        "成交额(万)": np.random.uniform(100, 10000),
                        "ma5": np.random.uniform(10, 100),
                        "ma10": np.random.uniform(10, 100),
                        "ma20": np.random.uniform(10, 100),
                        "振幅": np.random.uniform(1, 10)
                    }
                    for i in range(1, n_stocks + 1)
                ]
            }
        }
        
        # 执行分析
        result = engine.analyze(test_data)
        
        if result and "technical_score" in result:
            logger.info(f"✅ 技术面分析测试成功")
            logger.info(f"   技术评分: {result['technical_score']:.1f}")
            logger.info(f"   市场状态: {result['market_status']}")
            logger.info(f"   置信度: {result['confidence']:.1f}")
            return True
        else:
            logger.error("❌ 技术面分析测试失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 技术面分析测试异常: {e}")
        return False


def test_main_system():
    """测试主系统"""
    logger.info("测试主系统")
    
    try:
        from src.main import BiaogeStrategyV5
        
        # 创建系统实例
        system = BiaogeStrategyV5()
        
        # 运行分析
        report = system.run_daily_analysis()
        
        if report:
            logger.info(f"✅ 主系统测试成功")
            
            # 输出关键信息
            market_summary = report.get("market_summary", {})
            season_judgment = report.get("season_judgment", {})
            strategy_suggestions = report.get("strategy_suggestions", {})
            
            logger.info(f"   上涨家数: {market_summary.get('rise_count', 0)}")
            logger.info(f"   季节判断: {season_judgment.get('season', '未知')}")
            logger.info(f"   建议仓位: {strategy_suggestions.get('suggested_position', 0)}%")
            
            # 清理资源
            system.cleanup()
            
            return True
        else:
            logger.error("❌ 主系统测试失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 主系统测试异常: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    logger.info("开始运行彪哥战法v5.0系统测试")
    print("\n" + "="*60)
    print("🧪 彪哥战法v5.0系统测试")
    print("="*60)
    
    test_results = []
    
    # 测试1: 数据采集
    print("\n1. 测试数据采集模块...")
    result1 = test_data_collection()
    test_results.append(("数据采集", result1))
    
    # 测试2: 技术面分析
    print("\n2. 测试技术面分析模块...")
    result2 = test_technical_analysis()
    test_results.append(("技术面分析", result2))
    
    # 测试3: 主系统
    print("\n3. 测试主系统...")
    result3 = test_main_system()
    test_results.append(("主系统", result3))
    
    # 输出测试结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed_count = 0
    total_count = len(test_results)
    
    for test_name, passed in test_results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:20} {status}")
        if passed:
            passed_count += 1
    
    print(f"\n通过率: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)")
    
    if passed_count == total_count:
        print("\n🎉 所有测试通过！系统可以正常运行。")
        return True
    else:
        print(f"\n⚠️  {total_count - passed_count} 个测试失败，需要检查问题。")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)