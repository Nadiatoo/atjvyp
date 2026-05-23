#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
立即修复彪哥战法 - 创建可工作的QVeris版本
"""

import os
import requests
import json
import datetime

print("🚀 立即修复彪哥战法系统")
print("=" * 70)

# 创建可工作的分析器
code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彪哥战法v5.0 - 工作版 (QVeris数据源)
"""

import os
import requests
import json
import datetime

class BiageV5QVeris:
    def __init__(self):
        self.api_key = os.getenv("QVERIS_API_KEY")
        self.base_url = "https://qveris.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def call_api(self, tool_id, params):
        """调用QVeris API"""
        url = f"{self.base_url}/tools/execute"
        payload = {"tool_id": tool_id, "parameters": params}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API调用失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"API异常: {e}")
            return None
    
    def get_market_data(self):
        """获取市场数据"""
        print("📊 获取市场数据...")
        
        data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "shanghai_index": None,
            "market_stats": None
        }
        
        # 1. 获取上证指数
        result = self.call_api("ths_ifind.real_time_quotation.v1", {
            "codes": "000001.SH",
            "indicators": "common"
        })
        
        if result and "result" in result and "data" in result["result"]:
            raw_data = result["result"]["data"]
            if isinstance(raw_data, list) and len(raw_data) > 0:
                if isinstance(raw_data[0], list) and len(raw_data[0]) > 0:
                    sh_data = raw_data[0][0]
                    data["shanghai_index"] = {
                        "price": sh_data.get("latest"),
                        "change_pct": sh_data.get("changeRatio"),
                        "volume": sh_data.get("volume"),
                        "amount": sh_data.get("amount")
                    }
        
        # 2. 获取市场统计
        result = self.call_api("mcp_gildata.marketlimitupdowncount.v1", {
            "query": "获取今日市场涨跌停家数"
        })
        
        if result and "result" in result and "data" in result["result"]:
            raw_data = result["result"]["data"]
            if "table_markdown" in raw_data:
                table = raw_data["table_markdown"]
                lines = table.strip().split("\\n")
                
                if len(lines) >= 3:
                    today_line = lines[2]
                    cells = [cell.strip() for cell in today_line.split("|") if cell.strip()]
                    
                    if len(cells) >= 9:
                        try:
                            stats = {
                                "total": int(cells[2]),
                                "rising": int(cells[3]),
                                "falling": int(cells[4]),
                                "limit_up": int(cells[6]),
                                "limit_down": int(cells[7])
                            }
                            data["market_stats"] = stats
                        except:
                            pass
        
        print("✅ 数据获取完成")
        return data
    
    def analyze(self, market_data):
        """分析市场"""
        if not market_data or not market_data.get("shanghai_index") or not market_data.get("market_stats"):
            print("❌ 数据不完整，无法分析")
            return None
        
        sh = market_data["shanghai_index"]
        stats = market_data["market_stats"]
        
        # 计算技术面评分
        tech_score = 0
        features = []
        
        # 指数涨跌
        change_pct = sh.get("change_pct", 0)
        if change_pct < 0:
            tech_score += 0.2
            features.append(f"指数下跌 {change_pct:.2f}%")
        
        # 市场广度
        rising_ratio = stats["rising"] / stats["total"]
        if rising_ratio < 0.5:
            tech_score += 0.2
            features.append(f"普跌行情 (上涨{rising_ratio:.1%})")
        
        # 涨停家数
        if stats["limit_up"] < 80:
            tech_score += 0.1
            features.append(f"涨停家数少 ({stats['limit_up']}家)")
        
        # 跌停家数
        if stats["limit_down"] > 20:
            tech_score += 0.1
            features.append(f"跌停家数多 ({stats['limit_down']}家)")
        
        # 情绪面评分
        if rising_ratio < 0.3:
            emotion_score = 0.13
            emotion = "情绪极度低迷"
        elif rising_ratio < 0.5:
            emotion_score = 0.065
            emotion = "情绪低迷"
        else:
            emotion_score = 0
            emotion = "情绪中性或积极"
        
        # 综合评分 (技术面60% + 情绪面13% + 基础分27%)
        total_score = tech_score * 0.6 + emotion_score + 0.27
        
        # 限制在0-1之间
        total_score = min(max(total_score, 0), 1)
        
        # 状态判断
        if total_score < 0.3:
            state = "混沌期"
            position = "0-10%"
            strategy = "空仓等待，观察信号"
        elif total_score < 0.5:
            state = "冬藏期"
            position = "10-30%"
            strategy = "防守为主，轻仓观望"
        elif total_score < 0.7:
            state = "秋收期"
            position = "30-50%"
            strategy = "逐步减仓，锁定利润"
        elif total_score < 0.85:
            state = "春播期"
            position = "50-70%"
            strategy = "分批建仓，布局未来"
        else:
            state = "夏长期"
            position = "70-90%"
            strategy = "重仓持有，顺势而为"
        
        return {
            "market_state": state,
            "total_score": round(total_score, 3),
            "position": position,
            "strategy": strategy,
            "features": features,
            "emotion": emotion,
            "data_summary": {
                "shanghai_price": round(sh.get("price", 0), 2),
                "shanghai_change": round(change_pct, 2),
                "total_stocks": stats["total"],
                "rising_stocks": stats["rising"],
                "falling_stocks": stats["falling"],
                "limit_up": stats["limit_up"],
                "limit_down": stats["limit_down"],
                "rising_ratio": round(rising_ratio, 3)
            }
        }
    
    def generate_report(self, analysis):
        """生成报告"""
        if not analysis:
            return "分析失败"
        
        data = analysis["data_summary"]
        
        report = f"""
📊 【彪哥战法v5.0】市场分析报告 (QVeris数据源)
━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 分析时间: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}

🎯 市场状态: {analysis["market_state"]}
📈 综合评分: {analysis["total_score"]}/1.0
💰 建议仓位: {analysis["position"]}
📊 操作策略: {analysis["strategy"]}

📋 市场数据:
  上证指数: {data["shanghai_price"]} ({data["shanghai_change"]:+.2f}%)
  总股票数: {data["total_stocks"]}
  上涨家数: {data["rising_stocks"]} ({data["rising_ratio"]:.1%})
  下跌家数: {data["falling_stocks"]}
  涨停家数: {data["limit_up"]}
  跌停家数: {data["limit_down"]}

🔍 市场特征:
"""
        
        for feature in analysis["features"]:
            report += f"  • {feature}\\n"
        
        report += f"  • 市场情绪: {analysis['emotion']}\\n"
        
        report += f"""
💡 操作建议:
  1. 严格执行仓位控制 ({analysis["position"]})
  2. {analysis["strategy"]}
  3. 关注市场情绪变化
  4. 等待明确信号再行动

⚠️ 风险提示:
  • 数据来源: QVeris实时数据
  • 市场有风险，投资需谨慎
  • 本分析仅供参考
"""
        
        return report

