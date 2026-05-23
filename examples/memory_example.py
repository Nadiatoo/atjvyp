#!/usr/bin/env python3
"""
记忆系统使用示例
"""

import sys
sys.path.append("/Users/tuqibiao/.openclaw/workspace")

try:
    from memory_system import remember, recall, get_recent_conversations
    
    def main():
        print("🧠 记忆系统使用示例")
        print("=" * 50)
        
        # 示例1: 记忆重要信息
        print("1. 记忆重要信息:")
        try:
            memory_id = remember(
                "彪哥战法v5.0系统已完成数据源升级，使用QVeris替代AkShare",
                category="project_update",
                importance=0.9
            )
            print(f"   记忆ID: {memory_id}")
        except Exception as e:
            print(f"   记忆存储失败: {e}")
        
        # 示例2: 搜索记忆
        print("\n2. 搜索相关记忆:")
        try:
            results = recall("彪哥战法", limit=3)
            if results:
                for i, result in enumerate(results):
                    source = result.get('source', 'unknown')
                    content = result.get('content', '')[:60]
                    print(f"   结果{i+1} [{source}]: {content}...")
            else:
                print("   未找到相关记忆")
        except Exception as e:
            print(f"   记忆搜索失败: {e}")
        
        # 示例3: 查看近期对话
        print("\n3. 近期对话记录:")
        try:
            recent = get_recent_conversations(days=2)
            if recent:
                for i, conv in enumerate(recent):
                    date = conv.get('date', 'unknown')
                    user = conv.get('user', '')[:30]
                    assistant = conv.get('assistant', '')[:30]
                    print(f"   {date}: {user} → {assistant}")
            else:
                print("   暂无近期对话记录")
        except Exception as e:
            print(f"   获取近期对话失败: {e}")
        
        print("\n✅ 记忆系统测试完成！")
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ 无法导入记忆系统: {e}")
    print("请确保memory_system.py文件存在")
except Exception as e:
    print(f"❌ 记忆系统测试失败: {e}")
