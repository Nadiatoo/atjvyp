#!/usr/bin/env python3
import sys
import os
from PIL import Image
import pytesseract

def extract_text_from_image_advanced(image_path):
    """从图片中提取文本（高级版本）"""
    try:
        # 打开图片
        img = Image.open(image_path)
        print(f"图片信息: {img.format}, {img.size}, {img.mode}")
        
        # 尝试不同的OCR配置
        configs = [
            ('chi_sim+eng', '默认配置'),
            ('eng', '仅英文'),
            ('chi_sim', '仅中文'),
            ('', '自动检测')
        ]
        
        for lang, desc in configs:
            print(f"\n=== 尝试: {desc} (语言: {lang if lang else 'auto'}) ===")
            try:
                if lang:
                    text = pytesseract.image_to_string(img, lang=lang)
                else:
                    text = pytesseract.image_to_string(img)
                
                if text.strip():
                    print(f"提取到 {len(text.strip())} 个字符:")
                    print(text[:500] + ("..." if len(text) > 500 else ""))
                else:
                    print("未检测到文本")
                    
            except Exception as e:
                print(f"错误: {e}")
        
        # 尝试获取更详细的信息
        print(f"\n=== 详细分析 ===")
        try:
            # 获取边界框
            data = pytesseract.image_to_data(img, lang='chi_sim+eng', output_type=pytesseract.Output.DICT)
            print(f"检测到的文本块数量: {len(data['text'])}")
            
            # 统计非空文本
            non_empty = [t for t in data['text'] if t.strip()]
            print(f"非空文本块: {len(non_empty)}")
            
            if non_empty:
                print("前5个文本块:")
                for i, text in enumerate(non_empty[:5]):
                    print(f"  {i+1}. '{text}'")
        
        except Exception as e:
            print(f"详细分析错误: {e}")
        
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python3 ocr_test_advanced.py <图片路径>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"文件不存在: {image_path}")
        sys.exit(1)
    
    extract_text_from_image_advanced(image_path)