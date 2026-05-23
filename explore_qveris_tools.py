#!/usr/bin/env python3
"""
探索QVeris实际可用工具 - 立即执行
"""

import os
import sys
import json
import requests
from datetime import datetime

class QVerisExplorer:
    """QVeris工具探索器"""
    
    def __init__(self):
        self.api_key = os.getenv('QVERIS_API_KEY')
        if not self.api_key:
            print("❌ 错误: 未设置QVERIS_API_KEY环境变量")
            print("请设置: export QVERIS_API_KEY=your_key")
            sys.exit(1)
            
        self.base_url = "https://qveris.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 探索记录
        self.exploration_log = []
        self.available_tools = []
        
    def explore_by_keywords(self):
        """通过关键词探索工具"""
        print("🔍 通过关键词探索QVeris工具")
        print("=" * 60)
        
        # 彪哥战法相关的关键词
        keywords = [
            "stock", "market", "finance", "trading",  # 英文关键词
            "股票", "市场", "金融", "交易", "行情", "资金",  # 中文关键词
            "news", "data", "analysis", "trend",  # 通用关键词
            "A股", "上证", "深证", "创业板"  # A股特定关键词
        ]
        
        # 尝试不同的探索方法
        exploration_methods = [
            self._explore_direct_api,
            self._explore_known_tools,
            self._explore_by_category
        ]
        
        for method in exploration_methods:
            print(f"\n尝试方法: {method.__name__}")
            try:
                if method():
                    print("✅ 探索成功")
                    break
            except Exception as e:
                print(f"❌ 方法失败: {e}")
                continue
        
        return len(self.available_tools) > 0
    
    def _explore_direct_api(self):
        """直接API探索"""
        print("  尝试直接API调用...")
        
        # 尝试获取工具列表的常见端点
        endpoints = [
            "/tools",
            "/tool/list", 
            "/tools/list",
            "/available-tools",
            "/tool-catalog"
        ]
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            print(f"    测试端点: {endpoint}")
            
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                print(f"      状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"      ✅ 成功获取响应")
                    
                    # 解析工具列表
                    tools = self._parse_tool_list(data)
                    if tools:
                        print(f"      发现工具: {len(tools)}个")
                        self.available_tools.extend(tools)
                        self._log_exploration(f"直接API端点 {endpoint}", True, len(tools))
                        return True
                    else:
                        print(f"      未解析出工具列表")
                        print(f"      响应内容: {json.dumps(data, ensure_ascii=False)[:200]}...")
                else:
                    print(f"      请求失败: {response.text[:100]}")
                    
            except Exception as e:
                print(f"      异常: {e}")
        
        self._log_exploration("直接API探索", False, 0)
        return False
    
    def _explore_known_tools(self):
        """尝试已知的工具ID"""
        print("  尝试已知工具ID...")
        
        # 常见的工具ID模式
        known_tool_patterns = [
            "stock_data", "market_data", "financial_data",
            "news_search", "company_info", "economic_data",
            "technical_analysis", "fundamental_analysis"
        ]
        
        success_count = 0
        for pattern in known_tool_patterns:
            print(f"    测试工具: {pattern}")
            
            payload = {
                "tool_id": pattern,
                "params": {"test": "test"}  # 最小参数
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/tools/execute",
                    headers=self.headers,
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    error_msg = data.get("error_message", "")
                    
                    if "工具未找到" not in error_msg and "not found" not in error_msg.lower():
                        print(f"      ✅ 工具可能存在: {pattern}")
                        success_count += 1
                        self.available_tools.append({
                            "id": pattern,
                            "name": pattern,
                            "test_result": "可能存在"
                        })
                    else:
                        print(f"      ❌ 工具不存在: {pattern}")
                else:
                    print(f"      ❌ 请求失败: {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ 异常: {e}")
        
        self._log_exploration("已知工具探索", success_count > 0, success_count)
        return success_count > 0
    
    def _explore_by_category(self):
        """按类别探索"""
        print("  按类别探索...")
        
        # 尝试不同的类别
        categories = ["finance", "news", "data", "analysis", "market"]
        
        for category in categories:
            print(f"    探索类别: {category}")
            
            # 尝试搜索类别的工具
            search_payload = {
                "tool_id": "search_tools",  # 假设有搜索工具
                "params": {
                    "category": category,
                    "limit": 10
                }
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/tools/execute",
                    headers=self.headers,
                    json=search_payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"      响应: {json.dumps(data, ensure_ascii=False)[:200]}...")
                else:
                    print(f"      请求失败: {response.status_code}")
                    
            except Exception as e:
                print(f"      异常: {e}")
                # 继续尝试下一个类别
        
        # 由于不知道具体的搜索工具，这种方法可能有限
        self._log_exploration("类别探索", False, 0)
        return False
    
    def _parse_tool_list(self, data):
        """解析工具列表响应"""
        tools = []
        
        if isinstance(data, list):
            # 直接是工具列表
            for item in data:
                if isinstance(item, dict):
                    tool = {
                        "id": item.get("id", ""),
                        "name": item.get("name", ""),
                        "description": item.get("description", ""),
                        "category": item.get("category", "")
                    }
                    tools.append(tool)
        
        elif isinstance(data, dict):
            # 可能包含工具列表的字段
            possible_fields = ["tools", "data", "items", "results"]
            
            for field in possible_fields:
                if field in data and isinstance(data[field], list):
                    for item in data[field]:
                        if isinstance(item, dict):
                            tool = {
                                "id": item.get("id", ""),
                                "name": item.get("name", ""),
                                "description": item.get("description", ""),
                                "category": item.get("category", "")
                            }
                            tools.append(tool)
                    break
        
        return tools
    
    def _log_exploration(self, method, success, tool_count):
        """记录探索结果"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "success": success,
            "tool_count": tool_count
        }
        self.exploration_log.append(log_entry)
    
    def save_results(self):
        """保存探索结果"""
        results_dir = "/Users/tuqibiao/.openclaw/workspace/data/qveris_exploration"
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存可用工具
        if self.available_tools:
            tools_file = f"{results_dir}/available_tools_{timestamp}.json"
            with open(tools_file, 'w', encoding='utf-8') as f:
                json.dump(self.available_tools, f, ensure_ascii=False, indent=2)
            print(f"\n📁 可用工具保存至: {tools_file}")
        
        # 保存探索日志
        log_file = f"{results_dir}/exploration_log_{timestamp}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.exploration_log, f, ensure_ascii=False, indent=2)
        print(f"📁 探索日志保存至: {log_file}")
        
        # 生成总结报告
        report_file = f"{results_dir}/exploration_summary_{timestamp}.md"
        self._generate_summary_report(report_file)
        print(f"📁 总结报告保存至: {report_file}")
    
    def _generate_summary_report(self, report_file):
        """生成探索总结报告"""
        report = f"""# QVeris工具探索报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 探索结果摘要

### 探索方法尝试
"""
        
        for log in self.exploration_log:
            status = "✅ 成功" if log["success"] else "❌ 失败"
            report += f"- **{log['method']}**: {status} (发现工具: {log['tool_count']}个)\n"
        
        report += f"""
### 发现可用工具
总计: {len(self.available_tools)}个工具

"""
        
        if self.available_tools:
            for i, tool in enumerate(self.available_tools, 1):
                report += f"{i}. **{tool.get('name', '未知')}** (ID: `{tool.get('id', '未知')}`)\n"
                if tool.get('description'):
                    report += f"   描述: {tool['description']}\n"
                if tool.get('category'):
                    report += f"   类别: {tool['category']}\n"
                report += "\n"
        else:
            report += "⚠️ 未发现明确的可用工具\n"
        
        report += """## 💡 下一步建议

### 立即行动:
1. **验证发现工具**: 测试每个发现工具的实际可用性
2. **联系技术支持**: 获取完整的工具列表和文档
3. **重点测试**: 测试A股相关的数据工具

### 备用方案:
1. **并行开发东方财富API**作为主要A股数据源
2. **建立混合数据源架构**确保数据稳定性
3. **简化数据需求**聚焦彪哥战法核心数据

### 注意事项:
1. QVeris工具可能需要特定参数格式
2. 注意API调用频率限制
3. 建立错误处理和重试机制
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def print_summary(self):
        """打印探索总结"""
        print("\n" + "=" * 60)
        print("📈 QVeris工具探索总结")
        print("=" * 60)
        
        print(f"探索方法尝试: {len(self.exploration_log)}种")
        print(f"发现可用工具: {len(self.available_tools)}个")
        
        if self.available_tools:
            print("\n发现的工具:")
            for i, tool in enumerate(self.available_tools[:10], 1):  # 只显示前10个
                print(f"  {i}. {tool.get('name', '未知')} (ID: {tool.get('id', '未知')})")
            
            if len(self.available_tools) > 10:
                print(f"  ... 还有 {len(self.available_tools) - 10} 个工具")
        else:
            print("\n⚠️ 未发现明确的可用工具")
        
        print("\n💡 建议:")
        print("1. 联系QVeris技术支持获取完整工具列表")
        print("2. 并行开发东方财富API作为备用数据源")
        print("3. 建立混合数据源架构确保稳定性")

def main():
    """主函数"""
    print("🚀 QVeris工具探索 - 立即开始")
    print("=" * 60)
    
    explorer = QVerisExplorer()
    
    # 开始探索
    success = explorer.explore_by_keywords()
    
    # 保存结果
    explorer.save_results()
    
    # 打印总结
    explorer.print_summary()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ QVeris工具探索完成，发现可用工具")
    else:
        print("⚠️ QVeris工具探索有限，建议并行开发备用数据源")
    
    print("=" * 60)

if __name__ == "__main__":
    main()