#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实际调用QVeris工具获取A股市场数据
"""

import os
import requests
import json
import datetime

# QVeris API配置
QVERIS_API_KEY = os.getenv("QVERIS_API_KEY", "sk-PYDj7ulDpbYUtxeXnKeUzKLzMjS2IdTZ6N-2uYbX5bo")
QVERIS_API_URL = "https://qveris.ai/api/v1/tools/execute"

def execute_qveris_tool(tool_id, parameters):
    """执行QVeris工具"""
    
    headers = {
        "Authorization": f"Bearer {QVERIS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "tool_id": tool_id,
        "parameters": parameters
    }
    
    try:
        print(f"🔄 调用工具: {tool_id}")
        print(f"参数: {json.dumps(parameters, ensure_ascii=False)}")
        
        response = requests.post(
            QVERIS_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 调用成功")
            return result
        else:
            print(f"❌ 调用失败 (状态码: {response.status_code})")
            print(f"错误信息: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"❌ 调用异常: {e}")
        return None

def get_shanghai_composite_index():
    """获取上证指数实时数据"""
    
    tool_id = "ths_ifind.real_time_quotation.v1"
    
    # 上证指数代码: 000001.SH
    parameters = {
        "codes": "000001.SH",
        "indicators": "common"  # 常用指标
    }
    
    result = execute_qveris_tool(tool_id, parameters)
    
    if result:
        print("\n📊 上证指数实时数据:")
        print("-" * 40)
        
        # 解析结果
        if 'result' in result and 'data' in result['result']:
            data = result['result']['data']
            
            # 尝试不同的数据格式
            if isinstance(data, list) and len(data) > 0:
                stock_data = data[0]
                print(f"代码: {stock_data.get('thscode', 'N/A')}")
                print(f"名称: {stock_data.get('security_name', 'N/A')}")
                print(f"最新价: {stock_data.get('lastest_price', 'N/A')}")
                print(f"涨跌幅: {stock_data.get('changeRatio', 'N/A')}%")
                print(f"成交量: {stock_data.get('volume', 'N/A')}")
                print(f"成交额: {stock_data.get('amount', 'N/A')}")
            else:
                print(f"原始数据: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
        else:
            print(f"完整响应: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
    
    return result

def get_market_up_down_count():
    """获取市场涨跌停家数"""
    
    tool_id = "mcp_gildata.marketlimitupdowncount.v1"
    
    parameters = {
        "query": "获取今日市场涨跌停家数"
    }
    
    result = execute_qveris_tool(tool_id, parameters)
    
    if result:
        print("\n📈 市场涨跌停家数:")
        print("-" * 40)
        
        if 'result' in result and 'data' in result['result']:
            data = result['result']['data']
            print(f"数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"完整响应: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
    
    return result

def get_northbound_capital_flow():
    """获取北向资金数据"""
    
    tool_id = "mcp_gildata.astockcashflow.v1"
    
    # 获取上证指数和深证成指的北向资金数据
    parameters = {
        "query": "获取今日北向资金流向数据"
    }
    
    result = execute_qveris_tool(tool_id, parameters)
    
    if result:
        print("\n💰 北向资金数据:")
        print("-" * 40)
        
        if 'result' in result and 'data' in result['result']:
            data = result['result']['data']
            print(f"数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"完整响应: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
    
    return result

def get_market_money_flow():
    """获取市场资金流向"""
    
    tool_id = "ths_ifind.money_flow.v1"
    
    # 获取市场指数资金流
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    parameters = {
        "scope": "market",
        "codes": "000001.SH,399001.SZ",  # 上证指数和深证成指
        "startdate": today,
        "enddate": today
    }
    
    result = execute_qveris_tool(tool_id, parameters)
    
    if result:
        print("\n💸 市场资金流向:")
        print("-" * 40)
        
        if 'result' in result and 'data' in result['result']:
            data = result['result']['data']
            print(f"数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"完整响应: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
    
    return result

def test_all_market_data():
    """测试所有市场数据获取"""
    
    print("🚀 QVeris实际获取市场数据测试")
    print("=" * 60)
    print(f"测试时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API密钥: {QVERIS_API_KEY[:10]}...{QVERIS_API_KEY[-10:]}")
    print()
    
    results = {}
    
    # 1. 上证指数数据
    print("1️⃣ 测试上证指数数据获取")
    results['shanghai_index'] = get_shanghai_composite_index()
    
    print("\n" + "="*60)
    
    # 2. 市场涨跌停家数
    print("2️⃣ 测试市场涨跌停家数获取")
    results['market_up_down'] = get_market_up_down_count()
    
    print("\n" + "="*60)
    
    # 3. 北向资金数据
    print("3️⃣ 测试北向资金数据获取")
    results['northbound_flow'] = get_northbound_capital_flow()
    
    print("\n" + "="*60)
    
    # 4. 市场资金流向
    print("4️⃣ 测试市场资金流向获取")
    results['money_flow'] = get_market_money_flow()
    
    # 保存结果
    output_file = f"QVeris实际市场数据_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.datetime.now().isoformat(),
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 测试结果已保存至: {output_file}")
    
    # 分析结果
    print("\n📋 结果分析")
    print("=" * 60)
    
    success_count = sum(1 for r in results.values() if r is not None)
    total_count = len(results)
    
    print(f"总测试数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    if success_count > 0:
        print("\n✅ QVeris可以实际获取市场数据！")
        print("💡 建议立即集成到彪哥战法v5.0系统")
    else:
        print("\n❌ QVeris无法获取数据，需要进一步排查")
    
    return results

def create_qveris_data_module():
    """创建QVeris数据采集模块"""
    
    print("\n🔧 创建QVeris数据采集模块")
    print("=" * 60)
    
    module_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QVeris数据采集模块 - 用于彪哥战法v5.0系统
"""

