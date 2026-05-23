#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QVeris数据采集模块 - 彪哥战法v5.0专用
2026年3月26日创建
"""

import os
import requests
import json
import datetime
import time
from typing import Dict, List, Optional, Any
import pandas as pd

class QVerisDataCollector:
    """QVeris数据采集器 - 用于彪哥战法v5.0系统"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("QVERIS_API_KEY")
        if not self.api_key:
            raise ValueError("QVERIS_API_KEY环境变量未设置")
        
        self.base_url = "https://qveris.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 数据缓存
        self.cache = {}
        self.cache_ttl = 300  # 5分钟缓存
        
        print(f"✅ QVeris数据采集器初始化完成")
        print(f"   剩余额度: {self.get_remaining_credits()}")
    
    def _execute_tool(self, tool_id: str, parameters: Dict) -> Optional[Dict]:
        """执行QVeris工具"""
        
        # 检查缓存
        cache_key = f"{tool_id}_{json.dumps(parameters, sort_keys=True)}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                print(f"📦 使用缓存数据: {tool_id}")
                return cache_entry['data']
        
        url = f"{self.base_url}/tools/execute"
        payload = {
            "tool_id": tool_id,
            "parameters": parameters
        }
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # 缓存结果
                self.cache[cache_key] = {
                    'timestamp': time.time(),
                    'data': result
                }
                return result
            else:
                print(f"❌ 工具调用失败: {tool_id} (状态码: {response.status_code})")
                return None
                
        except Exception as e:
            print(f"❌ 工具调用异常: {tool_id} - {e}")
            return None
    
    def get_remaining_credits(self) -> float:
        """获取剩余额度"""
        # 通过一个简单的查询获取额度信息
        tool_id = "ths_ifind.real_time_quotation.v1"
        parameters = {
            "codes": "000001.SH",
            "indicators": "common"
        }
        
        result = self._execute_tool(tool_id, parameters)
        if result and 'remaining_credits' in result:
            return result['remaining_credits']
        return 0.0
    
    def get_index_data(self, index_codes: List[str] = None) -> Dict:
        """获取指数数据"""
        
        if index_codes is None:
            index_codes = ["000001.SH", "399001.SZ", "399006.SZ"]  # 上证、深证、创业板
        
        print(f"📈 获取指数数据: {', '.join(index_codes)}")
        
        tool_id = "ths_ifind.real_time_quotation.v1"
        parameters = {
            "codes": ",".join(index_codes),
            "indicators": "common"
        }
        
        result = self._execute_tool(tool_id, parameters)
        if result and 'result' in result and 'data' in result['result']:
            return self._parse_index_data(result['result']['data'])
        
        return {}
    
    def _parse_index_data(self, raw_data: Any) -> Dict:
        """解析指数数据"""
        
        index_data = {}
        
        if isinstance(raw_data, list) and len(raw_data) > 0:
            data_list = raw_data[0]  # 第一层是列表
            if isinstance(data_list, list):
                for item in data_list:
                    if isinstance(item, dict):
                        code = item.get('thscode', '')
                        if code:
                            index_data[code] = {
                                'name': self._get_index_name(code),
                                'latest_price': item.get('latest'),
                                'change': item.get('change'),
                                'change_ratio': item.get('changeRatio'),
                                'volume': item.get('volume'),
                                'amount': item.get('amount'),
                                'high': item.get('high'),
                                'low': item.get('low'),
                                'open': item.get('open'),
                                'pre_close': item.get('preClose'),
                                'trade_date': item.get('tradeDate'),
                                'trade_time': item.get('tradeTime'),
                                'timestamp': datetime.datetime.now().isoformat()
                            }
        
        return index_data
    
    def _get_index_name(self, code: str) -> str:
        """根据代码获取指数名称"""
        index_names = {
            "000001.SH": "上证指数",
            "399001.SZ": "深证成指",
            "399006.SZ": "创业板指",
            "000300.SH": "沪深300",
            "000905.SH": "中证500",
            "000852.SH": "中证1000"
        }
        return index_names.get(code, code)
    
    def get_market_statistics(self) -> Dict:
        """获取市场统计数据（涨跌停家数）"""
        
        print("📊 获取市场统计数据...")
        
        tool_id = "mcp_gildata.marketlimitupdowncount.v1"
        parameters = {
            "query": "获取今日市场涨跌停家数"
        }
        
        result = self._execute_tool(tool_id, parameters)
        if result and 'result' in result and 'data' in result['result']:
            return self._parse_market_stats(result['result']['data'])
        
        return {}
    
    def _parse_market_stats(self, raw_data: Any) -> Dict:
        """解析市场统计数据"""
        
        stats = {
            'total_stocks': 0,
            'rising_stocks': 0,
            'falling_stocks': 0,
            'unchanged_stocks': 0,
            'limit_up_stocks': 0,
            'limit_down_stocks': 0,
            'rising_ratio': 0.0,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        try:
            if isinstance(raw_data, dict) and 'table_markdown' in raw_data:
                table_md = raw_data['table_markdown']
                
                # 解析Markdown表格的第一行（今日数据）
                lines = table_md.strip().split('\n')
                if len(lines) >= 3:  # 表头 + 分隔线 + 数据行
                    data_line = lines[2]  # 第三行是今日数据
                    cells = [cell.strip() for cell in data_line.split('|') if cell.strip()]
                    
                    if len(cells) >= 9:
                        stats['total_stocks'] = int(cells[2]) if cells[2].isdigit() else 0
                        stats['rising_stocks'] = int(cells[3]) if cells[3].isdigit() else 0
                        stats['falling_stocks'] = int(cells[4]) if cells[4].isdigit() else 0
                        stats['unchanged_stocks'] = int(cells[5]) if cells[5].isdigit() else 0
                        stats['limit_up_stocks'] = int(cells[6]) if cells[6].isdigit() else 0
                        stats['limit_down_stocks'] = int(cells[7]) if cells[7].isdigit() else 0
                        
                        if stats['total_stocks'] > 0:
                            stats['rising_ratio'] = stats['rising_stocks'] / stats['total_stocks']
                
                # 保存原始数据供参考
                stats['raw_table'] = table_md
        
        except Exception as e:
            print(f"⚠️ 解析市场统计数据时出错: {e}")
            stats['error'] = str(e)
        
        return stats
    
    def get_northbound_flow(self) -> Dict:
        """获取北向资金数据"""
        
        print("💰 获取北向资金数据...")
        
        # 注意：这个工具可能需要不同的参数格式
        # 先尝试简单的查询
        tool_id = "mcp_gildata.astockcashflow.v1"
        parameters = {
            "query": "获取今日北向资金流向"
        }
        
        result = self._execute_tool(tool_id, parameters)
        
        northbound_data = {
            'shanghai_flow': 0.0,
            'shenzhen_flow': 0.0,
            'total_flow': 0.0,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        if result:
            # 这里需要根据实际返回格式解析
            # 暂时保存原始数据
            northbound_data['raw_data'] = result
        
        return northbound_data
    
    def get_market_money_flow(self) -> Dict:
        """获取市场资金流向"""
        
        print("💸 获取市场资金流向数据...")
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        tool_id = "ths_ifind.money_flow.v1"
        parameters = {
            "scope": "market",
            "codes": "000001.SH,399001.SZ",
            "startdate": today,
            "enddate": today
        }
        
        result = self._execute_tool(tool_id, parameters)
        
        money_flow = {
            'main_net_inflow': 0.0,
            'large_net_inflow': 0.0,
            'medium_net_inflow': 0.0,
            'small_net_inflow': 0.0,
            'total_turnover': 0.0,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        if result:
            money_flow['raw_data'] = result
        
        return money_flow
    
    def get_full_market_data(self) -> Dict:
        """获取完整的市场数据（彪哥战法v5.0所需）"""
        
        print("\n" + "="*60)
        print("🚀 彪哥战法v5.0 - 实时市场数据采集")
        print("="*60)
        print(f"采集时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        market_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'indices': {},
            'statistics': {},
            'northbound': {},
            'money_flow': {},
            'status': 'collecting'
        }
        
        try:
            # 1. 获取指数数据
            print("1️⃣ 获取指数数据...")
            market_data['indices'] = self.get_index_data()
            
            # 2. 获取市场统计数据
            print("2️⃣ 获取市场统计数据...")
            market_data['statistics'] = self.get_market_statistics()
            
            # 3. 获取北向资金数据
            print("3️⃣ 获取北向资金数据...")
            market_data['northbound'] = self.get_northbound_flow()
            
            # 4. 获取资金流向数据
            print("4️⃣ 获取资金流向数据...")
            market_data['money_flow'] = self.get_market_money_flow()
            
            market_data['status'] = 'completed'
            market_data['remaining_credits'] = self.get_remaining_credits()
            
            print("\n✅ 市场数据采集完成")
            print(f"   剩余额度: {market_data.get('remaining_credits', 0)}")
            
        except Exception as e:
            market_data['status'] = 'error'
            market_data['error'] = str(e)
            print(f"\n❌ 数据采集失败: {e}")
        
        return market_data
    
    def format_for_biage_strategy(self, market_data: Dict) -> Dict:
        """格式化为彪哥战法v5.0所需格式"""
        
        formatted = {
            'timestamp': market_data.get('timestamp', ''),
            'market_state': {},
            'technical_features': {},
            'fund_features': {},
            'emotion_features': {},
            'macro_features': {},
            'recommendations': {}
        }
        
        # 提取指数数据
        indices = market_data.get('indices', {})
        if '000001.SH' in indices:
            sh_index = indices['000001.SH']
            formatted['market_state']['shanghai_index'] = {
                'price': sh_index.get('latest_price'),
                'change_pct': sh_index.get('change_ratio'),
                'volume': sh_index.get('volume'),
                'amount': sh_index.get('amount')
            }
        
        # 提取市场统计数据
        stats = market_data.get('statistics', {})
        formatted['technical_features'] = {
            'total_stocks': stats.get('total_stocks', 0),
            'rising_stocks': stats.get('rising_stocks', 0),
            'falling_stocks': stats.get('falling_stocks', 0),
            'limit_up_stocks': stats.get('limit_up_stocks', 0),
            'limit_down_stocks': stats.get('limit_down_stocks', 0),
            'rising_ratio': stats.get('rising_ratio', 0.0)
        }
        
        # 提取资金数据
        northbound = market_data.get('northbound', {})
        money_flow = market_data.get('money_flow', {})
        
        formatted['fund_features'] = {
            'northbound_flow': northbound.get('total_flow', 0.0),
            'main_net_inflow': money_flow.get('main_net_inflow', 0.0)
        }
        
        # 计算情绪特征
        rising_ratio = stats.get('rising_ratio', 0.0)
        limit_up_ratio = stats.get('limit_up_stocks', 0) / max(stats.get('total_stocks', 1), 1)
        limit_down_ratio = stats.get('limit_down_stocks', 0) / max(stats.get('total_stocks', 1), 1)
        
        formatted['emotion_features'] = {
            'market_sentiment': rising_ratio,  # 上涨比例反映情绪
            'speculative_heat': limit_up_ratio,  # 涨停比例反映投机热度
            'panic_level': limit_down_ratio,  # 跌停比例反映恐慌程度
            'sentiment_score': (rising_ratio * 0.6 + (1 - limit_down_ratio) * 0.4)  # 综合情绪得分
        }
        
        return formatted
    
    def save_to_file(self, data: Dict, filename: str = None):
        """保存数据到文件"""
        
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"market_data_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 数据已保存至: {filename}")
        return filename
    
    def print_summary(self, market_data: Dict):
        """打印数据摘要"""
        
        print("\n" + "="*60)
        print("📋 市场数据摘要")
        print("="*60)
        
        # 指数数据
        indices = market_data.get('indices', {})
        if indices:
            print("📈 指数表现:")
            for code, data in indices.items():
                name = data.get('name', code)
                price = data.get('latest_price', 0)
                change = data.get('change', 0)
                change_pct = data.get('change_ratio', 0)
                
                change_icon = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➖"
                print(f"  {change_icon} {name}: {price:.2f} ({change_pct:+.2f}%)")
        
        # 市场统计
        stats = market_data.get('statistics', {})
        if stats:
            print(f"\n📊 市场广度:")
            total = stats.get('total_stocks', 0)
            rising = stats.get('rising_stocks', 0)
            falling = stats.get('falling_stocks', 0)
            limit_up = stats.get('limit_up_stocks', 0)
            limit_down = stats.get('limit_down_stocks', 0)
            rising_ratio = stats.get('rising_ratio', 0.0)
            
            print(f"  总股票数: {total}")
            print(f"  上涨: {rising} ({rising_ratio:.1%})")
            print(f"  下跌: {falling} ({(falling/total