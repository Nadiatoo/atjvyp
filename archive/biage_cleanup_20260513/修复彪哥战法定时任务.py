#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复彪哥战法定时任务 - 切换到QVeris数据源
"""

import subprocess
import json
import datetime
import os

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def get_cron_jobs():
    """获取当前的定时任务"""
    print("📋 获取当前定时任务...")
    code, stdout, stderr = run_command("openclaw cron list 2>/dev/null")
    
    if code == 0 and stdout:
        print("✅ 获取成功")
        # 解析输出
        lines = stdout.strip().split('\n')
        for line in lines:
            if "彪哥" in line:
                print(f"  发现: {line}")
    else:
        print("❌ 获取失败")
        print(f"  错误: {stderr}")
    
    return code, stdout

def create_qveris_premarket_job():
    """创建使用QVeris的盘前分析任务"""
    
    print("\n🔄 创建QVeris盘前分析任务...")
    
    # 创建新的盘前分析脚本
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彪哥战法盘前分析 - QVeris数据源版本
"""

import os
import sys
import json
import datetime

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from qveris_biage_analyzer import QVerisBiageAnalyzer
    
    print("🚀 彪哥战法盘前分析启动 (QVeris数据源)")
    print("=" * 60)
    
    # 初始化分析器
    analyzer = QVerisBiageAnalyzer()
    
    # 获取市场数据
    print("📊 获取实时市场数据...")
    market_data = analyzer.get_full_market_data()
    
    # 生成盘前分析
    print("🎯 生成盘前分析报告...")
    analysis = analyzer.generate_premarket_analysis(market_data)
    
    # 保存结果
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    output_file = f"/tmp/biage_premarket_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.datetime.now().isoformat(),
            'analysis': analysis,
            'market_data': market_data
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 分析完成，结果已保存: {output_file}")
    
    # 输出摘要
    print(f"\\n📈 市场状态: {analysis.get('market_state', '未知')}")
    print(f"💰 建议仓位: {analysis.get('position', '未知')}")
    print(f"🎯 操作策略: {analysis.get('strategy', '未知')}")
    
except Exception as e:
    print(f"❌ 分析失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
    
    script_path = "/Users/tuqibiao/.openclaw/workspace/biage_premarket_qveris.py"
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 设置执行权限
    run_command(f"chmod +x {script_path}")
    
    print(f"✅ 盘前分析脚本已创建: {script_path}")
    
    # 创建定时任务
    cron_command = f"python3 {script_path}"
    
    # 使用openclaw cron add创建任务
    # 注意：这里需要实际的openclaw cron命令格式
    cron_config = {
        "name": "彪哥战法-盘前分析-QVeris",
        "schedule": {
            "kind": "cron",
            "expr": "0 8 * * 1-5",  # 工作日8:00
            "tz": "Asia/Shanghai"
        },
        "payload": {
            "kind": "agentTurn",
            "message": f"执行彪哥战法盘前分析: {cron_command}",
            "model": "deepseek/deepseek-chat"
        },
        "sessionTarget": "isolated",
        "delivery": {
            "mode": "announce"
        }
    }
    
    config_file = "/tmp/cron_premarket_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(cron_config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 定时任务配置已保存: {config_file}")
    print("💡 需要手动执行: openclaw cron add --job @{config_file}")
    
    return script_path

