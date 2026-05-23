#!/usr/bin/env python3
"""
工作习惯分析与流程优化系统
基于老涂的工作习惯和需求，自动优化工作流程
"""

import os
import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict

class WorkflowOptimizer:
    """工作流程优化器"""
    
    def __init__(self):
        self.workflow_file = "/Users/tuqibiao/.openclaw/workspace/workflow_patterns.json"
        self.optimization_file = "/Users/tuqibiao/.openclaw/workspace/workflow_optimizations.json"
        
        # 加载工作习惯数据
        self.workflow_patterns = self.load_workflow_patterns()
        
        # 老涂的工作习惯特征（基于历史交互分析）
        self.work_habits = {
            "analysis_preference": {
                "market_analysis": "专业、务实、反应快",
                "report_format": "直接给出最终答案，不输出思考过程",
                "data_source": "真实数据，具体分析，战法应用",
                "communication": "语言通俗易懂，语气轻松随意"
            },
            "work_patterns": {
                "morning_routine": "08:00盘前分析，关注全球市场",
                "afternoon_routine": "17:00盘后分析，总结全天表现",
                "review_habits": "读取复盘文件，系统化分析",
                "optimization_focus": "强化量能验证，集成连板分析"
            },
            "system_requirements": {
                "automation": "完全自动化，主动监控，自我修复",
                "reliability": "系统可靠，无需人工干预",
                "data_quality": "真实数据，拒绝模拟数据",
                "analysis_depth": "具体分析，避免假大空"
            }
        }
        
        # 当前工作流程状态
        self.current_workflow = self.analyze_current_workflow()
    
    def load_workflow_patterns(self):
        """加载工作流程模式"""
        if os.path.exists(self.workflow_file):
            try:
                with open(self.workflow_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"patterns": [], "optimizations": []}
        return {"patterns": [], "optimizations": []}
    
    def save_workflow_patterns(self):
        """保存工作流程模式"""
        with open(self.workflow_file, 'w', encoding='utf-8') as f:
            json.dump(self.workflow_patterns, f, ensure_ascii=False, indent=2)
    
    def analyze_current_workflow(self):
        """分析当前工作流程"""
        # 分析HEARTBEAT.md配置
        heartbeat_config = self.analyze_heartbeat_config()
        
        # 分析定时任务
        cron_tasks = self.analyze_cron_tasks()
        
        # 分析技能使用情况
        skill_usage = self.analyze_skill_usage()
        
        # 分析复盘文件使用
        review_usage = self.analyze_review_usage()
        
        return {
            "heartbeat_config": heartbeat_config,
            "cron_tasks": cron_tasks,
            "skill_usage": skill_usage,
            "review_usage": review_usage,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def analyze_heartbeat_config(self):
        """分析心跳配置"""
        heartbeat_path = "/Users/tuqibiao/.openclaw/workspace/HEARTBEAT.md"
        
        if not os.path.exists(heartbeat_path):
            return {"status": "未配置", "tasks": []}
        
        try:
            with open(heartbeat_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取定时任务
            tasks = []
            if "盘前分析" in content:
                tasks.append({"name": "盘前分析", "time": "08:00", "weekdays": "周一至周五"})
            if "盘后分析" in content:
                tasks.append({"name": "盘后分析", "time": "17:00", "weekdays": "周一至周五"})
            if "EGPS系统" in content:
                tasks.append({"name": "EGPS系统分析", "time": "08:00", "weekdays": "周一至周五"})
            
            # 检查优化提醒
            optimizations_needed = []
            if "心跳检查优化提醒" in content:
                optimizations_needed.append("心跳频率优化")
            if "依赖问题" in content:
                optimizations_needed.append("依赖包修复")
            
            return {
                "status": "已配置",
                "task_count": len(tasks),
                "tasks": tasks,
                "optimizations_needed": optimizations_needed,
                "last_updated": os.path.getmtime(heartbeat_path)
            }
            
        except Exception as e:
            return {"status": "分析失败", "error": str(e)}
    
    def analyze_cron_tasks(self):
        """分析定时任务"""
        # 检查定时任务目录
        cron_dir = "/Users/tuqibiao/.openclaw/cron"
        tasks = []
        
        if os.path.exists(cron_dir):
            for file in os.listdir(cron_dir):
                if file.endswith('.json'):
                    try:
                        with open(os.path.join(cron_dir, file), 'r', encoding='utf-8') as f:
                            task_data = json.load(f)
                            tasks.append({
                                "name": task_data.get("name", file),
                                "schedule": task_data.get("schedule", "未知"),
                                "enabled": task_data.get("enabled", False)
                            })
                    except:
                        pass
        
        return {
            "task_count": len(tasks),
            "tasks": tasks,
            "directory": cron_dir if os.path.exists(cron_dir) else "未创建"
        }
    
    def analyze_skill_usage(self):
        """分析技能使用情况"""
        skills_dir = "/Users/tuqibiao/.openclaw/workspace/skills"
        skill_usage = defaultdict(int)
        
        # 基于历史交互分析常用技能
        common_skills = {
            "彪哥战法相关": ["biage-market-analyzer", "biage-premarket-analyzer", "biage-report-generator"],
            "系统管理": ["self-improving", "openclaw-agent-optimize", "find-skills"],
            "数据处理": ["qveris-official", "data-analyst", "tushare-finance"],
            "新闻收集": ["ai-news-collector"]
        }
        
        # 检查技能目录
        if os.path.exists(skills_dir):
            for skill_type, skill_list in common_skills.items():
                for skill in skill_list:
                    skill_path = os.path.join(skills_dir, skill)
                    if os.path.exists(skill_path):
                        skill_usage[skill_type] += 1
        
        return {
            "skill_categories": dict(skill_usage),
            "total_skills": sum(skill_usage.values()),
            "most_used": max(skill_usage.items(), key=lambda x: x[1]) if skill_usage else ("无", 0)
        }
    
    def analyze_review_usage(self):
        """分析复盘文件使用情况"""
        review_dir = "/Users/tuqibiao/Downloads/2026复盘"
        
        if not os.path.exists(review_dir):
            return {"status": "目录不存在", "file_count": 0}
        
        try:
            files = os.listdir(review_dir)
            pdf_files = [f for f in files if f.endswith('.pdf')]
            
            # 按月份统计
            monthly_stats = defaultdict(int)
            for file in pdf_files:
                # 提取月份信息（假设文件名格式为 X.X复盘.pdf）
                if '.' in file:
                    parts = file.split('.')
                    if len(parts) >= 2:
                        month = parts[0]  # 第一个点前的部分
                        monthly_stats[month] += 1
            
            return {
                "status": "正常",
                "total_files": len(files),
                "pdf_files": len(pdf_files),
                "monthly_stats": dict(monthly_stats),
                "latest_files": sorted(pdf_files, reverse=True)[:5]
            }
            
        except Exception as e:
            return {"status": "分析失败", "error": str(e)}
    
    def identify_optimization_opportunities(self):
        """识别优化机会"""
        opportunities = []
        
        # 1. 心跳频率优化
        if self.current_workflow["heartbeat_config"].get("optimizations_needed"):
            if "心跳频率优化" in self.current_workflow["heartbeat_config"]["optimizations_needed"]:
                opportunities.append({
                    "category": "性能优化",
                    "priority": "高",
                    "description": "心跳检查过于频繁，导致不必要的Token消耗",
                    "solution": "调整心跳检查频率为每天2-4次，或实现智能检查逻辑",
                    "expected_impact": "减少80%以上的Token消耗"
                })
        
        # 2. 数据源可靠性
        if self.work_habits["system_requirements"]["data_quality"] == "真实数据，拒绝模拟数据":
            opportunities.append({
                "category": "数据质量",
                "priority": "高",
                "description": "需要确保所有分析使用真实数据，拒绝模拟数据",
                "solution": "建立多数据源验证机制，实时监控数据质量",
                "expected_impact": "提高分析准确性和可信度"
            })
        
        # 3. 自动化程度提升
        if self.work_habits["system_requirements"]["automation"] == "完全自动化，主动监控，自我修复":
            opportunities.append({
                "category": "自动化",
                "priority": "中",
                "description": "需要实现完全自动化，减少人工干预",
                "solution": "建立系统健康监控和自动修复机制",
                "expected_impact": "减少90%以上的人工干预需求"
            })
        
        # 4. 复盘文件集成
        if self.current_workflow["review_usage"]["status"] == "正常":
            opportunities.append({
                "category": "分析深度",
                "priority": "中",
                "description": "复盘文件分析需要更深度集成到彪哥战法系统",
                "solution": "建立复盘文件自动解析和模式识别系统",
                "expected_impact": "提高市场分析的历史参考价值"
            })
        
        # 5. 技能使用优化
        skill_stats = self.current_workflow["skill_usage"]
        if skill_stats["total_skills"] > 0:
            opportunities.append({
                "category": "技能管理",
                "priority": "低",
                "description": f"已安装{skill_stats['total_skills']}个技能，需要优化使用效率",
                "solution": "建立技能使用统计和优先级排序系统",
                "expected_impact": "提高技能使用效率和系统性能"
            })
        
        return opportunities
    
    def generate_optimization_plan(self):
        """生成优化计划"""
        opportunities = self.identify_optimization_opportunities()
        
        # 按优先级排序
        priority_order = {"高": 3, "中": 2, "低": 1}
        opportunities.sort(key=lambda x: priority_order.get(x["priority"], 0), reverse=True)
        
        optimization_plan = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "work_habits_summary": self.work_habits,
            "current_workflow_status": self.current_workflow,
            "optimization_opportunities": opportunities,
            "implementation_plan": self.create_implementation_plan(opportunities)
        }
        
        # 保存优化计划
        with open(self.optimization_file, 'w', encoding='utf-8') as f:
            json.dump(optimization_plan, f, ensure_ascii=False, indent=2)
        
        return optimization_plan
    
    def create_implementation_plan(self, opportunities):
        """创建实施计划"""
        implementation_steps = []
        
        # 第一阶段：立即实施（高优先级）
        high_priority = [opp for opp in opportunities if opp["priority"] == "高"]
        if high_priority:
            implementation_steps.append({
                "phase": "第一阶段（立即实施）",
                "timeline": "1-3天",
                "tasks": [
                    {
                        "task": "优化心跳检查频率",
                        "description": "实现智能检查逻辑，减少Token消耗",
                        "deliverable": "更新HEARTBEAT.md配置，创建智能检查脚本"
                    },
                    {
                        "task": "强化数据源验证",
                        "description": "确保所有分析使用真实数据",
                        "deliverable": "建立多数据源交叉验证机制"
                    }
                ]
            })
        
        # 第二阶段：短期优化（中优先级）
        medium_priority = [opp for opp in opportunities if opp["priority"] == "中"]
        if medium_priority:
            implementation_steps.append({
                "phase": "第二阶段（短期优化）",
                "timeline": "1-2周",
                "tasks": [
                    {
                        "task": "提升自动化程度",
                        "description": "建立系统健康监控和自动修复",
                        "deliverable": "创建系统监控脚本和自动修复机制"
                    },
                    {
                        "task": "深度集成复盘文件",
                        "description": "将复盘分析集成到彪哥战法系统",
                        "deliverable": "创建复盘文件自动解析和模式识别模块"
                    }
                ]
            })
        
        # 第三阶段：长期改进（低优先级）
        low_priority = [opp for opp in opportunities if opp["priority"] == "低"]
        if low_priority:
            implementation_steps.append({
                "phase": "第三阶段（长期改进）",
                "timeline": "1个月",
                "tasks": [
                    {
                        "task": "优化技能管理",
                        "description": "提高技能使用效率和系统性能",
                        "deliverable": "创建技能使用统计和优先级排序系统"
                    },
                    {
                        "task": "建立工作习惯学习系统",
                        "description": "基于交互历史持续优化工作流程",
                        "deliverable": "创建工作习惯学习和自适应优化模块"
                    }
                ]
            })
        
        return implementation_steps
    
    def generate_report(self):
        """生成优化报告"""
        optimization_plan = self.generate_optimization_plan()
        
        report = f"""
# 工作流程优化分析报告
## 生成时间：{optimization_plan['generated_at']}

## 一、工作习惯特征总结

### 1. 分析偏好
- **市场分析风格**：{optimization_plan['work_habits_summary']['analysis_preference']['market_analysis']}
- **报告格式要求**：{optimization_plan['work_habits_summary']['analysis_preference']['report_format']}
- **数据源要求**：{optimization_plan['work_habits_summary']['analysis_preference']['data_source']}
- **沟通风格**：{optimization_plan['work_habits_summary']['analysis_preference']['communication']}

### 2. 工作模式
- **早晨例行**：{optimization_plan['work_habits_summary']['work_patterns']['morning_routine']}
- **下午例行**：{optimization_plan['work_habits_summary']['work_patterns']['afternoon_routine']}
- **复盘习惯**：{optimization_plan['work_habits_summary']['work_patterns']['review_habits']}
- **优化重点**：{optimization_plan['work_habits_summary']['work_patterns']['optimization_focus']}

### 3. 系统要求
- **自动化程度**：{optimization_plan['work_habits_summary']['system_requirements']['automation']}
- **可靠性要求**：{optimization_plan['work_habits_summary']['system_requirements']['reliability']}
- **数据质量**：{optimization_plan['work_habits_summary']['system_requirements']['data_quality']}
- **分析深度**：{optimization_plan['work_habits_summary']['system_requirements']['analysis_depth']}

## 二、当前工作流程状态

### 1. 心跳配置
- **状态**：{optimization_plan['current_workflow_status']['heartbeat_config']['status']}
- **任务数量**：{optimization_plan['current_workflow_status']['heartbeat_config'].get('task_count', 0)}
- **需要优化**：{', '.join(optimization_plan['current_workflow_status']['heartbeat_config'].get('optimizations_needed', [])) or '无'}

### 2. 定时任务
- **任务数量**：{optimization_plan['current_workflow_status']['cron_tasks']['task_count']}
- **目录状态**：{optimization_plan['current_workflow_status']['cron_tasks']['directory']}

### 3. 技能使用
- **技能分类**：{json.dumps(optimization_plan['current_workflow_status']['skill_usage']['skill_categories'], ensure_ascii=False)}
- **总技能数**：{optimization_plan['current_workflow_status']['skill_usage']['total_skills']}
- **最常用**：{optimization_plan['current_workflow_status']['skill_usage']['most_used'][0]}（{optimization_plan['current_workflow_status']['skill_usage']['most_used'][1]}次）

### 4. 复盘文件使用
- **状态**：{optimization_plan['current_workflow_status']['review_usage']['status']}
- **总文件数**：{optimization_plan['current_workflow_status']['review_usage'].get('total_files', 0)}
- **PDF文件**：{optimization_plan['current_workflow_status']['review_usage'].get('pdf_files', 0)}

## 三、优化机会识别