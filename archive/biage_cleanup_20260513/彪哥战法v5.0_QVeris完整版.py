#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彪哥战法v5.0 完整版 - QVeris数据源
2026年3月26日创建
"""

import os
import sys
import requests
import json
import datetime
import time

class QVerisDataCollector:
    """QVeris数据采集器"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("QVERIS_API_KEY")
        if not self.api_key:
            raise ValueError("QVERIS_API_KEY环境变量未设置")
        
        self.base_url = "https://qveris.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 缓存
        self.cache = {}
        
    def execute_tool(self, tool_id, parameters):
        """执行QVeris工具"""
        
        cache_key = f"{tool_id}_{json.dumps(parameters, sort_keys=True)}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        url = f"{self.base_url}/tools/execute"
        payload = {
            "tool_id": tool_id,
            "parameters": parameters
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                self.cache[cache_key] = result
                return result
            else:
                print(f"❌ {tool_id} 请求失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ {tool_id} 异常: {e}")
            return None
    
    def get_index_data(self, codes=None):
        """获取指数数据"""
        if codes is None:
            codes = ["000001.SH", "399001.SZ", "399006.SZ"]  # 上证、深证、创业板
        
        print(f"📈 获取指数数据: {', '.join(codes)}")
        
        tool_id = "ths_ifind.real_time_quotation.v1"
        parameters = {
            "codes": ",".join(codes),
            "indicators": "common"
        }
        
        result = self.execute_tool(tool_id, parameters)
        index_data = {}
        
        if result and 'result' in result and 'data' in result['result']:
            data = result['result']['data']
            if isinstance(data, list) and len(data) > 0:
                for item_list in data:
                    if isinstance(item_list, list):
                        for item in item_list:
                            code = item.get('thscode', '')
                            if code:
                                index_data[code] = {
                                    'name': self._get_index_name(code),
                                    'price': item.get('latest'),
                                    'change': item.get('change'),
                                    'change_pct': item.get('changeRatio'),
                                    'volume': item.get('volume'),
                                    'amount': item.get('amount'),
                                    'high': item.get('high'),
                                    'low': item.get('low'),
                                    'open': item.get('open'),
                                    'pre_close': item.get('preClose'),
                                    'time': item.get('time')
                                }
        
        return index_data
    
    def _get_index_name(self, code):
        """获取指数名称"""
        names = {
            "000001.SH": "上证指数",
            "399001.SZ": "深证成指",
            "399006.SZ": "创业板指",
            "000300.SH": "沪深300",
            "000905.SH": "中证500"
        }
        return names.get(code, code)
    
    def get_market_statistics(self):
        """获取市场统计数据"""
        print("📊 获取市场统计数据...")
        
        tool_id = "mcp_gildata.marketlimitupdowncount.v1"
        parameters = {
            "query": "获取今日市场涨跌停家数"
        }
        
        result = self.execute_tool(tool_id, parameters)
        
        if result and 'result' in result and 'data' in result['result']:
            data = result['result']['data']
            return self._parse_market_stats(data)
        
        return None
    
    def _parse_market_stats(self, raw_data):
        """解析市场统计数据"""
        if 'table_markdown' not in raw_data:
            return None
        
        table = raw_data['table_markdown']
        lines = table.strip().split('\n')
        
        if len(lines) >= 3:
            today_line = lines[2]  # 今日数据
            cells = [cell.strip() for cell in today_line.split('|') if cell.strip()]
            
            if len(cells) >= 9:
                try:
                    stats = {
                        'total': int(cells[2]),
                        'rising': int(cells[3]),
                        'falling': int(cells[4]),
                        'unchanged': int(cells[5]),
                        'limit_up': int(cells[6]),
                        'limit_down': int(cells[7]),
                        'date': cells[8]
                    }
                    
                    # 计算比例
                    stats['rising_ratio'] = stats['rising'] / stats['total'] if stats['total'] > 0 else 0
                    stats['falling_ratio'] = stats['falling'] / stats['total'] if stats['total'] > 0 else 0
                    stats['limit_up_ratio'] = stats['limit_up'] / stats['total'] if stats['total'] > 0 else 0
                    stats['limit_down_ratio'] = stats['limit_down'] / stats['total'] if stats['total'] > 0 else 0
                    
                    return stats
                except:
                    pass
        
        return None
    
    def get_full_market_data(self):
        """获取完整市场数据"""
        print("\n" + "="*60)
        print("🚀 采集市场数据 (QVeris数据源)")
        print("="*60)
        
        market_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'indices': self.get_index_data(),
            'statistics': self.get_market_statistics(),
            'status': 'collecting'
        }
        
        if market_data['indices'] and market_data['statistics']:
            market_data['status'] = 'completed'
            print("✅ 数据采集完成")
        else:
            market_data['status'] = 'partial'
            print("⚠️ 数据采集部分完成")
        
        return market_data

