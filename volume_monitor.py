#!/usr/bin/env python3
"""
量能持续性监控系统
基于复盘文件发现的量能验证法则：
1. 2.4万亿天量次日骤缩3000亿 → 情绪退潮
2. 无法维持2.2万亿以上成交 → 缺口回补需求
3. 量能快速退潮 → 场外资金入场意愿边际衰减
"""

import os
import sys
import json
import urllib.request
import ssl
from datetime import datetime, timedelta
import statistics

# 禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

class VolumeMonitor:
    """量能持续性监控器"""
    
    def __init__(self):
        self.base_url = "https://push2.eastmoney.com/api"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://quote.eastmoney.com/'
        }
        
        # 量能阈值（基于复盘文件分析）
        self.volume_thresholds = {
            '天量': 2.4e12,  # 2.4万亿
            '健康量': 2.2e12,  # 2.2万亿
            '萎缩量': 2.0e12,  # 2.0万亿
            '地量': 1.8e12   # 1.8万亿
        }
        
        # 历史数据存储
        self.history_file = "/Users/tuqibiao/.openclaw/workspace/volume_history.json"
        self.load_history()
    
    def load_history(self):
        """加载历史量能数据"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            self.history = []
    
    def save_history(self):
        """保存历史量能数据"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history[-30:], f, ensure_ascii=False, indent=2)  # 保留最近30天
    
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
    
    def get_market_volume(self):
        """获取市场总成交量"""
        # 获取上证指数和深证成指数据
        url = f"{self.base_url}/qt/ulist.np/get?fltt=2&invt=2&secids=1.000001,0.399001&fields=f12,f13,f14,f5,f6"
        
        try:
            data = self.fetch_with_retry(url)
            if not data or 'data' not in data or 'diff' not in data['data']:
                return self.get_mock_volume()
            
            total_volume = 0
            total_amount = 0
            
            for item in data['data']['diff']:
                volume = item.get('f5', 0)  # 成交量(手)
                amount = item.get('f6', 0)  # 成交额
                
                # 转换为亿元
                total_volume += volume * 100  # 手 → 股（假设100股/手）
                total_amount += amount / 100000000  # 元 → 亿元
            
            return {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'volume_shares': total_volume,
                'amount_billion': total_amount,
                'volume_level': self.classify_volume(total_amount)
            }
            
        except Exception as e:
            print(f"获取量能数据失败: {e}")
            return self.get_mock_volume()
    
    def get_mock_volume(self):
        """获取模拟量能数据"""
        # 模拟数据，用于测试
        import random
        amount = random.uniform(1.8, 2.5)  # 1.8-2.5万亿
        
        return {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'volume_shares': int(amount * 1e12 / 10),  # 粗略估算
            'amount_billion': amount,
            'volume_level': self.classify_volume(amount),
            'is_mock': True
        }
    
    def classify_volume(self, amount_billion):
        """分类量能水平"""
        if amount_billion >= self.volume_thresholds['天量']:
            return '天量'
        elif amount_billion >= self.volume_thresholds['健康量']:
            return '健康量'
        elif amount_billion >= self.volume_thresholds['萎缩量']:
            return '萎缩量'
        else:
            return '地量'
    
    def analyze_volume_trend(self, days=5):
        """分析量能趋势"""
        if len(self.history) < 2:
            return "数据不足，无法分析趋势"
        
        recent_data = self.history[-days:] if len(self.history) >= days else self.history
        
        # 计算变化率
        amounts = [item['amount_billion'] for item in recent_data]
        
        if len(amounts) < 2:
            return "数据不足，无法计算变化"
        
        # 计算日变化率
        changes = []
        for i in range(1, len(amounts)):
            change = (amounts[i] - amounts[i-1]) / amounts[i-1] * 100
            changes.append(change)
        
        avg_change = statistics.mean(changes) if changes else 0
        
        # 基于复盘文件的量能验证法则
        if amounts[-1] >= 2.4 and len(amounts) >= 2:
            # 天量次日验证
            prev_amount = amounts[-2] if len(amounts) >= 2 else 0
            if prev_amount >= 2.4 and amounts[-1] <= prev_amount - 0.3:
                return "⚠️ 天量次日骤缩，警惕情绪退潮"
        
        if amounts[-1] < 2.2:
            return "⚠️ 量能低于2.2万亿，缺口回补需求"
        
        if avg_change < -10:
            return "⚠️ 量能快速退潮，场外资金入场意愿衰减"
        
        if avg_change > 5:
            return "📈 量能持续放大，资金入场积极"
        
        return "➡️ 量能平稳，市场情绪稳定"
    
    def generate_volume_report(self):
        """生成量能分析报告"""
        print("📊 量能持续性监控报告")
        print("=" * 60)
        
        # 获取当前量能
        current_volume = self.get_market_volume()
        
        print(f"📅 日期: {current_volume['date']}")
        print(f"💰 成交额: {current_volume['amount_billion']:.2f} 万亿元")
        print(f"📈 量能水平: {current_volume['volume_level']}")
        
        if current_volume.get('is_mock'):
            print("⚠️ 注: 当前使用模拟数据")
        
        # 添加到历史
        self.history.append(current_volume)
        self.save_history()
        
        # 分析趋势
        print(f"\n📊 量能趋势分析（最近{min(5, len(self.history))}天）:")
        
        if len(self.history) >= 2:
            print("  历史成交额:")
            for i, item in enumerate(self.history[-5:]):
                print(f"    {item['date']}: {item['amount_billion']:.2f}万亿 ({item['volume_level']})")
        
        trend_analysis = self.analyze_volume_trend()
        print(f"\n🔍 趋势判断: {trend_analysis}")
        
        # 基于复盘文件的投资建议
        print(f"\n💡 投资建议（基于复盘文件量能验证法则）:")
        
        amount = current_volume['amount_billion']
        
        if amount >= 2.4:
            print("  1. 天量出现，关注次日量能持续性")
            print("  2. 若次日骤缩3000亿以上，警惕情绪退潮")
            print("  3. 建议降低仓位，等待方向明确")
        
        elif amount >= 2.2:
            print("  1. 量能健康，市场情绪稳定")
            print("  2. 可维持正常仓位操作")
            print("  3. 关注连板梯队健康度")
        
        elif amount >= 2.0:
            print("  1. 量能萎缩，市场情绪谨慎")
            print("  2. 建议控制仓位，避免追高")
            print("  3. 关注政策面和资金面变化")
        
        else:
            print("  1. 地量水平，市场情绪低迷")
            print("  2. 建议轻仓观望，等待量能放大")
            print("  3. 关注超跌反弹机会")
        
        # 保存报告
        report_dir = "/Users/tuqibiao/.openclaw/workspace/reports"
        os.makedirs(report_dir, exist_ok=True)
        
        report_path = os.path.join(report_dir, f"volume_report_{current_volume['date']}.txt")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"量能持续性监控报告 - {current_volume['date']}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"成交额: {current_volume['amount_billion']:.2f} 万亿元\n")
            f.write(f"量能水平: {current_volume['volume_level']}\n\n")
            f.write(f"趋势判断: {trend_analysis}\n")
        
        print(f"\n📁 报告已保存至: {report_path