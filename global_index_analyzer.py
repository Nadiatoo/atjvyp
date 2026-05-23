#!/usr/bin/env python3
"""
全球指数与板块分析系统
专门分析对A股有影响的港美股指数和板块
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta

class GlobalIndexAnalyzer:
    """全球指数与板块分析器"""
    
    def __init__(self):
        self.today = datetime.now()
        self.date_str = self.today.strftime("%Y-%m-%d")
        
        # 关键港美股指数（影响A股）
        self.key_indices = {
            # 港股指数
            'HSI': {'name': '恒生指数', 'symbol': '^HSI', 'impact': 'A股大盘情绪'},
            'HSTECH': {'name': '恒生科技指数', 'symbol': '^HSTECH', 'impact': 'A股科技板块'},
            
            # 美股指数
            'NDX': {'name': '纳斯达克100', 'symbol': '^NDX', 'impact': 'A股科技成长股'},
            'SPX': {'name': '标普500', 'symbol': '^GSPC', 'impact': 'A股大盘蓝筹'},
            'DJI': {'name': '道琼斯工业', 'symbol': '^DJI', 'impact': 'A股传统行业'},
            
            # 重要板块ETF
            'SOXX': {'name': '半导体板块', 'symbol': 'SOXX', 'impact': 'A股半导体/芯片'},
            'KARS': {'name': '新能源车板块', 'symbol': 'KARS', 'impact': 'A股新能源汽车'},
            'XBI': {'name': '生物科技板块', 'symbol': 'XBI', 'impact': 'A股医药生物'},
            'SKYY': {'name': '云计算板块', 'symbol': 'SKYY', 'impact': 'A股云计算/软件'},
            'ARKK': {'name': '创新科技板块', 'symbol': 'ARKK', 'impact': 'A股创新科技'},
        }
    
    def fetch_yahoo_data(self, symbol):
        """从Yahoo Finance获取数据（模拟）"""
        # 这里可以集成真实的Yahoo Finance API
        # 暂时返回模拟数据
        
        模拟数据 = {
            '^HSI': {'price': 16500.45, 'change': 125.67, 'change_pct': 0.77},
            '^HSTECH': {'price': 3450.23, 'change': 45.89, 'change_pct': 1.35},
            '^NDX': {'price': 18500.78, 'change': 156.34, 'change_pct': 0.85},
            '^GSPC': {'price': 5250.12, 'change': 23.45, 'change_pct': 0.45},
            '^DJI': {'price': 39850.67, 'change': 89.12, 'change_pct': 0.22},
            'SOXX': {'price': 645.89, 'change': 8.76, 'change_pct': 1.37},
            'KARS': {'price': 45.67, 'change': 1.23, 'change_pct': 2.77},
            'XBI': {'price': 89.45, 'change': -0.56, 'change_pct': -0.62},
            'SKYY': {'price': 112.34, 'change': 2.45, 'change_pct': 2.23},
            'ARKK': {'price': 56.78, 'change': 1.89, 'change_pct': 3.44},
        }
        
        return 模拟数据.get(symbol, {'price': 0, 'change': 0, 'change_pct': 0})
    
    def analyze_index_impact(self, symbol, data):
        """分析指数对A股的影响"""
        name = self.key_indices[symbol]['name']
        impact = self.key_indices[symbol]['impact']
        change_pct = data['change_pct']
        
        if change_pct > 2.0:
            level = "🔥 强烈正面"
            suggestion = f"预计对{impact}有显著正面影响"
        elif change_pct > 0.5:
            level = "📈 正面"
            suggestion = f"预计对{impact}有正面影响"
        elif change_pct > -0.5:
            level = "➡️ 中性"
            suggestion = f"对{impact}影响有限"
        elif change_pct > -2.0:
            level = "📉 负面"
            suggestion = f"预计对{impact}有负面影响"
        else:
            level = "💥 强烈负面"
            suggestion = f"预计对{impact}有显著负面影响"
        
        return level, suggestion
    
    def analyze_sector_trend(self, sector_data):
        """分析板块趋势对A股的影响"""
        # 分析各板块表现
        sectors = {
            '半导体': sector_data.get('SOXX', {}).get('change_pct', 0),
            '新能源车': sector_data.get('KARS', {}).get('change_pct', 0),
            '生物科技': sector_data.get('XBI', {}).get('change_pct', 0),
            '云计算': sector_data.get('SKYY', {}).get('change_pct', 0),
            '创新科技': sector_data.get('ARKK', {}).get('change_pct', 0),
        }
        
        # 找出强势和弱势板块
        sorted_sectors = sorted(sectors.items(), key=lambda x: x[1], reverse=True)
        
        strong_sectors = [s for s in sorted_sectors[:2] if s[1] > 1.0]
        weak_sectors = [s for s in sorted_sectors[-2:] if s[1] < -0.5]
        
        return strong_sectors, weak_sectors
    
    def generate_global_outlook(self, index_data):
        """生成全球市场展望"""
        # 分析主要指数表现
        hsi_change = index_data.get('^HSI', {}).get('change_pct', 0)
        ndx_change = index_data.get('^NDX', {}).get('change_pct', 0)
        spx_change = index_data.get('^GSPC', {}).get('change_pct', 0)
        
        avg_change = (hsi_change + ndx_change + spx_change) / 3
        
        if avg_change > 1.5:
            outlook = "🔥 全球市场情绪积极"
            a股影响 = "预计对A股开盘有正面提振"
        elif avg_change > 0.3:
            outlook = "📈 全球市场偏暖"
            a股影响 = "对A股开盘影响偏正面"
        elif avg_change > -0.3:
            outlook = "➡️ 全球市场平稳"
            a股影响 = "对A股开盘影响有限"
        elif avg_change > -1.5:
            outlook = "📉 全球市场偏弱"
            a股影响 = "对A股开盘有一定压力"
        else:
            outlook = "💥 全球市场情绪谨慎"
            a股影响 = "预计对A股开盘有负面影响"
        
        return outlook, a股影响
    
    def generate_report(self):
        """生成分析报告"""
        print(f"🌍 全球指数与板块分析 - {self.date_str}")
        print("=" * 60)
        
        # 1. 获取数据
        print("\n1. 📊 关键指数表现（对A股有影响）")
        index_data = {}
        for symbol, info in self.key_indices.items():
            data = self.fetch_yahoo_data(info['symbol'])
            index_data[info['symbol']] = data
            
            level, suggestion = self.analyze_index_impact(symbol, data)
            
            arrow = "📈" if data['change_pct'] > 0 else "📉" if data['change_pct'] < 0 else "➡️"
            print(f"   {arrow} {info['name']}: {data['price']:.2f} ({data['change']:+.2f}, {data['change_pct']:+.2f}%)")
            print(f"     影响: {info['impact']}")
            print(f"     评级: {level}")
            print(f"     建议: {suggestion}\n")
        
        # 2. 板块趋势分析
        print("\n2. 🏭 板块趋势分析（对A股板块影响）")
        strong_sectors, weak_sectors = self.analyze_sector_trend(index_data)
        
        if strong_sectors:
            print("   🔥 强势板块（可能带动A股对应板块）:")
            for sector, change in strong_sectors:
                print(f"      {sector}: {change:+.2f}%")
        
        if weak_sectors:
            print("\n   📉 弱势板块（可能压制A股对应板块）:")
            for sector, change in weak_sectors:
                print(f"      {sector}: {change:+.2f}%")
        
        # 3. 全球市场展望
        print("\n3. 🌐 全球市场展望")
        outlook, a股影响 = self.generate_global_outlook(index_data)
        print(f"   整体判断: {outlook}")
        print(f"   对A股影响: {a股影响}")
        
        # 4. A股策略建议
        print("\n4. 🎯 对A股的策略建议")
        suggestions = self.generate_a股_suggestions(index_data)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
        
        # 5. 技术突破监控提醒
        print("\n5. 🔍 技术突破监控提醒")
        print("   通过鹰眼系统监控以下方向:")
        print("   - 半导体芯片制程突破")
        print("   - 新能源电池技术革新")
        print("   - AI算法重大进展")
        print("   - 生物医药技术突破")
        print("   - 产业政策重大变化")
        
        # 保存报告
        self.save_report(index_data, strong_sectors, weak_sectors, outlook, a股影响, suggestions)
        
        return True
    
    def generate_a股_suggestions(self, index_data):
        """生成对A股的策略建议"""
        suggestions = []
        
        # 分析半导体板块
        soxx_change = index_data.get('SOXX', {}).get('change_pct', 0)
        if soxx_change > 2.0:
            suggestions.append("关注A股半导体/芯片板块，港美股半导体强势可能传导")
        elif soxx_change < -1.0:
            suggestions.append("谨慎对待A股半导体板块，注意港美股调整风险")
        
        # 分析新能源车板块
        kars_change = index_data.get('KARS', {}).get('change_pct', 0)
        if kars_change > 2.0:
            suggestions.append("关注A股新能源汽车产业链，全球新能源车趋势向好")
        
        # 分析科技指数
        ndx_change = index_data.get('^NDX', {}).get('change_pct', 0)
        hstech_change = index_data.get('^HSTECH', {}).get('change_pct', 0)
        if ndx_change > 1.0 and hstech_change > 1.0:
            suggestions.append("全球科技股表现强势，关注A股科技成长股机会")
        
        # 分析整体市场情绪
        hsi_change = index_data.get('^HSI', {}).get('change_pct', 0)
        spx_change = index_data.get('^GSPC', {}).get('change_pct', 0)
        avg_global = (hsi_change + ndx_change + spx_change) / 3
        
        if avg_global > 1.0:
            suggestions.append("全球市场情绪积极，可适当提高A股仓位")
        elif avg_global < -0.5:
            suggestions.append("全球市场偏弱，控制A股仓位，注意风险")
        
        # 通用建议
        suggestions.append("结合A股自身技术面和资金面，制定具体操作策略")
        suggestions.append("关注北向资金流向，验证全球资金对A股态度")
        
        return suggestions[:6]  # 最多6条建议
    
    def save_report(self, index_data, strong_sectors, weak_sectors, outlook, a股影响, suggestions):
        """保存报告"""
        report_dir = "/Users/tuqibiao/.openclaw/workspace/reports"
        os.makedirs(report_dir, exist_ok=True)
        
        report_path = os.path.join(report_dir, f"global_index_analysis_{self.date_str}.txt")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"全球指数与板块分析报告 - {self.date_str}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("📊 关键指数表现:\n")
            for symbol, info in self.key_indices.items():
                data = index_data.get(info['symbol'], {})
                level, suggestion = self.analyze_index_impact(symbol, data)
                
                f.write(f"  {info['name']}: {data.get('price', 0):.2f} ({data.get('change', 0):+.2f}, {data.get('change_pct', 0):+.2f}%)\n")
                f.write(f"    影响: {info['impact']}\n")
                f.write(f"    评级: {level}\n")
                f.write(f"    建议: {suggestion}\n\n")
            
            f.write("🏭 板块趋势分析:\n")
            if strong_sectors:
                f.write("  强势板块:\n")
                for sector, change in strong_sectors:
                    f.write(f"    {sector}: {change:+.2f}%\n")
            
            if weak_sectors:
                f.write("\n  弱势板块:\n")
                for sector, change in weak_sectors:
                    f.write(f"    {sector}: {change:+.2f}%\n")
            
            f.write(f"\n🌐 全球市场展望:\n")
            f.write(f"  整体判断: {outlook}\n")
            f.write(f"  对A股影响: {a股影响}\n")
            
            f.write(f"\n🎯 对A股的策略建议:\n")
            for i, suggestion in enumerate(suggestions, 1):
                f.write(f"  {i}. {suggestion}\n")
            
            f.write(f"\n🔍 技术突破监控方向:\n")
            f.write(f"  - 半导体芯片制程突破\n")
            f.write(f"  - 新能源电池技术革新\n")
            f.write(f"  - AI算法重大进展\n")
            f.write(f"  - 生物医药技术突破\n")
            f.write(f"  - 产业政策重大变化\n")
        
        print(f"\n📁 报告已保存至: {report_path}")

def main():
    """主函数"""
    analyzer = GlobalIndexAnalyzer()
    analyzer.generate_report()

if __name__ == "__main__":
    main()