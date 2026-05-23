#!/usr/bin/env python3
"""
千问 Vision 批量处理个股清单图
从 image_cache 读取已下载图片，调用 VL API，结果写回 DB
"""

import base64
import hashlib
import io
import json
import os
import re
import sqlite3
import time
import urllib.request
import urllib.error
from pathlib import Path

QWEN_API_KEY = os.environ.get("QWEN_API_KEY", "")
QWEN_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen-vl-max"

DB = Path("/Users/tuqibiao/.hermes/knowledge_base/knowledge_base.db")
CACHE_DIR = Path("/Users/tuqibiao/.openclaw/workspace/image_cache")

STOCK_LIST_PROMPT = """请仔细提取这张「个股/标的/公司清单」图片中的所有文字信息。

对于图片中的每一行，请提取：
- 公司名称
- 股票代码（如有，6位数字）
- 所属细分领域/产业链环节
- 核心优势/逻辑（简要）

请用以下格式输出，方便程序解析：
```
公司名 | 股票代码 | 细分领域 | 核心优势
```

如果图片不是个股清单（是走势图、纯插图等），请回复「非清单图」并简要说明图片内容。"""


def encode_image_from_bytes(data: bytes, ext: str = "jpg") -> str:
    return base64.b64encode(data).decode("utf-8")


def call_qwen_vision(image_data: bytes, prompt: str, max_retries: int = 3) -> str:
    """调用千问 VL API，带重试"""
    b64 = encode_image_from_bytes(image_data)
    mime = f"image/jpeg"

    body = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    }

    for attempt in range(max_retries):
        try:
            data = json.dumps(body).encode("utf-8")
            req = urllib.request.Request(
                f"{QWEN_BASE}/chat/completions",
                data=data,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Authorization": f"Bearer {QWEN_API_KEY}",
                },
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                result = json.loads(resp.read())
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                return f"API异常: {json.dumps(result, ensure_ascii=False)[:200]}"

        except urllib.error.HTTPError as e:
            err = e.read().decode()[:200]
            if e.code == 429:
                wait = min(30, (attempt + 1) * 10)
                print(f"    限流，等待 {wait}s...")
                time.sleep(wait)
                continue
            return f"HTTP{e.code}: {err}"
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            return f"错误: {str(e)[:200]}"

    return "重试耗尽"


def get_cached_image(url: str) -> bytes | None:
    """从缓存读取已下载的图片"""
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    cache_path = CACHE_DIR / f"{url_hash}.jpg"
    if cache_path.exists():
        with open(cache_path, 'rb') as f:
            return f.read()
    return None


def main():
    if not QWEN_API_KEY:
        print("❌ QWEN_API_KEY 未设置")
        return

    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row

    # 确保列存在
    for col, dtype in [('vl_result', 'TEXT DEFAULT ""'), ('vl_processed', 'BOOLEAN DEFAULT 0')]:
        try:
            conn.execute(f"ALTER TABLE article_images ADD COLUMN {col} {dtype}")
        except:
            pass
    conn.commit()

    # 获取待处理图片：个股清单图 AND 非重复 AND 未处理
    images = conn.execute("""
        SELECT DISTINCT url FROM article_images
        WHERE is_stock_list = 1
          AND is_duplicate = 0
          AND vl_processed = 0
    """).fetchall()

    urls = [r['url'] for r in images]
    print(f"待处理: {len(urls)} 张 (去重URL)")

    success = 0
    fail = 0
    non_list = 0

    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] {url[:70]}...", end=" ", flush=True)

        img_data = get_cached_image(url)
        if not img_data:
            # 重新下载
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    img_data = resp.read()
            except Exception as e:
                print(f"❌ 下载失败: {e}")
                fail += 1
                continue

        result = call_qwen_vision(img_data, STOCK_LIST_PROMPT)

        is_non_list = '非清单图' in result
        if is_non_list:
            non_list += 1
            print(f"⊘ 非清单")
        elif '错误' in result or '异常' in result or 'API' in result[:10]:
            print(f"❌ {result[:60]}")
            fail += 1
            # 即使失败也标记已处理，避免死循环
            conn.execute(
                "UPDATE article_images SET vl_processed = 1, vl_result = ? WHERE url = ? AND is_stock_list = 1",
                (result[:500], url)
            )
            conn.commit()
            continue
        else:
            print(f"✅ ({len(result)} 字)")
            success += 1

        # 写回数据库
        conn.execute(
            "UPDATE article_images SET vl_processed = 1, vl_result = ?, is_stock_list = ? WHERE url = ? AND is_stock_list = 1",
            (result[:5000], int(not is_non_list), url)
        )
        conn.commit()

        # API 限流控制：每秒1次
        time.sleep(0.8)

    conn.commit()

    print(f"\n✅ VL 批量处理完成:")
    print(f"  成功(个股清单): {success} 张")
    print(f"  非清单图:       {non_list} 张")
    print(f"  失败:           {fail} 张")

    # 更新 query 统计
    total_processed = conn.execute(
        "SELECT COUNT(DISTINCT url) FROM article_images WHERE vl_processed = 1 AND is_stock_list = 1"
    ).fetchone()[0]
    print(f"  已处理清单图:   {total_processed} 张")

    conn.close()


if __name__ == "__main__":
    main()
