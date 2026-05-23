#!/usr/bin/env python3
"""
增强型记忆系统 - 无需API Key的完整解决方案
替代原来的memory_system.py
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

class EnhancedMemorySystem:
    """增强型记忆系统 - 无需外部API Key"""
    
    def __init__(self):
        self.memory_dir = Path("/Users/tuqibiao/.openclaw/workspace/memory")
        self.memory_dir.mkdir(exist_ok=True)
        
        # 创建索引目录
        self.index_dir = self.memory_dir / "index"
        self.index_dir.mkdir(exist_ok=True)
        
        # 关键词索引
        self.keyword_index = self._load_keyword_index()
        
        print("🧠 增强型记忆系统已就绪（无需API Key）")
    
    def _load_keyword_index(self) -> Dict[str, List[str]]:
        """加载关键词索引"""
        index_file = self.index_dir / "keywords.json"
        if index_file.exists():
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_keyword_index(self):
        """保存关键词索引"""
        index_file = self.index_dir / "keywords.json"
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(self.keyword_index, f, ensure_ascii=False, indent=2)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 移除标点符号，转换为小写
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text_clean.split()
        
        # 过滤停用词和短词
        stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"}
        keywords = []
        
        for word in words:
            if len(word) >= 2 and word not in stop_words:
                keywords.append(word)
        
        # 返回前10个关键词
        return keywords[:10]
    
    def store_memory(self, content: str, category: str = "general", 
                    importance: float = 0.5, metadata: Optional[Dict] = None) -> str:
        """存储记忆"""
        timestamp = datetime.now().isoformat()
        memory_id = f"mem_{int(datetime.now().timestamp())}"
        
        # 记忆数据
        memory_data = {
            "id": memory_id,
            "timestamp": timestamp,
            "content": content,
            "category": category,
            "importance": importance,
            "metadata": metadata or {}
        }
        
        # 1. 存储到日期文件
        date_str = datetime.now().strftime("%Y-%m-%d")
        memory_file = self.memory_dir / f"{date_str}.jsonl"
        
        with open(memory_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(memory_data, ensure_ascii=False) + "\n")
        
        # 2. 更新关键词索引
        keywords = self._extract_keywords(content)
        for keyword in keywords:
            if keyword not in self.keyword_index:
                self.keyword_index[keyword] = []
            if memory_id not in self.keyword_index[keyword]:
                self.keyword_index[keyword].append(memory_id)
        
        # 3. 按类别索引
        category_key = f"category_{category}"
        if category_key not in self.keyword_index:
            self.keyword_index[category_key] = []
        if memory_id not in self.keyword_index[category_key]:
            self.keyword_index[category_key].append(memory_id)
        
        # 4. 按重要性索引（高重要性记忆）
        if importance >= 0.8:
            if "high_importance" not in self.keyword_index:
                self.keyword_index["high_importance"] = []
            if memory_id not in self.keyword_index["high_importance"]:
                self.keyword_index["high_importance"].append(memory_id)
        
        # 保存索引
        self._save_keyword_index()
        
        # 5. 同时存储到结构化记忆文件（便于人类阅读）
        self._store_to_structured_memory(memory_data)
        
        return memory_id
    
    def _store_to_structured_memory(self, memory_data: Dict):
        """存储到结构化记忆文件（Markdown格式）"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        structured_file = self.memory_dir / f"{date_str}_structured.md"
        
        # 如果文件不存在，创建标题
        if not structured_file.exists():
            with open(structured_file, "w", encoding="utf-8") as f:
                f.write(f"# {date_str} 记忆记录\n\n")
        
        # 追加记忆
        with open(structured_file, "a", encoding="utf-8") as f:
            f.write(f"\n## 🧠 记忆 {memory_data['id']}\n")
            f.write(f"**时间**: {memory_data['timestamp']}\n")
            f.write(f"**类别**: {memory_data['category']}\n")
            f.write(f"**重要性**: {memory_data['importance']}\n")
            f.write(f"\n**内容**:\n{memory_data['content']}\n")
            
            if memory_data['metadata']:
                f.write(f"\n**元数据**:\n")
                for key, value in memory_data['metadata'].items():
                    f.write(f"- {key}: {value}\n")
            
            f.write("\n---\n")
    
    def search_memories(self, query: str, category: Optional[str] = None, 
                       min_importance: float = 0.0, limit: int = 10) -> List[Dict]:
        """搜索记忆"""
        results = []
        
        # 方法1: 关键词索引搜索（快速）
        keyword_results = self._search_by_keywords(query, category, min_importance, limit)
        results.extend(keyword_results)
        
        # 方法2: 全文搜索（如果关键词搜索结果不足）
        if len(results) < limit:
            full_text_results = self._search_full_text(query, category, min_importance, limit - len(results))
            results.extend(full_text_results)
        
        # 去重并按相关性排序
        unique_results = []
        seen_ids = set()
        
        for result in results:
            if result["id"] not in seen_ids:
                seen_ids.add(result["id"])
                unique_results.append(result)
        
        # 按重要性排序
        unique_results.sort(key=lambda x: x.get("importance", 0), reverse=True)
        
        return unique_results[:limit]
    
    def _search_by_keywords(self, query: str, category: Optional[str], 
                           min_importance: float, limit: int) -> List[Dict]:
        """通过关键词索引搜索"""
        results = []
        query_keywords = self._extract_keywords(query)
        
        # 收集相关记忆ID
        related_ids = set()
        
        for keyword in query_keywords:
            if keyword in self.keyword_index:
                related_ids.update(self.keyword_index[keyword])
        
        # 按类别过滤
        if category:
            category_key = f"category_{category}"
            if category_key in self.keyword_index:
                category_ids = set(self.keyword_index[category_key])
                related_ids = related_ids.intersection(category_ids)
        
        # 获取记忆内容
        for memory_id in list(related_ids)[:limit*2]:  # 多取一些用于重要性过滤
            memory = self._get_memory_by_id(memory_id)
            if memory and memory.get("importance", 0) >= min_importance:
                # 计算简单相关性分数
                relevance = self._calculate_relevance(memory["content"], query_keywords)
                memory["relevance"] = relevance
                results.append(memory)
        
        return results
    
    def _search_full_text(self, query: str, category: Optional[str], 
                         min_importance: float, limit: int) -> List[Dict]:
        """全文搜索"""
        results = []
        query_lower = query.lower()
        query_keywords = self._extract_keywords(query)
        
        # 搜索最近30天的记忆文件
        for i in range(30):
            date = datetime.now().date() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            memory_file = self.memory_dir / f"{date_str}.jsonl"
            
            if not memory_file.exists():
                continue
            
            try:
                with open(memory_file, "r", encoding="utf-8") as f:
                    for line in f:
                        memory_data = json.loads(line.strip())
                        
                        # 过滤条件
                        if category and memory_data.get("category") != category:
                            continue
                        
                        if memory_data.get("importance", 0) < min_importance:
                            continue
                        
                        # 全文匹配
                        content = memory_data.get("content", "").lower()
                        if query_lower in content:
                            relevance = self._calculate_relevance(content, query_keywords)
                            memory_data["relevance"] = relevance
                            results.append(memory_data)
                            
                            if len(results) >= limit:
                                return results
            except Exception as e:
                print(f"⚠️ 读取记忆文件失败 {memory_file}: {e}")
        
        return results
    
    def _get_memory_by_id(self, memory_id: str) -> Optional[Dict]:
        """根据ID获取记忆"""
        # 从最近30天的文件中查找
        for i in range(30):
            date = datetime.now().date() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            memory_file = self.memory_dir / f"{date_str}.jsonl"
            
            if not memory_file.exists():
                continue
            
            try:
                with open(memory_file, "r", encoding="utf-8") as f:
                    for line in f:
                        memory_data = json.loads(line.strip())
                        if memory_data.get("id") == memory_id:
                            return memory_data
            except:
                continue
        
        return None
    
    def _calculate_relevance(self, content: str, query_keywords: List[str]) -> float:
        """计算相关性分数"""
        if not query_keywords:
            return 0.0
        
        content_lower = content.lower()
        matches = 0
        
        for keyword in query_keywords:
            if keyword in content_lower:
                matches += 1
        
        return matches / len(query_keywords)
    
    def get_recent_memories(self, days: int = 7, category: Optional[str] = None, 
                           min_importance: float = 0.0) -> List[Dict]:
        """获取近期记忆"""
        memories = []
        
        for i in range(days):
            date = datetime.now().date() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            memory_file = self.memory_dir / f"{date_str}.jsonl"
            
            if not memory_file.exists():
                continue
            
            try:
                with open(memory_file, "r", encoding="utf-8") as f:
                    for line in f:
                        memory_data = json.loads(line.strip())
                        
                        # 过滤条件
                        if category and memory_data.get("category") != category:
                            continue
                        
                        if memory_data.get("importance", 0) < min_importance:
                            continue
                        
                        memories.append(memory_data)
            except Exception as e:
                print(f"⚠️ 读取记忆文件失败 {memory_file}: {e}")
        
        # 按时间倒序排序
        memories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return memories
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        stats = {
            "total_memories": 0,
            "by_category": {},
            "by_day": {},
            "high_importance_count": 0
        }
        
        # 统计最近90天
        for i in range(90):
            date = datetime.now().date() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            memory_file = self.memory_dir / f"{date_str}.jsonl"
            
            if not memory_file.exists():
                continue
            
            try:
                with open(memory_file, "r", encoding="utf-8") as f:
                    day_count = 0
                    for line in f:
                        memory_data = json.loads(line.strip())
                        stats["total_memories"] += 1
                        day_count += 1
                        
                        # 按类别统计
                        category = memory_data.get("category", "unknown")
                        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
                        
                        # 高重要性统计
                        if memory_data.get("importance", 0) >= 0.8:
                            stats["high_importance_count"] += 1
                    
                    stats["by_day"][date_str] = day_count
            except:
                continue
        
        return stats
    
    def cleanup_old_memories(self, days_to_keep: int = 90):
        """清理旧记忆（保留结构化文件）"""
        print(f"🧹 清理 {days_to_keep} 天前的记忆...")
        
        for i in range(days_to_keep, 365):  # 清理90-365天前的
            date = datetime.now().date() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            memory_file = self.memory_dir / f"{date_str}.jsonl"
            
            if memory_file.exists():
                try:
                    # 只删除JSONL文件，保留结构化文件
                    memory_file.unlink()
                    print(f"  已删除: {memory_file.name}")
                except Exception as e:
                    print(f"  删除失败 {memory_file}: {e}")

