#!/usr/bin/env python3
"""
mem0正确使用测试
基于mem0的实际API
"""

def test_mem0_correct_usage():
    """测试mem0的正确使用方法"""
    print("=" * 60)
    print("mem0正确使用测试")
    print("=" * 60)
    
    try:
        from mem0 import Memory
        
        print("1. 创建Memory实例...")
        # 注意：这需要有效的OpenAI API Key
        memory = Memory()
        print("✅ Memory实例创建成功")
        
        print("\n2. 添加记忆（使用messages参数）...")
        # mem0使用messages参数，格式是消息列表
        memory_id = memory.add(
            messages=[
                {"role": "user", "content": "用户喜欢喝咖啡"},
                {"role": "assistant", "content": "好的，已记录用户喜欢喝咖啡"}
            ],
            metadata={
                "test": True,
                "category": "用户偏好",
                "timestamp": "2026-04-03"
            }
        )
        print(f"✅ 记忆添加成功，ID: {memory_id}")
        
        print("\n3. 搜索记忆...")
        results = memory.search(
            query="用户喜欢喝什么？",
            limit=5
        )
        print(f"✅ 搜索成功，找到 {len(results)} 条相关记忆")
        
        if results:
            print("搜索结果示例:")
            for i, result in enumerate(results[:2], 1):
                # mem0返回的记忆包含messages
                messages = result.get('messages', [])
                if messages:
                    for msg in messages:
                        print(f"    {msg.get('role', 'unknown')}: {msg.get('content', '')[:50]}...")
        
        print("\n4. 获取所有记忆...")
        all_memories = memory.get_all(limit=10)
        print(f"✅ 获取到 {len(all_memories)} 条记忆")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        
        # 提供更具体的错误信息
        error_str = str(e)
        if "api_key" in error_str:
            print("\n⚠️ 需要OpenAI API Key")
            print("解决方案:")
            print("1. 设置环境变量: export OPENAI_API_KEY='your-key'")
            print("2. 或在代码中传递api_key")
        elif "connection" in error_str or "connect" in error_str:
            print("\n⚠️ 连接问题")
            print("可能需要配置向量数据库")
        
        return False

def test_mem0_with_qdrant():
    """测试使用Qdrant作为向量数据库"""
    print("\n" + "=" * 60)
    print("mem0 + Qdrant测试")
    print("=" * 60)
    
    try:
        # 首先检查是否安装了qdrant-client
        import importlib
        qdrant_spec = importlib.util.find_spec("qdrant_client")
        if qdrant_spec is None:
            print("安装qdrant-client...")
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "qdrant-client"], 
                          capture_output=True)
        
        from mem0 import Memory
        from mem0.configs.base import MemoryConfig
        from mem0.configs.vector_store import VectorStoreConfig
        
        print("1. 配置Qdrant向量数据库...")
        
        # 创建使用Qdrant的配置
        config = MemoryConfig(
            vector_store=VectorStoreConfig(
                provider="qdrant",
                config={
                    "collection_name": "mem0_test",
                    "path": "/tmp/mem0_qdrant_test",  # 本地存储路径
                    "on_disk": True  # 持久化存储
                }
            )
        )
        
        print("✅ Qdrant配置创建成功")
        
        print("\n2. 创建Memory实例...")
        memory = Memory(config=config)
        print("✅ Memory实例创建成功（使用Qdrant）")
        
        print("\n3. 测试基本操作...")
        # 添加记忆
        memory_id = memory.add(
            messages=[
                {"role": "user", "content": "测试使用Qdrant存储记忆"},
                {"role": "assistant", "content": "已使用Qdrant存储测试记忆"}
            ],
            metadata={"storage": "qdrant", "test": True}
        )
        print(f"✅ 记忆添加成功: {memory_id}")
        
        # 搜索
        results = memory.search("Qdrant测试", limit=3)
        print(f"✅ 搜索成功，找到 {len(results)} 条记忆")
        
        return True
        
    except Exception as e:
        print(f"❌ Qdrant测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("mem0正确使用测试")
    print("=" * 60)
    
    # 测试基本使用
    print("\n测试1: 基本使用（需要OpenAI API Key）")
    test_mem0_correct_usage()
    
    # 测试Qdrant集成
    print("\n测试2: Qdrant集成测试")
    test_mem0_with_qdrant()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    print("\nmem0使用总结:")
    print("1. 需要OpenAI API Key用于Embedding和LLM")
    print("2. 默认使用Qdrant作为向量数据库")
    print("3. 使用messages参数存储对话记忆")
    print("4. 支持metadata用于过滤和分类")
    
    print("\n实际部署建议:")
    print("1. 获取OpenAI API Key")
    print("2. 配置Qdrant数据库（本地或云端）")
    print("3. 根据业务需求设计记忆结构")
    print("4. 测试性能和准确性")

if __name__ == "__main__":
    main()