import os
import requests
import json
import datetime
import time
from typing import Dict, List, Optional, Any

class QVerisDataCollector:
    """QVeris数据采集器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("QVERIS_API_KEY")
        if not self.api_key:
            raise ValueError("QVERIS_API_KEY未设置")
        
        self.base_url = "https://qveris.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 数据缓存
        self.cache = {}
        self.cache_ttl = 300  # 5分钟缓存
        
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
    
    def get_index_data(self, index_codes: List[str] = None) -> Dict:
        """获取指数数据"""
        
        if index_codes is None:
            index_codes = ["000001.SH", "399001.SZ", "399006.SZ"]  # 上证、深证、创业板
        
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
        
        if isinstance(raw_data, list):
            for item in raw_data:
                code = item.get('thscode', '')
                name = item.get('security_name', '')
                
                index_data[code] = {
                    'name': name,
                    'latest_price': item.get('lastest_price'),
                    'change': item.get('change'),
                    'change_ratio': item.get('changeRatio'),
                    'volume': item.get('volume'),
                    'amount': item.get('amount'),
                    'high': item.get('high'),
                    'low': item.get('low'),
                    'open': item.get('open'),
                    'pre_close': item.get('preClose'),
                    'timestamp': datetime.datetime.now().isoformat()
                }
        
        return index_data
    
    def get_market_statistics(self) -> Dict:
        """获取市场统计数据（涨跌停家数）"""
        
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
        
        # 这里需要根据实际返回格式进行解析
        # 暂时返回原始数据
        return {
            'raw_data': raw_data,
            'timestamp': datetime.datetime.now().isoformat()
        }
    
    def get_northbound_flow(self) -> Dict:
        """获取北向资金数据"""
        
        tool_id = "mcp_gildata.astockcashflow.v1"
        parameters = {
            "query": "获取今日北向资金流向"
        }
        
        result = self._execute_tool(tool_id, parameters)
        if result and 'result' in result and 'data' in result['result']:
            return self._parse_northbound_data(result['result']['data'])
        
        return {}
    
    def _parse_northbound_data(self, raw_data: Any) -> Dict:
        """解析北向资金数据"""
        
        return {
            'raw_data': raw_data,
            'timestamp': datetime.datetime.now().isoformat()
        }
    
    def get_full_market_data(self) -> Dict:
        """获取完整的市场数据"""
        
        print("📊 开始获取完整市场数据...")
        
        market_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'indices': {},
            'statistics': {},
            'northbound': {},
            'status': 'collecting'
        }
        
        try:
            # 1. 获取指数数据
            print("  1. 获取指数数据...")
            market_data['indices'] = self.get_index_data()
            
            # 2. 获取市场统计数据
            print("  2. 获取市场统计数据...")
            market_data['statistics'] = self.get_market_statistics()
            
            # 3. 获取北向资金数据
            print("  3. 获取北向资金数据...")
            market_data['northbound'] = self.get_northbound_flow()
            
            market_data['status'] = 'completed'
            print("✅ 市场数据获取完成")
            
        except Exception as e:
            market_data['status'] = 'error'
            market_data['error'] = str(e)
            print(f"❌ 数据获取失败: {e}")
        
        return market_data
    
    def save_to_file(self, data: Dict, filename: str = None):
        """保存数据到文件"""
        
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"market_data_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 数据已保存至: {filename}")
        return filename

# 使用示例
if __name__ == "__main__":
    # 初始化采集器
    collector = QVerisDataCollector()
    
    # 获取完整市场数据
    market_data = collector.get_full_market_data()
    
    # 保存数据