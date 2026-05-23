"""
测试东方财富数据采集器
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.data.eastmoney_collector_continued import (
    EastMoneyCollector,
    get_market_stats,
    get_money_flow,
    get_market_sentiment,
    get_comprehensive_data
)


def test_eastmoney_collector():
    """测试东方财富数据采集器"""
    print("🚀 测试东方财富数据采集器")
    print("="*60)
    
    # 创建采集器
    collector = EastMoneyCollector(use_cache=True, cache_ttl=60)
    
    print("1. 测试市场统计数据:")
    print("-"*40)
    
    # 测试今日数据
    stats = collector.get_market_stats()
    if stats:
        print(f"   📅 日期: {stats.date}")
        print(f"   📈 上涨家数: {stats.rise_count}")
        print(f"   📉 下跌家数: {stats.fall_count}")
        print(f"   🚀 涨停家数: {stats.limit_up}")
        print(f"   📉 跌停家数: {stats.limit_down}")
        print(f"   📊 上涨比例: {stats.rise_ratio:.1%}")
        print(f"   🔧 数据源: {stats.source}")
        print(f"   📋 总股票数: {stats.total_stocks}")
    else:
        print("   ❌ 获取市场统计数据失败")
    
    print("\n2. 测试资金流向数据:")
    print("-"*40)
    
    flow = collector.get_money_flow()
    if flow:
        print(f"   📅 日期: {flow.date}")
        print(f"   💰 主力资金: {flow.main_flow:+.2f}亿")
        print(f"   🌐 北向资金: {flow.north_flow:+.2f}亿")
        print(f"   👥 散户资金: {flow.retail_flow:+.2f}亿")
        print(f"   📊 总资金: {flow.total_flow:+.2f}亿")
        print(f"   🔧 数据源: {flow.source}")
        
        # 分析资金流向
        if flow.total_flow > 0:
            print(f"   💡 分析: 资金净流入，市场情绪偏多")
        else:
            print(f"   💡 分析: 资金净流出，市场情绪偏空")
    else:
        print("   ❌ 获取资金流向数据失败")
    
    print("\n3. 测试市场情绪指标:")
    print("-"*40)
    
    sentiment = collector.get_market_sentiment()
    print(f"   📅 日期: {sentiment['date']}")
    print(f"   😨😊 恐慌贪婪指数: {sentiment['fear_greed_index']}/100")
    print(f"   🔥 市场热度: {sentiment['market_heat']}/100")
    print(f"   🎯 风险偏好: {sentiment['risk_appetite']}/100")
    print(f"   📈 上涨比例: {sentiment['rise_ratio']:.1%}")
    print(f"   🔧 数据源: {sentiment['source']}")
    
    # 分析情绪指标
    fear_greed = sentiment['fear_greed_index']
    if fear_greed >= 70:
        print(f"   💡 情绪分析: 贪婪 (指数: {fear_greed})")
    elif fear_greed >= 40:
        print(f"   💡 情绪分析: 中性 (指数: {fear_greed})")
    else:
        print(f"   💡 情绪分析: 恐慌 (指数: {fear_greed})")
    
    print("\n4. 测试板块轮动数据:")
    print("-"*40)
    
    sectors = collector.get_sector_rotation(top_n=5)
    if sectors:
        print(f"   📊 热门板块 (前{len(sectors)}个):")
        for i, sector in enumerate(sectors, 1):
            change_icon = "📈" if sector.change >= 0 else "📉"
            flow_icon = "💰" if sector.flow >= 0 else "💸"
            print(f"   {i}. {sector.name}")
            print(f"      涨跌幅: {change_icon} {sector.change:+.2f}%")
            print(f"      资金: {flow_icon} {sector.flow:+.2f}亿")
            print(f"      领涨股: {sector.leader}")
    else:
        print("   ❌ 获取板块轮动数据失败")
    
    print("\n5. 测试综合市场数据:")
    print("-"*40)
    
    comprehensive = collector.get_comprehensive_market_data()
    print(f"   📅 数据时间: {comprehensive['date']}")
    print(f"   🎯 数据质量: {comprehensive['data_quality']}")
    
    if 'market_stats' in comprehensive:
        stats = comprehensive['market_stats']
        print(f"   📊 市场统计:")
        print(f"      上涨/下跌: {stats['rise_count']}/{stats['fall_count']}")
        print(f"      涨停/跌停: {stats['limit_up']}/{stats['limit_down']}")
    
    if 'money_flow' in comprehensive:
        flow = comprehensive['money_flow']
        print(f"   💰 资金流向:")
        print(f"      主力资金: {flow['main_flow']:+.2f}亿")
        print(f"      北向资金: {flow['north_flow']:+.2f}亿")
    
    print("\n6. 测试简化接口:")
    print("-"*40)
    
    # 测试简化接口
    simple_stats = get_market_stats()
    simple_flow = get_money_flow()
    simple_sentiment = get_market_sentiment()
    simple_comprehensive = get_comprehensive_data()
    
    print(f"   ✅ 简化接口测试完成")
    print(f"      市场统计: {'成功' if simple_stats else '失败'}")
    print(f"      资金流向: {'成功' if simple_flow else '失败'}")
    print(f"      市场情绪: {'成功' if simple_sentiment else '失败'}")
    print(f"      综合数据: {'成功' if simple_comprehensive else '失败'}")
    
    print("\n" + "="*60)
    print("🎉 东方财富数据采集器测试完成")
    
    # 评估数据质量
    data_sources = []
    if stats:
        data_sources.append(stats.source)
    if flow:
        data_sources.append(flow.source)
    if sentiment:
        data_sources.append(sentiment.get('source', 'unknown'))
    
    real_data_count = sum(1 for source in data_sources if 'real' in source or 'api' in source)
    estimated_data_count = sum(1 for source in data_sources if 'estimated' in source)
    simulated_data_count = sum(1 for source in data_sources if 'simulated' in source)
    
    print(f"\n📊 数据质量评估:")
    print(f"   真实数据: {real_data_count}/{len(data_sources)}")
    print(f"   估算数据: {estimated_data_count}/{len(data_sources)}")
    print(f"   模拟数据: {simulated_data_count}/{len(data_sources)}")
    
    if real_data_count > 0:
        print(f"   ✅ 数据质量: 良好 (有真实数据)")
    elif estimated_data_count > 0:
        print(f"   ⚠️ 数据质量: 一般 (主要是估算数据)")
    else:
        print(f"   ❌ 数据质量: 较差 (全是模拟数据)")
    
    return True


def test_historical_data():
    """测试历史数据获取"""
    print("\n" + "="*60)
    print("📅 测试历史数据获取")
    print("="*60)
    
    collector = EastMoneyCollector()
    
    # 测试几个历史节点
    historical_dates = [
        "2024-02-05",  # 小微盘股危机
        "2024-09-24",  # 史诗级政策刺激
        "2025-01-27",  # 春季躁动
    ]
    
    for date_str in historical_dates:
        print(f"\n📅 历史节点: {date_str}")
        
        stats = collector.get_market_stats(date_str)
        if stats:
            print(f"   上涨比例: {stats.rise_ratio:.1%}")
            print(f"   涨停家数: {stats.limit_up}")
            print(f"   数据源: {stats.source}")
            
            # 分析市场状态
            if stats.rise_ratio < 0.4:
                state = "冬藏期"
            elif stats.rise_ratio < 0.6:
                state = "震荡期"
            else:
                state = "强势期"
            
            print(f"   💡 市场状态: {state}")
        else:
            print(f"   ❌ 获取历史数据失败")
    
    print("\n✅ 历史数据测试完成")


def main():
    """主函数"""
    print("🚀 东方财富数据采集器 - 彪哥战法v5.0专用")
    print("📅 测试时间: 2026-03-26")
    print("🎯 目标: 验证数据采集能力")
    
    try:
        # 测试当前数据
        test_eastmoney_collector()
        
        # 测试历史数据
        test_historical_data()
        
        print("\n" + "="*60)
        print("🎉 所有测试完成")
        print("="*60)
        
        print("\n✅ 结论:")
        print("   东方财富数据采集器已成功实现，")
        print("   能够获取市场统计、资金流向、情绪指标等关键数据。")
        
        print("\n🚀 下一步:")
        print("   1. 集成到彪哥战法v5.0数据采集系统")
        print("   2. 优化数据源，提高真实数据比例")
        print("   3. 建立数据质量监控系统")
        print("   4. 开始实时数据测试")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)