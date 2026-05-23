#!/usr/bin/env python3
"""抓取弘信电子AI算力业务信息"""
import requests
import re

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

urls = [
    "https://www.baidu.com/s?wd=%E5%BC%98%E4%BF%A1%E7%94%B5%E5%AD%90+AI%E7%AE%97%E5%8A%9B+%E6%9C%8D%E5%8A%A1%E5%99%A8",
    "https://www.baidu.com/s?wd=%E5%BC%98%E4%BF%A1%E7%94%B5%E5%AD%90+%E6%8B%93%E7%9F%B3%E7%AE%97%E5%8A%9B+%E7%AE%97%E5%8A%9B%E7%A7%9F%E8%B5%81",
    "https://www.baidu.com/s?wd=%E5%BC%98%E4%BF%A1%E7%94%B5%E5%AD%90+%E7%AE%97%E5%8A%9B%E4%B8%9A%E5%8A%A1+%E8%90%A5%E6%94%B6",
]

for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.encoding = 'utf-8'
        # 提取摘要
        snippets = re.findall(r'弘信[^。]{30,150}', r.text)
        for s in snippets[:5]:
            s = re.sub(r'<[^>]+>', '', s)
            print(f"  {s}")
        print()
    except Exception as e:
        print(f"error: {e}")
