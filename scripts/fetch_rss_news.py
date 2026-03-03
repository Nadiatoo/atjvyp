#!/usr/bin/env python3
"""
盘前 RSS 新闻获取工具
用于获取宏观政策和财经新闻
"""

import feedparser
import ssl
import yaml
import re
from datetime import datetime, timedelta
from pathlib import Path

# 禁用SSL验证
ssl._create_default_https_context = ssl._create_unverified_context

CONFIG_PATH = Path("/Users/tuqibiao/.openclaw/workspace/config/rss_sources.yaml")


def load_config():
    """加载配置"""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def fetch_rss(url, name, max_items=10):
    """获取RSS内容"""
    try:
        d = feedparser.parse(url)
        entries = []
        for entry in d.entries[:max_items]:
            entries.append({
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'summary': entry.get('summary', '')[:200],
                'published': entry.get('published', ''),
            })
        return entries
    except Exception as e:
        print(f"❌ 获取 {name} 失败: {e}")
        return []


def filter_by_keywords(entries, keywords):
    """根据关键词过滤新闻"""
    filtered = []
    keyword_list = []
    for category in keywords.values():
        keyword_list.extend(category)
    
    for entry in entries:
        text = f"{entry['title']} {entry['summary']}"
        matched = [kw for kw in keyword_list if kw in text]
        if matched:
            entry['matched_keywords'] = matched
            filtered.append(entry)
    
    return filtered


def analyze_themes(entries):
    """分析热门题材"""
    themes = {}
    for entry in entries:
        for kw in entry.get('matched_keywords', []):
            if kw not in themes:
                themes[kw] = []
            themes[kw].append(entry)
    
    # 按出现次数排序
    sorted_themes = sorted(themes.items(), key=lambda x: len(x[1]), reverse=True)
    return sorted_themes[:5]  # Top 5 热门题材


def format_output(entries, themes, config):
    """格式化输出"""
    output = []
    output.append("📰 盘前 RSS 新闻摘要")
    output.append("=" * 50)
    
    # 热门题材
    if themes:
        output.append("\n🔥 热门题材 TOP5:")
        for i, (theme, items) in enumerate(themes, 1):
            output.append(f"{i}. {theme} ({len(items)}条相关)")
    
    # 重要新闻
    output.append("\n📌 重要新闻:")
    important_keywords = config['keywords']['macro']
    important_news = [e for e in entries if any(kw in e['title'] for kw in important_keywords)]
    
    if important_news:
        for i, entry in enumerate(important_news[:5], 1):
            output.append(f"\n{i}. {entry['title']}")
            if entry.get('matched_keywords'):
                output.append(f"   关键词: {', '.join(entry['matched_keywords'][:3])}")
    else:
        output.append("暂无宏观政策相关新闻")
    
    # 全部新闻
    output.append("\n📋 全部财经新闻:")
    for i, entry in enumerate(entries[:10], 1):
        output.append(f"{i}. {entry['title']}")
    
    return "\n".join(output)


def main():
    """主函数"""
    print("🔄 正在获取 RSS 新闻...\n")
    
    config = load_config()
    all_entries = []
    
    # 获取各源新闻
    for source in config['sources']:
        name = source['name']
        url = source['url']
        print(f"📡 获取 {name}...", end=" ")
        
        entries = fetch_rss(url, name, config['output']['max_items_per_source'])
        if entries:
            print(f"✅ {len(entries)}条")
            for e in entries:
                e['source'] = name
            all_entries.extend(entries)
        else:
            print("⚠️ 无数据")
    
    if not all_entries:
        print("\n❌ 未获取到任何新闻")
        return
    
    # 关键词过滤
    if config['output']['filter_by_keywords']:
        filtered = filter_by_keywords(all_entries, config['keywords'])
    else:
        filtered = all_entries
    
    # 分析热门题材
    themes = analyze_themes(filtered)
    
    # 输出结果
    output = format_output(filtered, themes, config)
    print("\n" + output)
    
    # 保存到文件
    output_file = Path("/tmp/rss_news_" + datetime.now().strftime("%Y%m%d") + ".txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)
    print(f"\n💾 已保存到: {output_file}")


if __name__ == "__main__":
    main()
