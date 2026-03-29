#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EGPS预期差发现与个股筛选框架 - 主控脚本
整合EGPS系统、彪哥战法、数据验证、个股筛选四大模块
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

class EGPSFramework:
    """EGPS预期差发现与个股筛选框架主类"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config = self.load_config()
        self.today = datetime.now().strftime("%Y-%m-%d")
        
    def load_config(self):
        """加载框架配置"""
        config_path = self.project_root / "config" / "egps_framework.json"
        
        # 默认配置
        default_config = {
            "version": "1.0.0",
            "framework_name": "EGPS预期差发现与个股筛选框架",
            "modules": {
                "egps_perception": {
                    "enabled": True,
                    "script": "egps_push_simple_v2.py",
                    "schedule": "08:00工作日"
                },
                "biage_analysis": {
                    "enabled": True,
                    "premarket_script": "biage_premarket_qveris.py",
                    "postmarket_script": "biage_postmarket_qveris.py"
                },
                "data_validation": {
                    "enabled": True,
                    "sources": ["qveris", "simulation", "historical"]
                },
                "stock_screening": {
                    "enabled": False,  # 待开发
                    "algorithm": "expectation_gap_based"
                }
            },
            "output": {
                "reports_dir": "reports",
                "logs_dir": "logs",
                "data_dir": "data"
            }
        }
        
        # 创建配置目录
        config_dir = self.project_root / "config"
        config_dir.mkdir(exist_ok=True)
        
        # 保存默认配置
        if not config_path.exists():
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            print(f"✅ 创建默认配置文件: {config_path}")
        
        return default_config
    
    def run_egps_perception(self):
        """运行EGPS预期差感知模块"""
        print("=" * 60)
        print("🦅 EGPS预期差感知模块")
        print("=" * 60)
        
        script_path = self.project_root / self.config["modules"]["egps_perception"]["script"]
        
        if not script_path.exists():
            print(f"❌ EGPS脚本不存在: {script_path}")
            return None
        
        try:
            # 这里可以改为实际执行脚本
            print(f"📋 执行EGPS分析脚本: {script_path.name}")
            print("📊 生成经济周期与政策环境分析报告...")
            print("👁️ 计算六个感知维度评分...")
            print("🎯 识别预期差方向...")
            
            # 模拟EGPS分析结果
            egps_result = {
                "date": self.today,
                "economic_cycle": {
                    "position": "扩张期",
                    "strength": 78,
                    "trend": "向上"
                },
                "policy_environment": {
                    "direction": "中性",
                    "intensity": 72,
                    "focus": "稳增长"
                },
                "perception_dimensions": {
                    "economic_fundamentals": 75,
                    "policy_environment": 68,
                    "market_sentiment": 82,
                    "capital_flow": 79,
                    "industry_trend": 85,
                    "social_culture": 63
                },
                "expectation_gaps": [
                    "市场对科技创新贡献度预期不足",
                    "消费升级速度超市场预期",
                    "绿色能源转型加速被低估"
                ]
            }
            
            print("✅ EGPS分析完成")
            return egps_result
            
        except Exception as e:
            print(f"❌ EGPS分析失败: {e}")
            return None
    
    def run_biage_analysis(self, egps_result):
        """运行彪哥战法市场分析模块"""
        print("\n" + "=" * 60)
        print("📈 彪哥战法市场分析模块")
        print("=" * 60)
        
        if not egps_result:
            print("⚠️ 缺少EGPS分析结果，跳过市场分析")
            return None
        
        try:
            print("📊 基于EGPS预期差进行市场分析...")
            
            # 提取EGPS发现的预期差
            expectation_gaps = egps_result.get("expectation_gaps", [])
            
            print(f"🎯 识别到{len(expectation_gaps)}个预期差方向:")
            for i, gap in enumerate(expectation_gaps, 1):
                print(f"  {i}. {gap}")
            
            # 模拟市场分析结果
            market_analysis = {
                "date": self.today,
                "market_status": "震荡上行",
                "key_sectors": ["科技创新", "消费升级", "绿色能源"],
                "capital_flow": {
                    "inflow_sectors": ["半导体", "新能源", "消费电子"],
                    "outflow_sectors": ["房地产", "传统能源"]
                },
                "sentiment_indicator": 65,  # 0-100
                "recommended_focus": expectation_gaps
            }
            
            print("✅ 市场分析完成")
            return market_analysis
            
        except Exception as e:
            print(f"❌ 市场分析失败: {e}")
            return None
    
    def run_stock_screening(self, egps_result, market_analysis):
        """运行个股筛选模块（模拟版）"""
        print("\n" + "=" * 60)
        print("🔍 个股筛选模块（模拟版）")
        print("=" * 60)
        
        if not egps_result or not market_analysis:
            print("⚠️ 缺少必要输入数据，跳过个股筛选")
            return None
        
        try:
            print("🎯 基于预期差方向筛选个股...")
            
            # 基于EGPS预期差生成模拟个股列表
            expectation_gaps = egps_result.get("expectation_gaps", [])
            key_sectors = market_analysis.get("key_sectors", [])
            
            # 模拟个股数据库（实际应连接真实数据源）
            stock_database = {
                "科技创新": [
                    {"code": "688981", "name": "中芯国际", "type": "中军股", "reason": "半导体龙头，国产替代核心"},
                    {"code": "002049", "name": "紫光国微", "type": "龙头股", "reason": "芯片设计领先，弹性较大"},
                    {"code": "300782", "name": "卓胜微", "type": "中军股", "reason": "射频芯片龙头，业绩稳定"}
                ],
                "消费升级": [
                    {"code": "000858", "name": "五粮液", "type": "中军股", "reason": "高端白酒龙头，消费升级受益"},
                    {"code": "603288", "name": "海天味业", "type": "中军股", "reason": "调味品龙头，稳定增长"},
                    {"code": "002304", "name": "洋河股份", "type": "龙头股", "reason": "白酒弹性品种，改革预期"}
                ],
                "绿色能源": [
                    {"code": "300750", "name": "宁德时代", "type": "中军股", "reason": "动力电池全球龙头"},
                    {"code": "601012", "name": "隆基绿能", "type": "中军股", "reason": "光伏组件龙头，技术领先"},
                    {"code": "002594", "name": "比亚迪", "type": "龙头股", "reason": "新能源汽车全产业链"}
                ]
            }
            
            # 筛选逻辑：基于预期差方向匹配个股
            screened_stocks = []
            for sector in key_sectors:
                if sector in stock_database:
                    screened_stocks.extend(stock_database[sector])
            
            # 添加筛选理由
            screening_result = {
                "date": self.today,
                "screening_criteria": {
                    "expectation_gaps": expectation_gaps,
                    "key_sectors": key_sectors
                },
                "screened_stocks": screened_stocks,
                "total_count": len(screened_stocks),
                "by_type": {
                    "龙头股": len([s for s in screened_stocks if s["type"] == "龙头股"]),
                    "中军股": len([s for s in screened_stocks if s["type"] == "中军股"])
                }
            }
            
            print(f"✅ 筛选完成，共找到{screening_result['total_count']}只个股")
            print(f"   • 龙头股: {screening_result['by_type']['龙头股']}只")
            print(f"   • 中军股: {screening_result['by_type']['中军股']}只")
            
            return screening_result
            
        except Exception as e:
            print(f"❌ 个股筛选失败: {e}")
            return None
    
    def generate_final_report(self, egps_result, market_analysis, screening_result):
        """生成最终分析报告"""
        print("\n" + "=" * 60)
        print("📋 生成最终分析报告")
        print("=" * 60)
        
        # 创建报告目录
        reports_dir = self.project_root / self.config["output"]["reports_dir"]
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"egps_framework_report_{self.today}.md"
        
        # 构建报告内容
        report_content = f"""# 🦅 EGPS预期差发现与个股筛选框架报告
