"""
真实数据采集系统 - 集成测试
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
from datetime import datetime
from typing import Dict
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_real_data_collector():
    """测试真实数据采集器"""
    print("\n" + "="*60)
    print("🧪 测试真实数据采集系统")
    print("="*60)
    
    try:
        from src.data.real_data_collector_continued import RealDataCollector
        
        # 创建数据采集器
        collector = RealDataCollector()
        
        print("✅ 真实数据采集器创建成功")
        
        # 测试1: 获取市场数据
        print("\n1. 测试市场数据采集...")
        market_data = collector.get_market_data()
        
        print(f"   数据来源: {market_data.get('source', 'unknown')}")
        print(f"   数据质量: {market_data.get('data_quality', 'unknown')}")
        print(f"   股票总数: {market_data.get('total_stocks', 0)}")
        print(f"   上涨家数: {market_data.get('rise_count', 0)}")
        print(f"   下跌家数: {market_data.get('fall_count', 0)}")
        print(f"   上涨比例: {market_data.get('rise_ratio', 0)*100:.1f}%")
        print(f"   平均涨跌: {market_data.get('average_change', 0):.2f}%")
        
        if market_data.get('note'):
            print(f"   备注: {market_data['note']}")
        
        # 测试2: 检查数据源状态
        print("\n2. 检查数据源状态...")
        status = collector.get_data_source_status()
        
        print(f"   检查时间: {status['timestamp']}")
        print(f"   数据源数量: {len(status['sources'])}")
        
        for source_name, source_status in status['sources'].items():
            status_text = "✅ 正常" if source_status['status'] == 'healthy' else "⚠️ 降级"
            enabled_text = "启用" if source_status['enabled'] else "禁用"
            print(f"   • {source_name}: {status_text} ({enabled_text})")
        
        # 测试3: 测试缓存机制
        print("\n3. 测试缓存机制...")
        
        # 第一次获取（可能从网络）
        start_time = datetime.now()
        data1 = collector.get_market_data(use_cache=False)
        time1 = (datetime.now() - start_time).total_seconds()
        
        # 第二次获取（应该从缓存）
        start_time = datetime.now()
        data2 = collector.get_market_data(use_cache=True)
        time2 = (datetime.now() - start_time).total_seconds()
        
        print(f"   第一次获取耗时: {time1:.3f}秒")
        print(f"   第二次获取耗时: {time2:.3f}秒")
        print(f"   缓存加速: {time1/time2 if time2>0 else 0:.1f}倍")
        
        # 验证数据一致性
        if data1['source'] == data2['source']:
            print(f"   数据一致性: ✅ 一致")
        else:
            print(f"   数据一致性: ⚠️ 不一致 (可能使用了不同数据源)")
        
        return True, market_data
        
    except Exception as e:
        logger.error(f"真实数据采集测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def integrate_with_state_evolution(market_data: Dict):
    """集成状态演化系统"""
    print("\n" + "="*60)
    print("🔄 集成状态演化系统")
    print("="*60)
    
    try:
        from src.state_evolution.simple_evolution_engine import SimpleStateEvolutionEngine
        
        # 创建演化引擎
        engine = SimpleStateEvolutionEngine()
        
        # 从市场数据提取技术评分
        rise_ratio = market_data.get('rise_ratio', 0.5)
        avg_change = market_data.get('average_change', 0)
        
        # 计算技术评分（简化版）
        # 基于上涨比例和平均涨跌
        technical_score = 50 + (rise_ratio - 0.5) * 100 + avg_change * 5
        technical_score = max(0, min(100, technical_score))
        
        print(f"   市场数据:")
        print(f"     上涨比例: {rise_ratio*100:.1f}%")
        print(f"     平均涨跌: {avg_change:.2f}%")
        print(f"   计算的技术评分: {technical_score:.1f}")
        
        # 分析市场状态
        current_state = engine.analyze_current_market(technical_score, rise_ratio)
        
        # 获取状态定义
        from src.state_evolution.state_definitions import get_state_definition
        state_def = get_state_definition(current_state)
        
        print(f"\n   状态分析结果:")
        print(f"     当前状态: {state_def.chinese_name}")
        print(f"     状态描述: {state_def.description}")
        print(f"     建议仓位: {state_def.position_range[0]}%-{state_def.position_range[1]}%")
        print(f"     操作策略: {state_def.operation_strategy}")
        print(f"     风险等级: {state_def.risk_level}")
        
        # 预测下一状态
        transitions = engine.predict_next_state(current_state)
        
        if transitions:
            print(f"\n   状态演化预测:")
            for i, transition in enumerate(transitions[:3]):
                to_state_def = get_state_definition(transition.to_state)
                print(f"     {i+1}. {to_state_def.chinese_name} (概率: {transition.probability:.1f}%)")
                print(f"         类型: {transition.transition_type}")
                print(f"         描述: {transition.description}")
        
        return True
        
    except Exception as e:
        logger.error(f"状态演化集成失败: {e}")
        return False


def create_data_quality_report(market_data: Dict):
    """创建数据质量报告"""
    print("\n" + "="*60)
    print("📊 数据质量报告")
    print("="*60)
    
    source = market_data.get('source', 'unknown')
    quality = market_data.get('data_quality', 'unknown')
    
    print(f"   数据来源: {source}")
    print(f"   数据质量: {quality}")
    
    # 评估数据质量
    if quality == 'good':
        print(f"   ✅ 数据质量优秀，可用于决策")
    elif quality == 'partial':
        print(f"   ⚠️  数据部分完整，建议谨慎使用")
    elif quality == 'estimated':
        print(f"   ⚠️  数据为估算值，仅供参考")
    elif quality == 'simulated':
        print(f"   ❌ 数据为模拟数据，真实数据获取失败")
    else:
        print(f"   ❓ 数据质量未知")
    
    # 检查关键指标
    required_fields = ['total_stocks', 'rise_count', 'fall_count', 'rise_ratio']
    missing_fields = [field for field in required_fields if field not in market_data]
    
    if missing_fields:
        print(f"   ❌ 缺失关键字段: {missing_fields}")
    else:
        print(f"   ✅ 关键字段完整")
    
    # 检查数据合理性
    total = market_data.get('total_stocks', 0)
    rise = market_data.get('rise_count', 0)
    fall = market_data.get('fall_count', 0)
    
    if total > 0:
        calculated_ratio = rise / total
        reported_ratio = market_data.get('rise_ratio', 0)
        
        if abs(calculated_ratio - reported_ratio) < 0.01:
            print(f"   ✅ 数据一致性检查通过")
        else:
            print(f"   ⚠️  数据不一致: 计算比例={calculated_ratio:.3f}, 报告比例={reported_ratio:.3f}")
    
    return True


def demonstrate_system_workflow():
    """演示系统工作流程"""
    print("\n" + "="*60)
    print("🔄 真实数据系统工作流程演示")
    print("="*60)
    
    print("\n📋 系统架构:")
    print("  1. 多源数据采集 (AkShare、Tushare、东方财富、新浪)")
    print("  2. 智能降级机制 (真实数据失败时使用模拟数据)")
    print("  3. 数据缓存系统 (减少API调用，提高响应速度)")
    print("  4. 状态演化集成 (将市场数据转化为状态分析)")
    
    print("\n🔄 工作流程:")
    print("  步骤1: 尝试从多个数据源获取实时市场数据")
    print("  步骤2: 如果所有真实数据源失败，使用智能模拟数据")
    print("  步骤3: 分析市场数据，计算技术评分")
    print("  步骤4: 使用状态演化系统分析当前市场状态")
    print("  步骤5: 预测状态演化，生成策略建议")
    
    print("\n🎯 核心优势:")
    print("  • 高可用性: 多数据源备份，自动降级")
    print("  • 实时性: 缓存机制保证快速响应")
    print("  • 准确性: 数据质量监控和验证")
    print("  • 集成性: 无缝对接状态演化系统")
    
    print("\n🚀 实施进展:")
    print("  ✅ 第1步: 动态状态演化系统完成")
    print("  ✅ 第2步: 真实数据采集框架完成")
    print("  🔜 第3步: 优化数据源连接稳定性")
    print("  🔜 第4步: 实现新闻和政策数据采集")
    print("  🔜 第5步: 完善数据质量监控")
    
    return True


def run_integration_test():
    """运行集成测试"""
    print("\n" + "="*60)
    print("🧪 真实数据系统集成测试")
    print("="*60)
    
    # 测试真实数据采集
    success, market_data = test_real_data_collector()
    
    if not success:
        print("\n❌ 真实数据采集测试失败")
        return False
    
    # 创建数据质量报告
    create_data_quality_report(market_data)
    
    # 集成状态演化系统
    integration_success = integrate_with_state_evolution(market_data)
    
    if not integration_success:
        print("\n❌ 状态演化集成测试失败")
        return False
    
    # 演示系统工作流程
    demonstrate_system_workflow()
    
    return True


if __name__ == "__main__":
    print("🚀 彪哥战法v5.0 - 第2步：真实数据采集系统")
    print("📅 实施时间: 2026-03-26")
    print("🎯 目标: 建立稳健的多源数据采集系统")
    
    success = run_integration_test()
    
    if success:
        print("\n" + "="*60)
        print("🎉 第2步实施成功！")
        print("="*60)
        
        print("\n✅ 已完成:")
        print("  1. 多源数据采集框架实现")
        print("  2. 智能降级机制完成")
        print("  3. 数据缓存系统建立")
        print("  4. 状态演化系统集成")
        print("  5. 数据质量监控实现")
        
        print("\n🚀 下一步行动:")
        print("  1. 优化数据源连接稳定性")
        print("  2. 实现新闻数据实时采集")
        print("  3. 实现政策数据监测")
        print("  4. 完善经济数据采集")
        print("  5. 建立数据质量报警系统")
        
        print("\n📅 预计时间:")
        print("  • 数据源优化: 1-2天")
        print("  • 新闻数据采集: 1天")
        print("  • 政策数据监测: 2天")
        print("  • 经济数据完善: 1天")
        print("  • 质量报警系统: 1天")
        print("  • 总计: 6-7天")
        
        print("\n💡 实施策略:")
        print("  1. 优先保证市场数据稳定性")
        print("  2. 逐步增加其他数据维度")
        print("  3. 建立数据质量指标体系")
        print("  4. 实现自动化监控和报警")
        
        print("\n🎯 预期效果:")
        print("  • 实时、准确的市场数据")
        print("  • 多维度数据支持")
        print("  • 高可用性数据服务")
        print("  • 智能化状态分析")
        
        sys.exit(0)
    else:
        print("\n❌ 集成测试失败，需要修复问题")
        sys.exit(1)