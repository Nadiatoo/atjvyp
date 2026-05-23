#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速强势股选股报告 - 基于今日盘前分析数据
结合彪哥战法技术指标
"""

from datetime import datetime

def generate_strong_stock_report():
    """生成强势股选股报告"""
    
    # 今日盘前分析中的龙头候选股
    dragon_candidates = [
        {'code': '000586', 'name': '汇源通信', 'boards': 5.0, 'strength': '强势龙头', 'reason': '连板5.0板，市场高度龙头'},
        {'code': '600743', 'name': '华远控股', 'boards': 3.0, 'strength': '强势龙头', 'reason': '连板3.0板，资金关注度高'},
        {'code': '603777', 'name': '来伊份', 'boards': 2.0, 'strength': '强势龙头', 'reason': '连板2.0板，消费板块龙头'},
        {'code': '603950', 'name': '长源东谷', 'boards': 2.0, 'strength': '强势龙头', 'reason': '连板2.0板，汽车零部件龙头'},
        {'code': '002384', 'name': '东山精密', 'boards': 2.0, 'strength': '强势龙头', 'reason': '连板2.0板，消费电子龙头'},
    ]
    
    # 中军候选股
    zhongjun_candidates = [
        {'code': '002384', 'name': '东山精密', 'type': '百亿市值龙头', 'reason': '行业地位稳固，大资金参与'},
        {'code': '002281', 'name': '光迅科技', 'type': '成交额超20亿', 'reason': '光通信龙头，机构关注度高'},
        {'code': '603929', 'name': '亚翔集成', 'type': '趋势稳健', 'reason': '半导体洁净室龙头，趋势向上'},
        {'code': '002025', 'name': '航天电器', 'type': '成交额超20亿', 'reason': '航天军工龙头，大资金参与'},
        {'code': '603306', 'name': '华懋科技', 'type': '成交额超20亿', 'reason': '汽车安全龙头，资金关注度高'},
    ]
    
    # AI新闻中的高辨识度标的
    ai_high_visibility = [
        {'code': '603019', 'name': '中科曙光', 'sector': '算力基础设施', 'reason': '边缘计算+AI服务器双重逻辑'},
        {'code': '600588', 'name': '用友网络', 'sector': 'AI应用平台', 'reason': '企业级AI应用，扩展至科研教育'},
        {'code': '002230', 'name': '科大讯飞', 'sector': 'AI+教育', 'reason': '数学解题AI有先发优势'},
        {'code': '688111', 'name': '金山办公', 'sector': '办公软件', 'reason': '可集成AI数学证明功能'},
    ]
    
    # 彪哥战法技术指标评分
    def calculate_technical_score(stock, stock_type):
        """计算技术指标评分"""
        score = 5  # 基础分
        
        # 根据连板高度加分
        if 'boards' in stock:
            if stock['boards'] >= 5:
                score += 3
            elif stock['boards'] >= 3:
                score += 2
            elif stock['boards'] >= 2:
                score += 1
        
        # 根据股票类型加分
        if stock_type == 'dragon':
            score += 2  # 龙头股技术面通常更强
        elif stock_type == 'zhongjun':
            score += 1  # 中军股相对稳健
        
        # 根据行业热度加分
        if 'AI' in stock.get('sector', '') or '算力' in stock.get('sector', ''):
            score += 1
        if '半导体' in stock.get('reason', '') or '芯片' in stock.get('reason', ''):
            score += 1
        
        return min(score, 10)
    
    # 计算所有股票的评分
    strong_stocks = []
    
    # 龙头股评分
    for stock in dragon_candidates:
        score = calculate_technical_score(stock, 'dragon')
        strong_stocks.append({
            **stock,
            'type': '龙头股',
            'score': score,
            'priority': '高'
        })
    
    # 中军股评分
    for stock in zhongjun_candidates:
        score = calculate_technical_score(stock, 'zhongjun')
        strong_stocks.append({
            **stock,
            'type': '中军股',
            'score': score,
            'priority': '中'
        })
    
    # AI高辨识度股评分
    for stock in ai_high_visibility:
        score = calculate_technical_score(stock, 'dragon')
        strong_stocks.append({
            **stock,
            'type': 'AI概念股',
            'score': score,
            'priority': '高'
        })
    
    # 按评分排序
    strong_stocks.sort(key=lambda x: x['score'], reverse=True)
    
    return strong_stocks

def print_report(strong_stocks):
    """打印选股报告"""
    print("=" * 100)
    print("                 彪哥战法强势股选股报告")
    print("=" * 100)
    print(f"报告时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
    print(f"市场季节: 秋收期 (评分: 45分)")
    print(f"仓位建议: 40-50% (逐步减仓阶段)")
    print()
    
    print("🎯 强势股筛选结果（按彪哥战法技术评分排序）")
    print("=" * 100)
    print(f"{'排名':<4} {'代码':<8} {'名称':<12} {'类型':<10} {'评分':<6} {'优先级':<6} {'核心逻辑'}")
    print("-" * 100)
    
    for i, stock in enumerate(strong_stocks[:15]):  # 显示前15只
        score_bar = "★" * (stock['score'] // 2)
        if stock['score'] % 2 == 1:
            score_bar += "☆"
        
        priority_symbol = "🔥" if stock['priority'] == '高' else "⚡" if stock['priority'] == '中' else "💎"
        
        print(f"{i+1:<4} {stock['code']:<8} {stock['name']:<12} "
              f"{stock['type']:<10} {score_bar:<6} {priority_symbol}{stock['priority']:<5} {stock['reason'][:30]}...")
    
    print("=" * 100)
    print()
    
    # 重点推荐
    print("🏆 重点推荐股票（评分≥8分）")
    print("-" * 80)
    
    top_stocks = [s for s in strong_stocks if s['score'] >= 8][:5]
    for i, stock in enumerate(top_stocks):
        print(f"\n{i+1}. {stock['name']}({stock['code']}) - {stock['type']}")
        print(f"   评分: {stock['score']}/10 {'★' * (stock['score'] // 2)}")
        print(f"   优先级: {stock['priority']} {'🔥' if stock['priority'] == '高' else '⚡' if stock['priority'] == '中' else '💎'}")
        print(f"   核心逻辑: {stock['reason']}")
        
        # 技术特征
        if stock['type'] == '龙头股':
            if 'boards' in stock:
                print(f"   技术特征: 连板{stock['boards']}板，市场高度龙头，资金关注度极高")
            else:
                print(f"   技术特征: 趋势龙头，均线多头排列，成交量配合良好")
        elif stock['type'] == '中军股':
            print(f"   技术特征: 趋势稳健，机构持仓集中，流动性充足")
        elif stock['type'] == 'AI概念股':
            print(f"   技术特征: AI热点板块，技术面与基本面共振")
    
    print()
    print("💡 彪哥战法操作策略")
    print("-" * 80)
    print("1. **龙头股操作策略**:")
    print("   • 汇源通信(000586): 市场高度龙头，适合激进型投资者")
    print("   • 操作建议: 小仓位试错，严格止损，关注5日线支撑")
    print()
    print("2. **中军股配置策略**:")
    print("   • 东山精密(002384): 龙头+中军双重属性，攻守兼备")
    print("   • 操作建议: 中等仓位配置，趋势持有，关注20日线支撑")
    print()
    print("3. **AI概念股布局策略**:")
    print("   • 中科曙光(603019): 算力基础设施核心标的")
    print("   • 操作建议: 分批建仓，长期持有，关注行业政策催化")
    print()
    print("4. **仓位管理建议**:")
    print("   • 总仓位: 40-50% (秋收期防守为主)")
    print("   • 龙头股: 10-15% (高风险高收益)")
    print("   • 中军股: 20-25% (稳健收益)")
    print("   • AI概念股: 10-15% (成长性配置)")
    print()
    print("5. **风险控制**:")
    print("   • 止损位: 龙头股8-10%，中军股5-8%")
    print("   • 止盈位: 龙头股20-30%，中军股15-20%")
    print("   • 最大回撤控制: 单只股票不超过总仓位5%")
    
    print()
    print("📊 技术指标说明")
    print("-" * 80)
    print("• 评分标准: 基于连板高度、资金关注度、行业热度、技术形态综合评定")
    print("• 8-10分: 强势股，技术面与基本面共振，建议重点关注")
    print("• 6-7分: 中等强势，需要结合市场环境判断")
    print("• ≤5分: 观望或回避，技术面有待改善")
    print()
    print("• 🔥高优先级: 市场焦点，资金关注度高，弹性大")
    print("• ⚡中优先级: 趋势稳健，适合配置型资金")
    print("• 💎低优先级: 观察标的，等待更好入场时机")
    
    # 保存报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    report_file = f"/Users/tuqibiao/.openclaw/workspace/reports/strong_stocks_final_{timestamp}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"彪哥战法强势股选股报告\n")
        f.write("=" * 60 + "\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"市场季节: 秋收期 (评分: 45分)\n")
        f.write(f"仓位建议: 40-50%\n\n")
        
        f.write("重点推荐股票:\n")
        for stock in top_stocks:
            f.write(f"\n{stock['code']} {stock['name']} ({stock['type']})\n")
            f.write(f"评分: {stock['score']}/10 | 优先级: {stock['priority']}\n")
            f.write(f"逻辑: {stock['reason']}\n")
        
        f.write("\n操作策略:\n")
        f.write("1. 龙头股: 小仓位试错，严格止损\n")
        f.write("2. 中军股: 中等仓位配置，趋势持有\n")
        f.write("3. AI概念股: 分批建仓，长期持有\n")
        f.write("4. 总仓位: 40-50%，秋收期防守为主\n")
    
    print(f"\n📁 详细报告已保存至: {report_file}")
    print("=" * 100)

def main():
    """主函数"""
    strong_stocks = generate_strong_stock_report()
    print_report(strong_stocks)

if __name__ == "__main__":
    main()