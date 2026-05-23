#!/usr/bin/env python3
"""
彪哥战法 - 控制面板
统一管理任务、审批、产出和Token消耗
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

# 控制面板数据存储
DASHBOARD_DIR = Path("/Users/tuqibiao/.openclaw/workspace/dashboard")
DASHBOARD_DIR.mkdir(exist_ok=True)

DATA_FILE = DASHBOARD_DIR / "dashboard_data.json"


@dataclass
class Task:
    """任务"""
    id: str
    name: str
    status: str  # running, pending, completed, failed
    priority: str  # high, medium, low
    created_at: str
    updated_at: str
    description: str
    output_file: str = ""


@dataclass
class PendingApproval:
    """待审批内容"""
    id: str
    type: str  # strategy, report, analysis
    title: str
    content_summary: str
    submitted_at: str
    status: str  # pending, approved, rejected


@dataclass
class CompletedOutput:
    """已完成产出"""
    id: str
    type: str  # report, chart, analysis, code
    title: str
    file_path: str
    created_at: str
    description: str


@dataclass
class TokenRecord:
    """Token消耗记录"""
    date: str
    session_id: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    task_name: str


class DashboardManager:
    """控制面板管理器"""
    
    def __init__(self):
        self.tasks: List[Task] = []
        self.pending_approvals: List[PendingApproval] = []
        self.completed_outputs: List[CompletedOutput] = []
        self.token_records: List[TokenRecord] = []
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tasks = [Task(**t) for t in data.get('tasks', [])]
                self.pending_approvals = [PendingApproval(**p) for p in data.get('pending_approvals', [])]
                self.completed_outputs = [CompletedOutput(**c) for c in data.get('completed_outputs', [])]
                self.token_records = [TokenRecord(**t) for t in data.get('token_records', [])]
    
    def save_data(self):
        """保存数据"""
        data = {
            'tasks': [asdict(t) for t in self.tasks],
            'pending_approvals': [asdict(p) for p in self.pending_approvals],
            'completed_outputs': [asdict(c) for c in self.completed_outputs],
            'token_records': [asdict(t) for t in self.token_records],
            'updated_at': datetime.now().isoformat()
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ===== 任务管理 =====
    def add_task(self, name: str, description: str, priority: str = "medium") -> Task:
        """添加任务"""
        task = Task(
            id=f"任务_{len(self.tasks)+1:03d}",
            name=name,
            status="pending",
            priority=priority,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            description=description
        )
        self.tasks.append(task)
        self.save_data()
        return task
    
    def start_task(self, task_id: str):
        """开始任务"""
        for task in self.tasks:
            if task.id == task_id:
                task.status = "running"
                task.updated_at = datetime.now().isoformat()
                self.save_data()
                return True
        return False
    
    def complete_task(self, task_id: str, output_file: str = ""):
        """完成任务"""
        for task in self.tasks:
            if task.id == task_id:
                task.status = "completed"
                task.output_file = output_file
                task.updated_at = datetime.now().isoformat()
                self.save_data()
                return True
        return False
    
    def get_running_tasks(self) -> List[Task]:
        """获取运行中任务"""
        return [t for t in self.tasks if t.status == "running"]
    
    def get_pending_tasks(self) -> List[Task]:
        """获取待处理任务"""
        return [t for t in self.tasks if t.status == "pending"]
    
    # ===== 审批管理 =====
    def submit_for_approval(self, type_: str, title: str, content_summary: str) -> PendingApproval:
        """提交审批"""
        approval = PendingApproval(
            id=f"审批_{len(self.pending_approvals)+1:03d}",
            type=type_,
            title=title,
            content_summary=content_summary,
            submitted_at=datetime.now().isoformat(),
            status="pending"
        )
        self.pending_approvals.append(approval)
        self.save_data()
        return approval
    
    def approve(self, approval_id: str):
        """审批通过"""
        for apv in self.pending_approvals:
            if apv.id == approval_id:
                apv.status = "approved"
                self.save_data()
                return True
        return False
    
    def get_pending_approvals(self) -> List[PendingApproval]:
        """获取待审批列表"""
        return [p for p in self.pending_approvals if p.status == "pending"]
    
    # ===== 产出管理 =====
    def add_output(self, type_: str, title: str, file_path: str, description: str) -> CompletedOutput:
        """添加产出"""
        output = CompletedOutput(
            id=f"产出_{len(self.completed_outputs)+1:03d}",
            type=type_,
            title=title,
            file_path=file_path,
            created_at=datetime.now().isoformat(),
            description=description
        )
        self.completed_outputs.append(output)
        self.save_data()
        return output
    
    def get_recent_outputs(self, n: int = 10) -> List[CompletedOutput]:
        """获取最近产出"""
        return sorted(self.completed_outputs, key=lambda x: x.created_at, reverse=True)[:n]
    
    # ===== Token记录 =====
    def record_token_usage(self, session_id: str, input_tokens: int, output_tokens: int, 
                          cost_usd: float, task_name: str):
        """记录Token使用"""
        record = TokenRecord(
            date=datetime.now().strftime("%Y-%m-%d"),
            session_id=session_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_usd=cost_usd,
            task_name=task_name
        )
        self.token_records.append(record)
        self.save_data()
    
    def get_today_token_stats(self) -> Dict[str, Any]:
        """获取今日Token统计"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_records = [r for r in self.token_records if r.date == today]
        
        if not today_records:
            return {"total_tokens": 0, "cost_usd": 0, "count": 0}
        
        total_tokens = sum(r.total_tokens for r in today_records)
        total_cost = sum(r.cost_usd for r in today_records)
        
        return {
            "date": today,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "total_cost_cny": round(total_cost * 7.2, 2),
            "session_count": len(today_records),
            "records": today_records
        }
    
    def get_weekly_token_stats(self) -> Dict[str, Any]:
        """获取本周Token统计"""
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        week_records = [r for r in self.token_records if r.date >= week_ago]
        
        if not week_records:
            return {"total_tokens": 0, "cost_usd": 0}
        
        total_tokens = sum(r.total_tokens for r in week_records)
        total_cost = sum(r.cost_usd for r in week_records)
        
        # 按日期分组
        daily_stats = {}
        for r in week_records:
            if r.date not in daily_stats:
                daily_stats[r.date] = 0
            daily_stats[r.date] += r.total_tokens
        
        return {
            "week_range": f"{week_ago} 至 {datetime.now().strftime('%Y-%m-%d')}",
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "total_cost_cny": round(total_cost * 7.2, 2),
            "session_count": len(week_records),
            "daily_breakdown": daily_stats
        }
    
    # ===== 生成报告 =====
    def generate_dashboard_report(self) -> str:
        """生成控制面板报告（全中文）"""
        report = []
        report.append("=" * 70)
        report.append("【彪哥战法】控制面板")
        report.append("=" * 70)
        report.append(f"📅 更新时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        report.append("")
        
        # 1. 当前运行任务
        report.append("【一、任务状态概览】")
        running = self.get_running_tasks()
        pending_tasks = self.get_pending_tasks()
        completed_tasks = [t for t in self.tasks if t.status == 'completed']
        failed_tasks = [t for t in self.tasks if t.status == 'failed']
        
        report.append(f"   🔄 运行中：{len(running)} 项")
        report.append(f"   ⏳ 待处理：{len(pending_tasks)} 项") 
        report.append(f"   ✅ 已完成：{len(completed_tasks)} 项")
        if failed_tasks:
            report.append(f"   ❌ 失败：{len(failed_tasks)} 项")
        report.append("")
        
        if running:
            report.append("   ▶️ 正在进行的任务：")
            for task in running:
                report.append(f"      • {task.name}")
                report.append(f"        描述：{task.description}")
                report.append(f"        优先级：{self._translate_priority(task.priority)}")
                report.append("")
        else:
            report.append("   当前无运行中任务")
            report.append("")
        
        # 2. 待审批内容
        report.append("【二、待审批内容】")
        pending = self.get_pending_approvals()
        if pending:
            report.append(f"   您有 {len(pending)} 项内容待审批：")
            report.append("")
            for apv in pending:
                report.append(f"   📝 {apv.title}")
                report.append(f"      类型：{self._translate_type(apv.type)}")
                report.append(f"      提交时间：{apv.submitted_at[:10]}")
                report.append(f"      摘要：{apv.content_summary[:50]}...")
                report.append("")
        else:
            report.append("   暂无待审批内容 🎉")
            report.append("")
        
        # 3. 已完成产出
        report.append("【三、最近已完成产出】")
        outputs = self.get_recent_outputs(5)
        if outputs:
            report.append(f"   最近完成 {len(outputs)} 项产出：")
            report.append("")
            for out in outputs:
                type_emoji = {"chart": "📊", "report": "📄", "analysis": "🔍", "code": "💻"}.get(out.type, "📁")
                report.append(f"   {type_emoji} {out.title}")
                report.append(f"      类型：{self._translate_type(out.type)}")
                report.append(f"      完成时间：{out.created_at[:10]}")
                report.append(f"      文件位置：{out.file_path}")
                report.append("")
        else:
            report.append("   暂无已完成产出")
            report.append("")
        
        # 4. Token消耗统计
        report.append("【四、Token消耗统计】")
        today_stats = self.get_today_token_stats()
        
        if today_stats['total_tokens'] > 0:
            report.append(f"   📊 今日消耗（{today_stats.get('date', 'N/A')}）：")
            report.append(f"      💰 预估费用：¥{today_stats['total_cost_cny']}（约${today_stats['total_cost_usd']}）")
            report.append(f"      🔢 Token用量：{today_stats['total_tokens']:,} tokens")
            report.append(f"      💬 会话数：{today_stats['session_count']} 个")
            
            # 预算提醒
            cost_cny = today_stats['total_cost_cny']
            if cost_cny < 10:
                budget_status = "✅ 正常"
            elif cost_cny < 15:
                budget_status = "⚠️ 偏高"
            else:
                budget_status = "🚨 警告"
            report.append(f"      📈 预算状态：{budget_status}")
        else:
            report.append("   📊 今日暂无Token消耗记录")
        
        report.append("")
        
        # 本周统计
        week_stats = self.get_weekly_token_stats()
        if week_stats['total_tokens'] > 0:
            report.append(f"   📈 本周统计（{week_stats.get('week_range', 'N/A')}）：")
            report.append(f"      💰 总费用：¥{week_stats['total_cost_cny']}（约${week_stats['total_cost_usd']}）")
            report.append(f"      🔢 总Token：{week_stats['total_tokens']:,} tokens")
            report.append(f"      📊 日均：{week_stats['total_tokens']//7:,} tokens")
        
        report.append("")
        report.append("=" * 70)
        report.append("💡 使用提示：运行 'python3 control_panel.py' 可刷新此报告")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def _translate_priority(self, priority: str) -> str:
        """翻译优先级"""
        mapping = {'high': '🔴 高优先级', 'medium': '🟡 中优先级', 'low': '🟢 低优先级'}
        return mapping.get(priority, priority)
    
    def _translate_type(self, type_: str) -> str:
        """翻译类型"""
        mapping = {
            'strategy': '策略',
            'report': '报告', 
            'analysis': '分析',
            'code': '代码',
            'chart': '图表'
        }
        return mapping.get(type_, type_)


# 全局实例
dashboard = DashboardManager()


# 初始化一些示例数据（首次运行）
def init_sample_data():
    """初始化示例数据"""
    if not DATA_FILE.exists():
        print("🔄 首次运行，初始化示例数据...")
        
        # 添加今日完成的任务
        dashboard.add_task(
            name="Qlib + 彪哥战法融合",
            description="完成数据对接、四季判断模型、回测引擎",
            priority="high"
        )
        dashboard.complete_task(
            task_id="任务_001",
            output_file="qlib_biaoge/"
        )
        
        dashboard.add_task(
            name="实战仪表盘开发",
            description="开发可视化仪表盘，全中文显示",
            priority="high"
        )
        dashboard.complete_task(
            task_id="任务_002",
            output_file="dashboard.py"
        )
        
        # 添加产出
        dashboard.add_output(
            type_="chart",
            title="实战仪表盘",
            file_path="/Users/tuqibiao/Desktop/彪哥战法_实战仪表盘.png",
            description="四季判断可视化仪表盘"
        )
        
        dashboard.add_output(
            type_="chart",
            title="明日策略",
            file_path="/Users/tuqibiao/Desktop/彪哥战法_明日策略_0302.png",
            description="3月2日周一策略分析"
        )
        
        dashboard.add_output(
            type_="chart",
            title="美伊冲突影响分析",
            file_path="/Users/tuqibiao/Desktop/美伊冲突_市场影响分析.png",
            description="美伊局势对市场影响深度分析"
        )
        
        # 添加Token记录（示例）
        dashboard.record_token_usage(
            session_id="main_20260301",
            input_tokens=125000,
            output_tokens=2000,
            cost_usd=0.15,
            task_name="Qlib融合+仪表盘开发"
        )
        
        print("✅ 控制面板初始化完成！")
        print("")


if __name__ == "__main__":
    # 初始化
    init_sample_data()
    
    # 显示控制面板
    print(dashboard.generate_dashboard_report())
