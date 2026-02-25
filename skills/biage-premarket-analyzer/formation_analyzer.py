#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
板块阵型分析器 - 整合版
整合龙头扫描、中军扫描、阵型评估、报告生成
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')


class FormationAnalyzer:
    """板块阵型分析器"""
    
    # 配置参数
    DRAGON_CONFIG = {
        'market_cap_min': 30,
        'market_cap_max': 500,
        'optimal_cap_range': (50, 300),
        'min_turnover': 3,
        'optimal_turnover': (5, 20),
        'min_lianban': 2,
        'optimal_first_time': '10:00',
    }
    
    GENERAL_CONFIG = {
        'min_market_cap': 500,
        'optimal_market_cap': 1000,
        'max_daily_change': 9.5,
        'optimal_change_range': (3, 8),
    }
    
    FORMATION_WEIGHTS = {
        'dragon': 0.40,
        'general': 0.35,
        'followers': 0.25,
    }
    
    def __init__(self, cache_dir="./formation_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.date = datetime.now().strftime('%Y%m%d')
        self.data = {
            'zt_pool': pd.DataFrame(),
            'stock_spot': pd.DataFrame(),
            'lhb_data': pd.DataFrame(),
            'index_data': pd.DataFrame()
        }
    
    def fetch_data(self, date: str = None):
        """获取基础数据"""
        if date:
            self.date = date
        
        print(f"获取 {self.date} 数据...")
        
        # 涨停股池
        try:
            self.data['zt_pool'] = ak.stock_zt_pool_em(date=self.date)
            print(f"  ✓ 涨停数据: {len(self.data['zt_pool'])}家")
        except Exception as e:
            print(f"  ✗ 涨停数据: {e}")
        
        # 股票列表
        try:
            self.data['stock_spot'] = ak.stock_zh_a_spot_em()
            print(f"  ✓ 股票列表: {len(self.data['stock_spot'])}家")
        except Exception as e:
            print(f"  ✗ 股票列表: {e}")
        
        # 龙虎榜
        try:
            self.data['lhb_data'] = ak.stock_lhb_detail_daily_sina(
                start_date=self.date, end_date=self.date
            )
            print(f"  ✓ 龙虎榜: {len(self.data['lhb_data'])}条")
        except Exception as e:
            print(f"  ✗ 龙虎榜: {e}")
    
    def scan_dragons(self, sector_filter: List[str] = None) -> List[Dict]:
        """扫描龙头候选"""
        print("\n扫描龙头候选...")
        
        candidates = []
        zt_df = self.data['zt_pool']
        spot_df = self.data['stock_spot']
        
        if zt_df.empty:
            return candidates
        
        for _, row in zt_df.iterrows():
            symbol = row.get('代码', '')
            name = row.get('名称', '')
            
            stock_info = spot_df[spot_df['代码'] == symbol]
            if stock_info.empty:
                continue
            
            market_cap = stock_info['总市值'].values[0] / 1e8
            circulating_cap = stock_info['流通市值'].values[0] / 1e8
            lianban = row.get('连板数', 1)
            turnover = row.get('换手率', 0)
            industry = row.get('所属行业', '未知')
            
            if sector_filter and industry not in sector_filter:
                continue
            
            # 评分
            score = 0
            reasons = []
            
            # 市值评分
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
            
            # 换手评分
            if 5 <= turnover <= 20:
                score += 20
                reasons.append("换手充分")
            elif turnover > 20:
                score += 10
                reasons.append("高换手")
            
            lhb = self._get_lhb_info(symbol)
            
            candidates.append({
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
                'lhb': lhb
            })
        
        candidates.sort(key=lambda x: x['score'], reverse=True)
        print(f"  发现 {len(candidates)} 个候选")
        return candidates[:10]
    
    def scan_generals(self, sector_filter: List[str] = None) -> List[Dict]:
        """扫描中军候选"""
        print("\n扫描中军候选...")
        
        candidates = []
        spot_df = self.data['stock_spot']
        
        if spot_df.empty:
            return candidates
        
        large_cap = spot_df[spot_df['总市值'] >= 500e8].copy()
        
        if '涨跌幅' in large_cap.columns:
            large_cap = large_cap.sort_values('涨跌幅', ascending=False)
        
        for _, row in large_cap.head(30).iterrows():
            symbol = row.get('代码', '')
            name = row.get('名称', '')
            market_cap = row['总市值'] / 1e8
            change = row.get('涨跌幅', 0)
            industry = row.get('所属行业', '未知')
            
            if sector_filter and industry not in sector_filter:
                continue
            
            score = 0
            reasons = []
            
            if market_cap > 1000:
                score += 30
                reasons.append("超大市值")
            elif market_cap > 500:
                score += 25
                reasons.append("大市值")
            
            if 3 <= change < 9.5:
                score += 25
                reasons.append(f"中大阳线({change:.1f}%)")
            elif 0 < change < 3:
                score += 15
                reasons.append(f"小阳线({change:.1f}%)")
            
            lhb = self._get_lhb_info(symbol)
            if lhb['has_lhb']:
                score += 15
                reasons.append("机构参与")
            
            candidates.append({
                'symbol': symbol,
                'name': name,
                'market_cap': round(market_cap, 1),
                'change': round(change, 2),
                'industry': industry,
                'score': score,
                'reasons': '，'.join(reasons),
                'status': '核心' if score >= 60 else '跟风',
                'lhb': lhb
            })
        
        candidates.sort(key=lambda x: x['score'], reverse=True)
        print(f"  发现 {len(candidates)} 个候选")
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
            'net_amount': stock_lhb.get('净额', [0]).values[0] / 1e4,
        }
    
    def evaluate_formation(self, dragons: List[Dict], generals: List[Dict]) -> Dict:
        """评估阵型健康度"""
        print("\n评估阵型健康度...")
        
        formation = {
            'has_dragon': False,
            'has_general': False,
            'has_followers': False,
            'overall_score': 0,
            'type': '松散型'
        }
        
        # 先锋评分
        high_board = [d for d in dragons if d['lianban'] >= 3]
        if high_board:
            formation['has_dragon'] = True
            formation['dragon_leader'] = high_board[0]
            formation['overall_score'] += 40
        elif dragons:
            formation['has_dragon'] = True
            formation['dragon_leader'] = dragons[0]
            formation['overall_score'] += 25
        
        # 中军评分
        core_general = [g for g in generals if g['status'] == '核心']
        if core_general:
            formation['has_general'] = True
            formation['general_leader'] = core_general[0]
            formation['overall_score'] += 35
        elif generals:
            formation['has_general'] = True
            formation['general_leader'] = generals[0]
            formation['overall_score'] += 20
        
        # 后排评分
        followers = len([d for d in dragons if d['lianban'] == 1])
        if followers >= 5:
            formation['has_followers'] = True
            formation['follower_count'] = followers
            formation['overall_score'] += 25
        
        # 阵型类型
        if formation['overall_score'] >= 80:
            formation['type'] = '进攻型'
        elif formation['overall_score'] >= 50:
            formation['type'] = '防守型'
        
        print(f"  评分: {formation['overall_score']}/100 - {formation['type']}")
        return formation
    
    def generate_report(self, sector: str = "主线板块") -> str:
        """生成阵型报告"""
        self.fetch_data()
        dragons = self.scan_dragons()
        generals = self.scan_generals()
        formation = self.evaluate_formation(dragons, generals)
        
        return self._format_report(sector, dragons, generals, formation)
    
    def _format_report(self, sector: str, dragons: List[Dict], 
                      generals: List[Dict], formation: Dict) -> str:
        """格式化报告"""
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        report = f"""【{today} 板块阵型分析报告】

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
        
        d_check = "✓" if formation['has_dragon'] else "✗"
        g_check = "✓" if formation['has_general'] else "✗"
        f_check = "✓" if formation['has_followers'] else "✗"
        
        report += f"""【阵型健康度】评分：{formation['overall_score']}/100
