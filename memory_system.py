#!/usr/bin/env python3
"""
记忆系统集成模块
整合mem0和ontology，提供统一的记忆管理接口
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

class MemorySystem:
    """记忆系统集成类"""
    
    def __init__(self):
        self.memory_dir = Path("/Users/tuqibiao/.openclaw/workspace/memory")
        self.memory_dir.mkdir(exist_ok=True)
        
        # 检查mem0是否可用
        self.mem0_available = False
        try:
            from mem0 import Memory
            # 尝试初始化mem0，如果失败则使用文件系统
            import os
            if os.environ.get("OPENAI_API_KEY"):
                self.mem0 = Memory()
                self.mem0_available = True
                print("✅ mem0记忆系统已启用（使用OpenAI embeddings）")
            else:
                print("⚠️ OPENAI_API_KEY未设置，mem0使用受限，仅使用文件系统记忆")
                self.mem0_available = False
        except ImportError:
            print("⚠️ mem0未安装，使用文件系统记忆")
        except Exception as e:
            print(f"⚠️ mem0初始化失败: {e}，使用文件系统记忆")
        
        # 初始化ontology（如果需要）
        self.ontology_available = False
        
    def store_conversation(self, user_message, assistant_response, metadata=None):
        """存储对话记忆"""
        timestamp = datetime.now().isoformat()
        
        # 基础记忆数据
        memory_data = {
            "timestamp": timestamp,
            "user": user_message,
            "assistant": assistant_response,
            "metadata": metadata or {}
        }
        
        # 1. 存储到文件系统（基础备份）
        self._store_to_filesystem(memory_data)
        
        # 2. 存储到mem0（如果可用）
        if self.mem0_available:
            self._store_to_mem0(memory_data)
        
        return timestamp
    
    def _store_to_filesystem(self, memory_data):
        """存储到文件系统"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        memory_file = self.memory_dir / f"{date_str}.jsonl"
        
        with open(memory_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(memory_data, ensure_ascii=False) + "\n")
    
    def _store_to_mem0(self, memory_data):
        """存储到mem0"""
        try:
            memory_id = self.mem0.add(
                messages=[
                    {"role": "user", "content": memory_data["user"]},
                    {"role": "assistant", "content": memory_data["assistant"]}
                ],
                metadata={
                    "timestamp": memory_data["timestamp"],
                    **memory_data["metadata"]
                }
            )
            return memory_id
        except Exception as e:
            print(f"⚠️ mem0存储失败: {e}")
            return None
    
    def search_memories(self, query, top_k=5):
        """搜索记忆"""
        results = []
        
        # 1. 从mem0搜索（如果可用）
        if self.mem0_available:
            try:
                mem0_results = self.mem0.search(query, top_k=top_k)
                for result in mem0_results:
                    results.append({
                        "source": "mem0",
                        "content": result.get("messages", [{}])[0].get("content", ""),
                        "metadata": result.get("metadata", {}),
                        "score": result.get("score", 0)
                    })
            except Exception as e:
                print(f"⚠️ mem0搜索失败: {e}")
        
        # 2. 从文件系统搜索（如果mem0结果不足）
        if len(results) < top_k:
            file_results = self._search_filesystem(query, top_k - len(results))
            results.extend(file_results)
        
        return results[:top_k]
    
    def _search_filesystem(self, query, limit=5):
        """从文件系统搜索"""
        results = []
        query_lower = query.lower()
        
        # 搜索最近7天的记忆文件
        for i in range(7):
            date = datetime.now().date() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            memory_file = self.memory_dir / f"{date_str}.jsonl"
            
            if memory_file.exists():
                try:
                    with open(memory_file, "r", encoding="utf-8") as f:
                        for line in f:
                            memory_data = json.loads(line.strip())
                            content = f"{memory_data.get('user', '')} {memory_data.get('assistant', '')}"
                            
                            # 简单关键词匹配
                            if query_lower in content.lower():
                                results.append({
                                    "source": "filesystem",
                                    "content": content[:100] + "..." if len(content) > 100 else content,
                                    "metadata": memory_data.get("metadata", {}),
                                    "timestamp": memory_data.get("timestamp", ""),
                                    "score": 0.5  # 基础分数
                                })
                                
                                if len(results) >= limit:
                                    return results
                except Exception as e:
                    print(f"⚠️ 读取记忆文件失败 {memory_file}: {e}")
        
        return results
    
    def get_recent_memories(self, days=3, limit=10):
        """获取近期记忆"""
        memories = []
        
        for i in range(days):
            date = datetime.now().date() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            memory_file = self.memory_dir / f"{date_str}.jsonl"
            
            if memory_file.exists():
                try:
                    with open(memory_file, "r", encoding="utf-8") as f:
                        lines = list(f)
                        # 取最近的一些记录
                        for line in lines[-5:]:  # 每天最多取5条
                            memory_data = json.loads(line.strip())
                            memories.append({
                                "date": date_str,
                                "user": memory_data.get("user", "")[:50],
                                "assistant": memory_data.get("assistant", "")[:50],
                                "timestamp": memory_data.get("timestamp", "")
                            })
                except Exception as e:
                    print(f"⚠️ 读取记忆文件失败 {memory_file}: {e}")
        
        return memories[:limit]

# 全局记忆系统实例
memory_system = MemorySystem()

def remember(conversation_text, category="general", importance=0.5):
    """记忆重要对话"""
    return memory_system.store_conversation(
        user_message=conversation_text,
        assistant_response="已记忆",
        metadata={
            "category": category,
            "importance": importance,
            "action": "memory_store"
        }
    )

def recall(query, limit=5):
    """回忆相关对话"""
    return memory_system.search_memories(query, top_k=limit)

def get_recent_conversations(days=3):
    """获取近期对话"""
    return memory_system.get_recent_memories(days=days)

if __name__ == "__main__":
    # 测试记忆系统
    print("🧠 记忆系统测试...")
    
    # 创建一些测试记忆
    test_id = remember("用户是证券公司投资顾问，主要关注A股市场", "user_profile", 0.8)
    print(f"测试记忆存储: {test_id}")
    
    # 搜索记忆
    results = recall("投资顾问", 3)
    print(f"搜索到 {len(results)} 条相关记忆")
    
    # 获取近期对话
    recent = get_recent_conversations(2)
    print(f"近期 {len(recent)} 条对话记录")
