#!/usr/bin/env python3
"""
从已入库的公众号文章中提取图片 URL
标记尾部疑似「个股清单」的图片，供千问 VL 识别
"""

import re
import sqlite3
from pathlib import Path

ARTICLES_DIR = Path("/Users/tuqibiao/Downloads/2026复盘/公众号文章")
DB = Path("/Users/tuqibiao/.hermes/knowledge_base/knowledge_base.db")

# 个股清单图判定关键词
STOCK_LIST_KEYWORDS = [
    '受益标的', '核心公司', '核心标的', '个股清单', '相关标的',
    '受益公司', '产业链公司', '标的公司', '相关公司', '上市公司',
    '投资标的', '重点关注', '受益股', '核心个股', '股票清单',
    '梳理', '标的梳理', '公司梳理', '产业链梳理',
]


def extract_images_from_raw(raw: str) -> list[dict]:
    """从原始 Markdown 提取所有图片 URL 及上下文"""
    images = []
    lines = raw.split('\n')
    total_lines = len(lines)

    # 匹配 markdown 图片: ![alt](url)
    for i, line in enumerate(lines):
        matches = re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', line)
        for m in matches:
            alt = m.group(1).strip()
            url = m.group(2).strip()
            if url and not url.startswith('data:'):
                images.append({
                    'url': url,
                    'alt': alt,
                    'line_num': i,
                    'rel_pos': i / max(total_lines, 1),  # 相对位置 0~1
                })

        # 也匹配直接的图片 URL（非 markdown 格式的 mmbiz 图片）
        mmbiz = re.finditer(r'(https?://mmbiz\.qpic\.cn[^\s"\']+)', line)
        for m in mmbiz:
            images.append({
                'url': m.group(1),
                'alt': '',
                'line_num': i,
                'rel_pos': i / max(total_lines, 1),
            })

    return images


def is_stock_list_image(img: dict, body_text: str, total_lines: int) -> bool:
    """
    判断图片是否为「个股清单」类型：
    1. 位置在文章后 40%（个股清单通常在尾部）
    2. 附近文字含「个股/标的/受益」等关键词
    """
    # 位置信号：后 40%
    pos_signal = img['rel_pos'] >= 0.6

    # 关键词信号：检查 alt 文本 + 图片前后 5 行
    context = img['alt']
    lines = body_text.split('\n')
    start = max(0, img['line_num'] - 5)
    end = min(len(lines), img['line_num'] + 5)
    context += ' '.join(lines[start:end])

    kw_signal = any(kw in context for kw in STOCK_LIST_KEYWORDS)

    return pos_signal and kw_signal


def ensure_schema(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS article_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL REFERENCES articles(id),
            url TEXT NOT NULL,
            alt TEXT DEFAULT '',
            position INTEGER DEFAULT 0,
            is_stock_list BOOLEAN DEFAULT 0,
            vl_processed BOOLEAN DEFAULT 0,
            vl_result TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE INDEX IF NOT EXISTS idx_ai_article ON article_images(article_id);
        CREATE INDEX IF NOT EXISTS idx_ai_stock_list ON article_images(is_stock_list) WHERE is_stock_list = 1;
    """)
    conn.commit()


def main():
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    ensure_schema(conn)

    # 查询已有文章
    articles = conn.execute(
        "SELECT id, file_path FROM articles WHERE file_path IS NOT NULL"
    ).fetchall()

    if not articles:
        print("没有文章，请先运行 import_articles.py")
        conn.close()
        return

    print(f"文章数: {len(articles)}")

    # 清理旧图片数据
    conn.execute("DELETE FROM article_images")
    conn.commit()

    total_images = 0
    stock_list_images = 0

    for i, art in enumerate(articles):
        fp = Path(art['file_path'])
        if not fp.exists():
            continue

        try:
            with open(fp, 'r', errors='ignore') as f:
                raw = f.read()
        except:
            continue

        images = extract_images_from_raw(raw)
        if not images:
            continue

        # 获取 body 文本用于关键词匹配（简单去除 CSS）
        body = re.sub(r'\{[^}]*\}', '', raw)
        body = re.sub(r'<[^>]+>', '', body)

        for img in images:
            is_list = is_stock_list_image(img, body, len(raw.split('\n')))
            conn.execute(
                "INSERT INTO article_images (article_id, url, alt, position, is_stock_list) VALUES (?, ?, ?, ?, ?)",
                (art['id'], img['url'][:500], img['alt'][:200], img['line_num'], int(is_list))
            )
            total_images += 1
            if is_list:
                stock_list_images += 1

        if (i + 1) % 500 == 0:
            conn.commit()
            print(f"  进度: {i+1}/{len(articles)} (图片: {total_images}, 清单图: {stock_list_images})")

    conn.commit()

    print(f"\n✅ 完成:")
    print(f"  总图片: {total_images} 张")
    print(f"  个股清单图: {stock_list_images} 张 (待 VL 识别)")
    print(f"  普通图: {total_images - stock_list_images} 张 (仅保存URL)")

    conn.close()


if __name__ == "__main__":
    main()
