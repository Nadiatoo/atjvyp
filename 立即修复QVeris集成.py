#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
立即修复彪哥战法系统 - 集成QVeris数据源
"""

import os
import sys
import json
import datetime
import subprocess

print("🚀 立即修复彪哥战法系统 - 集成QVeris数据源")
print("=" * 70)
print(f"开始时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 步骤1: 创建QVeris数据采集器
print("1️⃣ 创建QVeris数据采集器...")

qveris_collector_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QVeris数据采集器 - 彪哥战法v5.0专用
"""

import os
import requests
import json
import datetime
import time

class QVerisCollector:
    def __init__(self):
        self.api_key = os.getenv("QVERIS_API_KEY")
        self.base_url = "https://qveris.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def execute_tool(self, tool_id, parameters):
        """执行QVeris工具"""
        url = f"{self.base_url}/tools/execute"
        payload = {
            "tool_id": tool_id,
            "parameters": parameters
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 请求失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 异常: {e}")
            return None
    
    def get_shanghai_index(self):
        """获取上证指数数据"""
        result = self.execute_tool("ths_ifind.real_time_quotation.v1", {
            "codes": "000001.SH",
            "indicators": "common"
        })
        
        if result and 'result' in result and 'data' in result['result']:
            data = result['result']['data']
            if isinstance(data, list) and len(data) > 0:
                return data[0][0]  # 嵌套结构
        return None
    
    def get_market_stats(self):
        """获取市场统计数据"""
        result = self.execute_tool("mcp_gildata.marketlimitupdowncount.v1", {
            "query": "获取今日市场涨跌停家数"
        })
        
        if result and 'result' in result and 'data' in result['result']:
            return result['result']['data']
        return None
    
    def get_cyb_index(self):
        """获取创业板指数据"""
        result = self.execute_tool("ths_ifind.real_time_quotation.v1", {
            "codes": "399006.SZ",
            "indicators": "common"
        })
        
        if result and 'result' in result and 'data' in result['result']:
            data = result['result']['data']
            if isinstance(data, list) and len(data) > 0:
                return data[0][0]
        return None
    
    def get_all_data(self):
        """获取所有数据"""
        print("📊 采集市场数据...")
        
        data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'shanghai_index': self.get_shanghai_index(),
            'market_stats': self.get_market_stats(),
            'cyb_index': self.get_cyb_index()
        }
        
        print("✅ 数据采集完成")
        return data

# 使用示例
if __name__ == "__main__":
    collector = QVerisCollector()
    data = collector.get_all_data()
    
    # 保存数据
    filename = f"qveris_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"📁 数据已保存: {filename}")