# 全局实例
memory_system = EnhancedMemorySystem()

def remember(content: str, category: str = "general", importance: float = 0.5, **kwargs) -> str:
    """记忆重要信息"""
    return memory_system.store_memory(content, category, importance, kwargs)

def recall(query: str, category: Optional[str] = None, min_importance: float = 0.0, limit: int = 10) -> List[Dict]:
    """回忆相关信息"""
    return memory_system.search_memories(query, category, min_importance, limit)

def get_recent(days: int = 7, category: Optional[str] = None, min_importance: float = 0.0) -> List[Dict]:
    """获取近期记忆"""
    return memory_system.get_recent_memories(days, category, min_importance)

def get_stats() -> Dict[str, Any]:
    """获取记忆统计"""
    return memory_system.get_memory_stats()

def cleanup(days_to_keep: int = 90):
    """清理旧记忆"""
    memory_system.cleanup_old_memories(days_to_keep)

# 兼容旧版API
def store_conversation(user_message: str, assistant_response: str, metadata: Optional[Dict] = None) -> str:
    """存储对话记忆（兼容旧版）"""
    content = f"用户: {user_message}\n助手: {assistant_response}"
    category = metadata.get("category", "conversation") if metadata else "conversation"
    importance = metadata.get("importance", 0.5) if metadata else 0.5
    return remember(content, category, importance, **(metadata or {}))

