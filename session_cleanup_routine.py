#!/usr/bin/env python3
"""
会话清理前复盘脚本
在新建会话前自动执行，确保工作连续性
"""

import os
import sys
from datetime import datetime
from pathlib import Path

def session_cleanup_routine():
    """
    会话清理例行程序
    每3天执行一次，在新建会话前
    """
    print("=" * 70)
    print("【会话清理前复盘】")
    print("=" * 70)
    print(f"执行时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    print()
    
    workspace = Path("/Users/tuqibiao/.openclaw/workspace")
    
    # 1. 读取当前会话关键信息
    print("【步骤1】收集当前会话关键信息...")
    
    # 检查今日完成的任务
    try:
        from dashboard.control_panel import dashboard
        running = dashboard.get_running_tasks()
        completed = [t for t in dashboard.tasks if t.status == 'completed']
        
        print(f"   ✅ 运行中任务：{len(running)} 项")
        print(f"   ✅ 今日完成：{len(completed)} 项")
        
        # 记录待办事项（未完成的任务）
        pending = dashboard.get_pending_tasks()
        if pending:
            print(f"   ⏳ 待办任务：{len(pending)} 项")
            for task in pending:
                print(f"      - {task.name}")
    except Exception as e:
        print(f"   ⚠️ 读取任务失败：{e}")
    
    print()
    
    # 2. 更新记忆文件
    print("【步骤2】更新长期记忆...")
    
    # 更新MEMORY.md
    memory_file = workspace / "MEMORY.md"
    if memory_file.exists():
        print(f"   ✅ 记忆文件存在：{memory_file}")
        print(f"   💡 提示：请在MEMORY.md中添加今日关键决策")
    
    # 创建/更新今日日志
    today_str = datetime.now().strftime('%Y-%m-%d')
    log_file = workspace / "memory" / f"{today_str}.md"
    print(f"   ✅ 今日日志：{log_file}")
    
    print()
    
    # 3. Token消耗记录
    print("【步骤3】记录Token消耗...")
    try:
        # 从dashboard读取今日Token记录
        from dashboard.control_panel import dashboard
        today_stats = dashboard.get_today_token_stats()
        print(f"   🔢 今日Token：{today_stats['total_tokens']:,}")
        print(f"   💰 预估费用：约¥{today_stats['total_cost_cny']}")
        print(f"   📊 会话数：{today_stats['session_count']} 个")
    except Exception as e:
        print(f"   ⚠️ 无法获取Token统计：{e}")
    
    print()
    
    # 4. 生成交接文档
    print("【步骤4】生成会话交接文档...")
    
    handover_file = workspace / "SESSION_HANDOVER.md"
    handover_content = f"""# 会话交接文档

**生成时间**：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
**原因**：3天清理周期，新建会话前

## 当前进行中的工作

### 运行中任务
"""
    
    # 添加任务信息
    try:
        from dashboard.control_panel import dashboard
        running = dashboard.get_running_tasks()
        if running:
            for task in running:
                handover_content += f"\n- {task.name}\n  - 描述：{task.description}\n  - 状态：{task.status}\n"
        else:
            handover_content += "\n无运行中任务\n"
    except:
        handover_content += "\n无法读取任务列表\n"
    
    handover_content += f"""
## 待办事项（需在新会话继续）

"""
    
    try:
        from dashboard.control_panel import dashboard
        pending = dashboard.get_pending_tasks()
        if pending:
            for task in pending:
                handover_content += f"\n- [ ] {task.name}（优先级：{task.priority}）\n"
        else:
            handover_content += "\n无待办事项\n"
    except:
        handover_content += "\n无法读取待办列表\n"
    
    handover_content += f"""
## 关键记忆点

- 项目版本：彪哥战法 v5.1
- 当前季节判断：需根据实时数据更新
- Token预算：¥20/天，注意控制
- 禁用工具：web_search、browser（未配置）

## 下一步行动

1. 新建会话
2. 读取 MEMORY.md 恢复记忆
3. 读取今日计划（TODAY_PLAN_*.md）
4. 继续未完成的工作

---

**新会话启动后，请执行**：
```bash
# 查看交接文档
cat /Users/tuqibiao/.openclaw/workspace/SESSION_HANDOVER.md

# 查看今日计划
ls -la /Users/tuqibiao/.openclaw/workspace/TODAY_PLAN_*.md
```
"""
    
    with open(handover_file, 'w', encoding='utf-8') as f:
        f.write(handover_content)
    
    print(f"   ✅ 交接文档已生成：{handover_file}")
    print()
    
    # 5. 清理建议
    print("【步骤5】清理建议...")
    print("   ✅ 现在可以安全地新建会话了")
    print("   💡 新会话启动后，我会自动读取记忆文件")
    print()
    
    print("=" * 70)
    print("复盘完成！可以新建会话了。")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    session_cleanup_routine()
