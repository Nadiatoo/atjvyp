#!/usr/bin/env python3
"""
开发东方财富API备用数据源 - 立即执行
"""

import os
import sys
import json
import requests
import time
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional

class EastMoneyAPIDeveloper:
    """东方财富API开发者"""
    
    def __init__(self):
        # 东方财富API基础配置
        self.base_urls = {
            "行情数据": "http://push2.eastmoney.com/api",
            "资金流向": "http://push2his.eastmoney.com/api",
            "板块数据": "http://push2.eastmoney.com/api",
            "个股数据": "http://push2.eastmoney.com/api"
        }
        
        # 彪哥战法核心数据需求
        self.core_data_needs = [
            "涨跌停家数",
            "成交量数据", 
            "资金流向",
            "板块热度",
            "市场情绪"
        ]
        
        # 开发记录
        self.development_log = []
        self.available_apis = []
        
    def develop_core_apis(self):
        """开发核心API接口"""
        print("🔧 开发东方财富核心API接口")
        print("=" * 60)
        
        # 按核心数据需求开发API
        development_plan = [
            {
                "数据需求": "涨跌停家数",
                "开发方法": self._develop_zt_dt_count_api,
                "优先级": "最高"
            },
            {
                "数据需求": "成交量数据",
                "开发方法": self._develop_volume_data_api,
                "优先级": "高"
            },
            {
                "数据需求": "资金流向",
                "开发方法": self._develop_money_flow_api,
                "优先级": "高"
            },
            {
                "数据需求": "板块热度",
                "开发方法": self._develop_sector_heat_api,
                "优先级": "中"
            },
            {
                "数据需求": "市场情绪",
                "开发方法": self._develop_market_sentiment_api,
                "优先级": "中"
            }
        ]
        
        success_count = 0
        for plan in development_plan:
            print(f"\n📊 开发: {plan['数据需求']} (优先级: {plan['优先级']})")
            
            try:
                result = plan["开发方法"]()
                if result["success"]:
                    print(f"   ✅ 开发成功")
                    success_count += 1
                    self.available_apis.append({
                        "data_need": plan["数据需求"],
                        "api_endpoint": result.get("endpoint", ""),
                        "description": result.get("description", ""),
                        "example_data": result.get("example_data", {})
                    })
                else:
                    print(f"   ❌ 开发失败: {result.get('error', '未知错误')}")
                    
                # 记录开发日志
                self._log_development(plan["数据需求"], result["success"], result)
                
            except Exception as e:
                print(f"   ❌ 开发异常: {e}")
                self._log_development(plan["数据需求"], False, {"error": str(e)})
        
        print(f"\n📈 开发结果: {success_count}/{len(development_plan)} 成功")
        return success_count > 0
    
    def _develop_zt_dt_count_api(self):
        """开发涨跌停家数API"""
        print("  尝试获取涨跌停家数...")
        
        # 东方财富涨停跌停数据API
        url = "http://push2.eastmoney.com/api/qt/clist/get"
        
        params = {
            "pn": 1,
            "pz": 5000,  # 获取足够多的股票
            "po": 1,
            "np": 1,
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": 2,
            "invt": 2,
            "fid": "f3",
            "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23",  # 沪深A股
            "fields": "f2,f3,f4,f12,f14",  # 最新价,涨跌幅,涨跌额,代码,名称
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("rc") == 0 and "data" in data:
                    stocks = data["data"].get("diff", [])
                    
                    # 计算涨跌停家数
                    zt_count = 0  # 涨停
                    dt_count = 0  # 跌停
                    
                    for stock in stocks[:100]:  # 只检查前100只，避免计算量过大
                        change_percent = stock.get("f3", 0)  # 涨跌幅
                        
                        if change_percent >= 9.9:  # 涨停
                            zt_count += 1
                        elif change_percent <= -9.9:  # 跌停
                            dt_count += 1
                    
                    result = {
                        "success": True,
                        "endpoint": url,
                        "description": "获取沪深A股涨跌停家数",
                        "example_data": {
                            "涨停家数": zt_count,
                            "跌停家数": dt_count,
                            "检查股票数": len(stocks[:100]),
                            "数据时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
                    
                    print(f"     涨停: {zt_count}家, 跌停: {dt_count}家")
                    return result
                else:
                    return {
                        "success": False,
                        "error": f"API响应格式异常: {data.get('rc', '未知')}"
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP请求失败: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"请求异常: {e}"
            }
    
    def _develop_volume_data_api(self):
        """开发成交量数据API"""
        print("  尝试获取成交量数据...")
        
        # 获取市场总成交量
        url = "http://push2.eastmoney.com/api/qt/ulist.np/get"
        
        params = {
            "fields": "f6,f7,f8",  # 成交量,成交额,换手率
            "secids": "1.000001,0.399001",  # 上证指数,深证成指
            "ut": "bd1d9ddb04089700cf9c27f6f7426281"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("rc") == 0 and "data" in data:
                    market_data = data["data"].get("diff", [])
                    
                    total_volume = 0
                    total_amount = 0
                    
                    for market in market_data:
                        volume = market.get("f6", 0)  # 成交量(手)
                        amount = market.get("f7", 0)  # 成交额(元)
                        
                        total_volume += volume
                        total_amount += amount
                    
                    # 转换为亿手和亿元
                    total_volume_yi = total_volume / 100000000  # 亿手
                    total_amount_yi = total_amount / 100000000  # 亿元
                    
                    result = {
                        "success": True,
                        "endpoint": url,
                        "description": "获取市场总成交量和成交额",
                        "example_data": {
                            "总成交量(亿手)": round(total_volume_yi, 2),
                            "总成交额(亿元)": round(total_amount_yi, 2),
                            "数据时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
                    
                    print(f"     成交量: {round(total_volume_yi, 2)}亿手, 成交额: {round(total_amount_yi, 2)}亿元")
                    return result
                else:
                    return {
                        "success": False,
                        "error": f"API响应格式异常"
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP请求失败: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"请求异常: {e}"
            }
    
    def _develop_money_flow_api(self):
        """开发资金流向API"""
        print("  尝试获取资金流向数据...")
        
        # 获取北向资金数据
        url = "http://push2.eastmoney.com/api/qt/kamt.get"
        
        params = {
            "fields": "f1,f2,f3,f4",  # 沪股通,深股通,港股通(沪),港股通(深)
            "ut": "bd1d9ddb04089700cf9c27f6f7426281"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("rc") == 0 and "data" in data:
                    flow_data = data["data"]
                    
                    # 北向资金净流入
                    sh_north = flow_data.get("f1", 0)  # 沪股通净流入(万元)
                    sz_north = flow_data.get("f2", 0)  # 深股通净流入(万元)
                    
                    total_north = sh_north + sz_north
                    total_north_yi = total_north / 10000  # 转换为亿元
                    
                    result = {
                        "success": True,
                        "endpoint": url,
                        "description": "获取北向资金净流入数据",
                        "example_data": {
                            "沪股通净流入(万元)": sh_north,
                            "深股通净流入(万元)": sz_north,
                            "北向资金总净流入(亿元)": round(total_north_yi, 2),
                            "数据时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
                    
                    print(f"     北向资金净流入: {round(total_north_yi, 2)}亿元")
                    return result
                else:
                    return {
                        "success": False,
                        "error": f"API响应格式异常"
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP请求失败: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"请求异常: {e}"
            }
    
    def _develop_sector_heat_api(self):
        """开发板块热度API"""
        print("  尝试获取板块热度数据...")
        
        # 获取板块涨幅排行
        url = "http://push2.eastmoney.com/api/qt/clist/get"
        
        params = {
            "pn": 1,
            "pz": 20,  # 前20个板块
            "po": 1,
            "np": 1,
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": 2,
            "invt": 2,
            "fid": "f3",
            "fs": "m:90 t:2",  # 板块
            "fields": "f2,f3,f12,f14",  # 最新价,涨跌幅,代码,名称
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("rc") == 0 and "data" in data:
                    sectors = data["data"].get("diff", [])
                    
                    hot_sectors = []
                    for sector in sectors[:5]:  # 前5个热门板块
                        hot_sectors.append({
                            "name": sector.get("f14", "未知"),
                            "change_percent": sector.get("f3", 0),
                            "code": sector.get("f12", "")
                        })
                    
                    result = {
                        "success": True,
                        "endpoint": url,
                        "description": "获取板块热度排行",
                        "example_data": {
                            "热门板块": hot_sectors,
                            "数据时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
                    
                    print(f"     热门板块: {', '.join([s['name'] for s in hot_sectors])}")
                    return result
                else:
                    return {
                        "success": False,
                        "error": f"API响应格式异常"
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP请求失败: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"请求异常: {e}"
            }
    
    def _develop_market_sentiment_api(self):
        """开发市场情绪API"""
        print("  尝试获取市场情绪数据...")
        
        # 通过涨跌家数比判断市场情绪
        url = "http://push2.eastmoney.com/api/qt/ulist.np/get"
        
        params = {
            "fields": "f2,f3,f4",  # 最新价,涨跌幅,涨跌额
            "secids": "1.000001",  # 上证指数
            "ut": "bd1d9ddb04089700cf9c27f6f7426281"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("rc") == 0 and "data" in data:
                    sh_index = data["data"].get("diff", [])
                    
                    if sh_index:
                        index_data = sh_index[0]
                        change_percent = index_data.get("f3", 0)  # 上证指数涨跌幅
                        
                        # 简单的情绪判断
                        if change_percent > 1:
                            sentiment = "乐观"
                        elif change_percent < -1:
                            sentiment = "悲观"
                        else:
                            sentiment = "中性"
                        
                        result = {
                            "success": True,
                            "endpoint": url,
                            "description": "通过指数涨跌幅判断市场情绪",
                            "example_data": {
                                "上证指数涨跌幅": change_percent,
                                "市场情绪": sentiment,
                                "数据时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                        }
                        
                        print(f"     上证指数涨跌幅: {change_percent}%, 情绪: {sentiment}")
                        return result
                    else:
                        return {
                            "success": False,
                            "error": "未获取到指数数据"
                        }
                else:
                    return {
                        "success": False,
                        "error": f"API响应格式异常"
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP请求失败: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"请求异常: {e}"
            }
    
    def _log_development(self, data_need, success, result):
        """记录开发日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "data_need": data_need,
            "success": success,
            "result": result
        }
        self.development_log.append(log_entry)
    
    def save_results(self):
        """保存开发结果"""
        results_dir = "/Users/tuqibiao/.openclaw/workspace/data/eastmoney_development"
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存可用API
        if self.available_apis:
            apis_file = f"{results_dir}/available_apis_{timestamp}.json"
            with open(apis_file, 'w', encoding='utf-8') as f:
                json.dump(self.available_apis, f, ensure_ascii=False, indent=2)
            print(f"\n📁 可用API保存至: {apis_file}")
        
        # 保存开发日志
        log_file = f"{results_dir}/development_log_{timestamp}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.development_log, f, ensure_ascii=False, indent=2)
        print(f"📁 开发日志保存至: {log_file}")
        
        # 生成总结报告
        report_file = f"{results_dir}/development_summary_{timestamp}.md"
        self._generate_summary_report(report_file)
        print(f"📁 总结报告保存至: {report_file}")
    
    def _generate_summary_report(self, report_file):
        """生成开发总结报告"""
        report = f"""# 东方财富API开发报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 开发结果摘要

### 核心数据需求开发情况
彪哥战法核心数据需求: {len(self.core_data_needs)}项
成功开发API: {len(self.available_apis)}项

### 详细开发结果
"""
        
        for api in self.available_apis:
            report += f"""
#### {api['data_need']}
- **API端点**: `{api['api_endpoint']}`
- **描述**: {api['description']}
- **示例数据**:
```json
{json.dumps(api['example_data'], ensure_ascii=False, indent=2)}
```
"""
        
        report += """
### 开发日志摘要
"""
        
        for log in self.development_log:
            status = "✅ 成功" if log["success"] else "❌ 失败"
            report += f"- **{log['data_need']}**: {status}\n"
        
        report += """
## 💡 下一步建议

### 立即行动:
1. **API稳定性测试**: 测试每个API的稳定性和响应时间
2. **数据准确性验证**: 验证获取数据的准确性
3. **错误处理完善**: 完善API调用错误处理机制

### 集成计划:
1. **集成到彪哥战法**: 将开发的API集成到战法数据采集模块
2. **建立数据缓存**: 建立数据缓存机制，减少API调用
3. **监控报警**: 建立API健康监控和报警机制

### 优化方向:
1. **参数优化**: 优化API调用参数，提高效率
2. **数据清洗**: 建立数据清洗和验证流程
3. **备用方案**: 为每个API准备备用数据源

## 🎯 彪哥战法数据源架构建议

### 推荐架构:
```
东方财富API (主要数据源)
    ↓
数据清洗验证
    ↓
彪哥战法分析引擎
    ↓
QVeris (补充数据源，新闻/宏观)
    ↓
数据融合验证
```

### 优势:
1. **数据准确**: 东方财富数据直接来自交易所
2. **实时性强**: API响应快，数据及时
3. **免费稳定**: 东方财富API免费且相对稳定
4. **互补性强**: QVeris补充新闻和宏观数据

### 注意事项:
1. **API频率限制**: 注意东方财富API调用频率
2. **数据格式变化**: 注意API数据格式可能变化
3. **网络稳定性**: 确保网络连接稳定
4. **错误处理**: 建立完善的错误处理机制
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def print_summary(self):
        """打印开发总结"""
        print("\n" + "=" * 60)
        print("📈 东方财富API开发总结")
        print("=" * 60)
        
        print(f"核心数据需求: {len(self.core_data_needs)}项")
        print(f"成功开发API: {len(self.available_apis)}项")
        
        if self.available_apis:
            print("\n开发的API:")
            for i, api in enumerate(self.available_apis, 1):
                print(f"  {i}. {api['data_need']}")
                print(f"     端点: {api['api_endpoint'][:50]}...")
                if api['example_data']:
                    sample = json.dumps(api['example_data'], ensure_ascii=False)
                    print(f"     示例: {sample[:50]}...")
        else:
            print("\n⚠️ 未成功开发任何API")
        
        print("\n💡 建议:")
        print("1. 立即测试开发的API稳定性和准确性")
        print("2. 集成到彪哥战法数据采集模块")
        print("3. 建立数据验证和错误处理机制")

def main():
    """主函数"""
    print("🚀 东方财富API开发 - 立即开始")
    print("=" * 60)
    
    developer = EastMoneyAPIDeveloper()
    
    # 开始开发
    success = developer.develop_core_apis()
    
    # 保存结果
    developer.save_results()
    
    # 打印总结
    developer.print_summary()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 东方财富API开发完成，成功开发核心API")
    else:
        print("⚠️ 东方财富API开发有限，需要进一步探索")
    
    print("=" * 60)

if __name__ == "__main__":
    main()

