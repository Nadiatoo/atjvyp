#!/usr/bin/env python3
"""
知识库查询工具 — 小禾用
用法:
  python3 query_kb.py --company 中科曙光              # 查公司关联的所有题材
  python3 query_kb.py --theme AI算力                   # 查题材下的所有公司
  python3 query_kb.py --search 液冷                     # 全文搜索(公司/题材/描述)
  python3 query_kb.py --search 液冷 --source 公众号     # 包含文章搜索
  python3 query_kb.py --company 宁德时代 --articles     # 查哪些文章提到该公司
  python3 query_kb.py --article 存储芯片                # 搜索文章标题/内容
  python3 query_kb.py --stats                           # 库统计
  python3 query_kb.py --company 中科曙光 --json         # JSON 输出
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

DB = Path("/Users/tuqibiao/.hermes/knowledge_base/knowledge_base.db")


def get_conn():
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    return conn


def search_company(conn, name: str, exact: bool = False):
    if exact:
        rows = conn.execute(
            "SELECT c.name, t.name as theme, a.stock_code, a.description "
            "FROM companies c "
            "JOIN associations a ON a.company_id = c.id "
            "JOIN themes t ON t.id = a.theme_id "
            "WHERE c.name = ? "
            "ORDER BY t.name", (name,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT c.name, t.name as theme, a.stock_code, a.description "
            "FROM companies c "
            "JOIN associations a ON a.company_id = c.id "
            "JOIN themes t ON t.id = a.theme_id "
            "WHERE c.name LIKE ? "
            "ORDER BY c.name, t.name", (f"%{name}%",)
        ).fetchall()
    return rows


def search_theme(conn, name: str):
    rows = conn.execute(
        "SELECT t.name as theme, c.name as company, a.stock_code, a.description "
        "FROM themes t "
        "JOIN associations a ON a.theme_id = t.id "
        "JOIN companies c ON c.id = a.company_id "
        "WHERE t.name LIKE ? "
        "ORDER BY t.name, c.name", (f"%{name}%",)
    ).fetchall()
    return rows


def search_all(conn, query: str, source: str = None):
    """LIKE 搜索公司名 + 题材名 + 关联描述 + (可选)文章"""
    results = []
    like = f"%{query}%"

    for row in conn.execute(
        "SELECT '公司' as kind, name FROM companies WHERE name LIKE ? LIMIT 20", (like,)
    ):
        results.append((row["kind"], row["name"]))

    for row in conn.execute(
        "SELECT '题材' as kind, name FROM themes WHERE name LIKE ? LIMIT 20", (like,)
    ):
        results.append((row["kind"], row["name"]))

    for row in conn.execute(
        "SELECT '描述' as kind, c.name || ' → ' || substr(a.description,1,60) as name "
        "FROM associations a JOIN companies c ON c.id = a.company_id "
        "WHERE a.description LIKE ? LIMIT 10", (like,)
    ):
        results.append((row["kind"], row["name"]))

    # 文章搜索
    if source == '公众号' or source == 'all':
        src_filter = "AND source = ?" if source == '公众号' else ""
        params = (like, like) if source != '公众号' else (like, '公众号', like, '公众号')

        try:
            for row in conn.execute(
                f"SELECT '文章' as kind, title || ' [' || COALESCE(source,'') || ']' as name "
                f"FROM articles WHERE (title LIKE ? OR content LIKE ?) {src_filter} LIMIT 15",
                (params if source == '公众号' else (like, like))
            ):
                results.append((row["kind"], row["name"]))
        except:
            pass

    return results


def search_articles(conn, query: str, source: str = None):
    """搜索文章标题+内容"""
    like = f"%{query}%"
    src_filter = "AND source = ?" if source else ""
    params = (like, like, source) if source else (like, like)
    rows = conn.execute(
        f"SELECT id, title, source, substr(content, 1, 200) as preview "
        f"FROM articles WHERE (title LIKE ? OR content LIKE ?) {src_filter} "
        f"ORDER BY id LIMIT 20", params
    ).fetchall()
    return rows


def company_articles(conn, company_name: str):
    """查哪些文章提到某公司"""
    rows = conn.execute(
        "SELECT a.title, a.source, substr(a.content,1,200) as preview, ac.mention_count "
        "FROM articles a "
        "JOIN article_companies ac ON ac.article_id = a.id "
        "JOIN companies c ON c.id = ac.company_id "
        "WHERE c.name LIKE ? "
        "ORDER BY a.id LIMIT 30", (f"%{company_name}%",)
    ).fetchall()
    return rows


def get_stats(conn):
    n_companies = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    n_themes = conn.execute("SELECT COUNT(*) FROM themes").fetchone()[0]
    n_assoc = conn.execute("SELECT COUNT(*) FROM associations").fetchone()[0]
    n_with_code = conn.execute(
        "SELECT COUNT(*) FROM associations WHERE stock_code != ''"
    ).fetchone()[0]
    top_themes = conn.execute(
        "SELECT t.name, COUNT(*) as cnt FROM themes t "
        "JOIN associations a ON a.theme_id = t.id "
        "GROUP BY t.id ORDER BY cnt DESC LIMIT 10"
    ).fetchall()

    # 文章统计
    try:
        n_articles = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        article_sources = conn.execute(
            "SELECT source, COUNT(*) as cnt FROM articles GROUP BY source"
        ).fetchall()
    except:
        n_articles = 0
        article_sources = []

    try:
        n_article_companies = conn.execute("SELECT COUNT(*) FROM article_companies").fetchone()[0]
    except:
        n_article_companies = 0

    return n_companies, n_themes, n_assoc, n_with_code, top_themes, \
           n_articles, article_sources, n_article_companies


def format_output(rows, mode: str):
    if not rows:
        print("(无结果)")
        return

    if mode == "company":
        current_company = None
        for r in rows:
            if r["name"] != current_company:
                current_company = r["name"]
                print(f"\n📌 {current_company}")
            parts = [f"  ├─ {r['theme']}"]
            if r["stock_code"]:
                parts.append(f"[{r['stock_code']}]")
            if r["description"]:
                parts.append(r["description"][:60])
            print(" ".join(parts))

    elif mode == "theme":
        current_theme = None
        for r in rows:
            if r["theme"] != current_theme:
                current_theme = r["theme"]
                print(f"\n📌 {current_theme}")
            code_str = f"[{r['stock_code']}]" if r['stock_code'] else ""
            desc_str = r['description'][:50] if r['description'] else ""
            print(f"  ├─ {r['company']} {code_str} {desc_str}")

    elif mode == "search":
        companies = [(n,) for t, n in rows if t == "公司"]
        themes = [(n,) for t, n in rows if t == "题材"]
        descs = [(n,) for t, n in rows if t == "描述"]
        articles = [(n,) for t, n in rows if t == "文章"]
        if companies:
            print(f"\n🏢 公司 ({len(companies)}):")
            for c in companies:
                print(f"  ├─ {c[0]}")
        if themes:
            print(f"\n🏷️ 题材 ({len(themes)}):")
            for t in themes:
                print(f"  ├─ {t[0]}")
        if descs:
            print(f"\n📝 描述匹配 ({len(descs)}):")
            for d in descs:
                print(f"  ├─ {d[0]}")
        if articles:
            print(f"\n📄 文章 ({len(articles)}):")
            for a in articles:
                print(f"  ├─ {a[0][:100]}")

    elif mode == "articles":
        for r in rows:
            print(f"\n📄 [{r['source']}] {r['title']}")
            print(f"   {r['preview'][:120]}...")


def to_json(rows):
    return [dict(r) for r in rows]


def main():
    parser = argparse.ArgumentParser(description="知识库查询")
    parser.add_argument("--company", "-c", help="按公司名搜索")
    parser.add_argument("--theme", "-t", help="按题材名搜索")
    parser.add_argument("--search", "-s", help="全文搜索")
    parser.add_argument("--article", "-a", help="搜索文章标题/内容")
    parser.add_argument("--articles", action="store_true", help="配合 --company 查关联文章")
    parser.add_argument("--source", help="数据来源过滤: 知识星球, 公众号, all")
    parser.add_argument("--stats", action="store_true", help="库统计")
    parser.add_argument("--exact", action="store_true", help="公司名精确匹配")
    parser.add_argument("--json", action="store_true", help="JSON 输出")

    args = parser.parse_args()

    if not any([args.company, args.theme, args.search, args.article, args.stats]):
        parser.print_help()
        sys.exit(1)

    if not DB.exists():
        print("❌ 数据库未找到，请先运行 clean_and_build_db.py")
        sys.exit(1)

    conn = get_conn()
    results = None
    mode = None

    try:
        if args.stats:
            n_companies, n_themes, n_assoc, n_with_code, top_themes, \
            n_articles, article_sources, n_ac = get_stats(conn)
            if args.json:
                print(json.dumps({
                    'companies': n_companies, 'themes': n_themes,
                    'associations': n_assoc, 'with_stock_code': n_with_code,
                    'top_themes': [{'name': r['name'], 'count': r['cnt']} for r in top_themes],
                    'articles': n_articles,
                    'article_sources': [{'source': r['source'], 'count': r['cnt']} for r in article_sources],
                }, ensure_ascii=False, indent=2))
            else:
                print(f"知识图谱: {n_companies} 家公司 | {n_themes} 个题材 | {n_assoc} 条关联")
                print(f"含股票代码: {n_with_code} 条")
                if n_articles:
                    print(f"文章: {n_articles} 篇 ({n_ac} 条公司关联)")
                    for r in article_sources:
                        print(f"  {r['source']}: {r['cnt']} 篇")
                print(f"\nTOP 10 题材:")
                for r in top_themes:
                    print(f"  {r['name']}: {r['cnt']} 家公司")
            return

        if args.company:
            if args.articles:
                results = company_articles(conn, args.company)
                mode = "articles"
            else:
                results = search_company(conn, args.company, exact=args.exact)
                mode = "company"

        elif args.theme:
            results = search_theme(conn, args.theme)
            mode = "theme"

        elif args.article:
            results = search_articles(conn, args.article, source=args.source)
            mode = "articles"

        elif args.search:
            results = search_all(conn, args.search, source=args.source)
            mode = "search"

        if args.json and results is not None:
            print(json.dumps(to_json(results), ensure_ascii=False, indent=2))
        elif results is not None:
            format_output(results, mode)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
