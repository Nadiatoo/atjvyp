#!/usr/bin/env python3
import sys
import os
from PIL import Image
import pytesseract

def extract_text_from_image(image_path):
    """从图片中提取文本"""
    try:
        # 打开图片
        img = Image.open(image_path)
        print(f"图片信息: {img.format}, {img.size}, {img.mode}")
        
        # 尝试OCR（先尝试中文，如果失败则用英文）
        try:
            text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        except:
            text = pytesseract.image_to_string(img, lang='eng')
        
        if text.strip():
            print("=== 提取的文本内容 ===")
            print(text)
            print("=====================")
            return text
        else:
            print("未检测到文本")
            return None
            
    except Exception as e:
        print(f"错误: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python3 ocr_test.py <图片路径>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"文件不存在: {image_path}")
        sys.exit(1)
    
    extract_text_from_image(image_path)