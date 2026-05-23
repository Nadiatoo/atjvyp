#!/usr/bin/env python3
"""
公众号文章导入 knowledge_base.db
扫描 ~/Downloads/2026复盘/公众号文章/*.md
提取标题 + 正文 + 识别公司名，写入数据库
"""

import re
import sqlite3
import sys
from pathlib import Path

ARTICLES_DIR = Path("/Users/tuqibiao/Downloads/2026复盘/公众号文章")
DB = Path("/Users/tuqibiao/.hermes/knowledge_base/knowledge_base.db")


def strip_css_and_html(text: str) -> str:
    """移除 CSS 样式块、HTML 标签、图片链接，保留纯文本"""
    # 删除 CSS 块
    text = re.sub(r'\{[^}]*\}', '', text)
    # 全局 unescape：公众号导出格式大量使用 \_ \. \* 转义
    text = text.replace('\\_', '_').replace('\\.', '.').replace('\\*', '').replace('\\#', '#')
    # 删除 CSS 选择器残留
    text = re.sub(r'\.[a-zA-Z_][a-zA-Z0-9_-]*', ' ', text)
    text = re.sub(r'#[a-zA-Z_-]+', ' ', text)
    text = re.sub(r'\b(blockquote|img|a|body|html|div|span|section|svg|g|path|rect|circle|mask|defs|use)\b', ' ', text)
    text = re.sub(r'\*', ' ', text)
    text = re.sub(r'rgb\([^)]*\)', ' ', text)
    text = re.sub(r'url\([^)]*\)', ' ', text)
    text = re.sub(r'item_show_type_\d+', ' ', text)
    text = re.sub(r'(text_content|picture_content|bottom_bar|page_content|sns_opr_btn)', ' ', text)
    text = re.sub(r':(not|nth-child|first-child|last-child|before|after|hover|focus|active|visited)\([^)]*\)', ' ', text)
    text = re.sub(r'\s+>\s+', ' ', text)
    # 删除不含中文的纯 CSS 残留行
    lines = text.split('\n')
    text = '\n'.join(
        l for l in lines
        if re.search(r'[一-鿿]', l) or not re.search(r'^[\s\._a-zA-Z#;:>\-\(\)]+$', l)
    )
    # 删除 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)
    # 删除 markdown 图片
    text = re.sub(r'!\[.*?\]\([^)]+\)', '', text)
    # 删除 mmbiz 图片 URL
    text = re.sub(r'https?://mmbiz\.qpic\.cn[^\s]+', '', text)
    text = re.sub(r'https?://[^\s]+\.(jpg|jpeg|png|gif|webp)[^\s]*', '', text)
    # 删除非微信 URL
    text = re.sub(r'https?://(?!mp\.weixin)[^\s]+', '', text)
    # 删除 data URI
    text = re.sub(r'data:image[^\s"]+', '', text)
    # 压缩空行和多余空格
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    text = re.sub(r' {3,}', '  ', text)
    text = re.sub(r'^ {2,}', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\*{3,}\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\.\s*$', '', text, flags=re.MULTILINE)
    return text.strip()


def extract_title_and_body(filepath: Path) -> tuple[str, str]:
    """从 .md 文件提取标题和正文"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        raw = f.read()

    # 先清理
    text = strip_css_and_html(raw)

    lines = [l.strip() for l in text.split('\n') if l.strip()]
    title = filepath.stem  # 默认用文件名

    for line in lines[:15]:
        line = line.lstrip('#').strip()
        if re.match(r'^(原创|转自|\d{4}年|\d{2}:\d{2}|亲爱|最近|邀请|以下是我|原文地址)', line):
            continue
        if len(line) >= 6 and not line.startswith('http') and not line.startswith('data:'):
            # 截断 CSS 残留：取第一个 `\` 之前的内容（公众号导出格式的 CSS 残留特征）
            css_cut = line.find(' \\ ')
            if css_cut > 0:
                line = line[:css_cut]
            # 如果还有 .class 模式残留，裁掉
            if re.search(r'\s\.\w', line):
                line = re.sub(r'\s+\.\w.*$', '', line)
            title = line.strip()[:120]
            break

    body = '\n'.join(lines)
    return title, body


def match_companies(text: str, known_companies: list[str]) -> set[str]:
    """在文本中匹配已知公司名（长名优先避免部分匹配）"""
    found = set()
    # 按长度降序匹配，避免「中芯」匹配到「中芯国际」
    sorted_companies = sorted(known_companies, key=len, reverse=True)
    for name in sorted_companies:
        if name in text:
            found.add(name)
            # 可选：标记后避免重复匹配
            # text = text.replace(name, '')  # 会影响后续短名匹配
    return found


def ensure_schema(conn: sqlite3.Connection):
    """确保数据库有 articles 和 article_companies 表"""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL DEFAULT '',
            source TEXT NOT NULL DEFAULT '公众号',
            file_path TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS article_companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL REFERENCES articles(id),
            company_id INTEGER NOT NULL REFERENCES companies(id),
            mention_count INTEGER DEFAULT 1,
            UNIQUE(article_id, company_id)
        );

        CREATE INDEX IF NOT EXISTS idx_article_source ON articles(source);
        CREATE INDEX IF NOT EXISTS idx_ac_article ON article_companies(article_id);
        CREATE INDEX IF NOT EXISTS idx_ac_company ON article_companies(company_id);
    """)
    conn.commit()


