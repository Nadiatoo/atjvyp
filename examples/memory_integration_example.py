#!/usr/bin/env python3
"""
记忆系统集成示例
展示如何在日常工作中使用记忆系统
"""

import sys
sys.path.append("/Users/tuqibiao/.openclaw/workspace")

from enhanced_memory_system import remember, recall, get_recent

class MemoryEnhancedAssistant:
    """记忆增强型助手"""
    
    def __init__(self):
        print("🧠 记忆增强型助手已初始化")
    
    def handle_conversation(self, user_message: str) -> str:
        """处理对话，使用记忆系统增强"""
        
        print(f"\n👤 用户: {user_message}")
        
        # 1. 首先检索相关记忆
        related_memories = self._search_related_memories(user_message)
        
        # 2. 根据记忆生成响应
        response = self._generate_response(user_message, related_memories)
        
        # 3. 存储这次对话到记忆系统
        self._store_conversation(user_message, response)
        
        return response
    
    def _search_related_memories(self, query: str, limit: int = 3) -> list:
        """搜索相关记忆"""
        print(f"🔍 正在搜索相关记忆: \"{query}\"")
        
        # 尝试不同搜索策略
        search_results = []
        
        # 策略1: 直接关键词搜索
        results = recall(query, limit=limit)
        search_results.extend(results)
        
        # 策略2: 如果没有结果，尝试提取关键词搜索
        if len(search_results) < limit:
            # 简单关键词提取
            keywords = self._extract_keywords(query)
            for keyword in keywords[:3]:  # 尝试前3个关键词
                if len(search_results) >= limit:
                    break
                keyword_results = recall(keyword, limit=1)
                search_results.extend(keyword_results)
        
        # 去重
        unique_results = []
        seen_ids = set()
        for result in search_results:
            if result.get('id') not in seen_ids:
                seen_ids.add(result.get('id'))
                unique_results.append(result)
        
        print(f"   找到 {len(unique_results)} 条相关记忆")
        return unique_results[:limit]
    
    def _extract_keywords(self, text: str) -> list:
        """简单关键词提取"""
        # 移除常见停用词
        stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都"}
        words = text.split()
        keywords = [word for word in words if word not in stop_words and len(word) > 1]
        return keywords
    
    def _generate_response(self, user_message: str, related_memories: list) -> str:
        """基于记忆生成响应"""
        
        # 分析用户意图
        if "记忆" in user_message or "记住" in user_message or "忘记" in user_message:
            return self._handle_memory_related_query(user_message, related_memories)
        elif "今天" in user_message or "最近" in user_message or "讨论" in user_message:
            return self._handle_recent_activity_query(user_message, related_memories)
        elif "系统" in user_message or "配置" in user_message or "设置" in user_message:
            return self._handle_system_query(user_message, related_memories)
        else:
            return self._handle_general_query(user_message, related_memories)
    
    def _handle_memory_related_query(self, user_message: str, related_memories: list) -> str:
        """处理与记忆相关的查询"""
        if "试用" in user_message or "测试" in user_message:
            return "🧠 记忆系统试用正在进行中！我已经记录了这次对话，并且可以检索之前的讨论。系统运行正常，无需外部API Key。"
        
        elif "效果" in user_message or "如何" in user_message:
            # 基于记忆系统统计生成响应
            recent = get_recent(days=1)
            important_count = len([m for m in recent if m.get('importance', 0) >= 0.7])
            
            return f"📊 记忆系统效果：今天已存储 {len(recent)} 条记忆，其中 {important_count} 条是高重要性记忆。系统支持关键词搜索和类别过滤。"
        
        else:
            return "🧠 我正在使用增强型记忆系统，所有对话都会根据重要性分级存储。需要我记住什么特别的信息吗？"
    
    def _handle_recent_activity_query(self, user_message: str, related_memories: list) -> str:
        """处理近期活动查询"""
        # 获取今天的记忆
        today_memories = get_recent(days=1)
        
        if not today_memories:
            return "📅 今天还没有记录重要对话。"
        
        # 按类别统计
        categories = {}
        for memory in today_memories:
            category = memory.get('category', '其他')
            categories[category] = categories.get(category, 0) + 1
        
        # 生成总结
        summary = f"📅 今天共有 {len(today_memories)} 条记忆记录：\n"
        for category, count in categories.items():
            summary += f"  • {category}: {count}条\n"
        
        # 添加具体内容（如果有高重要性记忆）
        important = [m for m in today_memories if m.get('importance', 0) >= 0.8]
        if important:
            summary += "\n🎯 高重要性记忆：\n"
            for i, memory in enumerate(important[:2]):  # 只显示前2条
                content = memory.get('content', '')[:60]
                summary += f"  {i+1}. {content}...\n"
        
        return summary
    
    def _handle_system_query(self, user_message: str, related_memories: list) -> str:
        """处理系统相关查询"""
        # 检查是否有相关系统配置记忆
        system_memories = [m for m in related_memories if m.get('category') in ['system_config', 'system_decision']]
        
        if system_memories:
            response = "🔧 系统相关记录：\n"
            for i, memory in enumerate(system_memories[:2]):
                content = memory.get('content', '')[:70]
                response += f"  {i+1}. {content}...\n"
            return response
        else:
            return "🔧 系统运行正常。需要了解具体的系统配置或状态吗？"
    
    def _handle_general_query(self, user_message: str, related_memories: list) -> str:
        """处理一般查询"""
        if related_memories:
            # 基于相关记忆生成响应
            response = "💭 根据相关记忆：\n"
            for i, memory in enumerate(related_memories[:2]):
                content = memory.get('content', '')[:80]
                response += f"  {i+1}. {content}...\n"
            response += "\n这是基于我们之前讨论的相关信息。"
            return response
        else:
            return "🤔 这是一个新的讨论话题。我会记住这次对话，便于后续参考。"
    
    def _store_conversation(self, user_message: str, assistant_response: str):
        """存储对话到记忆系统"""
        # 根据内容判断重要性
        importance = 0.5  # 默认重要性
        
        # 提高特定类型对话的重要性
        if any(keyword in user_message for keyword in ["重要", "记住", "系统", "配置", "决策"]):
            importance = 0.8
        elif any(keyword in user_message for keyword in ["记忆", "试用", "测试", "效果"]):
            importance = 0.7
        
        # 确定类别
        category = "conversation"
        if "系统" in user_message:
            category = "system_config"
        elif "记忆" in user_message:
            category = "system_test"
        
        # 存储记忆
        memory_id = remember(
            f"用户: {user_message}\n助手: {assistant_response}",
            category=category,
            importance=importance,
            conversation_type="q_a",
            timestamp=self._get_current_time()
        )
        
        print(f"💾 对话已存储到记忆系统 (ID: {memory_id}, 重要性: {importance})")
    
    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """主函数：演示记忆增强型助手"""
    print("=" * 60)
    print("🧠 记忆增强型助手演示")
    print("=" * 60)
    
    assistant = MemoryEnhancedAssistant()
    
    # 演示对话
    demo_conversations = [
        "我们开始试用记忆系统吧",
        "记忆系统效果怎么样？",
        "我们今天讨论了什么？",
        "系统配置有什么更新吗？",
        "记住我是投资顾问，关注A股市场",
        "彪哥战法系统状态如何？"
    ]
    
    for user_message in demo_conversations:
        print("\n" + "-" * 60)
        response = assistant.handle_conversation(user_message)
        print(f"\n🤖 助手: {response}")
    
    print("\n" + "=" * 60)
    print("✅ 记忆增强型助手演示完成")
    print("\n💡 特点总结:")
    print("1. 自动记忆检索：每次对话前搜索相关记忆")
    print("2. 智能响应生成：基于记忆内容生成响应")
    print("3. 自动记忆存储：根据重要性分级存储对话")
    print("4. 无需外部API：完全本地运行，零成本")
    print("5. 持续学习改进：对话越多，记忆越丰富")

if __name__ == "__main__":
    main()