#!/usr/bin/env python3
"""
mem0简单测试脚本
测试mem0的基本功能
"""

import os
import sys

def test_mem0_simple():
    """简单测试mem0"""
    print("=" * 60)
    print("mem0简单功能测试")
    print("=" * 60)
    
    try:
        from mem0 import Memory
        
        print("1. 尝试创建Memory实例...")
        
        # 设置一个虚拟的OpenAI API Key用于测试
        os.environ["OPENAI_API_KEY"] = "sk-test123"
        
        # 尝试创建Memory实例
        memory = Memory()
        print("✅ Memory实例创建成功")
        
        print("\n2. 测试添加记忆...")
        # 添加测试记忆
        memory_id = memory.add(
            text="这是一个测试记忆，用于验证mem0的基本功能",
            metadata={
                "test": True,
                "category": "功能验证",
                "timestamp": "2026-04-03"
            }
        )
        print(f"✅ 记忆添加成功，ID: {memory_id}")
        
        print("\n3. 测试检索记忆...")
        # 检索记忆
        results = memory.search("测试记忆", top_k=3)
        print(f"✅ 检索到 {len(results)} 条相关记忆")
        
        if results:
            print("检索结果:")
            for i, result in enumerate(results, 1):
                text = result.get('text', '')[:80]
                print(f"  {i}. {text}...")
        
        print("\n4. 测试获取记忆数量...")
        all_memories = memory.get_all()
        print(f"✅ 总记忆数量: {len(all_memories)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print("\n可能的原因:")
        print("1. 需要有效的OpenAI API Key")
        print("2. 需要配置向量数据库")
        print("3. 网络连接问题")
        
        # 尝试查看更详细的错误
        import traceback
        traceback.print_exc()
        return False

def test_mem0_with_config():
    """使用配置测试mem0"""
    print("\n" + "=" * 60)
    print("mem0配置测试")
    print("=" * 60)
    
    try:
        from mem0 import Memory
        from mem0.configs.base import MemoryConfig
        from mem0.configs.vector_store import VectorStoreConfig
        from mem0.configs.llm import LlmConfig
        from mem0.configs.embedder import EmbedderConfig
        
        print("1. 创建自定义配置...")
        
        # 创建配置
        config = MemoryConfig(
            vector_store=VectorStoreConfig(
                provider="qdrant",
                config={
                    "collection_name": "mem0_test_collection",
                    "path": "/tmp/mem0_test_db"
                }
            ),
            llm=LlmConfig(
                provider="openai",
                config={
                    "api_key": "sk-test123",
                    "model": "gpt-3.5-turbo"
                }
            ),
            embedder=EmbedderConfig(
                provider="openai",
                config={
                    "api_key": "sk-test123",
                    "model": "text-embedding-3-small"
                }
            )
        )
        
        print("✅ 配置创建成功")
        
        print("\n2. 使用配置创建Memory实例...")
        memory = Memory(config=config)
        print("✅ Memory实例创建成功")
        
        print("\n3. 测试基本操作...")
        # 添加记忆
        memory_id = memory.add(
            text="使用自定义配置存储的记忆",
            metadata={"config_test": True}
        )
        print(f"✅ 记忆添加成功: {memory_id}")
        
        # 检索
        results = memory.search("自定义配置", top_k=2)
        print(f"✅ 检索成功，找到 {len(results)} 条记忆")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_mem0_client():
    """测试mem0客户端模式"""
    print("\n" + "=" * 60)
    print("mem0客户端测试")
    print("=" * 60)
    
    try:
        from mem0 import MemoryClient
        
        print("1. 创建MemoryClient...")
        # MemoryClient通常用于连接远程mem0服务
        client = MemoryClient(base_url="http://localhost:8080")
        print("✅ MemoryClient创建成功")
        
        print("\n注意: MemoryClient需要mem0服务正在运行")
        print("启动mem0服务: docker run -p 8080:8080 mem0ai/mem0")
        
        return True
    except Exception as e:
        print(f"❌ 客户端测试失败: {e}")
        print("这通常是正常的，因为mem0服务可能没有运行")
        return False

def main():
    """主函数"""
    print("mem0安装验证和功能测试")
    print("=" * 60)
    
    # 检查是否已安装
    try:
        import mem0
        print(f"✅ mem0已安装，版本: {mem0.__version__ if hasattr(mem0, '__version__') else '未知'}")
    except ImportError:
        print("❌ mem0未安装")
        print("\n安装命令:")
        print("pip install mem0ai")
        return
    
    # 运行简单测试
    test_mem0_simple()
    
    # 运行配置测试
    test_mem0_with_config()
    
    # 运行客户端测试
    test_mem0_client()
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print("\nmem0已成功安装，但需要正确配置才能使用:")
    print("1. 需要有效的OpenAI API Key")
    print("2. 需要配置向量数据库（如Qdrant）")
    print("3. 或者使用mem0的Docker服务模式")
    
    print("\n下一步建议:")
    print("1. 获取OpenAI API Key")
    print("2. 安装和配置Qdrant向量数据库")
    print("3. 或使用mem0的Docker服务")
    print("4. 测试实际业务场景")

if __name__ == "__main__":
    main()