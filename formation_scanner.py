#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日阵型扫描器
自动识别龙头候选和中军候选
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')


class FormationScanner:
    """板块阵型扫描器"""
    
    def __init__(self, cache_dir="./formation_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.today = datetime.now().strftime('%Y%m%d')
        self.data = {
            'zt_pool': pd.DataFrame(),
            'stock_spot': pd.DataFrame(),
            'lhb_data': pd.DataFrame()
        }
    
    def fetch_daily_data(self):
        """获取每日基础数据"""
        print("获取当日数据...")
        
        # 1. 涨停股池
        try:
            self.data['zt_pool'] = ak.stock_zt_pool_em(date=self.today)
            print(f"  涨停股: {len(self.data['zt_pool'])}家")
        except Exception as e:
            print(f"  获取涨停数据失败: {e}")
        
        # 2. 股票列表和市值
        try:
            self.data['stock_spot'] = ak.stock_zh_a_spot_em()
            print(f"  股票列表: {len(self.data['stock_spot'])}家")
        except Exception as e:
            print(f"  获取股票列表失败: {e}")
        
        # 3. 龙虎榜
        try:
            self.data['lhb_data'] = ak.stock_lhb_detail_daily_sina(
                start_date=self.today, end_date=self.today
            )
            print(f"  龙虎榜: {len(self.data['lhb_data'])}条")
        except Exception as e:
            print(f"  获取龙虎榜失败: {e}")
    
    def scan_dragon_candidates(self, sector_filter: List[str] = None) -> List[Dict]:
        """
        扫描龙头候选
        
        龙头识别标准：
        - 市值：50-300亿
        - 涨停时间：早盘（简化处理）
        - 连板数：>=2优先
        - 换手率：5-20%
        - 板块地位：最先涨停或连板最高
        """
        print("\n扫描龙头候选...")
        
        candidates = []
        zt_df = self.data['zt_pool']
        spot_df = self.data['stock_spot']
        
        if zt_df.empty:
            return candidates
        
        for _, row in zt_df.iterrows():
            symbol = row.get('代码', '')
            name = row.get('名称', '')
            
            # 获取股票信息
            stock_info = spot_df[spot_df['代码'] == symbol]
            if stock_info.empty:
                continue
            
            market_cap = stock_info['总市值'].values[0] / 1e8  # 转为亿
            circulating_cap = stock_info['流通市值'].values[0] / 1e8
            
            # 龙头筛选条件
            lianban = row.get('连板数', 1)
            turnover = row.get('换手率', 0)
            industry = row.get('所属行业', '未知')
            
            # 计算龙头潜力分
            score = 0
            reasons = []
            
            # 市值评分 (50-300亿最佳)
            if 50 <= market_cap <= 300:
                score += 30
                reasons.append("市值适中")
            elif market_cap < 50:
                score += 20
                reasons.append("小市值")
            elif market_cap <= 500:
                score += 15
                reasons.append("市值偏大")
            
            # 连板评分
            if lianban >= 5:
                score += 30
                reasons.append(f"高度连板({lianban}板)")
            elif lianban >= 3:
                score += 25
                reasons.append(f"三连板+")
            elif lianban >= 2:
                score += 20
                reasons.append("二连板")
            else:
                score += 10
                reasons.append("首板")
            
            # 换手率评分 (5-20%最佳)
            if 5 <= turnover <= 20:
                score += 20
                reasons.append("换手充分")
            elif turnover > 20:
                score += 10
                reasons.append("高换手")
            elif turnover > 2:
                score += 5
                reasons.append("换手偏低")
            
            # 板块过滤
            if sector_filter and industry not in sector_filter:
                continue
            
            # 获取龙虎榜信息
            lhb_info = self._get_lhb_info(symbol)
            
            candidate = {
                'symbol': symbol,
                'name': name,
                'market_cap': round(market_cap, 1),
                'circulating_cap': round(circulating_cap, 1),
                'lianban': lianban,
                'turnover': round(turnover, 2),
                'industry': industry,
                'first_time': row.get('首次封板时间', 'unknown'),
                'score': score,
                'reasons': '，'.join(reasons),
                'potential': '高' if score >= 70 else ('中' if score >= 50 else '低'),
                'lhb': lhb_info
            }
            
            candidates.append(candidate)
        
        # 按评分排序
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"  发现 {len(candidates)} 个龙头候选")
        return candidates[:10]  # 返回前10
    
    def scan_general_candidates(self, sector_filter: List[str] = None) -> List[Dict]:
        """
        扫描中军候选
        
        中军识别标准：
        - 市值：>500亿
        - 涨幅：阶梯式，非连板（今日可能未涨停）
        - 行业龙头地位
        - 机构资金参与
        """
        print("\n扫描中军候选...")
        
        candidates = []
        spot_df = self.data['stock_spot']
        
        if spot_df.empty:
            return candidates
        
        # 筛选大市值股票 (>500亿)
        large_cap = spot_df[spot_df['总市值'] >= 500e8].copy()
        
        # 按涨幅排序（关注涨幅居前的）
        if '涨跌幅' in large_cap.columns:
            large_cap = large_cap.sort_values('涨跌幅', ascending=False)
        
        for _, row in large_cap.head(20).iterrows():  # 只看前20
            symbol = row.get('代码', '')
            name = row.get('名称', '')
            market_cap = row['总市值'] / 1e8
            change = row.get('涨跌幅', 0)
            industry = row.get('所属行业', '未知')
            
            # 板块过滤
            if sector_filter and industry not in sector_filter:
                continue
            
            # 中军特征评分
            score = 0
            reasons = []
            
            # 市值规模
            if market_cap > 1000:
                score += 30
                reasons.append("超大市值(>1000亿)")
            elif market_cap > 500:
                score += 25
                reasons.append("大市值(500-1000亿)")
            
            # 涨幅（中军不应连板）
            if 3 <= change < 9.5:
                score += 25
                reasons.append(f"中大阳线({change:.1f}%)")
            elif 0 < change < 3:
                score += 15
                reasons.append(f"小阳线({change:.1f}%)")
            elif change >= 9.5:
                score += 10
                reasons.append("涨停（罕见）")
            
            # 获取龙虎榜信息
            lhb_info = self._get_lhb_info(symbol)
            if lhb_info['has_lhb']:
                score += 15
                reasons.append("龙虎榜机构参与")
            
            candidate = {
                'symbol': symbol,
                'name': name,
                'market_cap': round(market_cap, 1),
                'change': round(change, 2),
                'industry': industry,
                'score': score,
                'reasons': '，'.join(reasons),
                'status': '核心' if score >= 60 else '跟风',
                'lhb': lhb_info
            }
            
            candidates.append(candidate)
        
        # 按评分排序
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"  发现 {len(candidates)} 个中军候选")
        return candidates[:8]
    
    def _get_lhb_info(self, symbol: str) -> Dict:
        """获取龙虎榜信息"""
        lhb_df = self.data['lhb_data']
        
        if lhb_df.empty:
            return {'has_lhb': False}
        
        stock_lhb = lhb_df[lhb_df['代码'] == symbol]
        
        if stock_lhb.empty:
            return {'has_lhb': False}
        
        return {
            'has_lhb': True,
            'buy_amount': stock_lhb.get('买入额', [0]).values[0] / 1e4,  # 万
            'sell_amount': stock_lhb.get('卖出额', [0]).values[0] / 1e4,
            'net_amount': stock_lhb.get('净额', [0]).values[0] / 1e4,
        }
    
    def evaluate_formation(self, dragon_candidates: List[Dict], 
                          general_candidates: List[Dict]) -> Dict:
        """
        评估板块阵型健康度
        
        阵型组成：
        - 先锋（连板龙头）
        - 中军（大市值核心）
        - 后排（补涨跟随）
        """
        print("\n评估阵型健康度...")
        
        formation = {
            'has_dragon': False,
            'has_general': False,
            'has_followers': False,
            'overall_score': 0,
            'type': '松散型'
        }
        
        # 1. 检查先锋（是否有高连板龙头）
        high_board_dragons = [d for d in dragon_candidates if d['lianban'] >= 3]
        if high_board_dragons:
            formation['has_dragon'] = True
            formation['dragon_leader'] = high_board_dragons[0]
            formation['overall_score'] += 40
        elif dragon_candidates:
            formation['has_dragon'] = True
            formation['dragon_leader'] = dragon_candidates[0]
            formation['overall_score'] += 25
        
        # 2. 检查中军
        core_generals = [g for g in general_candidates if g['status'] == '核心']
        if core_generals:
            formation['has_general'] = True
            formation['general_leader'] = core_generals[0]
            formation['overall_score'] += 35
        elif general_candidates:
            formation['has_general'] = True
            formation['general_leader'] = general_candidates[0]
            formation['overall_score'] += 20
        
        # 3. 检查后排（是否有足够补涨股）
        follower_count = len([d for d in dragon_candidates if d['lianban'] == 1])
        if follower_count >= 5:
            formation['has_followers'] = True
            formation['follower_count'] = follower_count
            formation['overall_score'] += 25
        
        # 阵型类型判定
        if formation['overall_score'] >= 80:
            formation['type'] = '进攻型'
        elif formation['overall_score'] >= 50:
            formation['type'] = '防守型'
        else:
            formation['type'] = '松散型'
        
        print(f"  阵型评分: {formation['overall_score']}/100")
        print(f"  阵型类型: {formation['type']}")
        
        return formation
    
    def generate_report(self, main_sector: str = "主线板块") -> str:
        """生成阵型分析报告"""
        
        # 获取数据
        self.fetch_daily_data()
        
        # 扫描候选
        dragons = self.scan_dragon_candidates()
        generals = self.scan_general_candidates()
        
        # 评估阵型
        formation = self.evaluate_formation(dragons, generals)
        
        # 生成报告
        report = self._format_report(main_sector, dragons, generals, formation)
        
        return report
    
    def _format_report(self, sector: str, dragons: List[Dict], 
                      generals: List[Dict], formation: Dict) -> str:
        """格式化报告"""
        
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        report = f"""【{today_str} 板块阵型分析报告】

【季节判断】需要结合市场环境
【主线板块】{sector}

【板块阵型分析】

◆ 龙头候选（按潜力排序）:
"""
        
        for i, d in enumerate(dragons[:5], 1):
            lhb_str = "有" if d['lhb']['has_lhb'] else "无"
            report += f"""  {i}. {d['name']}（{d['symbol']}）
     - 市值：{d['market_cap']}亿（流通{d['circulating_cap']}亿）
     - 连板数：{d['lianban']}板
     - 换手率：{d['turnover']}%
     - 涨停时间：{d['first_time']}
     - 龙虎榜：{lhb_str}
     - 龙头潜力：{d['potential']}（{d['reasons']}）

"""
        
        report += """◆ 中军候选:
"""
        
        for i, g in enumerate(generals[:3], 1):
            lhb_str = "机构参与" if g['lhb']['has_lhb'] else "无"
            report += f"""  {i}. {g['name']}（{g['symbol']}）
     - 市值：{g['market_cap']}亿
     - 涨幅：{g['change']}%
     - 龙虎榜：{lhb_str}
     - 中军地位：{g['status']}（{g['reasons']}）

"""
        
        # 阵型健康度
        dragon_check = "✓" if formation['has_dragon'] else "✗"
        general_check = "✓" if formation['has_general'] else "✗"
        follower_check = "✓" if formation['has_followers'] else "✗"
        
        report += f"""【阵型健康度】评分：{formation['overall_score']}/100
- 先锋：{dragon_check}（连板龙头）
- 中军：{general_check}（机构坐镇）
- 后排：{follower_check}（补涨跟随）
- 整体评价：{formation['type']}

【操作建议】
"""
        
        # 根据阵型给出建议
        if formation['type'] == '进攻型':
            report += """• 阵型完整，可积极参与
• 关注龙头分歧买点
• 中军可作为稳健配置
• 后排补涨谨慎追高"""
        elif formation['type'] == '防守型':
            report += """• 阵型尚可，控制仓位参与
• 等待龙头确认强度
• 中军打底仓观察
• 避免后排跟风股"""
        else:
            report += """• 阵型松散，观望为主
• 等待龙头走出来
• 不急于建仓
• 关注板块持续性"""
        
        return report
    
    def save_report(self, report: str, filename: str = None):
        """保存报告"""
        if filename is None:
            filename = f"formation_report_{self.today}.md"
        
        output_path = self.cache_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n报告已保存: {output_path}")
        return output_path


def main():
    """主函数"""
    print("="*80)
    print("每日阵型扫描器")
    print("="*80)
    
    scanner = FormationScanner()
    
    # 生成报告
    report = scanner.generate_report(main_sector="AI/科技")
    
    print("\n" + "="*80)
    print("【报告预览】")
    print("="*80)
    print(report)
    
    # 保存报告
    scanner.save_report(report)
    
    print("\n扫描完成!")


if __name__ == "__main__":
    main()