def create_qveris_aftermarket_job():
    """创建使用QVeris的盘后分析任务"""
    
    print("\n🔄 创建QVeris盘后分析任务...")
    
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彪哥战法盘后分析 - QVeris数据源版本
"""

import os
import sys
import json
import datetime

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from qveris_biage_analyzer import QVerisBiageAnalyzer
    
    print("🚀 彪哥战法盘后分析启动 (QVeris数据源)")
    print("=" * 60)
    
    # 初始化分析器
    analyzer = QVerisBiageAnalyzer()
    
    # 获取当日市场数据
    print("📊 获取当日市场数据...")
    market_data = analyzer.get_full_market_data()
    
    # 生成盘后分析
    print("🎯 生成盘后分析报告...")
    analysis = analyzer.generate_aftermarket_analysis(market_data)
    
    # 保存结果
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    output_file = f"/tmp/biage_aftermarket_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.datetime.now().isoformat(),
            'analysis': analysis,
            'market_data': market_data
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 分析完成，结果已保存: {output_file}")
    
    # 输出摘要
    print(f"\\n📊 当日涨跌: {analysis.get('rising_stocks', 0)}涨 / {analysis.get('falling_stocks', 0)}跌")
    print(f"📈 涨停: {analysis.get('limit_up', 0)}家，跌停: {analysis.get('limit_down', 0)}家")
    print(f"🎯 明日策略: {analysis.get('tomorrow_strategy', '未知')}")
    
except Exception as e:
    print(f"❌ 分析失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
    
    script_path = "/Users/tuqibiao/.openclaw/workspace/biage_aftermarket_qveris.py"
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 设置执行权限
    run_command(f"chmod +x {script_path}")
    
    print(f"✅ 盘后分析脚本已创建: {script_path}")
    
    # 创建定时任务配置
    cron_config = {
        "name": "彪哥战法-盘后分析-QVeris",
        "schedule": {
            "kind": "cron",
            "expr": "0 17 * * 1-5",  # 工作日17:00
            "tz": "Asia/Shanghai"
        },
        "payload": {
            "kind": "agentTurn",
            "message": f"执行彪哥战法盘后分析",
            "model": "deepseek/deepseek-chat"
        },
        "sessionTarget": "isolated",
        "delivery": {
            "mode": "announce"
        }
    }
    
    config_file = "/tmp/cron_aftermarket_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(cron_config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 定时任务配置已保存: {config_file}")
    
    return script_path

def create_qveris_biage_analyzer():
    """创建QVeris彪哥战法分析器"""
    
    print("\n🔧 创建QVeris彪哥战法分析器...")
    
    analyzer_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QVeris彪哥战法分析器 - v5.0数据源集成版
"""

import os
import requests
import json
import datetime
import time
from typing import Dict, List, Optional, Any