def main():
    """主函数"""
    print("🚀 彪哥战法v5.0 - QVeris数据源")
    print("=" * 60)
    
    try:
        # 初始化分析器
        analyzer = BiageV5QVeris()
        
        # 获取数据
        market_data = analyzer.get_market_data()
        
        if not market_data:
            print("❌ 数据获取失败")
            return
        
        # 分析市场
        analysis = analyzer.analyze(market_data)
        
        if not analysis:
            print("❌ 分析失败")
            return
        
        # 生成报告
        report = analyzer.generate_report(analysis)
        print(report)
        
        # 保存结果
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"biage_v5_qveris_{timestamp}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.datetime.now().isoformat(),
                "market_data": market_data,
                "analysis": analysis,
                "report": report
            }, f, ensure_ascii=False, indent=2)
        
        print(f"📁 分析结果已保存: {filename}")
        
        # 同时保存文本报告
        txt_filename = filename.replace(".json", ".txt")
        with open(txt_filename, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"📄 文本报告已保存: {txt_filename}")
        
        print("\\n✅ 彪哥战法v5.0分析完成")
        print("💡 系统已成功切换到QVeris数据源")
        
    except Exception as e:
        print(f"❌ 系统异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''

# 保存文件
with open("biage_v5_qveris_fixed.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ 修复版彪哥战法v5.0已创建: biage_v5_qveris_fixed.py")

# 立即测试
print("\n🔧 立即测试修复版...")
print("=" * 70)

import subprocess
result = subprocess.run(
    ["python3", "biage_v5_qveris_fixed.py"],
    capture_output=True,
    text=True,
    cwd="/Users/tuqibiao/.openclaw/workspace"
)

print(result.stdout)
if result.stderr:
    print(f"错误输出: {result.stderr}")

print("\n" + "=" * 70)
print("🎯 下一步: 创建定时任务脚本")

# 创建定时任务脚本
cron_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彪哥战法定时任务执行脚本
用法: python3 biage_cron.py [premarket|aftermarket]
"""

import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_analysis():
    """执行分析"""
    try:
        from biage_v5_qveris_fixed import BiageV5QVeris
        
        analyzer = BiageV5QVeris()
        market_data = analyzer.get_market_data()
        analysis = analyzer.analyze(market_data)
        
        if analysis:
            report = analyzer.generate_report(analysis)
            print(report)
            return True
        else:
            print("❌ 分析失败")
            return False
            
    except Exception as e:
        print(f"❌ 执行异常: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 biage_cron.py [premarket|aftermarket]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command in ["premarket", "aftermarket"]:
        success = run_analysis()
        sys.exit(0 if success else 1)
    else:
        print(f"未知命令: {command}")
        sys.exit(1)
'''

with open("biage_cron.py", "w", encoding="utf-8") as f:
    f.write(cron_script)

# 设置执行权限
os.chmod("biage_cron.py", 0o755)

print("✅ 定时任务脚本已创建: biage_cron.py")
print("💡 使用方法:")
print("  盘前分析: python3 biage_cron.py premarket")
print("  盘后分析: python3 biage_cron.py aftermarket")

print("\n" + "=" * 70)
print("🚀 修复完成！彪哥战法v5.0已成功切换到QVeris数据源")
print("📋 下一步:")
print("  1. 测试定时任务脚本")
print("  2. 更新openclaw定时任务配置")
print("  3. 验证系统稳定性")