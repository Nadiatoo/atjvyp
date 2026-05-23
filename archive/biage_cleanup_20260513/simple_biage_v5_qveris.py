
import os
import requests
import json
import datetime

class SimpleBiageV5:
    def __init__(self):
        self.api_key = os.getenv("QVERIS_API_KEY")
        self.base_url = "https://qveris.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def execute_tool(self, tool_id, params):
        url = f"{self.base_url}/tools/execute"
        payload = {"tool_id": tool_id, "parameters": params}
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    def get_data(self):
        """获取市场数据"""
        data = {'timestamp': datetime.datetime.now().isoformat()}
        
        # 上证指数
        result = self.execute_tool("ths_ifind.real_time_quotation.v1", {
            "codes": "000001.SH", "indicators": "common"
        })
        if result and 'result' in result and 'data' in result['result']:
            sh_data = result['result']['data'][0][0]
            data['shanghai'] = {
                'price': sh_data.get('latest'),
                'change_pct': sh_data.get('changeRatio'),
                'volume': sh_data.get('volume')
            }
        
        # 市场统计
        result = self.execute_tool("mcp_gildata.marketlimitupdowncount.v1", {
            "query": "获取今日市场涨跌停家数"
        })
        if result and 'result' in result and 'data' in result['result']:
            stats = result['result']['data']
            if 'table_markdown' in stats:
                table = stats['table_markdown']
                lines = table.strip().split('\n')
                if len(lines) >= 3:
                    cells = [c.strip() for c in lines[2].split('|') if c.strip()]
                    if len(cells) >= 9:
                        data['stats'] = {
                            'total': int(cells[2]),
                            'rising': int(cells[3]),
                            'falling': int(cells[4]),
                            'limit_up': int(cells[6]),
                            'limit_down': int(cells[7])
                        }
        
        return data
    
    def analyze(self, data):
        """分析市场"""
        if 'shanghai' not in data or 'stats' not in data:
            return None
        
        sh = data['shanghai']
        stats = data['stats']
        
        # 计算评分
        score = 0
        
        # 技术面 (60%)
        if sh.get('change_pct', 0) < 0:
            score += 0.12  # 20% of 60%
        
        rising_ratio = stats['rising'] / stats['total'] if stats['total'] > 0 else 0
        if rising_ratio < 0.5:
            score += 0.12
        
        if stats['limit_up'] < 80:
            score += 0.06
        
        if stats['limit_down'] > 20:
            score += 0.06
        
        # 情绪面 (13%)
        if rising_ratio < 0.3:
            score += 0.13
        elif rising_ratio < 0.5:
            score += 0.065
        
        # 确定状态
        if score < 0.3:
            state, position, strategy = "混沌期", "0-10%", "空仓等待"
        elif score < 0.5:
            state, position, strategy = "冬藏期", "10-30%", "防守为主"
        elif score < 0.7:
            state, position, strategy = "秋收期", "30-50%", "逐步减仓"
        elif score < 0.85:
            state, position, strategy = "春播期", "50-70%", "分批建仓"
        else:
            state, position, strategy = "夏长期", "70-90%", "重仓持有"
        
        return {
            'market_state': state,
            'score': round(score, 3),
            'position': position,
            'strategy': strategy,
            'rising_ratio': round(rising_ratio, 3),
            'data': data
        }
    
    def generate_report(self, analysis):
        """生成报告"""
        if not analysis:
            return "分析失败"
        
        data = analysis['data']
        sh = data.get('shanghai', {})
        stats = data.get('stats', {})
        
        report = f"""
📊 【彪哥战法v5.0】实时分析 (QVeris数据源)
━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}

🎯 市场状态: {analysis['market_state']}
📈 综合评分: {analysis['score']}/1.0
💰 建议仓位: {analysis['position']}
📊 操作策略: {analysis['strategy']}

📋 市场数据:
  上证指数: {sh.get('price', 0):.2f} ({sh.get('change_pct', 0):+.2f}%)
  总股票数: {stats.get('total', 0)}
  上涨家数: {stats.get('rising', 0)} ({analysis['rising_ratio']:.1%})
  下跌家数: {stats.get('falling', 0)}
  涨停家数: {stats.get('limit_up', 0)}
  跌停家数: {stats.get('limit_down', 0)}

💡 操作建议:
  1. 严格执行仓位控制 ({analysis['position']})
  2. {analysis['strategy']}
  3. 关注市场情绪变化
  4. 等待明确信号再行动

⚠️ 风险提示:
  • 数据来源: QVeris实时数据
  • 市场有风险，投资需谨慎
"""
        
        return report

# 使用示例
if __name__ == "__main__":
    analyzer = SimpleBiageV5()
    data = analyzer.get_data()
    analysis = analyzer.analyze(data)
    
    if analysis:
        report = analyzer.generate_report(analysis)
        print(report)
        
        # 保存结果
        filename = f"biage_qveris_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.datetime.now().isoformat(),
                'data': data,
                'analysis': analysis,
                'report': report
            }, f, ensure_ascii=False, indent=2)
        
        print(f"📁 结果已保存: {filename}")
    else:
        print("❌ 分析失败")
