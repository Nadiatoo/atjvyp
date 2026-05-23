#!/usr/bin/env python3
"""
个股研报生成器
用法: python3 generate_report.py 中科曙光
      python3 generate_report.py 宁德时代 --output report.md
      python3 generate_report.py 蓝思科技 --pdf   # 需要安装 pandoc
"""

import argparse
import json
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DB = Path("/Users/tuqibiao/.hermes/knowledge_base/knowledge_base.db")


def query_company(conn, name: str) -> dict:
    """查公司基础信息 + 题材覆盖 + 核心逻辑 + 相关文章"""
    # 精确匹配优先，否则模糊
    company = conn.execute(
        "SELECT id, name FROM companies WHERE name = ?", (name,)
    ).fetchone()
    if not company:
        companies = conn.execute(
            "SELECT id, name FROM companies WHERE name LIKE ? LIMIT 5", (f"%{name}%",)
        ).fetchall()
        if not companies:
            return None
        # 多个匹配时让用户选
        if len(companies) > 1:
            print(f"找到 {len(companies)} 个匹配:")
            for i, c in enumerate(companies):
                print(f"  [{i+1}] {c['name']}")
            choice = input(f"选哪个? (1-{len(companies)}): ").strip()
            try:
                company = companies[int(choice) - 1]
            except:
                company = companies[0]
        else:
            company = companies[0]

    company_id = company["id"]
    company_name = company["name"]

    # 题材覆盖 + 股票代码 + 核心逻辑
    themes = conn.execute("""
        SELECT t.name as theme, a.stock_code, a.description
        FROM associations a
        JOIN themes t ON t.id = a.theme_id
        WHERE a.company_id = ?
        ORDER BY t.name
    """, (company_id,)).fetchall()

    # 核心逻辑汇总（非空描述）
    logic_parts = []
    stock_codes = set()
    theme_names = []
    for r in themes:
        theme_names.append(r["theme"])
        if r["stock_code"]:
            stock_codes.add(r["stock_code"])
        if r["description"]:
            logic_parts.append(f"【{r['theme']}】{r['description']}")

    # 相关文章
    articles = conn.execute("""
        SELECT a.title, a.source, substr(a.content, 1, 300) as preview
        FROM articles a
        JOIN article_companies ac ON ac.article_id = a.id
        WHERE ac.company_id = ?
        ORDER BY a.id DESC LIMIT 15
    """, (company_id,)).fetchall()

    # 文章中被提及的次数
    article_count = conn.execute("""
        SELECT COUNT(*) FROM article_companies WHERE company_id = ?
    """, (company_id,)).fetchone()[0]

    # 同题材相关公司（TOP 5 每个题材）
    related_companies = {}
    for theme in theme_names[:10]:
        peers = conn.execute("""
            SELECT c.name, a.stock_code
            FROM associations a
            JOIN companies c ON c.id = a.company_id
            JOIN themes t ON t.id = a.theme_id
            WHERE t.name = ? AND c.id != ?
            ORDER BY a.stock_code DESC LIMIT 8
        """, (theme, company_id)).fetchall()
        if peers:
            related_companies[theme] = peers

    return {
        "name": company_name,
        "stock_codes": sorted(stock_codes),
        "themes": theme_names,
        "logic": logic_parts,
        "articles": articles,
        "article_count": article_count,
        "related_companies": related_companies,
    }


