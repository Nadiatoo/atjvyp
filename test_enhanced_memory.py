#!/usr/bin/env python3
"""
测试增强型记忆系统
"""

import sys
sys.path.append("/Users/tuqibiao/.openclaw/workspace")

try:
    from enhanced_memory_system import remember, recall, get_stats, get_recent
    
    print("🧠 测试增强型记忆系统")
    print("=" * 50)
    
    # 记录重要决策
    print("1. 记录重要决策...")
    memory_id = remember(
        '用户明确指示：mem0需要OpenAI API Key，不考虑该方案。专注于优化无需API Key的本地记忆系统。',
        category='system_decision',
        importance=0.95,
        user='老涂',
        decision_type='technology_selection',
        reason='避免外部API依赖和额外成本',
        date='2026-04-11'
    )
    print(f"   记忆ID: {memory_id}")
    
    # 搜索验证
    print("\n2. 搜索验证...")
    results = recall('API Key', category='system_decision', limit=2)
    print(f"   找到 {len(results)} 条相关记忆:")
    for i, result in enumerate(results):
        content = result.get('content', '')[:70]
        importance = result.get('importance', 0)
        relevance = result.get('relevance', 0)
        print(f"   结果{i+1}: {content}...")
        print(f"       重要性: {importance}, 相关性: {relevance:.2f}")
    
    # 显示近期记忆
    print("\n3. 近期高重要性记忆...")
    recent = get_recent(days=3, min_importance=0.8)
    print(f"   找到 {len(recent)} 条高重要性近期记忆")
    for i, mem in enumerate(recent[:3]):  # 只显示前3条
        content = mem.get('content', '')[:60]
        category = mem.get('category', 'unknown')
        print(f"   {i+1}. [{category}] {content}...")
    
    # 显示统计
    print("\n4. 记忆系统统计:")
    stats = get_stats()
    print(f"   总记忆数: {stats['total_memories']}")
    print(f"   高重要性记忆: {stats['high_importance_count']}")
    
    # 显示类别分布
    print("   类别分布:")
    for category, count in stats['by_category'].items():
        print(f"     - {category}: {count}")
    
    print("\n✅ 增强型记忆系统测试完成！")
    
except ImportError as e:
    print(f"❌ 无法导入增强型记忆系统: {e}")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()