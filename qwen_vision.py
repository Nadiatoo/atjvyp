#!/usr/bin/env python3
"""
千问 Vision 图片读取
用法: python3 qwen_vision.py <图片路径> [可选: 自定义 prompt]
"""

import base64
import json
import sys
import os
import urllib.request

QWEN_API_KEY = os.environ.get("QWEN_API_KEY", "")
QWEN_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen-vl-max"


def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def read_image(image_path, prompt="请详细描述这张图片中的所有文字、数据、图表内容。如果是截图，请逐行转录文字。如果是图表，请描述数据趋势和关键数值。"):
    if not QWEN_API_KEY:
        print("错误: QWEN_API_KEY 未设置")
        sys.exit(1)

    b64 = encode_image(image_path)
    ext = image_path.split(".")[-1].lower()
    mime = f"image/{'jpeg' if ext in ('jpg','jpeg') else ext}"

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

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{QWEN_BASE}/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {QWEN_API_KEY}",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return f"API 返回异常: {json.dumps(result, ensure_ascii=False)}"
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        return f"API 错误 ({e.code}): {err_body}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 qwen_vision.py <图片路径> [自定义prompt]")
        sys.exit(1)

    image_path = sys.argv[1]
    custom_prompt = sys.argv[2] if len(sys.argv) > 2 else None
    prompt = custom_prompt or "请详细描述这张图片中的所有文字、数据、图表内容。"

    print(f"正在用千问 {MODEL} 读取: {image_path}")
    result = read_image(image_path, prompt)
    print(result)
