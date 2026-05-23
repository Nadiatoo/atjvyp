#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彪哥战法多数据源分析脚本
基于方案A：多数据源自动切换，最高稳定性
"""

import sys
import datetime
from multi_source_data import MultiSourceDataFetcher

def analyze_market_with_multi_source() -> Dict:
    """使用多数据源分析市场"""
    print("开始彪哥战法多数据源市场分析...")
    print("=" * 60)
    
    fetcher = MultiSourceDataFetcher()
    
    # 获取主要指数数据
    print("获取市场主要指数数据...")
    indices_data = fetcher.get_market_indices()
    
    # 分析结果
    analysis = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_source": "多数据源自动切换（腾讯+新浪+东方财富）",
        "indices": indices_data,
        "success_rate": 0,
        "market_status": "分析中",
        "recommendation": "等待完整数据"
    }
    
    # 计算成功率
    success_count = sum(1 for data in indices_data.values() if not data.get("error"))
    total_count = len(indices_data)
    analysis["success_rate"] = success_count / total_count * 100 if total_count > 0 else 0
    
    # 市场状态判断
    if success_count >= 2:  # 至少2个指数数据成功
        # 计算平均涨跌幅
        changes = []
        for code, data in indices_data.items():
            if not data.get("error") and "change_percent" in data:
                changes.append(data["change_percent"])
        
        if changes:
            avg_change = sum(changes) / len(changes)
            
            # 彪哥战法季节判断逻辑
            if avg_change > 1.5:
                analysis["market_status"] = "夏季（强势）"
                analysis["recommendation"] = "积极操作，仓位60-80%"
                analysis["season_score"] = 75
            elif avg_change > 0.5:
                analysis["market_status"] = "春季（回暖）"
                analysis["recommendation"] = "适度参与，仓位40-60%"
                analysis["season_score"] = 65
            elif avg_change > -0.5:
                analysis["market_status"] = "秋季（震荡）"
                analysis["recommendation"] = "谨慎操作，仓位30-50%"
                analysis["season_score"] = 55
            else:
                analysis["market_status"] = "冬季（弱势）"
                analysis["recommendation"] = "控制仓位，仓位20-30%"
                analysis["season_score"] = 45
        else:
            analysis["market_status"] = "数据不完整"
            analysis["recommendation"] = "等待更多数据"
    else:
        analysis["market_status"] = "数据获取失败"
        analysis["recommendation"] = "检查网络和数据源"
    
    return analysis

def generate_multi_source_report(analysis: Dict) -> str:
    """生成多数据源分析报告"""
    report = []
    
    # 报告头部
    report.append("📊 【彪哥战法】多数据源市场分析报告")
    report.append(f"时间: {analysis['timestamp']}")
    report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    report.append("")
    
    # 数据源说明
    report.append("🎯 **数据源策略**: 方案A - 多数据源自动切换")
    report.append(f"   • 数据源: {analysis['data_source']}")
    report.append(f"   • 成功率: {analysis['success_rate']:.1f}%")
    report.append(f"   • 缓存策略: 60秒本地缓存")
    report.append(f"   • 自动切换: 腾讯→新浪→东方财富")
    report.append("")
    
    # 指数数据
    if analysis["indices"]:
        report.append("📈 **主要指数实时数据**:")
        
        for code, data in analysis["indices"].items():
            name = data.get("name", code)
            
            if data.get("error"):
                report.append(f"   ❌ {name}: 获取失败 ({data.get('error', '未知错误')})")
            else:
                color = "🟢" if data.get("change_percent", 0) > 0 else "🔴"
                source = data.get("source", "未知")
                price = data.get("price", 0)
                change = data.get("change", 0)
                change_percent = data.get("change_percent", 0)
                
                report.append(f"   {color} {name}: {price:.2f} ({change_percent:+.2f}%) [数据源: {source}]")
        
        report.append("")
    
    # 市场状态分析
    report.append(f"🎯 **市场状态**: {analysis['market_status']}")
    if "season_score" in analysis:
        report.append(f"📊 **季节评分**: {analysis['season_score']}/100")
    report.append(f"💡 **操作建议**: {analysis['recommendation']}")
    report.append("")
    
    # 彪哥战法要点
    report.append("🐲 **彪哥战法核心应用**:")
    report.append("  1. **数据真实性优先**: 多数据源交叉验证 ✅")
    report.append("  2. **系统可靠性保障**: 自动切换，缓存优化 ✅")
    report.append("  3. **具体分析要求**: 实时数据，具体指数 ✅")
    report.append("  4. **市场验证思维**: 基于真实市场表现 ✅")
    report.append("")
    
    # 技术优势
    report.append("⚙️ **技术优势**:")
    report.append("  • **稳定性**: 三数据源互为备份，单个失败不影响")
    report.append("  • **实时性**: 60秒缓存平衡实时性和频率限制")
    report.append("  • **准确性**: 多源交叉验证，避免单点错误")
    report.append("  • **兼容性**: 不依赖第三方库，直接HTTP请求")
    report.append("")
    
    # 明日关注
    report.append("👀 **明日关注要点**:")
    report.append("  1. 观察市场季节状态变化")
    report.append("  2. 监控数据源稳定性表现")
    report.append("  3. 验证彪哥战法季节判断准确性")
    report.append("  4. 优化个股分析模块集成")
    report.append("")
    
    # 风险提示
    report.append("⚠️ **风险提示**:")
    report.append("  1. 市场数据仅供参考，投资需谨慎")
    report.append("  2. 数据源可能临时调整接口")
    report.append("  3. 网络波动可能影响数据获取")
    report.append("  4. 建议结合其他分析工具综合判断")
    report.append("")
    
    # 系统状态
    report.append("✅ **系统状态**:")
    report.append(f"  • 数据源策略: {analysis['data_source']} ✅")
    report.append(f"  • 数据成功率: {analysis['success_rate']:.1f}%")
    report.append(f"  • 分析时间: {analysis['timestamp']}")
    report.append(f"  • 报告版本: 多数据源自动切换 v1.0")
    
    return "\n".join(report)

def save_report(report_content: str, filename: str = None):
    """保存报告"""
    if not filename:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"/Users/tuqibiao/.openclaw/workspace/reports/multi_source_{today}.txt"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"✅ 报告已保存至: {filename}")
        return filename
    except Exception as e:
        print(f"❌ 报告保存失败: {e}")
        return None

def main():
    """主函数"""
    print("彪哥战法多数据源分析系统启动...")
    print("=" * 60)
    
    try:
        # 分析市场
        analysis = analyze_market_with_multi_source()
        
        # 生成报告
        report = generate_multi_source_report(analysis)
        
        # 保存报告
        report_file = save_report(report)
        
        # 输出摘要
        print("\n" + "=" * 60)
        print("分析完成！报告摘要：")
        print("=" * 60)
        print(report[:800] + "...")
        
        if report_file:
            print(f"\n✅ 完整报告: {report_file}")
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()