- 先锋：{d_check}（连板龙头）
- 中军：{g_check}（机构坐镇）
- 后排：{f_check}（补涨跟随）
- 整体评价：{formation['type']}

【操作建议】
"""
        
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
            filename = f"formation_{self.date}.md"
        
        path = self.cache_dir / filename
        with open(path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n报告已保存: {path}")
        return path


def main():
    parser = argparse.ArgumentParser(description='板块阵型分析器')
    parser.add_argument('--date', type=str, help='分析日期(YYYYMMDD)')
    parser.add_argument('--sector', type=str, default='主线板块', help='板块名称')
    parser.add_argument('--output', type=str, help='输出文件名')
    parser.add_argument('--scan-only', action='store_true', help='仅扫描不生成报告')
    
    args = parser.parse_args()
    
    print("="*80)
    print("板块阵型分析器 v2.0")
    print("="*80)
    
    analyzer = FormationAnalyzer()
    
    if args.date:
        analyzer.date = args.date
    
    if args.scan_only:
        analyzer.fetch_data()
        dragons = analyzer.scan_dragons()
        generals = analyzer.scan_generals()
        print(f"\n龙头候选: {len(dragons)}个")
        print(f"中军候选: {len(generals)}个")
    else:
        report = analyzer.generate_report(sector=args.sector)
        print("\n" + "="*80)
        print(report)
        analyzer.save_report(report, args.output)
    
    print("\n分析完成!")


if __name__ == "__main__":
    main()
