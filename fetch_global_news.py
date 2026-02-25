#!/usr/bin/env python3
"""
全球财经新闻获取脚本
用于彪哥战法盘前分析
"""

import feedparser
import json
from datetime import datetime, timedelta

# 主流财经媒体 RSS 源
RSS_FEEDS = {
    "华尔街日报": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    "彭博社": "https://www.bloomberg.com/feeds/markets/sitemap_news.xml",
    "路透": "https://www.reutersagency.com/feed/?taxonomy=markets&post_type=reuters-best",
    "财新": "http://feeds.caixin.com/caixinfinance",
    "华尔街见闻": "https://wallstreetcn.com/rss.xml",
    "东方财富": "https://finance.eastmoney.com/rss/news.xml",
}

def fetch_news(hours=12):
    """获取最近 N 小时的新闻"""
    results = []
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:  # 每个源取前10条
                # 解析时间
                pub_time = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_time = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_time = datetime(*entry.updated_parsed[:6])
                
                # 只保留最近的新闻
                if pub_time and pub_time > cutoff_time:
                    results.append({
                        "source": source,
                        "title": entry.title,
                        "link": entry.link,
                        "published": pub_time.strftime("%Y-%m-%d %H:%M"),
                        "summary": entry.get('summary', '')[:200]
                    })
        except Exception as e:
            print(f"获取 {source} 失败: {e}")
    
    # 按时间排序
    results.sort(key=lambda x: x['published'], reverse=True)
    return results

def analyze_impact(news_list):
    """简单分析新闻对A股的影响"""
    impact = {
        "positive": [],
        "negative": [],
        "neutral": []
    }
    
    positive_keywords = ["降息", "利好", "增长", "上涨", "突破", "合作", "复苏"]
    negative_keywords = ["加息", "制裁", "下跌", "衰退", "冲突", "风险", "危机"]
    
    for news in news_list[:20]:  # 分析前20条
        title = news['title']
        if any(kw in title for kw in positive_keywords):
            impact["positive"].append(news)
        elif any(kw in title for kw in negative_keywords):
            impact["negative"].append(news)
        else:
            impact["neutral"].append(news)
    
    return impact

if __name__ == "__main__":
    print("正在获取全球财经新闻...")
    news = fetch_news(hours=12)
    print(f"获取到 {len(news)} 条新闻")
    
    print("\n=== 最新10条新闻 ===")
    for i, n in enumerate(news[:10], 1):
        print(f"{i}. [{n['source']}] {n['title']}")
        print(f"   时间: {n['published']}")
        print()
    
    # 保存结果
    with open("/Users/tuqibiao/.openclaw/workspace/daily_news.json", "w", encoding="utf-8") as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    
    print("新闻已保存到 daily_news.json")