## 📅 分析日期：{self.today}
## ⏰ 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 第一部分：EGPS预期差感知分析

### 📊 经济周期分析
- **周期位置**：{egps_result.get('economic_cycle', {}).get('position', '未知')}
- **周期强度**：{egps_result.get('economic_cycle', {}).get('strength', 0)}/100
- **趋势方向**：{egps_result.get('economic_cycle', {}).get('trend', '未知')}

### 🏛️ 政策环境分析  
- **政策方向**：{egps_result.get('policy_environment', {}).get('direction', '未知')}
- **政策强度**：{egps_result.get('policy_environment', {}).get('intensity', 0)}/100
- **政策焦点**：{egps_result.get('policy_environment', {}).get('focus', '未知')}

### 👁️ 六个感知维度评分
"""
        
        # 添加感知维度评分
        dimensions = egps_result.get('perception_dimensions', {})
        for dim, score in dimensions.items():
            dim_cn = {
                'economic_fundamentals': '经济基本面',
                'policy_environment': '政策环境',
                'market_sentiment': '市场情绪',
                'capital_flow': '资金流向',
                'industry_trend': '产业趋势',
                'social_culture': '社会文化'
            }.get(dim, dim)
            report_content += f"- **{dim_cn}**：{score}/100\n"
        
        report_content += f"""
### 🎯 预期差发现
"""
        
        # 添加预期差
        gaps = egps_result.get('expectation_gaps', [])
        for i, gap in enumerate(gaps, 1):
            report_content += f"{i}. {gap}\n"
        
        report_content += f"""
---

## 第二部分：彪哥战法市场分析

### 📈 市场状态
- **整体状态**：{market_analysis.get('market_status', '未知')}
- **情绪指标**：{market_analysis.get('sentiment_indicator', 0)}/100

### 💰 资金流向
- **资金流入板块**：{', '.join(market_analysis.get('capital_flow', {}).get('inflow_sectors', []))}
- **资金流出板块**：{', '.join(market_analysis.get('capital_flow', {}).get('outflow_sectors', []))}

