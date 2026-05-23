#!/usr/bin/env python3
"""
迁移.learnings/目录内容到知识库
"""

import os
import re
from datetime import datetime
from pathlib import Path

# 路径配置
WORKSPACE_DIR = Path("/Users/tuqibiao/.openclaw/workspace")
LEARNINGS_DIR = WORKSPACE_DIR / ".learnings"
KNOWLEDGE_BASE_DIR = WORKSPACE_DIR / "knowledge-base"

def read_learning_file(file_path):
    """读取学习文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件失败 {file_path}: {e}")
        return None

def parse_learning_entry(content):
    """解析学习条目"""
    entries = []
    
    # 查找所有学习条目（以###开头）
    pattern = r'### (.*?)\n(.*?)(?=\n###|\n---|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for title, body in matches:
        entry = {
            'title': title.strip(),
            'body': body.strip(),
            'date': extract_date(title),
            'category': extract_category(body),
            'keywords': extract_keywords(body)
        }
        entries.append(entry)
    
    return entries

def extract_date(title):
    """从标题提取日期"""
    # 匹配YYYY-MM-DD格式
    date_pattern = r'(\d{4}-\d{2}-\d{2})'
    match = re.search(date_pattern, title)
    if match:
        return match.group(1)
    return datetime.now().strftime("%Y-%m-%d")

def extract_category(body):
    """从内容提取类别"""
    # 查找**类别**: 行
    category_pattern = r'\*\*类别\*\*:\s*([^\n]+)'
    match = re.search(category_pattern, body)
    if match:
        return match.group(1).strip()
    return "未分类"

def extract_keywords(body):
    """从内容提取关键词"""
    keywords = []
    
    # 常见关键词
    common_keywords = [
        '彪哥战法', '四季战法', '庄稼人战法', '风险控制',
        '市场分析', '技术分析', '基本面分析', '资金面分析',
        'OpenClaw', 'Python', 'API', '数据源', '自动化',
        '错误处理', '性能优化', '技能安装', '配置管理'
    ]
    
    for keyword in common_keywords:
        if keyword in body:
            keywords.append(keyword)
    
    return keywords

def determine_domain(keywords, category):
    """确定知识所属领域"""
    trading_keywords = ['彪哥战法', '四季战法', '庄稼人战法', '风险控制', 
                       '市场分析', '技术分析', '基本面分析', '资金面分析']
    technical_keywords = ['OpenClaw', 'Python', 'API', '数据源', '自动化',
                         '错误处理', '性能优化', '技能安装', '配置管理']
    
    for keyword in keywords:
        if keyword in trading_keywords:
            return "trading"
        elif keyword in technical_keywords:
            return "technical"
    
    # 根据类别判断
    if 'correction' in category or 'best_practice' in category:
        return "workflow"
    elif 'knowledge_gap' in category:
        return "technical"
    
    return "trading"  # 默认

def save_to_knowledge_base(entry, domain):
    """保存到知识库"""
    # 创建目标目录
    domain_dir = KNOWLEDGE_BASE_DIR / "domains" / domain
    domain_dir.mkdir(exist_ok=True)
    
    # 生成文件名
    safe_title = re.sub(r'[^\w\-]', '_', entry['title'][:50])
    filename = f"{entry['date']}_{safe_title}.md"
    filepath = domain_dir / filename
    
    # 写入文件
    content = f"""# {entry['title']}

**日期**: {entry['date']}
**类别**: {entry['category']}
**关键词**: {', '.join(entry['keywords'])}

## 内容

{entry['body']}

## 来源

迁移自 `.learnings/` 目录

## 状态

待分类和整理

---

*最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已保存: {filepath}")
    return filepath

def main():
    """主函数"""
    print("开始迁移.learnings/内容到知识库...")
    
    # 检查目录
    if not LEARNINGS_DIR.exists():
        print(f"错误: .learnings目录不存在: {LEARNINGS_DIR}")
        return
    
    # 处理每个学习文件
    learning_files = ['LEARNINGS.md', 'ERRORS.md', 'FEATURE_REQUESTS.md']
    migrated_count = 0
    
    for filename in learning_files:
        filepath = LEARNINGS_DIR / filename
        if not filepath.exists():
            print(f"跳过: {filename} 不存在")
            continue
        
        print(f"\n处理文件: {filename}")
        content = read_learning_file(filepath)
        if not content:
            continue
        
        entries = parse_learning_entry(content)
        print(f"找到 {len(entries)} 个条目")
        
        for entry in entries:
            domain = determine_domain(entry['keywords'], entry['category'])
            save_to_knowledge_base(entry, domain)
            migrated_count += 1
    
    print(f"\n迁移完成! 共迁移 {migrated_count} 个条目到知识库")
    
    # 创建迁移报告
    report_path = KNOWLEDGE_BASE_DIR / "migration_report.md"
    report_content = f"""# 知识库迁移报告

## 迁移信息
- **迁移时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **源目录**: {LEARNINGS_DIR}
- **目标目录**: {KNOWLEDGE_BASE_DIR}
- **迁移条目数**: {migrated_count}

## 迁移文件
{chr(10).join(f'- {f}: {len(parse_learning_entry(read_learning_file(LEARNINGS_DIR / f) or "")) if (LEARNINGS_DIR / f).exists() else 0} 个条目' for f in learning_files)}

## 下一步建议
1. 检查迁移的知识条目
2. 进行分类和整理
3. 建立知识关联关系
4. 定期运行迁移脚本

---
*迁移脚本: migrate_learnings.py*
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"迁移报告已保存: {report_path}")

if __name__ == "__main__":
    main()