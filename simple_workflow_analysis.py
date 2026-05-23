#!/usr/bin/env python3
"""
简化版工作流程分析
"""

import os
import json
from datetime import datetime

def analyze_workflow():
    """分析工作流程"""
    
    print("🔍 工作流程分析报告")
    print("=" * 60)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 分析HEARTBEAT配置
    print("📊 1. 心跳配置分析")
    heartbeat_path = "/Users/tuqibiao/.openclaw/workspace/HEARTBEAT.md"
    if os.path.exists(heartbeat_path):
        with open(heartbeat_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tasks = []
        if "盘前分析" in content:
            tasks.append("盘前分析 (08:00)")
        if "盘后分析" in content:
            tasks.append("盘后分析 (17:00)")
        if "EGPS系统" in content:
            tasks.append("EGPS系统分析 (08:00)")
        
        print(f"  定时任务: {len(tasks)}个")
        for task in tasks:
            print(f"    • {task}")
        
        # 检查优化需求
        if "心跳检查优化提醒" in content:
            print("  ⚠️ 需要优化: 心跳频率过高")
        if "依赖问题" in content:
            print("  ⚠️ 需要修复: 依赖包缺失")
    else:
        print("  ❌ HEARTBEAT.md 不存在")
    
    print()
    
    # 2. 分析复盘文件使用
    print("📚 2. 复盘文件分析")
    review_dir = "/Users/tuqibiao/Downloads/2026复盘"
    if os.path.exists(review_dir):
        files = os.listdir(review_dir)
        pdf_files = [f for f in files if f.endswith('.pdf')]
        print(f"  总文件数: {len(files)}")
        print(f"  PDF文件: {len(pdf_files)}")
        
        # 显示最新文件
        latest_files = sorted(pdf_files, reverse=True)[:3]
        print(f"  最新文件:")
        for file in latest_files:
            print(f"    • {file}")
    else:
        print("  ❌ 复盘目录不存在")
    
    print()
    
    # 3. 分析技能使用
    print("🛠️ 3. 技能使用分析")
    skills_dir = "/Users/tuqibiao/.openclaw/workspace/skills"
    if os.path.exists(skills_dir):
        skill_count = len([f for f in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, f))])
        print(f"  已安装技能: {skill_count}个")
        
        # 常见技能检查
        common_skills = {
            "彪哥战法": ["biage-market-analyzer", "biage-premarket-analyzer", "biage-report-generator"],
            "自我提升": ["self-improving", "openclaw-agent-optimize"],
            "数据源": ["qveris-official", "tushare-finance"],
            "新闻收集": ["ai-news-collector"]
        }
        
        for category, skills in common_skills.items():
            installed = []
            for skill in skills:
                if os.path.exists(os.path.join(skills_dir, skill)):
                    installed.append(skill)
            if installed:
                print(f"  {category}: {len(installed)}/{len(skills)}")
    else:
        print("  ❌ 技能目录不存在")
    
    print()
    
    # 4. 工作习惯总结
    print("👤 4. 工作习惯特征")
    work_habits = {
        "分析风格": "专业、务实、反应快",
        "报告要求": "直接给出最终答案，不输出思考过程",
        "数据要求": "真实数据，具体分析，拒绝模拟数据",
        "沟通风格": "语言通俗易懂，语气轻松随意",
        "自动化要求": "完全自动化，主动监控，自我修复",
        "优化重点": "强化量能验证，集成连板分析"
    }
    
    for key, value in work_habits.items():
        print(f"  {key}: {value}")
    
    print()
    
    # 5. 优化建议
    print("🚀 5. 优化建议")
    
    suggestions = [
        {
            "优先级": "高",
            "建议": "优化心跳检查频率",
            "原因": "当前每小时检查一次，Token消耗过大",
            "方案": "调整为每天2-4次，或实现智能检查逻辑"
        },
        {
            "优先级": "高",
            "建议": "强化数据源验证",
            "原因": "需要确保所有分析使用真实数据",
            "方案": "建立多数据源交叉验证机制"
        },
        {
            "优先级": "中",
            "建议": "深度集成复盘分析",
            "原因": "复盘文件包含宝贵市场经验",
            "方案": "创建复盘文件自动解析和模式识别系统"
        },
        {
            "优先级": "中",
            "建议": "建立工作习惯学习系统",
            "原因": "基于历史交互持续优化工作流程",
            "方案": "创建工作习惯学习和自适应优化模块"
        }
    ]
    
    for suggestion in suggestions:
        print(f"  [{suggestion['优先级']}] {suggestion['建议']}")
        print(f"     原因: {suggestion['原因']}")
        print(f"     方案: {suggestion['方案']}")
        print()
    
    print("=" * 60)
    print("✅ 分析完成")
    
    # 保存分析结果
    save_analysis_result()

def save_analysis_result():
    """保存分析结果"""
    result = {
        "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": "工作流程分析完成",
        "recommendations": [
            "优化心跳检查频率，减少Token消耗",
            "强化数据源验证，确保分析准确性",
            "深度集成复盘文件分析",
            "建立工作习惯学习系统"
        ]
    }
    
    output_path = "/Users/tuqibiao/.openclaw/workspace/workflow_analysis_result.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"📁 分析结果已保存至: {output_path}")

if __name__ == "__main__":
    analyze_workflow()