def main():
    if not ARTICLES_DIR.exists():
        print(f"目录不存在: {ARTICLES_DIR}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    ensure_schema(conn)

    # 加载已知公司名
    known = [row[0] for row in conn.execute("SELECT name FROM companies").fetchall()]
    print(f"已知公司: {len(known)} 家")

    # 扫描文章
    files = sorted(ARTICLES_DIR.glob("*.md"))
    total = len(files)
    print(f"文章数: {total}")

    article_count = 0
    association_count = 0

    for i, fp in enumerate(files):
        try:
            title, body = extract_title_and_body(fp)

            if len(body) < 50:
                continue  # 跳过太短的文章

            # 检查是否已导入（按文件路径）
            existing = conn.execute(
                "SELECT id FROM articles WHERE file_path = ?", (str(fp),)
            ).fetchone()
            if existing:
                continue

            # 匹配公司名
            found = match_companies(body, known)

            # 插入文章
            conn.execute(
                "INSERT INTO articles (title, content, source, file_path) VALUES (?, ?, '公众号', ?)",
                (title, body, str(fp))
            )
            article_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            article_count += 1

            # 插入关联
            for cname in found:
                company = conn.execute(
                    "SELECT id FROM companies WHERE name = ?", (cname,)
                ).fetchone()
                if company:
                    try:
                        conn.execute(
                            "INSERT OR IGNORE INTO article_companies (article_id, company_id) VALUES (?, ?)",
                            (article_id, company["id"])
                        )
                        association_count += 1
                    except:
                        pass

            if (i + 1) % 200 == 0:
                conn.commit()
                print(f"  进度: {i+1}/{total} ({article_count} 篇入库, {association_count} 条关联)")

        except Exception as e:
            print(f"  跳过 [{fp.name}]: {e}")
            continue

    conn.commit()

    # 统计
    total_articles = conn.execute("SELECT COUNT(*) FROM articles WHERE source = '公众号'").fetchone()[0]
    total_assoc = conn.execute("SELECT COUNT(*) FROM article_companies").fetchone()[0]
    print(f"\n✅ 完成:")
    print(f"  文章入库: {article_count} 篇")
    print(f"  公司关联: {association_count} 条")
    print(f"  库内文章总数: {total_articles}")

    conn.close()


if __name__ == "__main__":
    main()
