#!/usr/bin/env python3
"""
ai-daily-digest - 适配版
专为"彪哥战法"定制的每日简报生成器

功能：
1. 自动收集市场数据（akshare/Wind）
2. 运行四季判断模型
3. 生成盘前简报
4. 推送到飞书
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

# 添加到路径
sys.path.insert(0, '/Users/tuqibiao/.openclaw/workspace/qlib_biaoge')

class DailyDigestGenerator:
    """每日简报生成器"""
    
    def __init__(self):
        self.config = {
            'push_time': '08:00',           # 推送时间
            'data_sources': ['akshare'],     # 数据源
            'output_channels': ['feishu'],   # 输出渠道
            'include_sectors': True,         # 包含板块分析
            'include_news': False,           # 包含新闻（暂时禁用）
        }
    
    def collect_market_data(self) -> Dict:
        """收集市场数据"""
        try:
            import akshare as ak
            
            data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'sources': []
            }
            
            # 1. 上证指数数据
            try:
                sh_index = ak.index_zh_a_hist(symbol="000001", period="daily", 
                                              start_date=(datetime.now()-timedelta(30)).strftime('%Y%m%d'),
                                              end_date=datetime.now().strftime('%Y%m%d'))
                data['sh_index'] = {
                    'latest_close': sh_index['收盘'].iloc[-1] if not sh_index.empty else None,
                    'change_pct': sh_index['涨跌幅'].iloc[-1] if not sh_index.empty else None,
                    'volume': sh_index['成交量'].iloc[-1] if not sh_index.empty else None,
                }
                data['sources'].append('上证指数')
            except Exception as e:
                data['sh_index'] = {'error': str(e)}
            
            # 2. 涨跌停统计
            try:
                zdt = ak.stock_zt_pool_em(date=datetime.now().strftime('%Y%m%d'))
                data['zt_pool'] = {
                    'limit_up_count': len(zdt) if zdt is not None else 0,
                }
                data['sources'].append('涨停池')
            except:
                data['zt_pool'] = {'limit_up_count': 'N/A'}
            
            # 3. 北向资金（简化版）
            data['northbound'] = {'status': '待获取'}
            
            return data
            
        except Exception as e:
            return {'error': str(e), 'date': datetime.now().strftime('%Y-%m-%d')}
    
    def analyze_market(self, data: Dict) -> Dict:
        """市场分析"""
        analysis = {
            'season': '未知',
            'confidence': 0,
            'position': 0,
            'key_points': [],
            'sectors': [],
        }
        
        # 基于数据判断季节
        sh_change = data.get('sh_index', {}).get('change_pct', 0)
        
        if sh_change is not None:
            if sh_change > 1:
                analysis['season'] = '夏长'
                analysis['confidence'] = 70
                analysis['position'] = 80
            elif sh_change > 0:
                analysis['season'] = '春播'
                analysis['confidence'] = 60
                analysis['position'] = 40
            elif sh_change > -1:
                analysis['season'] = '秋收'
                analysis['confidence'] = 60
                analysis['position'] = 40
            else:
                analysis['season'] = '冬藏'
                analysis['confidence'] = 70
                analysis['position'] = 10
        
        # 生成要点
        if data.get('zt_pool', {}).get('limit_up_count', 0) > 50:
            analysis['key_points'].append('涨停家数较多，情绪活跃')
        
        if sh_change and sh_change > 0:
            analysis['key_points'].append('指数上涨，趋势向好')
        else:
            analysis['key_points'].append('指数调整，谨慎观望')
        
        # 推荐板块（基于季节）
        sector_map = {
            '春播': ['AI算力', '机器人', '新能源'],
            '夏长': ['券商', '科技成长', '周期股'],
            '秋收': ['消费', '医药', '防守板块'],
            '冬藏': ['黄金', '军工', '高股息'],
        }
        analysis['sectors'] = sector_map.get(analysis['season'], ['观察'])
        
        return analysis
    
    def generate_digest(self, data: Dict, analysis: Dict) -> str:
        """生成简报"""
        
        digest = f"""📊 【彪哥战法】盘前简报（{data['date']}）

🎯 当前季节: {analysis['season']}（置信度{analysis['confidence']}%）
💰 建议仓位: {analysis['position']}%

📈 市场数据:
• 上证指数: {data.get('sh_index', {}).get('latest_close', 'N/A')}
• 涨跌: {data.get('sh_index', {}).get('change_pct', 'N/A')}%
• 涨停家数: {data.get('zt_pool', {}).get('limit_up_count', 'N/A')}

📋 市场要点:
"""
        
        for point in analysis['key_points']:
            digest += f"• {point}\n"
        
        digest += f"""
🔥 关注板块:
"""
        for i, sector in enumerate(analysis['sectors'], 1):
            digest += f"{i}. {sector}\n"
        
        digest += f"""
💡 操作建议:
• {analysis['season']}期，{'重仓持股' if analysis['season'] == '夏长' else '逐步建仓' if analysis['season'] == '春播' else '逢高减仓' if analysis['season'] == '秋收' else '空仓观望'}
• 仓位控制{analysis['position']}%，严格止损
• 重点关注上述板块龙头标的

---
⏰ 推送时间: {datetime.now().strftime('%H:%M')}
📊 数据来源: {', '.join(data.get('sources', []))}
"""
        
        return digest
    
    def push_to_feishu(self, content: str) -> bool:
        """推送到飞书"""
        try:
            from feishu_optimizer import send_optimized
            
            # 使用优化版发送（合并消息）
            send_optimized(text=content)
            success = send_optimized(flush=True, target="ou_cde15d08540b24715fa99809729cf1be")
            
            return success
        except Exception as e:
            print(f"推送失败: {e}")
            return False
    
    def run(self):
        """主运行流程"""
        print("=" * 60)
        print("【AI Daily Digest】盘前简报生成器")
        print("=" * 60)
        print()
        
        # 1. 收集数据
        print("📊 正在收集市场数据...")
        data = self.collect_market_data()
        
        if 'error' in data:
            print(f"❌ 数据收集失败: {data['error']}")
            return False
        
        print(f"✅ 数据收集完成: {', '.join(data.get('sources', []))}")
        print()
        
        # 2. 分析市场
        print("🧠 正在分析市场...")
        analysis = self.analyze_market(data)
        print(f"✅ 分析完成: 当前季节 {analysis['season']}")
        print()
        
        # 3. 生成简报
        print("📝 正在生成简报...")
        digest = self.generate_digest(data, analysis)
        print("✅ 简报生成完成")
        print()
        
        # 4. 推送
        print("📤 正在推送到飞书...")
        if self.push_to_feishu(digest):
            print("✅ 推送成功!")
        else:
            print("❌ 推送失败，请检查飞书配置")
        
        print()
        print("=" * 60)
        print("完成!")
        print("=" * 60)
        
        return True


# 定时任务配置（用于crontab）
"""
# 编辑 crontab: crontab -e
# 添加以下行（每天08:00执行）

0 8 * * * cd /Users/tuqibiao/.openclaw/workspace && python3 ai_daily_digest.py >> /tmp/digest.log 2>&1

"""

if __name__ == "__main__":
    # 运行
    generator = DailyDigestGenerator()
    generator.run()
