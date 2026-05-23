#!/usr/bin/env python3
"""
简单实时收盘报告 - 基于东方财富真实数据
"""

import json
import urllib.request
import ssl
from datetime import datetime

# 禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

def get_real_time_data():
    """获取实时数据"""
    print("📊 获取东方财富实时数据...")
    
    url = 'https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2&secids=1.000001,0.399001,0.399006&fields=f12,f13,f14,f2,f3,f4'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://quote.eastmoney.com/'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if 'data' in data and 'diff' in data['data']:
                indices = []
                for item in data['data']['diff']:
                    indices.append({
                        'name': item.get('f14', '未知'),
                        'price': item.get('f2', 0),
                        'change_pct': item.get('f3', 0),
                        'change': item.get('f4', 0)
                    })
                return indices
    except Exception as e:
        print(f"❌ 数据获取失败: {e}")
    
    return None

def generate_report(indices_data):
    """生成报告"""
    if not indices_data:
        print("❌ 无有效数据，无法生成报告")
        return None
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 计算平均涨幅
    avg_change = sum(item['change_pct'] for item in indices_data) / len(indices_data)
    
    # 季节判断
    if avg_change > 3:
        season = "夏长期"
        position = "60-80%"
    elif avg_change > 1:
        season = "春生期"
        position = "50-70%"
    elif avg_change > -1:
        season = "秋收期"
        position = "30-50%"
    else:
        season = "冬藏期"
        position = "10-30%"
    
    # 生成报告
    report = f"""🏁 【实时收盘报告】{datetime.now().strftime('%Y-%m-%d %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 **一、实时指数数据（东方财富API）**

"""
    
    for item in indices_data:
        report += f"• {item['name']}: {item['price']} ({item['change_pct']:+.2f}%)\n"
    
    report += f"""
**数据时间**: {current_time}
**数据源**: 东方财富实时API

🎯 **二、彪哥战法分析**

**季节判断**: {season}
**仓位建议**: {position}
**平均涨幅**: {avg_change:+.2f}%

**分析依据**:
• 基于实时指数表现判断市场季节
• 仓位建议根据季节状态调整
• 所有数据均为实时获取，非模拟数据

💡 **三、操作建议**

1. **仓位管理**: {position}，{season}期合理配置
2. **关注方向**: 根据领涨板块调整持仓
3. **风险控制**: 设置止损，防范市场波动
4. **明日关注**: 跟踪资金流向和板块轮动

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 **报告说明**: 本报告基于东方财富实时API数据生成
⏰ **下次更新**: 明日收盘后
"""
    
    return report

def main():
    """主函数"""
    print("=" * 60)
    print("实时收盘报告系统 - 基于东方财富真实数据")
    print("=" * 60)
    
    # 获取实时数据
    indices_data = get_real_time_data()
    
    if not indices_data:
        print("❌ 无法获取实时数据，报告生成失败")
        return
    
    # 生成报告
    report = generate_report(indices_data)
    
    if report:
        # 保存报告
        report_file = f"/Users/tuqibiao/.openclaw/workspace/reports/real_close_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("\n" + report)
        print(f"\n✅ 报告已保存至: {report_file}")
        print("🎉 实时收盘报告生成完成!")
    else:
        print("❌ 报告生成失败")

if __name__ == "__main__":
    main()