def generate_markdown(data: dict) -> str:
    """生成结构化 Markdown 研报"""
    name = data["name"]
    codes = data["stock_codes"]
    code_str = "、".join(codes) if codes else "无代码"
    theme_count = len(data["themes"])
    article_count = data["article_count"]

    lines = []
    lines.append(f"# {name}（{code_str}）深度分析报告\n")
    lines.append(f"**报告日期：** {datetime.now().strftime('%Y年%m月%d日')}")
    lines.append(f"**数据来源：** knowledge_base.db（知识星球 + 金融梦想家公众号）")
    lines.append(f"**题材覆盖：** {theme_count} 个 | **相关文章：** {article_count} 篇\n")
    lines.append("---\n")
    lines.append("## 一、公司概况\n")

    if codes:
        lines.append(f"{name}，股票代码 {code_str}。知识库覆盖 {theme_count} 个题材领域。\n")

    # 题材覆盖
    lines.append("## 二、题材覆盖\n")
    lines.append(f"{name} 覆盖以下题材领域：\n")
    for theme in data["themes"]:
        lines.append(f"- {theme}")
    lines.append("")

    # 核心逻辑
    if data["logic"]:
        lines.append("## 三、核心逻辑\n")
        for i, logic in enumerate(data["logic"][:20], 1):
            lines.append(f"### {i}. {logic[:200]}")
            lines.append("")

    # 同题材相关公司
    if data["related_companies"]:
        lines.append("## 四、同业对标\n")
        for theme, peers in data["related_companies"].items():
            lines.append(f"### {theme}\n")
            lines.append("| 公司 | 股票代码 |")
            lines.append("|------|:--------:|")
            lines.append(f"| **{name}** | {code_str} |")
            for p in peers[:7]:
                lines.append(f"| {p['name']} | {p['stock_code'] or '—'} |")
            lines.append("")

    # 相关文章
    if data["articles"]:
        lines.append("## 五、相关文章支撑\n")
        lines.append(f"知识库中共 {article_count} 篇文章提及 {name}，以下为最近部分：\n")
        for art in data["articles"][:15]:
            lines.append(f"### [{art['source']}] {art['title'][:80]}")
            # 摘取关键片段
            preview = art['preview'][:200].replace('\n', ' ')
            lines.append(f"> {preview}...\n")

    # 风险提示
    lines.append("## 六、风险提示\n")
    lines.append("1. 本报告基于公开数据自动生成，不构成投资建议")
    lines.append("2. 题材覆盖来源于知识星球及公众号公开信息，数据可能存在时效性差异")
    lines.append("3. 核心逻辑摘要自多篇文章，未经人工审核确认")
    lines.append(f"4. {name} 相关的财务数据、估值指标请参考券商研报和交易所公告\n")

    lines.append("---\n")
    lines.append(f"*本报告由 小猪 自动生成 | {datetime.now().strftime('%Y-%m-%d %H:%M')} | 数据源: knowledge_base.db*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="个股研报生成器")
    parser.add_argument("company", help="公司名")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--pdf", action="store_true", help="生成 PDF（需要 pandoc + wkhtmltopdf）")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出原始数据")
    args = parser.parse_args()

    if not DB.exists():
        print("❌ 数据库未找到，请先运行 clean_and_build_db.py")
        sys.exit(1)

    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row

    data = query_company(conn, args.company)
    if not data:
        print(f"❌ 未找到公司: {args.company}")
        conn.close()
        sys.exit(1)

    conn.close()

    if args.json:
        # 转换 row 对象
        out = {k: v for k, v in data.items()}
        out["articles"] = [dict(a) for a in data["articles"]]
        out["related_companies"] = {
            k: [dict(p) for p in v] for k, v in data["related_companies"].items()
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    md = generate_markdown(data)

    output_path = args.output or f"{data['name']}_研报_{datetime.now().strftime('%Y%m%d')}.md"
    with open(output_path, 'w') as f:
        f.write(md)
    print(f"✅ 研报已生成: {output_path}")

    if args.pdf:
        pdf_path = output_path.rsplit('.', 1)[0] + '.pdf'
        try:
            subprocess.run(
                ["pandoc", output_path, "-o", pdf_path,
                 "--pdf-engine=wkhtmltopdf", "-V", "encoding=UTF-8"],
                check=True, timeout=30
            )
            print(f"✅ PDF 已生成: {pdf_path}")
        except Exception as e:
            print(f"⚠️ PDF 生成失败: {e}（需要安装 pandoc + wkhtmltopdf）")


if __name__ == "__main__":
    main()