'''

with open("qveris_collector.py", "w", encoding="utf-8") as f:
    f.write(qveris_collector_code)

print("✅ QVeris数据采集器已创建: qveris_collector.py")

# 步骤2: 创建彪哥战法v5.0分析器
print("\n2️⃣ 创建彪哥战法v5.0分析器...")

biage_analyzer_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彪哥战法v5.0分析器 - QVeris数据源版本
"""

import json
import datetime
from qveris_collector import QVerisCollector

class BiageStrategyV5:
    """彪哥战法v5.0分析器"""
    
    def __init__(self):
        self.collector = QVerisCollector()
    
    def parse_market_stats(self, stats_data):
        """解析市场统计数据"""
        if not stats_data or 'table_markdown' not in stats_data:
            return None
        
        table = stats_data['table_markdown']
        lines = table.strip().split('\\n')
        
        if len(lines) >= 3:
            today_line = lines[2]  # 今日数据在第三行
            cells = [cell.strip() for cell in today_line.split('|') if cell.strip()]
            
            if len(cells) >= 9:
                return {
                    'total': int(cells[2]),
                    'rising': int(cells[3]),
                    'falling': int(cells[4]),
                    'unchanged': int(cells[5]),
                    'limit_up': int(cells[6]),
                    'limit_down': int(cells[7])
                }
        
        return None
    
    def analyze(self, market_data):
        """分析市场数据"""
        print("🎯 彪哥战法v5.0分析开始...")
        
        # 解析数据
        sh_index = market_data.get('shanghai_index', {})
        stats = self.parse_market_stats(market_data.get('market_stats'))
        cyb_index = market_data.get('cyb_index', {})
        
        if not stats:
            print("❌ 无法解析市场统计数据")
            return None
        
        # 计算技术面评分
        tech_score = 0
        features = []
        
        # 指数涨跌
        sh_change = sh_index.get('changeRatio', 0)
        if sh_change < 0:
            tech_score += 0.2
            features.append(f"上证指数下跌 {sh_change:.2f}%")
        
        # 市场广度
        rising_ratio = stats['rising'] / stats['total']
        if rising_ratio < 0.5:
            tech_score += 0.2
            features.append(f"普跌行情 (上涨{rising_ratio:.1%})")
        
        # 涨停家数
        if stats['limit_up'] < 80:
            tech_score += 0.1
            features.append(f"涨停家数少 ({stats['limit_up']}家)")
        
        # 跌停家数
        if stats['limit_down'] > 20:
            tech_score += 0.1
            features.append(f"跌停家数多 ({stats['limit_down']}家)")
        
        # 情绪面评分
        if rising_ratio < 0.3:
            emotion_score = 0.13
            emotion = "情绪低迷"
        elif rising_ratio < 0.5:
            emotion_score = 0.065
            emotion = "情绪中性"
        else:
            emotion_score = 0
            emotion = "情绪积极"
        
        # 综合评分
        total_score = tech_score * 0.6 + emotion_score
        
        # 状态判断
        if total_score < 0.3:
            state = "混沌期"
            position = "0-10%"
            strategy = "空仓等待"
        elif total_score < 0.5:
            state = "冬藏期"
            position = "10-30%"
            strategy = "防守为主"
        elif total_score < 0.7:
            state = "秋收期"
            position = "30-50%"
            strategy = "逐步减仓"
        elif total_score < 0.85:
            state = "春播期"
            position = "50-70%"
            strategy = "分批建仓"
        else:
            state = "夏长期"
            position = "70-90%"
            strategy = "重仓持有"
        
        analysis = {
            'timestamp': datetime.datetime.now().isoformat(),
            'market_state': state,
            'total_score': round(total_score, 3),
            'position': position,
            'strategy': strategy,
            'features': features,
            'emotion': emotion,
            'data_summary': {
                'shanghai_index': round(sh_index.get('latest', 0), 2),
                'shanghai_change': round(sh_change, 2),
                'total_stocks': stats['total'],
                'rising_stocks': stats['rising'],
                'falling_stocks': stats['falling'],
                'limit_up': stats['limit_up'],
                'limit_down': stats['limit_down'],
                'rising_ratio': round(rising_ratio, 3)
            }
        }
        
        print("✅ 分析完成")
        return analysis
    
    def generate_report(self, analysis):
        """生成分析报告"""
        if not analysis:
            return "❌ 分析失败"
        
        report = f"""
📊 【彪哥战法v5.0】市场分析报告
━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 分析时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}

🎯 市场状态: {analysis['market_state']}
📈 综合评分: {analysis['total_score']}/1.0
💰 建议仓位: {analysis['position']}
📊 操作策略: {analysis['strategy']}

📋 市场特征:
"""
        
        for feature in analysis['features']:
            report += f"  • {feature}\\n"
        
        report += f"  • 市场情绪: {analysis['emotion']}\\n"
        
        data = analysis['data_summary']
        report += f"""
📊 数据摘要:
  上证指数: {data['shanghai_index']} ({data['shanghai_change']}%)
  总股票数: {data['total_stocks']}
  上涨家数: {data['rising_stocks']} ({data['rising_ratio']:.1%})
  下跌家数: {data['falling_stocks']}
  涨停家数: {data['limit_up']}
  跌停家数: {data['limit_down']}

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

# 使用示例
if __name__ == "__main__":
    print("🚀 彪哥战法v5.0分析器启动")
    print("=" * 60)
    
    analyzer = BiageStrategyV5()
    
    # 获取数据
    market_data = analyzer.collector.get_all_data()
    
    # 分析数据
    analysis = analyzer.analyze(market_data)
    
    if analysis:
        # 生成报告
        report = analyzer.generate_report(analysis)
        print(report)
        
        # 保存结果
        filename = f"biage_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.datetime.now().isoformat(),
                'market_data': market_data,
                'analysis': analysis,
                'report': report
            }, f, ensure_ascii=False, indent=2)
        
        print(f"📁 分析结果已保存: {filename}")
    else:
        print("❌ 分析失败")
'''

