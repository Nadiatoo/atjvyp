#!/usr/bin/env python3
"""
mem0功能测试脚本
测试mem0的基本记忆存储和检索功能
"""

import sys
import os

def test_mem0_installation():
    """测试mem0是否已安装"""
    print("=" * 60)
    print("测试mem0安装状态")
    print("=" * 60)
    
    try:
        # 尝试导入mem0
        from mem0 import Memory
        print("✅ mem0 Python包已安装")
        return True
    except ImportError as e:
        print(f"❌ mem0未安装: {e}")
        print("\n安装建议:")
        print("1. 使用pip安装: pip install mem0ai")
        print("2. 使用国内镜像: pip install mem0ai -i https://pypi.tuna.tsinghua.edu.cn/simple")
        return False
    except Exception as e:
        print(f"❌ 导入mem0时出错: {e}")
        return False

def test_basic_functionality():
    """测试mem0基本功能"""
    print("\n" + "=" * 60)
    print("测试mem0基本功能")
    print("=" * 60)
    
    try:
        from mem0 import Memory
        
        # 创建内存实例（使用本地Embedding模型）
        print("1. 创建Memory实例（使用本地模型）...")
        memory = Memory(
            embedding_model="all-MiniLM-L6-v2",
            local_embedding=True
        )
        print("✅ Memory实例创建成功（使用本地Embedding）")
        
        # 测试添加记忆
        print("\n2. 测试添加记忆...")
        test_memory_id = memory.add(
            text="这是一个测试记忆，用于验证mem0功能",
            metadata={
                "test": True,
                "category": "功能测试",
                "timestamp": "2026-04-03"
            }
        )
        print(f"✅ 记忆添加成功，ID: {test_memory_id}")
        
        # 测试检索记忆
        print("\n3. 测试检索记忆...")
        results = memory.search("测试记忆", top_k=3)
        print(f"✅ 检索到 {len(results)} 条相关记忆")
        
        if results:
            print("检索结果示例:")
            for i, result in enumerate(results[:2], 1):
                print(f"  {i}. {result.get('text', '')[:50]}...")
        
        # 测试获取所有记忆
        print("\n4. 测试获取所有记忆...")
        all_memories = memory.get_all()
        print(f"✅ 总记忆数量: {len(all_memories)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_openai_embedding():
    """测试使用OpenAI Embedding（需要API Key）"""
    print("\n" + "=" * 60)
    print("测试OpenAI Embedding集成")
    print("=" * 60)
    
    # 检查是否有OpenAI API Key
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        print("⚠️ 未找到OPENAI_API_KEY环境变量")
        print("跳过OpenAI Embedding测试")
        return None
    
    try:
        from mem0 import Memory
        
        print("使用OpenAI Embedding创建Memory实例...")
        memory = Memory(
            embedding_model="text-embedding-3-small",
            openai_api_key=openai_key
        )
        
        # 添加测试记忆
        memory_id = memory.add(
            text="使用OpenAI Embedding存储的记忆",
            metadata={"embedding": "openai", "test": True}
        )
        
        # 检索
        results = memory.search("OpenAI记忆", top_k=2)
        print(f"✅ OpenAI Embedding测试成功，检索到 {len(results)} 条记忆")
        
        return True
    except Exception as e:
        print(f"❌ OpenAI Embedding测试失败: {e}")
        return False

def test_local_embedding():
    """测试本地Embedding模型"""
    print("\n" + "=" * 60)
    print("测试本地Embedding模型")
    print("=" * 60)
    
    try:
        # 尝试安装sentence-transformers
        import subprocess
        print("检查sentence-transformers...")
        
        try:
            import sentence_transformers
            print("✅ sentence-transformers已安装")
        except ImportError:
            print("安装sentence-transformers...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "sentence-transformers"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print("✅ sentence-transformers安装成功")
            else:
                print(f"❌ 安装失败: {result.stderr}")
                return False
        
        from mem0 import Memory
        
        print("使用本地模型创建Memory实例...")
        memory = Memory(
            embedding_model="all-MiniLM-L6-v2",
            local_embedding=True
        )
        
        # 添加测试记忆
        memory_id = memory.add(
            text="使用本地Embedding模型存储的记忆",
            metadata={"embedding": "local", "test": True}
        )
        
        # 检索
        results = memory.search("本地记忆", top_k=2)
        print(f"✅ 本地Embedding测试成功，检索到 {len(results)} 条记忆")
        
        return True
    except Exception as e:
        print(f"❌ 本地Embedding测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("mem0功能测试开始")
    print("=" * 60)
    
    # 测试安装状态
    if not test_mem0_installation():
        print("\n❌ mem0未安装，无法继续测试")
        print("\n请先安装mem0:")
        print("1. pip install mem0ai")
        print("2. 或使用国内镜像源")
        return
    
    # 测试基本功能
    if not test_basic_functionality():
        print("\n❌ 基本功能测试失败")
        return
    
    # 测试本地Embedding
    test_local_embedding()
    
    # 测试OpenAI Embedding（可选）
    test_with_openai_embedding()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n下一步建议:")
    print("1. 根据需要配置Embedding模型")
    print("2. 选择合适的向量数据库")
    print("3. 将mem0集成到您的项目中")
    print("4. 测试实际使用场景下的性能")

if __name__ == "__main__":
    main()