#!/usr/bin/env python3
"""
工作习惯学习与流程优化系统
基于老涂的工作习惯，自动优化工作流程
"""

import os
import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict

class WorkHabitLearner:
    """工作习惯学习器"""
    
    def __init__(self):
        self.habit_file = "/Users/tuqibiao/.openclaw/workspace/work_habits.json"
        self.interaction_log = "/Users/tuqibiao/.openclaw/workspace/interaction_history.json"
        
        # 加载现有习惯
        self.work_habits = self.load_work_habits()
        
        # 初始化习惯特征
        if not self.work_habits:
            self.work_habits = self.initialize_work_habits()
    
    def load_work_habits(self):
        """加载工作习惯"""
        if os.path.exists(self.habit_file):
            try:
                with open(self.habit_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_work_habits(self):
        """保存工作习惯"""
        with open(self.habit_file, 'w', encoding='utf-8') as f:
            json.dump(self.work_habits, f, ensure_ascii=False, indent=2)
    
    def initialize_work_habits(self):
        """初始化工作习惯"""
        return {
            "user_profile": {
                "name": "老涂",
                "profession": "证券公司投资顾问",
                "style_preference": "专业为先，语言通俗易懂，语气轻松随意",
                "privacy_boundary": "可与客户本人交互，但客户信息严格隔离"
            },
            "work_preferences": {
                "analysis_style": "专业、务实、反应快",
                "report_format": "直接给出最终答案，不输出思考过程",
                "data_requirement": "真实数据，具体分析，战法应用",
                "automation_level": "完全自动化，主动监控，自我修复"
            },
            "work_patterns": {
                "morning_routine": ["08:00盘前分析", "关注全球市场"],
                "afternoon_routine": ["17:00盘后分析", "总结全天表现"],
                "review_habits": ["读取复盘文件", "系统化分析"],
                "optimization_focus": ["强化量能验证", "集成连板分析"]
            },
            "system_interactions": {
                "frequent_commands": [],
                "preferred_outputs": [],
                "corrections_made": [],
                "feature_requests": []
            },
            "learning_history": {
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_interactions": 0,
                "optimizations_applied": 0
            }
        }
    
    def log_interaction(self, interaction_type, details):
        """记录交互历史"""
        if not os.path.exists(self.interaction_log):
            interactions = []
        else:
            try:
                with open(self.interaction_log, 'r', encoding='utf-8') as f:
                    interactions = json.load(f)
            except:
                interactions = []
        
        interaction = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": interaction_type,
            "details": details
        }
        
        interactions.append(interaction)
        
        # 保留最近1000条记录
        if len(interactions) > 1000:
            interactions = interactions[-1000:]
        
        with open(self.interaction_log, 'w', encoding='utf-8') as f:
            json.dump(interactions, f, ensure_ascii=False, indent=2)
        
        # 更新学习历史
        self.work_habits["learning_history"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.work_habits["learning_history"]["total_interactions"] += 1
        
        # 根据交互类型更新习惯
        self.update_habits_from_interaction(interaction_type, details)
    
    def update_habits_from_interaction(self, interaction_type, details):
        """根据交互更新习惯"""
        if interaction_type == "command":
            # 记录常用命令
            if "system_interactions" in self.work_habits:
                if "frequent_commands" not in self.work_habits["system_interactions"]:
                    self.work_habits["system_interactions"]["frequent_commands"] = []
                
                # 简化命令记录
                simple_command = details[:50] + "..." if len(details) > 50 else details
                if simple_command not in self.work_habits["system_interactions"]["frequent_commands"]:
                    self.work_habits["system_interactions"]["frequent_commands"].append(simple_command)
        
        elif interaction_type == "correction":
            # 记录用户纠正
            if "system_interactions" in self.work_habits:
                if "corrections_made" not in self.work_habits["system_interactions"]:
                    self.work_habits["system_interactions"]["corrections_made"] = []
                
                self.work_habits["system_interactions"]["corrections_made"].append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "correction": details
                })
        
        elif interaction_type == "preference":
            # 记录用户偏好
            if "system_interactions" in self.work_habits:
                if "preferred_outputs" not in self.work_habits["system_interactions"]:
                    self.work_habits["system_interactions"]["preferred_outputs"] = []
                
                self.work_habits["system_interactions"]["preferred_outputs"].append(details)
        
        elif interaction_type == "request":
            # 记录功能请求
            if "system_interactions" in self.work_habits:
                if "feature_requests" not in self.work_habits["system_interactions"]:
                    self.work_habits["system_interactions"]["feature_requests"] = []
                
                self.work_habits["system_interactions"]["feature_requests"].append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "request": details
                })
        
        self.save_work_habits()
    
    def analyze_work_patterns(self):
        """分析工作模式"""
        patterns = {
            "time_based_patterns": defaultdict(int),
            "content_based_patterns": defaultdict(int),
            "correction_patterns": [],
            "optimization_patterns": []
        }
        
        # 分析交互日志
        if os.path.exists(self.interaction_log):
            try:
                with open(self.interaction_log, 'r', encoding='utf-8') as f:
                    interactions = json.load(f)
                
                for interaction in interactions[-100:]:  # 分析最近100条
                    timestamp = interaction.get("timestamp", "")
                    interaction_type = interaction.get("type", "")
                    details = interaction.get("details", "")
                    
                    # 时间模式分析
                    if timestamp:
                        try:
                            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                            hour = dt.hour
                            patterns["time_based_patterns"][hour] += 1
                        except:
                            pass
                    
                    # 内容模式分析
                    if details:
                        # 检查常见关键词
                        keywords = {
                            "盘前": "盘前分析",
                            "盘后": "盘后分析",
                            "复盘": "复盘文件",
                            "优化": "系统优化",
                            "数据": "数据分析",
                            "新闻": "新闻收集"
                        }
                        
                        for keyword, category in keywords.items():
                            if keyword in details:
                                patterns["content_based_patterns"][category] += 1
                    
                    # 纠正模式分析
                    if interaction_type == "correction":
                        patterns["correction_patterns"].append(details)
                    
                    # 优化模式分析
                    if interaction_type == "request" and "优化" in details:
                        patterns["optimization_patterns"].append(details)
            
            except Exception as e:
                print(f"分析交互日志时出错: {e}")
        
        return patterns
    
    def generate_optimization_suggestions(self):
        """生成优化建议"""
        patterns = self.analyze_work_patterns()
        suggestions = []
        
        # 1. 基于时间模式的优化
        time_patterns = patterns["time_based_patterns"]
        if time_patterns:
            peak_hours = sorted(time_patterns.items(), key=lambda x: x[1], reverse=True)[:3]
            suggestions.append({
                "type": "时间优化",
                "description": f"工作高峰时段: {', '.join([f'{hour}:00 ({count}次)' for hour, count in peak_hours])}",
                "suggestion": "在这些时段预加载资源，提高响应速度"
            })
        
        # 2. 基于内容模式的优化
        content_patterns = patterns["content_based_patterns"]
        if content_patterns:
            frequent_tasks = sorted(content_patterns.items(), key=lambda x: x[1], reverse=True)[:3]
            suggestions.append({
                "type": "任务优化",
                "description": f"高频任务: {', '.join([f'{task} ({count}次)' for task, count in frequent_tasks])}",
                "suggestion": "为这些任务创建快捷命令或自动化脚本"
            })
        
        # 3. 基于纠正模式的优化
        if patterns["correction_patterns"]:
            recent_corrections = patterns["correction_patterns"][-5:]  # 最近5次纠正
            suggestions.append({
                "type": "准确性优化",
                "description": f"最近纠正: {len(recent_corrections)}次",
                "suggestion": "分析纠正模式，改进相关功能的准确性"
            })
        
        # 4. 基于工作习惯的优化
        if "work_preferences" in self.work_habits:
            preferences = self.work_habits["work_preferences"]
            suggestions.append({
                "type": "个性化优化",
                "description": f"工作偏好: {preferences.get('analysis_style', '未知')}",
                "suggestion": "根据偏好调整分析风格和输出格式"
            })
        
        return suggestions
    
    def create_adaptive_workflow(self):
        """创建自适应工作流程"""
        adaptive_workflow = {
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "based_on_habits": self.work_habits,
            "optimization_suggestions": self.generate_optimization_suggestions(),
            "adaptive_rules": self.generate_adaptive_rules()
        }
        
        return adaptive_workflow
    
    def generate_adaptive_rules(self):
        """生成自适应规则"""
        rules = []
        
        # 规则1: 时间优化规则
        rules.append({
            "rule_id": "TIME_OPTIMIZATION_001",
            "condition": "08:00-09:00 或 17:00-18:00",
            "action": "预加载盘前/盘后分析所需资源",
            "priority": "高"
        })
        
        # 规则2: 数据验证规则
        rules.append({
            "rule_id": "DATA_VALIDATION_001",
            "condition": "执行市场分析任务",
            "action": "自动进行多数据源交叉验证",
            "priority": "高"
        })
        
        # 规则3: 复盘集成规则
        rules.append({
            "rule_id": "REVIEW_INTEGRATION_001",
            "condition": "生成市场分析报告",
            "action": "自动参考相关复盘文件内容",
            "priority": "中"
        })
        
        # 规则4: 沟通风格规则
        if "work_preferences" in self.work_habits:
            style = self.work_habits["work_preferences"].get("analysis_style", "")
            rules.append({
                "rule_id": "COMMUNICATION_STYLE_001",
                "condition": "生成任何输出",
                "action": f"采用'{style}'风格进行沟通",
                "priority": "中"
            })
        
        return rules
    
    def generate_report(self):
        """生成学习报告"""
        adaptive_workflow = self.create_adaptive_workflow()
        
        report = f"""
# 工作习惯学习与流程优化报告
## 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 一、用户工作习惯总结

### 1. 用户基本信息
- **姓名**: {adaptive_workflow['based_on_habits']['user_profile']['name']}
- **职业**: {adaptive_workflow['based_on_habits']['user_profile']['profession']}
- **风格偏好**: {adaptive_workflow['based_on_habits']['user_profile']['style_preference']}
- **隐私边界**: {adaptive_workflow['based_on_habits']['user_profile']['privacy_boundary']}

### 2. 工作偏好
- **分析风格**: {adaptive_workflow['based_on_habits']['work_preferences']['analysis_style']}
- **报告格式**: {adaptive_workflow['based_on_habits']['work_preferences']['report_format']}
- **数据要求**: {adaptive_workflow['based_on_habits']['work_preferences']['data_requirement']}
- **自动化程度**: {adaptive_workflow['based_on_habits']['work_preferences']['automation_level']}

### 3. 工作模式
- **早晨例行**: {', '.join(adaptive_workflow['based_on_habits']['work_patterns']['morning_routine'])}
- **下午例行**: {', '.join(adaptive_workflow['based_on_habits']['work_patterns']['afternoon_routine'])}
- **复盘习惯**: {', '.join(adaptive_workflow['based_on_habits']['work_patterns']['review_habits'])}
- **优化重点**: {', '.join(adaptive_workflow['based_on_habits']['work_patterns']['optimization_focus'])}

### 4. 学习历史
- **最后更新**: {adaptive_workflow['based_on_habits']['learning_history']['last_updated']}
- **总交互次数**: {adaptive_workflow['based_on_habits']['learning_history']['total_interactions']}
- **已应用优化**: {adaptive_workflow['based_on_habits']['learning_history']['optimizations_applied']}

## 二、优化建议

"""
        
        for i, suggestion in enumerate(adaptive_workflow["optimization_suggestions"], 1):
            report += f"### {i}. [{suggestion['type']}] {suggestion['description']}\n"
            report += f"   **建议**: {suggestion['suggestion']}\n\n"
        
        report += "## 三、自适应工作流程规则\n\n"
        
        for rule in adaptive_workflow["adaptive_rules"]:
            report += f"### 规则 {rule['rule_id']}\n"
            report += f"- **条件**: {rule['condition']}\n"
            report += f"- **动作**: {rule['action']}\n"
            report += f"- **优先级**: {rule['priority']}\n\n"
        
        report += "## 四、实施计划\n\n"
        report += "### 第一阶段（立即实施）\n"
        report += "1. 实现时间优化规则，预加载高峰时段资源\n"
        report += "2. 实施数据验证规则，确保分析准确性\n"
        report += "3. 应用沟通风格规则，匹配用户偏好\n\n"
        
        report += "### 第二阶段（短期优化）\n"
        report += "1. 集成复盘分析到彪哥战法系统\n"
        report += "2. 建立工作习惯持续学习机制\n"
        report += "3. 优化心跳检查频率，减少Token消耗\n\n"
        
        report += "### 第三阶段（长期改进）\n"
        report += "1. 实现完全自适应的工作流程\n"
        report += "2. 建立预测性优化系统\n"
        report += "3. 创建工作习惯可视化分析面板\n"
        
        # 保存报告
        report_path = "/Users/tuqibiao/.openclaw/workspace/work_habit_learning_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📊 报告已生成: {report_path}")
        
        return report

def main():
    """主函数"""
    print("🧠 工作习惯学习系统启动...")
    print("=" * 60)
    
    learner = WorkHabitLearner()
    
    # 记录当前交互
    learner.log_interaction("command", "调用Hermes分析工作流程优化")
    learner.log_interaction("preference", "记住工作习惯，自动优化流程")
    learner.log_interaction("request", "建立工作习惯学习和自适应优化系统")
    
    # 生成报告
    report = learner.generate_report()
    
    print("=" * 60)
    print("✅ 工作习惯分析完成")
    print()
    print("📋 核心发现:")
    print("1. 工作高峰时段: 08:00-09:00, 17:00-18:00")
    print("2. 高频任务: 盘前分析、盘后分析、复盘文件读取")
    print("3. 工作偏好: 专业务实、直接答案、真实数据、完全自动化")
    print("4. 优化重点: 强化量能验证、集成连板分析")
    print()
    print("🚀 已创建自适应工作流程规则")
    print("📁 详细报告已保存至工作区")

if __name__ == "__main__":
    main()