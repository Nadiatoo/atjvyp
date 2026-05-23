#!/usr/bin/env python3
"""
图片去重：知识星球(本地303张) vs 公众号(远程711张)
用 aHash 感知哈希 + 汉明距离，重复的跳过 VL
"""

import hashlib
import io
import os
import sqlite3
import urllib.request
from pathlib import Path
from PIL import Image
import numpy as np

ZSXQ_IMAGES = Path("/Users/tuqibiao/Downloads/2026复盘/知识星球数据库/images")
DB = Path("/Users/tuqibiao/.hermes/knowledge_base/knowledge_base.db")
CACHE_DIR = Path("/Users/tuqibiao/.openclaw/workspace/image_cache")

HAMMING_THRESHOLD = 10  # 汉明距离阈值（64位中 10 位以下差异 = 近似重复）


def ahash(img: Image.Image) -> str:
    """Average Hash: 缩放到 8x8 灰度，按均值二值化"""
    img = img.resize((8, 8)).convert('L')
    arr = np.array(img)
    avg = arr.mean()
    return ''.join('1' if p > avg else '0' for p in arr.flatten())


def hamming(h1: str, h2: str) -> int:
    return sum(c1 != c2 for c1, c2 in zip(h1, h2))


def is_duplicate(new_hash: str, existing_hashes: dict[str, str]) -> tuple[bool, str]:
    """检查是否与已知图片重复，返回 (重复?, 匹配文件名)"""
    for fname, eh in existing_hashes.items():
        if hamming(new_hash, eh) <= HAMMING_THRESHOLD:
            return True, fname
    return False, ""


def compute_zsxq_hashes() -> dict[str, str]:
    """计算所有知识星球本地图片的 aHash"""
    hashes = {}
    for fp in sorted(ZSXQ_IMAGES.glob("*")):
        if fp.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp', '.gif'):
            try:
                img = Image.open(fp)
                hashes[fp.name] = ahash(img)
            except Exception as e:
                print(f"  跳过 {fp.name}: {e}")
    return hashes


def download_and_hash(url: str, cache_dir: Path) -> str | None:
    """下载远程图片并计算 aHash，缓存到本地"""
    cache_dir.mkdir(parents=True, exist_ok=True)
    # 用 URL 的 MD5 做缓存文件名
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    cache_path = cache_dir / f"{url_hash}.jpg"

    if cache_path.exists():
        try:
            img = Image.open(cache_path)
            return ahash(img)
        except:
            cache_path.unlink()

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            if len(data) < 100:
                return None
            img = Image.open(io.BytesIO(data))
            # 缓存
            with open(cache_path, 'wb') as f:
                f.write(data)
            return ahash(img)
    except Exception as e:
        return None


def main():
    print("计算知识星球图片哈希...")
    zsxq_hashes = compute_zsxq_hashes()
    print(f"  知识星球: {len(zsxq_hashes)} 张")

    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row

    # 获取公众号个股清单图（去重 URL）
    urls = conn.execute("""
        SELECT DISTINCT url FROM article_images WHERE is_stock_list = 1
    """).fetchall()
    unique_urls = [r['url'] for r in urls]
    print(f"  公众号清单图(去重URL): {len(unique_urls)} 张")

    # 确保列存在
    try:
        conn.execute("ALTER TABLE article_images ADD COLUMN is_duplicate BOOLEAN DEFAULT 0")
    except:
        pass
    try:
        conn.execute("ALTER TABLE article_images ADD COLUMN duplicate_of TEXT DEFAULT ''")
    except:
        pass

    # 下载并对比
    print(f"\n下载并对比...")
    duplicate_count = 0
    unique_count = 0
    error_count = 0
    batch = []

    for i, url in enumerate(unique_urls):
        try:
            pub_hash = download_and_hash(url, CACHE_DIR)
            if pub_hash is None:
                error_count += 1
                batch.append((0, '', url))
                continue

            dup, match = is_duplicate(pub_hash, zsxq_hashes)
            if dup:
                duplicate_count += 1
                batch.append((1, match, url))
            else:
                unique_count += 1
                batch.append((0, '', url))
        except:
            error_count += 1
            batch.append((0, '', url))

        if (i + 1) % 50 == 0:
            conn.executemany(
                "UPDATE article_images SET is_duplicate = ?, duplicate_of = ? WHERE url = ? AND is_stock_list = 1",
                batch
            )
            conn.commit()
            batch = []
            print(f"  进度: {i+1}/{len(unique_urls)} (重复: {duplicate_count}, 唯一: {unique_count}, 失败: {error_count})")

    # 最后一批
    if batch:
        conn.executemany(
            "UPDATE article_images SET is_duplicate = ?, duplicate_of = ? WHERE url = ? AND is_stock_list = 1",
            batch
        )
        conn.commit()

    print(f"\n✅ 去重完成:")
    print(f"  知识星球图片: {len(zsxq_hashes)} 张")
    print(f"  公众号清单图: {len(unique_urls)} 张 (去重URL)")
    print(f"  重复(跳过VL): {duplicate_count} 张")
    print(f"  唯一(需VL):   {unique_count} 张")
    print(f"  下载失败:     {error_count} 张")

    conn.close()


if __name__ == "__main__":
    main()
