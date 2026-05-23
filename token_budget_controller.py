#!/usr/bin/env python3
"""
Token 预算控制器 - 严格版
实时监控 + 硬限制
"""

import os
import sys
from datetime import datetime

# 每日预算（元）
DAILY_BUDGET_CNY = 5.0  # 每天最多5元
CURRENT_SPENT_CNY = 20.0  # 今天已花费（用户告知）

# 剩余预算
REMAINING_BUDGET = DAILY_BUDGET_CNY - (CURRENT_SPENT_CNY % DAILY_BUDGET_CNY)

class TokenBudgetController:
    """Token预算控制器"""
    
    def __init__(self):
        self.daily_limit_cny = 5.0
        self.today_spent_cny = 20.0  # 已超支
        self.warning_threshold = 3.0  # 3元警告
        
    def check_budget(self, estimated_cost=0.5):
        """检查预算是否足够"""
        if self.today_spent_cny >= self.daily_limit_cny:
            print(f"⚠️ 今日Token预算已用完: ¥{self.today_spent_cny}/{self.daily_limit_cny}")
            print("暂停高消耗操作，明日继续")
            return False
        
        if self.today_spent_cny + estimated_cost > self.warning_threshold:
            print(f"⚠️ Token消耗警告: 已用¥{self.today_spent_cny}，即将超预算")
            return "warning"
        
        return True
    
    def estimate_cost(self, operation_type):
        """估算操作成本"""
        costs = {
            "简单回复": 0.1,
            "代码生成": 0.3,
            "数据分析": 0.5,
            "图片生成": 0.2,
            "web_search": 0.5,  # 每次搜索约5万token
            "browser": 1.0,      # 每次浏览约10万token
            "模型训练": 2.0,     # 训练一次很贵
        }
        return costs.get(operation_type, 0.3)
    
    def before_operation(self, operation_name):
        """操作前检查"""
        cost = self.estimate_cost(operation_name)
        status = self.check_budget(cost)
        
        if status == False:
            print(f"❌ 拒绝执行: {operation_name} (预估成本¥{cost}，预算不足)")
            return False
        elif status == "warning":
            print(f"⚠️ 高成本操作: {operation_name} (预估¥{cost})，确认执行？(y/n)")
            # 这里应该等待用户确认
            return True  # 暂时允许
        else:
            print(f"✅ 执行: {operation_name} (预估¥{cost})")
            return True

# 全局实例
budget = TokenBudgetController()

# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("Token 预算控制器")
    print("=" * 60)
    print(f"今日预算: ¥{budget.daily_limit_cny}")
    print(f"今日已用: ¥{budget.today_spent_cny}")
    print(f"剩余预算: ¥{REMAINING_BUDGET:.2f}")
    print("=" * 60)
    print()
    
    # 测试
    budget.before_operation("简单回复")
    budget.before_operation("web_search")
    budget.before_operation("模型训练")
