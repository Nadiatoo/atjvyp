#!/usr/bin/env python3
"""
Token 预算控制器 - 优化版
预算：20元/天（约200万tokens）
策略：高预算+强优化，追求性价比
"""

import os
from datetime import datetime

class TokenBudgetManager:
    """Token预算管理器"""
    
    def __init__(self):
        self.daily_budget_cny = 20.0      # 每日预算20元
        self.warning_threshold = 15.0     # 15元警告
        self.critical_threshold = 18.0    # 18元严控
        self.today_spent = 20.0           # 今日已用（从明天开始重新计算）
        self.operation_log = []
        
    def log_operation(self, name, estimated_cost, actual_cost=None):
        """记录操作"""
        self.operation_log.append({
            'time': datetime.now().isoformat(),
            'name': name,
            'estimated': estimated_cost,
            'actual': actual_cost
        })
        if actual_cost:
            self.today_spent += actual_cost
    
    def check_permission(self, operation_type, detail=""):
        """检查是否允许执行"""
        cost = self.estimate_cost(operation_type)
        
        # 超预算拒绝
        if self.today_spent >= self.daily_budget_cny:
            return False, f"预算已用完(¥{self.today_spent})，建议明日继续"
        
        # 严格管控区
        if self.today_spent >= self.critical_threshold:
            return "strict", f"预算紧张(¥{self.today_spent})，仅允许核心任务"
        
        # 警告区
        if self.today_spent + cost >= self.warning_threshold:
            return "warning", f"即将超支(预估¥{self.today_spent + cost})"
        
        return True, f"允许执行(¥{cost})"
    
    def estimate_cost(self, operation_type):
        """精确估算成本（基于实际经验）"""
        costs = {
            # 低成本操作 (< ¥0.5)
            "简单回复": 0.1,
            "代码片段": 0.2,
            "文本分析": 0.3,
            "读取文件": 0.05,
            
            # 中成本操作 (¥0.5-1.0)
            "代码生成_小": 0.5,       # <100行
            "数据分析_简单": 0.6,
            "图片生成_单张": 0.3,
            "执行命令_简单": 0.4,
            
            # 高成本操作 (¥1.0-2.0)
            "代码生成_大": 1.2,       # >300行
            "模型训练_轻量": 1.5,
            "数据分析_复杂": 1.0,
            "多文件处理": 1.0,
            
            # 极高成本操作 (> ¥2.0，需审批)
            "web_search": 2.0,        # 每次失败重试很费
            "browser_自动化": 3.0,     # 未配置时反复失败
            "模型训练_完整": 3.0,
            "长对话_上下文": 2.5,      # >200k上下文
        }
        return costs.get(operation_type, 0.5)
    
    def get_daily_report(self):
        """生成日报"""
        remaining = self.daily_budget_cny - self.today_spent
        return {
            'budget': self.daily_budget_cny,
            'spent': round(self.today_spent, 2),
            'remaining': round(remaining, 2),
            'usage_rate': round(self.today_spent / self.daily_budget_cny * 100, 1),
            'operation_count': len(self.operation_log),
            'status': '正常' if remaining > 5 else '紧张' if remaining > 2 else '临界'
        }

# 全局实例
budget = TokenBudgetManager()

if __name__ == "__main__":
    print("Token 预算管理器 - 优化版")
    print(f"每日预算: ¥{budget.daily_budget_cny}")
    print(f"警告阈值: ¥{budget.warning_threshold}")
    print(f"严控阈值: ¥{budget.critical_threshold}")
    
    # 测试
    for op in ["简单回复", "代码生成_小", "web_search", "browser_自动化"]:
        status, msg = budget.check_permission(op)
        print(f"{op}: {status} - {msg}")