def search_memories(query: str, top_k: int = 5) -> List[Dict]:
    """搜索记忆（兼容旧版）"""
    results = recall(query, limit=top_k)
    # 转换为旧版格式
    formatted_results = []
    for result in results:
        formatted_results.append({
            "source": "enhanced_memory",
            "content": result.get("content", ""),
            "metadata": result.get("metadata", {}),
            "score": result.get("relevance", 0.0)
        })
    return formatted_results

def get_recent_conversations(days: int = 3) -> List[Dict]:
    """获取近期对话（兼容旧版）"""
    memories = get_recent(days=days)
    formatted = []
    for memory in memories:
        content = memory.get("content", "")
        # 尝试解析用户和助手消息
        if "用户:" in content and "助手:" in content:
            parts = content.split("助手:")
            if len(parts) >= 2:
                user_part = parts[0].replace("用户:", "").strip()
                assistant_part = parts[1].strip()
                formatted.append({
                    "date": memory.get("timestamp", "").split("T")[0],
                    "user": user_part[:50],
                    "assistant": assistant_part[:50],
                    "timestamp": memory.get("timestamp", "")
                })
    return formatted

if __name__ == "__main__":
    print("🧠 增强型记忆系统")
    print("=" * 50)
    
    # 显示当前状态
    stats = get_stats()
    print(f"📊 当前记忆统计:")
    print(f"   总记忆数: {stats['total_memories']}")
    print(f"   高重要性记忆: {stats['high_importance_count']}")
    print(f"   类别分布: {json.dumps(stats['by_category'], ensure_ascii=False, indent=2)}")
    
    print("\n🔧 可用函数:")
    print("   1. remember(content, category, importance, **metadata)")
    print("   2. recall(query, category, min_importance, limit)")
    print("   3. get_recent(days, category, min_importance)")
    print("   4. get_stats()")
    print("   5. cleanup(days_to_keep)")
    
    print("\n💡 提示: 所有功能都无需外部API Key，完全免费！")