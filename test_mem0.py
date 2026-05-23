#!/usr/bin/env python3
"""
测试mem0记忆管理系统
"""

import os
from mem0 import Memory

def test_basic_memory():
    """测试基本记忆功能"""
    print("🧠 测试mem0记忆管理系统...")
    
    # 检查OpenAI API Key
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        print("⚠️ 未找到OPENAI_API_KEY环境变量")
        print("💡 提示: mem0需要OpenAI API Key用于embeddings")
        return False
    
    try:
        # 初始化记忆系统
        print("1. 初始化记忆系统...")
        memory = Memory()
        
        # 存储一些测试记忆
        print("2. 存储测试记忆...")
        
        # 记忆1: 用户信息
        memory_id1 = memory.add(
            messages=[
                {"role": "user", "content": "我是老涂，证券公司投资顾问"},
                {"role": "assistant", "content": "好的，已记录用户职业信息"}
            ],
            metadata={
                "user": "老涂",
                "profession": "投资顾问",
                "category": "user_profile",
                "importance": "high"
            }
        )
        print(f"  记忆1 ID: {memory_id1}")
        
        # 记忆2: 项目信息
        memory_id2 = memory.add(
            messages=[
                {"role": "user", "content": "我们正在开发彪哥战法v5.0系统"},
                {"role": "assistant", "content": "这是一个A股市场分析系统"}
            ],
            metadata={
                "project": "彪哥战法",
                "version": "v5.0",
                "type": "trading_system",
                "status": "active"
            }
        )
        print(f"  记忆2 ID: {memory_id2}")
        
        # 记忆3: 今天的工作
        memory_id3 = memory.add(
            messages=[
                {"role": "user", "content": "今天修复了飞书推送配置和头像问题"},
                {"role": "assistant", "content": "系统状态已恢复正常"}
            ],
            metadata={
                "date": "2026-04-11",
                "tasks": ["飞书推送修复", "头像更新"],
                "status": "completed"
            }
        )
        print(f"  记忆3 ID: {memory_id3}")
        
        # 测试检索功能
        print("\n3. 测试记忆检索...")
        
        # 检索用户信息
        print("  检索'用户职业':")
        results = memory.search("用户职业是什么？", top_k=2)
        for i, result in enumerate(results):
            print(f"    结果{i+1}: {result['messages'][0]['content'][:50]}...")
        
        # 检索项目信息
        print("  检索'彪哥战法':")
        results = memory.search("彪哥战法系统", top_k=2)
        for i, result in enumerate(results):
            print(f"    结果{i+1}: {result['messages'][0]['content'][:50]}...")
        
        # 检索今天的工作
        print("  检索'今天的工作':")
        results = memory.search("今天做了什么工作", top_k=2)
        for i, result in enumerate(results):
            print(f"    结果{i+1}: {result['messages'][0]['content'][:50]}...")
        
        # 测试元数据过滤
        print("\n4. 测试元数据过滤:")
        results = memory.search(
            query="系统",
            metadata_filter={"project": "彪哥战法"},
            top_k=2
        )
        print(f"  找到{len(results)}条彪哥战法相关记忆")
        
        # 获取所有记忆
        print("\n5. 获取所有记忆统计:")
        all_memories = memory.get_all()
        print(f"  总记忆数量: {len(all_memories)}")
        
        print("\n✅ mem0测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ mem0测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_persistence():
    """测试记忆持久化"""
    print("\n🧪 测试记忆持久化...")
    
    try:
        # 第一次初始化并存储记忆
        memory1 = Memory()
        test_id = memory1.add(
            messages=[
                {"role": "user", "content": "这是一个持久化测试记忆"},
                {"role": "assistant", "content": "记忆应该在不同会话间保持"}
            ],
            metadata={"test": "persistence", "timestamp": "2026-04-11"}
        )
        print(f"  存储测试记忆 ID: {test_id}")
        
        # 模拟新会话：重新初始化
        print("  模拟新会话...")
        memory2 = Memory()
        
        # 尝试检索
        results = memory2.search("持久化测试", top_k=1)
        if results:
            print(f"  ✅ 成功检索到持久化记忆: {results[0]['messages'][0]['content']}")
            return True
        else:
            print("  ❌ 未找到持久化记忆")
            return False
            
    except Exception as e:
        print(f"  ❌ 持久化测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("mem0记忆管理系统测试")
    print("=" * 50)
    
    # 测试基本功能
    basic_ok = test_basic_memory()
    
    # 测试持久化（如果基本功能正常）
    if basic_ok:
        persistence_ok = test_memory_persistence()
    
    print("\n" + "=" * 50)
    print("测试总结:")
    print(f"  基本功能: {'✅ 通过' if basic_ok else '❌ 失败'}")
    if basic_ok:
        print(f"  持久化: {'✅ 通过' if persistence_ok else '❌ 失败'}")
    
    print("\n💡 使用建议:")
    print("1. 确保OPENAI_API_KEY环境变量已设置")
    print("2. mem0默认使用ChromaDB本地存储")
    print("3. 可以配置使用其他向量数据库")
    print("4. 建议定期备份记忆数据")