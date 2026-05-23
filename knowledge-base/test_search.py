#!/usr/bin/env python3
"""
知识库搜索测试
"""

import os
import sys
from pathlib import Path

def search_in_knowledge_base(query: str):
    """在知识库中搜索相关内容"""
    print(f"🔍 搜索: '{query}'")
    print("="*60)
    
    kb_dir = "raw/domains"
    results = []
    
    # 遍历所有Markdown文件
    for md_file in Path(kb_dir).glob("**/*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 简单关键词匹配
            if query.lower() in content.lower():
                # 提取标题
                lines = content.split('\n')
                title = "未知"
                for line in lines:
                    if line.startswith('title:'):
                        title = line.replace('title:', '').strip()
                        break
                
                # 提取相关片段
                content_lower = content.lower()
                query_lower = query.lower()
                pos = content_lower.find(query_lower)
                
                if pos != -1:
                    start = max(0, pos - 100)
                    end = min(len(content), pos + len(query) + 100)
                    snippet = content[start:end].replace('\n', ' ')
                    
                    results.append({
                        'file': str(md_file),
                        'title': title,
                        'snippet': '...' + snippet + '...',
                        'relevance': content_lower.count(query_lower)
                    })
        
        except Exception as e:
            print(f"⚠️ 读取文件失败 {md_file}: {e}")
    
    # 按相关性排序
    results.sort(key=lambda x: x['relevance'], reverse=True)
    
    # 显示结果
    if results:
        print(f"📊 找到 {len(results)} 个相关结果:")
        print("")
        
        for i, result in enumerate(results[:5], 1):  # 显示前5个结果
            print(f"{i}. {result['title']}")
            print(f"   文件: {result['file']}")
            print(f"   相关度: {result['relevance']}")
            print(f"   片段: {result['snippet'][:150]}...")
            print("")
    else:
        print("❌ 未找到相关结果")
    
    return results

def show_knowledge_base_stats():
    """显示知识库统计信息"""
    print("📊 知识库统计信息")
    print("="*60)
    
    kb_dir = "raw/domains"
    
    stats = {
        'total_files': 0,
        'by_domain': {},
        'by_category': {}
    }
    
    for md_file in Path(kb_dir).glob("**/*.md"):
        stats['total_files'] += 1
        
        # 提取路径信息
        parts = md_file.relative_to(kb_dir).parts
        if len(parts) >= 2:
            domain = parts[0]
            category = parts[1]
            
            stats['by_domain'][domain] = stats['by_domain'].get(domain, 0) + 1
            stats['by_category'][f"{domain}/{category}"] = stats['by_category'].get(f"{domain}/{category}", 0) + 1
    
    print(f"📁 总文件数: {stats['total_files']}")
    print("")
    
    print("📈 按领域分布:")
    for domain, count in sorted(stats['by_domain'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {domain}: {count}个文件")
    
    print("")
    print("📈 按分类分布:")
    for category, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {category}: {count}个文件")
    
    return stats

def main():
    """主函数"""
    print("🧠 彪哥战法知识库 - 搜索测试")
    print("="*60)
    
    # 显示统计信息
    stats = show_knowledge_base_stats()
    
    print("\n" + "="*60)
    print("🔍 测试搜索功能")
    print("="*60)
    
    # 测试搜索
    test_queries = [
        "市场分析",
        "概率思维", 
        "复盘",
        "风险控制",
        "彪哥战法"
    ]
    
    for query in test_queries:
        search_in_knowledge_base(query)
        print("-"*60)
    
    print("\n✅ 知识库搜索测试完成")
    print(f"💡 提示: 您的知识库已包含 {stats['total_files']} 个文件")
    print("   包括: 复盘PDF解析结果 + 分析框架文档")

if __name__ == "__main__":
    main()