with open("biage_analyzer_v5_qveris.py", "w", encoding="utf-8") as f:
    f.write(biage_analyzer_code)

print("✅ 彪哥战法v5.0分析器已创建: biage_analyzer_v5_qveris.py")

# 步骤3: 创建定时任务脚本
print("\n3️⃣ 创建定时任务执行脚本...")

cron_script_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彪哥战法定时任务执行脚本 - QVeris版本
"""

import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_premarket():
    """执行盘前分析"""
    print("🌅 执行彪哥战法盘前分析...")
    
    try:
        from biage_analyzer_v5_qveris import BiageStrategyV5
        
        analyzer = BiageStrategyV5()
        market_data = analyzer.collector.get_all_data()
        analysis = analyzer.analyze(market_data)
        
        if analysis:
            report = analyzer.generate_report(analysis)
            print("\\n" + "="*60)
            print("📈 盘前分析结果:")
            print("="*60)
            print(report)
            
            # 保存到文件
            import datetime
            filename = f"/tmp/biage_premarket_{datetime.datetime.now().strftime('%Y%m%d')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"✅ 盘前分析已保存: {filename}")
            return True
        else:
            print("❌ 盘前分析失败")
            return False
            
    except Exception as e:
        print(f"❌ 盘前分析异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_aftermarket():
    """执行盘后分析"""
    print("🌇 执行彪哥战法盘后分析...")
    
    try:
        from biage_analyzer_v5_qveris import BiageStrategyV5
        
        analyzer = BiageStrategyV5()
        market_data = analyzer.collector.get_all_data()
        analysis = analyzer.analyze(market_data)
        
        if analysis:
            # 盘后分析增加更多内容
            report = analyzer.generate_report(analysis)
            
            # 添加盘后特有内容
            enhanced_report = report + f"""
📊 盘后总结:
  • 当日分析完成
  • 数据已保存
  • 明日策略已生成

🎯 明日重点关注:
  1. 观察成交量变化
  2. 关注市场情绪指标
  3. 严格执行仓位控制
  4. 等待明确市场信号
"""
            
            print("\\n" + "="*60)
            print("📊 盘后分析结果:")
            print("="*60)
            print(enhanced_report)
            
            # 保存到文件
            import datetime
            filename = f"/tmp/biage_aftermarket_{datetime.datetime.now().strftime('%Y%m%d')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(enhanced_report)
            
            print(f"✅ 盘后分析已保存: {filename}")
            return True
        else:
            print("❌ 盘后分析失败")
            return False
            
    except Exception as e:
        print(f"❌ 盘后分析异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 biage_cron_qveris.py [premarket|aftermarket]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "premarket":
        success = run_premarket()
        sys.exit(0 if success else 1)
    elif command == "aftermarket":
        success = run_aftermarket()
        sys.exit(0 if success else 1)
    else:
        print(f"未知命令: {command}")
        sys.exit(1)
'''

with open("biage_cron_qveris.py", "w", encoding="utf-8") as f:
    f.write(cron_script_code)

# 设置执行权限
os.chmod("biage_cron_qveris.py", 0o755)

print("✅ 定时任务脚本已创建: biage_cron_qveris.py")

# 步骤4: 测试新系统
print("\n4️⃣ 测试新系统...")

print("🔧 测试QVeris数据采集...")
test_code = '''
import sys
sys.path.append(".")
from qveris_collector import QVerisCollector

collector = QVerisCollector()
data = collector.get_all_data()

if data and data.get("shanghai_index"):
    print("✅ QVeris数据采集测试成功")
    print(f"上证指数: {data['shanghai_index'].get('latest')}")
else:
    print("❌ QVeris数据采集测试失败")
'''

# 执行测试
try:
    import subprocess
    result = subprocess.run([sys.executable, "-c", test_code], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"错误: {result.stderr}")
except Exception as e:
    print(f"测试异常: {e}")

# 步骤5: 创建修复定时任务的说明
print("\n5️⃣ 创建修复指南...")

repair_guide = """
📋 彪哥战法系统修复指南 - QVeris数据源集成
==========================================

✅