class QVerisBiageAnalyzer:
    """彪哥战法v5.0 - QVeris数据源分析器"""
    
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
        
        print(f"✅ QVeris彪哥战法分析器初始化完成")
    
    def _execute_tool(self, tool_id: str, parameters: Dict) -> Optional[Dict]:
        """执行QVeris工具"""
        
        cache_key = f"{tool_id}_{json.dumps(parameters, sort_keys=True)}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                return cache_entry['data']
        
        url = f"{self.base_url}/tools/execute"
        payload = {
            "tool_id": tool_id,
            "parameters": parameters
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                self.cache[cache_key] = {
                    'timestamp': time.time(),
                    'data': result
                }
                return result
            else:
                print(f"❌ 工具调用失败: {tool_id}")
                return None
        except Exception as e:
            print(f"❌ 工具调用异常: {tool_id} - {e}")
            return None
    
    def get_index_data(self) -> Dict:
        """获取指数数据"""
        
        tool_id = "ths_ifind.real_time_quotation.v1"
        parameters = {
            "codes": "000001.SH,399001.SZ,399006.SZ",
            "indicators": "common"
        }
        
        result = self._execute_tool(tool_id, parameters)
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
                                    'change_pct': item.get('changeRatio'),
                                    'volume': item.get('volume'),
                                    'amount': item.get('amount'),
                                    'high': item.get('high'),
                                    'low': item.get('low'),
                                    'open': item.get('open')
                                }
        
        return index_data
    
    def _get_index_name(self, code: str) -> str:
        """获取指数名称"""
        names = {
            "000001.SH": "上证指数",
            "399001.SZ": "深证成指", 
            "399006.SZ": "创业板指"
        }
        return names.get(code, code)
    
    def get_market_statistics(self) -> Dict:
        """获取市场统计数据"""
        
        tool_id = "mcp_gildata.marketlimitupdowncount.v1"
        parameters = {
            "query": "获取今日市场涨跌停家数"
        }
        
        result = self._execute_tool(tool_id, parameters)
        stats = {
            'total': 0,
            'rising': 0,
            'falling': 0,
            'limit_up': 0,
            'limit_down': 0,
            'rising_ratio': 0.0
        }
        
        if result and 'result' in result and 'data' in result['result']:
            data = result['result']['data']
            if 'table_markdown' in data:
                table = data['table_markdown']
                lines = table.strip().split('\\n')
                if len(lines) >= 3:
                    today_data = lines[2].split('|')
                    if len(today_data) >= 9:
                        try:
                            stats['total'] = int(today_data[2].strip())
                            stats['rising'] = int(today_data[3].strip())
                            stats['falling'] = int(today_data[4].strip())
                            stats['limit_up'] = int(today_data[6].strip())
                            stats['limit_down'] = int(today_data[7].strip())
                            
                            if stats['total'] > 0:
                                stats['rising_ratio'] = stats['rising'] / stats['total']
                        except:
                            pass
        
        return stats
    
    def get_full_market_data(self) -> Dict:
        """获取完整市场数据"""
        
        print("📊 采集市场数据...")
        
        market_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'indices': self.get_index_data(),
            'statistics': self.get_market_statistics(),
            'status': 'completed'
        }
        
        print("✅ 数据采集完成")
        return market_data
    
    def analyze_market_state(self, market_data: Dict) -> Dict:
        """分析市场状态（彪哥战法v5.0逻辑）"""
        
        stats = market_data.get('statistics', {})
        indices = market_data.get('indices', {})
        
        # 技术面评分（权重60%）
        tech_score = 0
        tech_features = []
        
        # 检查指数涨跌
        sh_index = indices.get('000001.SH', {})
        if sh_index.get('change_pct', 0) < 0:
            tech_score += 0.2
            tech_features.append("指数下跌")
        
        # 检查市场广度
        rising_ratio = stats.get('rising_ratio', 0)
        if rising_ratio < 0.5:
            tech_score += 0.2
            tech_features.append("普跌行情")
        
        # 检查涨停家数
        if stats.get('limit_up', 0) < 80:
            tech_score += 0.1
            tech_features.append("涨停家数少")
        
        # 检查跌停家数
        if stats.get('limit_down', 0) > 20:
            tech_score += 0.1
            tech_features.append("跌停家数多")
        
        # 情绪面评分（权重13%）
        emotion_score = 0
        if rising_ratio < 0.3:
            emotion_score = 0.13
            emotion_status = "情绪低迷"
        elif rising_ratio < 0.5:
            emotion_score = 0.065
            emotion_status = "情绪中性"
        else:
            emotion_status = "情绪积极"
        
        # 综合评分
        total_score = tech_score * 0.6 + emotion_score
        
        # 状态判断
        if total_score < 0.3:
            market_state = "混沌期"
            position = "0-10%"
            strategy = "空仓等待，观察信号"
        elif total_score < 0.5:
            market_state = "冬藏期"
            position = "10-30%"
            strategy = "防守为主，轻仓观望"
        elif total_score < 0.7:
            market_state = "秋收期"
            position = "30-50%"
            strategy = "逐步减仓，锁定利润"
        elif total_score < 0.85:
            market_state = "春播期"
            position = "50-70%"
            strategy = "分批建仓，布局未来"
        else:
            market_state = "夏长期"
            position = "70-90%"
            strategy = "重仓持有，顺势而为"
        
        return {
            'market_state': market_state,
            'total_score': round(total_score, 3),
            'position': position,
            'strategy': strategy,
            'tech_features': tech_features,
            'emotion_status': emotion_status,
            'rising_ratio': round(rising_ratio, 3),
            'limit_up': stats.get('limit_up', 0),
            'limit_down': stats.get('limit_down', 0)
        }
    
    def generate_premarket_analysis(self, market_data: Dict) -> Dict:
        """生成盘前分析"""
        
        print("🎯 生成盘前分析...")
        
        analysis = self.analyze_market_state(market_data)
        
        #