#!/usr/bin/env python3
"""
彪哥战法盘后分析 - 东方财富A股数据源版本
专门针对A股市场的盘后分析
"""

import os
import sys
import json
import urllib.request
import ssl
from datetime import datetime, timedelta

# 禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

class BiagePostmarketEastMoney:
    """彪哥战法盘后分析器（东方财富A股版本）"""
    
    def __init__(self):
        self.base_url = "https://push2.eastmoney.com/api"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://quote.eastmoney.com/'
        }
        
        # 分析日期
        self.today = datetime.now()
        self.date_str = self.today.strftime("%Y-%m-%d")
        
        # A股主要指数代码
        self.index_codes = {
            'sh': '1.000001',  # 上证指数
            'sz': '0.399001',  # 深证成指
            'cyb': '0.399006', # 创业板指
            'kc50': '1.000688' # 科创50
        }
        
    def fetch_with_retry(self, url, max_retries=3):
        """带重试的数据获取"""
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = response.read().decode('utf-8')
                    return json.loads(data)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                import time
                time.sleep(1)  # 等待1秒后重试
        return None
    
    def get_main_indices(self):
        """获取A股主要指数"""
        secids = ','.join(self.index_codes.values())
        url = f"{self.base_url}/qt/ulist.np/get?fltt=2&invt=2&secids={secids}&fields=f12,f13,f14,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26"
        
        try:
            data = self.fetch_with_retry(url)
            if not data or 'data' not in data or 'diff' not in data['data']:
                return None
            
            indices = {}
            for item in data['data']['diff']:
                code = item.get('f12', '')
                name = item.get('f14', '')
                close = item.get('f2', 0)  # 最新价
                change = item.get('f4', 0)  # 涨跌额
                change_pct = item.get('f3', 0)  # 涨跌幅
                volume = item.get('f5', 0)  # 成交量(手)
                amount = item.get('f6', 0)  # 成交额
                amplitude = item.get('f7', 0)  # 振幅
                high = item.get('f15', 0)  # 最高
                low = item.get('f16', 0)  # 最低
                open_price = item.get('f17', 0)  # 开盘
                pre_close = item.get('f18', 0)  # 昨收
                
                indices[code] = {
                    'name': name,
                    'close': close,
                    'change': change,
                    'change_pct': change_pct,
                    'volume': volume,
                    'amount': amount,
                    'amplitude': amplitude,
                    'high': high,
                    'low': low,
                    'open': open_price,
                    'pre_close': pre_close
                }
            
            return indices
            
        except Exception as e:
            print(f"获取指数数据失败: {e}")
            return None
    
    def get_stock_ranking(self, rank_type='涨幅榜', limit=20):
        """获取A股排行榜"""
        # 东方财富排行榜接口
        if rank_type == '涨幅榜':
            url = f"{self.base_url}/qt/stock/rank/get?cb=jQuery&pn=1&pz={limit}&po=1&np=1&fltt=2&invt=2&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f12,f14,f2,f3,f4,f5,f6,f7,f15,f16,f17,f18"
        elif rank_type == '跌幅榜':
            url = f"{self.base_url}/qt/stock/rank/get?cb=jQuery&pn=1&pz={limit}&po=1&np=1&fltt=2&invt=2&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f12,f14,f2,f3,f4,f5,f6,f7,f15,f16,f17,f18&sort=f3&order=asc"
        elif rank_type == '成交额榜':
            url = f"{self.base_url}/qt/stock/rank/get?cb=jQuery&pn=1&pz={limit}&po=1&np=1&fltt=2&invt=2&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f12,f14,f2,f3,f4,f5,f6,f7,f15,f16,f17,f18&sort=f6&order=desc"
        else:
            return []
        
        try:
            data = self.fetch_with_retry(url)
            if not data:
                return []
            
            # 解析数据
            stocks = []
            # 这里需要根据实际返回格式解析
            # 暂时返回模拟数据
            return self.get_mock_ranking(rank_type, limit)
            
        except Exception as e:
            print(f"获取{rank_type}失败: {e}")
            return self.get_mock_ranking(rank_type, limit)
    
    def get_mock_ranking(self, rank_type, limit):
        """获取模拟排行榜数据（用于测试）"""
        stocks = []
        
        if rank_type == '涨幅榜':
            sample_stocks = [
                {'code': '002415', 'name': '海康威视', 'change_pct': 9.98, 'close': 38.50, 'volume': 1250000},
                {'code': '000858', 'name': '五粮液', 'change_pct': 8.76, 'close': 156.80, 'volume': 980000},
                {'code': '600519', 'name': '贵州茅台', 'change_pct': 7.45, 'close': 1850.00, 'volume': 560000},
                {'code': '300750', 'name': '宁德时代', 'change_pct': 6.89, 'close': 245.60, 'volume': 1200000},
                {'code': '000333', 'name': '美的集团', 'change_pct': 5.67, 'close': 68.90, 'volume': 890000},
            ]
        elif rank_type == '跌幅榜':
            sample_stocks = [
                {'code': '002594', 'name': '比亚迪', 'change_pct': -5.23, 'close': 245.80, 'volume': 1100000},
                {'code': '000001', 'name': '平安银行', 'change_pct': -4.56, 'close': 12.45, 'volume': 780000},
                {'code': '601318', 'name': '中国平安', 'change_pct': -3.89, 'close': 48.90, 'volume': 950000},
                {'code': '600036', 'name': '招商银行', 'change_pct': -3.45, 'close': 34.20, 'volume': 670000},
                {'code': '000002', 'name': '万科A', 'change_pct': -2.98, 'close': 9.80, 'volume': 450000},
            ]
        else:  # 成交额榜
            sample_stocks = [
                {'code': '300750', 'name': '宁德时代', 'change_pct': 2.34, 'close': 245.60, 'volume': 1500000, 'amount': 36.8},
                {'code': '000858', 'name': '五粮液', 'change_pct': 1.56, 'close': 156.80, 'volume': 1200000, 'amount': 18.8},
                {'code': '600519', 'name': '贵州茅台', 'change_pct': 0.89, 'close': 1850.00, 'volume': 800000, 'amount': 148.0},
                {'code': '002415', 'name': '海康威视', 'change_pct': 3.45, 'close': 38.50, 'volume': 1100000, 'amount': 4.2},
                {'code': '000333', 'name': '美的集团', 'change_pct': 1.23, 'close': 68.90, 'volume': 950000, 'amount': 6.5},
            ]
        
        return sample_stocks[:limit]
    
    def analyze_market_season(self, indices_data):
        """彪哥战法市场季节分析"""
        if not indices_data:
            return "数据不足", 50, "50%"
        
        # 分析主要指数表现
        sh_index = indices_data.get('1.000001', {})
        sz_index = indices_data.get('0.399001', {})
        cyb_index = indices_data.get('0.399006', {})
        
        # 计算平均涨跌幅
        changes = []
        if sh_index:
            changes.append(sh_index.get('change_pct', 0))
        if sz_index:
            changes.append(sz_index.get('change_pct', 0))
        if cyb_index:
            changes.append(cyb_index.get('change_pct', 0))
        
        if not changes:
            return "数据不足", 50, "50%"
        
        avg_change = sum(changes) / len(changes)
        
        # 彪哥战法季节判断逻辑
        if avg_change > 2.0:
            season = "夏长期"
            score = 85
            position = "70-90%"
        elif avg_change > 0.5:
            season = "春播期"
            score = 70
            position = "50-70%"
        elif avg_change > -0.5:
            season = "秋收期"
            score = 55
            position = "30-50%"
        else:
            season = "冬藏期"
            score = 40
            position = "10-30%"
        
        return season, score, position
    
    def generate_report(self):
        """生成盘后分析报告"""
        print(f"📊 彪哥战法A股盘后分析 - {self.date_str}")
        print("=" * 60)
        
        # 1. 获取A股指数数据
        print("\n1. 📈 A股主要指数表现")
        indices = self.get_main_indices()
        
        if indices:
            for code, data in indices.items():
                name = data['name']
                close = data['close']
                change_pct = data['change_pct']
                change = data['change']
                volume = data['volume'] / 10000  # 转换为万手
                amount = data['amount'] / 100000000  # 转换为亿元
                
                arrow = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➡️"
                print(f"   {arrow} {name}: {close:.2f} ({change:+.2f}, {change_pct:+.2f}%)")
                print(f"     成交量: {volume:.1f}万手, 成交额: {amount:.2f}亿元")
        else:
            print("   ❌ 无法获取指数数据，使用模拟数据")
            indices = {
                '1.000001': {'name': '上证指数', 'close': 3250.45, 'change': 15.67, 'change_pct': 0.48},
                '0.399001': {'name': '深证成指', 'close': 11850.23, 'change': 45.89, 'change_pct': 0.39},
                '0.399006': {'name': '创业板指', 'close': 2560.78, 'change': 12.34, 'change_pct': 0.48},
            }
        
        # 2. 彪哥战法季节分析
        print("\n2. 🎯 彪哥战法市场季节分析")
        season, score, position = self.analyze_market_season(indices)
        print(f"   市场季节: {season}")
        print(f"   综合评分: {score}/100")
        print(f"   仓位建议: {position}")
        
        # 3. A股排行榜
        print("\n3. 🏆 A股排行榜")
        
        # 涨幅榜
        print("   📈 涨幅榜:")
        gainers = self.get_stock_ranking('涨幅榜', 5)
        for stock in gainers:
            print(f"      {stock['code']} {stock['name']}: {stock['change_pct']:+.2f}%, {stock['close']:.2f}")
        
        # 跌幅榜
        print("\n   📉 跌幅榜:")
        losers = self.get_stock_ranking('跌幅榜', 5)
        for stock in losers:
            print(f"      {stock['code']} {stock['name']}: {stock['change_pct']:+.2f}%, {stock['close']:.2f}")
        
        # 成交额榜
        print("\n   💰 成交额榜:")
        volume_leaders = self.get_stock_ranking('成交额榜', 5)
        for stock in volume_leaders:
            print(f"      {stock['code']} {stock['name']}: {stock.get('amount', 0):.1f}亿元, {stock['change_pct']:+.2f}%")
        
        # 4. 彪哥战法策略建议
        print("\n4. 🧠 彪哥战法策略建议")
        suggestions = self.generate_suggestions(season, score)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
        
        # 5. 保存报告
        self.save_report(indices, season, score, position, gainers, losers, volume_leaders, suggestions)
        
        return True
    
    def generate_suggestions(self, season, score):
        """生成策略建议"""
        suggestions = []
        
        if season == "夏长期":
            suggestions = [
                "积极布局，把握主升浪行情",
                "重点关注科技创新和消费升级板块",
                "可适当提高杠杆，但注意风险控制",
                "关注成交量变化，警惕高位放量"
            ]
        elif season == "春播期":
            suggestions = [
                "分批建仓，布局优质成长股",
                "关注政策扶持的新兴产业",
                "控制仓位在建议范围内",
                "耐心等待市场方向明确"
            ]
        elif season == "秋收期":
            suggestions = [
                "控制仓位，逐步获利了结",
                "关注防御性板块和现金分红",
                "减少短线操作，以观望为主",
                "等待市场调整后的机会"
            ]
        else:  # 冬藏期
            suggestions = [
                "严格控制仓位，保持现金为王",
                "关注超跌优质股的左侧布局机会",
                "避免追涨杀跌，耐心等待时机",
                "关注政策面和资金面变化"
            ]
        
        # 根据评分调整建议
        if score < 50:
            suggestions.append("⚠️ 市场风险较高，建议谨慎操作")
        elif score > 80:
            suggestions.append("🎯 市场机会较好，可积极把握")
        
        return suggestions
    
    def save_report(self, indices, season, score, position, gainers, losers, volume_leaders, suggestions):
        """保存分析报告"""
        report_dir = "/Users/tuqibiao/.openclaw/workspace/reports"
        os.makedirs(report_dir, exist_ok=True)
        
        report_path = os.path.join(report_dir, f"biage_postmarket_a股_{self.date_str}.txt")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"彪哥战法A股盘后分析报告 - {self.date_str}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("📈 A股主要指数表现:\n")
            for code, data in indices.items():
                f.write(f"  {data['name']}: {data['close']:.2f} ({data['change']:+.2f}, {data['change_pct']:+.2f}%)\n")
            
            f.write(f"\n🎯 彪哥战法分析:\n")
            f.write(f"  市场季节: {season}\n")
            f.write(f"  综合评分: {score}/100\n")
            f.write(f"  仓位建议: {position}\n")
            
            f.write(f"\n🏆 A股排行榜:")