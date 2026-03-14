#!/usr/bin/env python3
"""
Skill注册表集成示例
展示如何在日常工作中使用skill注册表
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from skill_registry_manager import SkillRegistry

def example_project_startup(project_type, description):
    """
    项目启动示例：检查是否有现成skill可用
    """
    print(f"\n🔍 项目启动检查: {project_type}")
    print(f"   描述: {description}")
    print("=" * 60)
    
    registry = SkillRegistry()
    
    # 根据项目类型搜索相关skill
    if "金融" in project_type or "市场" in project_type or "股票" in project_type:
        print("📊 搜索金融相关skill...")
        finance_skills = registry.find_skill("市场", "finance")
        finance_skills.extend(registry.find_skill("股票", "finance"))
        finance_skills.extend(registry.find_skill("交易", "finance"))
        
        if finance_skills:
            print(f"✅ 找到 {len(finance_skills)} 个金融相关skill:")
            for skill in finance_skills[:5]:  # 显示前5个
                print(f"   • {skill['name']} - {skill['description'][:80]}...")
            
            # 推荐最相关的skill
            recommended = finance_skills[0]
            print(f"\n💡 推荐使用: {recommended['name']}")
            print(f"   位置: {recommended['location']}")
            return recommended['id']
        else:
            print("❌ 未找到金融相关skill，需要从头开发")
    
    elif "数据" in project_type or "分析" in project_type:
        print("📈 搜索数据分析相关skill...")
        data_skills = registry.find_skill("数据", "data")
        data_skills.extend(registry.find_skill("分析", "data"))
        
        if data_skills:
            print(f"✅ 找到 {len(data_skills)} 个数据分析相关skill:")
            for skill in data_skills[:5]:
                print(f"   • {skill['name']} - {skill['description'][:80]}...")
            
            recommended = data_skills[0]
            print(f"\n💡 推荐使用: {recommended['name']}")
            print(f"   位置: {recommended['location']}")
            return recommended['id']
    
    elif "系统" in project_type or "管理" in project_type:
        print("⚙️ 搜索系统管理相关skill...")
        system_skills = registry.find_skill("系统", "system")
        system_skills.extend(registry.find_skill("管理", "system"))
        
        if system_skills:
            print(f"✅ 找到 {len(system_skills)} 个系统管理相关skill:")
            for skill in system_skills[:5]:
                print(f"   • {skill['name']} - {skill['description'][:80]}...")
            
            recommended = system_skills[0]
            print(f"\n💡 推荐使用: {recommended['name']}")
            print(f"   位置: {recommended['location']}")
            return recommended['id']
    
    print("❌ 未找到相关skill，需要从头开发")
    return None

def example_skill_execution(skill_id, task_description):
    """
    skill执行示例：调用skill并更新使用统计
    """
    print(f"\n🚀 执行skill: {skill_id}")
    print(f"   任务: {task_description}")
    print("=" * 60)
    
    registry = SkillRegistry()
    skill_info = registry.get_skill(skill_id)
    
    if not skill_info:
        print(f"❌ Skill {skill_id} 未找到")
        return False
    
    print(f"✅ 找到skill: {skill_info['name']}")
    print(f"   描述: {skill_info['description'][:100]}...")
    print(f"   分类: {skill_info['category']}")
    print(f"   位置: {skill_info['location']}")
    
    # 模拟执行skill
    print(f"\n⚡ 执行中...")
    # 这里实际应该调用skill的执行逻辑
    
    # 更新使用统计
    success = registry.update_skill_usage(skill_id)
    if success:
        print(f"📊 使用统计已更新")
        print(f"   总使用次数: {skill_info.get('usage_count', 0) + 1}")
    else:
        print(f"⚠️ 更新使用统计失败")
    
    return True

def example_daily_workflow():
    """
    日常工作流示例
    """
    print("=" * 60)
    print("🏢 日常工作流示例")
    print("=" * 60)
    
    # 1. 早上：检查市场数据
    print("\n🌅 早上任务：市场数据分析")
    skill_id = example_project_startup(
        "金融数据分析", 
        "分析今日A股市场数据，生成盘前简报"
    )
    
    if skill_id:
        example_skill_execution(
            skill_id,
            "获取全球市场数据，分析对A股影响"
        )
    
    # 2. 下午：生成报告
    print("\n🌇 下午任务：报告生成")
    skill_id = example_project_startup(
        "金融报告生成",
        "生成今日市场分析报告"
    )
    
    if skill_id:
        example_skill_execution(
            skill_id,
            "生成JPG图片报告和Word文档"
        )
    
    # 3. 晚上：系统维护
    print("\n🌃 晚上任务：系统维护")
    skill_id = example_project_startup(
        "系统健康检查",
        "检查系统状态，清理临时文件"
    )
    
    if skill_id:
        example_skill_execution(
            skill_id,
            "运行健康检查，生成报告"
        )
    
    # 4. 生成今日工作报告
    print("\n📋 生成今日工作报告")
    registry = SkillRegistry()
    report = registry.generate_report()
    
    # 保存报告
    report_path = os.path.join(registry.workspace, "daily_work_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 工作报告已保存到: {report_path}")

def example_token_saving_analysis():
    """
    Token节省分析示例
    """
    print("\n" + "=" * 60)
    print("💰 Token节省分析")
    print("=" * 60)
    
    registry = SkillRegistry()
    
    # 假设每个skill开发需要消耗的Token
    TOKEN_PER_SKILL_DEV = 50000  # 开发一个skill平均消耗50k Token
    TOKEN_PER_SKILL_USE = 1000   # 使用一个skill平均消耗1k Token
    
    # 统计已注册的skill
    total_skills = len(registry.registry["registry"])
    user_skills = [s for s in registry.registry["registry"].values() if s.get("source") == "user"]
    system_skills = [s for s in registry.registry["registry"].values() if s.get("source") == "system"]
    
    print(f"📊 注册表统计:")
    print(f"   总skill数: {total_skills}")
    print(f"   用户skill: {len(user_skills)}")
    print(f"   系统skill: {len(system_skills)}")
    
    # 计算节省的Token
    saved_from_system = len(system_skills) * TOKEN_PER_SKILL_DEV
    saved_from_reuse = len(user_skills) * TOKEN_PER_SKILL_DEV * 0.5  # 假设重用节省50%开发成本
    
    total_saved = saved_from_system + saved_from_reuse
    
    print(f"\n💰 Token节省估算:")
    print(f"   系统skill节省: {saved_from_system:,} Token")
    print(f"   用户skill重用节省: {saved_from_reuse:,} Token")
    print(f"   总计节省: {total_saved:,} Token")
    
    # 假设每月执行100次任务
    monthly_tasks = 100
    reuse_rate = 0.7  # 70%的任务可以重用现有skill
    
    monthly_saving = monthly_tasks * reuse_rate * (TOKEN_PER_SKILL_DEV - TOKEN_PER_SKILL_USE)
    
    print(f"\n📈 月度节省估算:")
    print(f"   每月任务数: {monthly_tasks}")
    print(f"   skill重用率: {reuse_rate * 100:.0f}%")
    print(f"   每月节省: {monthly_saving:,} Token")
    print(f"   每年节省: {monthly_saving * 12:,} Token")

if __name__ == "__main__":
    # 运行示例
    example_daily_workflow()
    example_token_saving_analysis()
    
    print("\n" + "=" * 60)
    print("🎯 Skill注册表系统优势总结")
    print("=" * 60)
    print("""
1. ✅ 快速发现：无需记忆所有skill，快速找到所需功能
2. ✅ 避免重复：重用现有skill，避免重复开发
3. ✅ 节省Token：大幅减少开发成本，提高效率
4. ✅ 智能推荐：根据项目类型自动推荐最合适的skill
5. ✅ 使用统计：了解哪些skill最常用，优化资源分配
6. ✅ 统一管理：所有skill集中管理，便于维护和更新
    """)