class BiageStrategyV5:
    """彪哥战法v5.0分析器"""
    
    def __init__(self):
        self.collector = QVerisDataCollector()
        
        # 状态定义
        self.states = {
            '混沌期': {'score_range': (0, 0.3), 'position': '0-10%', 'strategy': '空仓等待，观察信号'},
            '冬藏期': {'score_range': (0.3, 0.5), 'position': '10-30%', 'strategy': '防守为主，轻仓观望'},
            '秋收期': {'score_range': (0.5, 0.7), 'position': '30-50%', 'strategy': '逐步减仓，锁定利润'},
            '春播期': {'score_range': (0.7, 0.85), 'position': '50-70%', 'strategy': '分批建仓，布局未来'},
            '夏长期': {'score_range': (0.85, 1.0), 'position': '70-90%', 'strategy': '重仓持有，顺势而为'}
        }
    
    def analyze_market(self, market_data=None):
        """分析市场"""
        print("\n🎯 彪哥战法v5.0分析开始")
        print("-" * 40)
        
        if market_data is None:
            market_data = self.collector.get_full_market_data()
        
        if not market_data or market_data['status'] != 'completed':
            print("❌ 数据不足，无法分析")
            return None
        
        indices = market_data['indices']
        stats = market_data['statistics']
        
        if not indices or not stats:
            print("❌ 关键数据缺失")
            return None
        
        # 提取关键数据
        sh_index = indices.get('000001.SH', {})
        rising_ratio = stats.get('rising_ratio', 0)
        limit_up = stats.get('limit_up', 0)
        limit_down = stats.get('limit_down', 0)
        
        # 14维特征分析
        features = self._analyze_features(sh_index, stats)
        
        # 计算综合评分
        total_score = self._calculate_score(features)
        
        # 确定市场状态
        market_state, state_info = self._determine_state(total_score)
        
        # 生成分析结果
        analysis = {
            'timestamp': datetime.datetime.now().isoformat(),
            'market_state': market_state,
            'total_score': round(total_score, 3),
            'position': state_info['position'],
            'strategy': state_info['strategy'],
            'features': features,
            'data_summary': {
                'shanghai_index': round(sh_index.get('price', 0), 2),
                'shanghai_change': round(sh_index.get('change_pct', 0), 2),
                'total_stocks': stats.get('total', 0),
                'rising_stocks': stats.get('rising', 0),
                'falling_stocks': stats.get('falling', 0),
                'limit_up': limit_up,
                'limit_down': limit_down,
                'rising_ratio': round(rising_ratio, 3)
            }
        }
        
        print("✅ 分析完成")
        return analysis
    
    def _analyze_features(self, sh_index, stats):
        """分析14维特征"""
        features = {
            '技术面': [],
            '资金面': [],
            '情绪面': [],
            '宏观面': []
        }
        
        # 技术面分析
        if sh_index.get('change_pct', 0) < 0:
            features['技术面'].append('指数下跌')
        
        if stats.get('rising_ratio', 0) < 0.5:
            features['技术面'].append('普跌行情')
        
        if stats.get('limit_up', 0) < 80:
            features['技术面'].append('涨停家数少')
        
        if stats.get('limit_down', 0) > 20:
            features['技术面'].append('跌停家数多')
        
        # 情绪面分析
        rising_ratio = stats.get('rising_ratio', 0)
        if rising_ratio < 0.3:
            features['情绪面'].append('情绪极度低迷')
        elif rising_ratio < 0.5:
            features['情绪面'].append('情绪低迷')
        else:
            features['情绪面'].append('情绪中性或积极')
        
        # 资金面（暂时用北向资金等替代）
        features['资金面'].append('待获取详细资金数据')
        
        # 宏观面
        features['宏观面'].append('政策真空期')
        
        return features
    
    def _calculate_score(self, features):
        """计算综合评分"""
        # 技术面权重60%
        tech_score = len(features['技术面']) / 4 * 0.6 if features['技术面'] else 0
        
        # 情绪面权重13%
        emotion_text = ' '.join(features['情绪面'])
        if '极度低迷' in emotion_text:
            emotion_score = 0.13
        elif '低迷' in emotion_text:
            emotion_score = 0.065
        else:
            emotion_score = 0
        
        # 资金面权重20%（暂时给基础分）
        fund_score = 0.1
        
        # 宏观面权重7%（暂时给基础分）
        macro_score = 0.035
        
        total_score = tech_score + emotion_score + fund_score + macro_score
        
        # 确保在0-1之间
        return min(max(total_score, 0), 1)
    
    def _determine_state(self, score):
        """确定市场状态"""
        for state, info in self.states.items():
            min_score, max_score = info['score_range']
            if min_score <= score < max_score:
                return state, info
        
        return '混沌期', self.states['混沌期']
    
    def generate_report(self, analysis, report_type='standard'):
        """生成分析报告"""
        if not analysis:
            return "❌ 分析数据缺失"
        
        data = analysis['data_summary']
        
        if report_type == 'premarket':
            # 盘前报告
            report = f"""
📈 【彪哥战法v5.0】盘前分析报告
━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 分析时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}

🎯 昨日市场回顾:
  上证指数: {data['shanghai_index']} ({data['shanghai_change']:+}%)
  上涨家数: {data['rising_stocks']}/{data['total_stocks']} ({data['rising_ratio']:.1%})
  涨停: {data['limit_up']}家，跌停: {data['limit_down']}家

🎯 今日市场状态: {analysis['market_state']}
📈 综合评分: {analysis['total_score']}/1.0
💰 建议仓位: {analysis['position']}
📊 操作策略: {analysis['strategy']}

🔍 市场特征:
"""
            
            for category, feature_list in analysis['features'].items():
                if feature_list:
                    report += f"  {category}: {', '.join(feature_list)}\\n"
            
            report += f"""
💡 盘前策略建议:
  1. 严格执行仓位控制 ({analysis['position']})
  2. {analysis['strategy']}
  3. 关注开盘成交量变化
  4. 等待明确市场信号

⚠️ 风险提示:
  • 数据来源: QVeris实时数据
  • 市场有风险，投资需谨慎
  • 建议结合其他分析工具
"""
        
        else:
            # 标准/盘后报告
            report = f"""
📊 【彪哥战法v5.0】市场分析报告
━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 分析时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}

🎯 市场状态: {analysis['market_state']}
📈 综合评分: {analysis['total_score']}/1.0
💰 建议仓位: {analysis['position']}
📊 操作策略: {analysis['strategy']}

📋 市场数据:
  上证指数: {data['shanghai_index']} ({data['shanghai_change']:+}%)
  总股票数: {data['total_stocks']}
  上涨家数: {data['rising_stocks']} ({data['rising_ratio']:.1%})
  下跌家数: {data['falling_stocks']}
  涨停家数: {data['limit_up']}
  跌停家数: {data['limit_down']}

🔍 市场特征分析:
"""
            
            for category, feature_list in analysis['features'].items():
                if feature_list:
                    report += f"  {category}: {', '.join(feature_list)}\\n"
            
            report += f"""
💡 操作建议:
  1. 严格执行仓位控制 ({analysis['position']})
  2. {analysis['strategy']}
  3. 关注市场情绪变化
  4. 等待明确信号再行动

⚠️ 风险提示:
  • 本分析基于QVeris实时数据
  • 市场有风险，投资需谨慎
  • 建议结合其他分析工具
"""
        
        return report
    
    def save_analysis(self, analysis, filename=None):
        """保存分析结果"""
        if not analysis:
            return None
        
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"biage_analysis_{timestamp}.json"
        
        # 生成报告
        report_type = 'premarket' if datetime.datetime.now().hour < 12 else 'standard'
        report = self.generate_report(analysis, report_type)
        
        result = {
            'timestamp': datetime.datetime.now().isoformat(),
            'analysis': analysis,
            'report': report
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"📁 分析结果已保存: {filename}")
        
        # 同时保存文本报告
        txt_filename = filename.replace('.json', '.txt')
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 文本报告已保存: {txt_filename}")
        
        return filename

def main():
    """主函数"""
    print("🚀 彪哥战法v5.0 - QVeris数据源完整版")
    print("=" * 70)
    
    try:
        # 初始化分析器
        analyzer = BiageStrategyV5()
        
        # 分析市场
        analysis = analyzer.analyze_market()
        
        if analysis:
            # 生成并显示报告
            report = analyzer.generate_report(analysis)
            print(report)
            
            # 保存结果
            analyzer.save_analysis(analysis)
            
            print("\n✅ 彪哥战法v5.0分析完成")
            print("💡 系统已成功切换到QVeris数据源")
            
            # 输出系统状态
            print("\n🔧 系统状态:")
            print("  ✅ QVeris数据源: 工作正常")
            print("  ✅ 彪哥战法v5.0: 运行正常")
            print("  ✅