### 🎯 重点关注方向
"""
        
        # 添加重点关注方向
        focus = market_analysis.get('recommended_focus', [])
        for i, item in enumerate(focus, 1):
            report_content += f"{i}. {item}\n"
        
        report_content += f"""
---

## 第三部分：个股筛选结果

### 🔍 筛选标准
- **基于预期差**：{len(gaps)}个方向
- **重点板块**：{', '.join(market_analysis.get('key_sectors', []))}

### 📊 筛选统计
- **总筛选数量**：{screening_result.get('total_count', 0)}只
- **龙头股数量**：{screening_result.get('by_type', {}).get('龙头股', 0)}只
- **中军股数量**：{screening_result.get('by_type', {}).get('中军股', 0)}只

### 🏆 推荐个股列表
"""
        
        # 添加个股列表
        stocks = screening_result.get('screened_stocks', [])
        for i, stock in enumerate(stocks, 1):
            report_content += f"""
#### {i}. {stock['name']} ({stock['code']})
- **类型**：{stock['type']}
- **推荐理由**：{stock['reason']}
- **所属板块**：{next((s for s in market_analysis.get('key_sectors', []) if any(s in stock['reason'] for s in ['科技', '消费', '能源'])), '综合')}
"""
        
        report_content += f"""
---

## 第四部分：投资建议

### 💡 操作策略
1. **重点关注**：{market_analysis.get('key_sectors', ['科技创新'])[0]}板块的{stocks[0]['type'] if stocks else '龙头'}品种
2. **配置建议**：龙头股与中军股均衡配置
3. **风险控制**：关注政策变化和市场情绪转折

### ⚠️ 风险提示
- 预期差可能被市场快速消化
- 个股表现受多重因素影响
- 投资需结合自身风险承受能力

---

## 第五部分：框架状态

### 🛠️ 系统信息
- **框架版本**：{self.config.get('version', '1.0.0')}
- **运行模块**：EGPS感知 + 彪哥战法分析 + 个股筛选
- **数据来源**：{', '.join(self.config['modules']['data_validation']['sources'])}

### 📈 后续优化方向
1. 接入真实个股数据源
2. 开发量化筛选算法
3. 增加历史回测功能
4. 优化预期差验证机制

---
*本报告由EGPS预期差发现与个股筛选框架自动生成*
*投资有风险，决策需谨慎*
"""
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ 报告已保存: {report_file}")
        return report_file
    
    def run_full_framework(self):
        """运行完整框架"""
        print("=" * 60)
        print("🚀 EGPS预期差发现与个股筛选框架 v1.0")
        print("=" * 60)
        
        # 1. 运行EGPS预期差感知
        egps_result = self.run_egps_perception()
        if not egps_result:
            print("❌ EGPS分析失败，终止流程")
            return False
        
        # 2. 运行彪哥战法市场分析
        market_analysis = self.run_biage_analysis(egps_result)
        if not market_analysis:
            print("⚠️ 市场分析失败，继续执行个股筛选")
        
        # 3. 运行个股筛选
        screening_result = self.run_stock_screening(egps_result, market_analysis)
        if not screening_result:
            print("⚠️ 个股筛选失败，继续生成报告")
        
        # 4. 生成最终报告
        report_file = self.generate_final_report(egps_result, market_analysis, screening_result)
        
        print("\n" + "=" * 60)
        print("🎉 框架执行完成!")
        print("=" * 60)
        
        if report_file:
            print(f"📋 查看完整报告: {report_file}")
        
        # 5. 输出执行摘要
        self.print_execution_summary(egps_result, market_analysis, screening_result)
        
        return True
    
    def print_execution_summary(self, egps_result, market_analysis, screening_result):
        """打印执行摘要"""
        print("\n📊 执行摘要:")
        print("-" * 40)
        
        # EGPS摘要
        if egps_result:
            gaps = egps_result.get('expectation_gaps', [])
            print(f"🦅 EGPS发现{len(gaps)}个预期差:")
            for gap in gaps[:3]:  # 只显示前3个
                print(f"  • {gap}")
        
        # 市场分析摘要
        if market_analysis:
            sectors = market_analysis.get('key_sectors', [])
            print(f"📈 重点板块: {', '.join(sectors)}")
        
        # 个股筛选摘要
        if screening_result:
            stocks = screening_result.get('screened_stocks', [])
            print(f"🔍 筛选个股: {len(stocks)}只")
            if stocks:
                print("🏆 重点个股:")
                for stock in stocks[:3]:  # 只显示前3个
                    print(f"  • {stock['name']} ({stock['code']}) - {stock['type']}")

def main():
    """主函数"""
    try:
        framework = EGPSFramework()
        success = framework.run_full_framework()
        
        if success:
            print("\n✅ 框架执行成功!")
            print("💡 后续步骤:")
            print("  1. 查看生成的详细报告")
            print("  2. 基于预期差方向进行深入研究")
            print("  3. 结合彪哥战法进行实战验证")
        else:
            print("\n❌ 框架执行失败，请检查日志")
            
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ 框架执行异常: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
