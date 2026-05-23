#!/usr/bin/env python3
"""
解析 VL 识别结果（个股清单图 → 公司+代码+领域+优势）
写入 companies / stock_codes / associations 表
"""

import re
import sqlite3
from pathlib import Path

DB = Path("/Users/tuqibiao/.hermes/knowledge_base/knowledge_base.db")


def parse_vl_line(line: str) -> dict | None:
    """解析一行: 公司名 | 代码 | 细分领域 | 核心优势"""
    line = line.strip().rstrip('|')
    if not line or line.startswith('#') or line.startswith('```'):
        return None
    if '---' in line:
        return None
    if not re.search(r'[一-鿿]', line):
        return None

    parts = [p.strip() for p in line.split('|')]
    if len(parts) < 1:
        return None

    name = parts[0]
    # 过滤明显不是公司名的
    if len(name) < 2 or len(name) > 12:
        return None
    if not re.search(r'[一-鿿]', name):
        return None
    skip_names = {'公司名称', '公司名', '企业名称', '上市公司', '相关公司', '所有公司'}
    if name in skip_names:
        return None

    code = ''
    sector = ''
    advantage = ''

    if len(parts) >= 2:
        raw_code = parts[1]
        m = re.search(r'\b(\d{6}(?:\.(?:SZ|SH|BJ|HK|sz|sh|bj|hk))?)\b', raw_code)
        if m:
            code = m.group(1).upper()
        elif raw_code:
            # 可能是领域名而非代码
            sector = raw_code[:50]

    if len(parts) >= 3:
        if sector:
            advantage = parts[2][:200]
        else:
            sector = parts[2][:50]
            if len(parts) >= 4:
                advantage = parts[3][:200]

    return {
        'name': name,
        'code': code,
        'sector': sector,
        'advantage': advantage,
    }


def main():
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row

    # 确保列存在
    try:
        conn.execute("ALTER TABLE companies ADD COLUMN source TEXT DEFAULT ''")
    except:
        pass

    # 读取所有 VL 结果
    rows = conn.execute("""
        SELECT DISTINCT ai.url, ai.vl_result, a.id as article_id, a.title
        FROM article_images ai
        JOIN articles a ON a.id = ai.article_id
        WHERE ai.vl_processed = 1 AND ai.is_stock_list = 1 AND ai.vl_result != ''
    """).fetchall()

    print(f"VL 结果: {len(rows)} 条")

    new_companies = 0
    new_codes = 0
    parsed_count = 0

    for row in rows:
        text = row['vl_result']
        # 提取 ``` 代码块内的表格
        block_match = re.search(r'```\s*\n(.*?)\n```', text, re.DOTALL)
        if block_match:
            text = block_match.group(1)

        lines = text.split('\n')
        for line in lines:
            parsed = parse_vl_line(line)
            if not parsed:
                continue
            parsed_count += 1

            # 插入或获取公司
            conn.execute(
                "INSERT OR IGNORE INTO companies (name) VALUES (?)",
                (parsed['name'],)
            )
            company = conn.execute(
                "SELECT id FROM companies WHERE name = ?", (parsed['name'],)
            ).fetchone()
            if not company:
                continue
            company_id = company['id']

            # 如果有股票代码，更新 associations
            if parsed['code']:
                # 找文章已有的 theme 关联
                article = conn.execute(
                    "SELECT id FROM articles WHERE id = ?", (row['article_id'],)
                ).fetchone()

                # 存到公司-代码映射：尝试更新已有空代码的关联
                updated = conn.execute("""
                    UPDATE associations SET stock_code = ?
                    WHERE company_id = ? AND stock_code = ''
                    AND id IN (SELECT id FROM associations WHERE company_id = ? LIMIT 1)
                """, (parsed['code'], company_id, company_id)).rowcount

                if updated == 0:
                    # 插入新的关联记录（用文章标题作为临时 theme）
                    theme_name = row['title'][:80] if row['title'] else '公众号VL提取'
                    conn.execute("INSERT OR IGNORE INTO themes (name) VALUES (?)", (theme_name,))
                    theme = conn.execute("SELECT id FROM themes WHERE name = ?", (theme_name,)).fetchone()
                    if theme:
                        conn.execute("""
                            INSERT OR IGNORE INTO associations (company_id, theme_id, stock_code, description)
                            VALUES (?, ?, ?, ?)
                        """, (company_id, theme['id'], parsed['code'],
                              f"{parsed['sector']} | {parsed['advantage']}"[:200]))
                    new_codes += 1
            else:
                # 没有代码但有公司名，标记来源
                new_companies += 1

    conn.commit()

    # 最终统计
    total_companies = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    total_codes = conn.execute(
        "SELECT COUNT(*) FROM associations WHERE stock_code != ''"
    ).fetchone()[0]

    print(f"\n✅ 解析完成:")
    print(f"  解析行数: {parsed_count}")
    print(f"  新增代码: {new_codes} 条")
    print(f"  公司总数: {total_companies} 家")
    print(f"  有代码关联: {total_codes} 条")

    conn.close()


if __name__ == "__main__":
    main()
