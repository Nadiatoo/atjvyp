#!/usr/bin/env python3
import sys
import os
import subprocess
import json

def extract_text_with_vision(image_path):
    """使用macOS Vision框架提取文本"""
    try:
        # 创建AppleScript来使用Vision框架
        applescript = f'''
        use framework "Vision"
        use scripting additions
        
        set imagePath to POSIX file "{image_path}"
        set theImage to current application's NSImage's alloc()'s initWithContentsOfFile:imagePath
        
        -- 创建文本识别请求
        set request to current application's VNRecognizeTextRequest's alloc()'s init()
        request's setRecognitionLevel:(current application's VNRequestTextRecognitionLevelAccurate)
        
        -- 执行请求
        set handler to current application's VNImageRequestHandler's alloc()'s initWithData:(theImage's TIFFRepresentation()) options:{{}}
        handler's performRequests:{{request}} |error|:(missing value)
        
        -- 获取结果
        set results to request's results()
        set extractedText to ""
        
        repeat with observation in results
            set text to (observation's topCandidates:1)'s firstObject()'s |string|() as text
            set extractedText to extractedText & text & "\\n"
        end repeat
        
        return extractedText
        '''
        
        # 执行AppleScript
        result = subprocess.run(['osascript', '-e', applescript], 
                               capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            print("=== 使用Vision框架提取的文本 ===")
            print(result.stdout)
            print("===============================")
            return result.stdout
        else:
            print("Vision框架未检测到文本")
            return None
            
    except Exception as e:
        print(f"Vision框架错误: {e}")
        return None

def extract_text_with_system(image_path):
    """使用系统命令尝试提取文本"""
    try:
        # 尝试使用tesseract（如果已安装）
        result = subprocess.run(['which', 'tesseract'], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("尝试使用tesseract OCR...")
            tesseract_result = subprocess.run(['tesseract', image_path, 'stdout', '-l', 'chi_sim+eng'], 
                                             capture_output=True, text=True)
            if tesseract_result.stdout.strip():
                print("=== tesseract提取的文本 ===")
                print(tesseract_result.stdout)
                print("===========================")
                return tesseract_result.stdout
        return None
        
    except Exception as e:
        print(f"系统OCR错误: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python3 vision_ocr.py <图片路径>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"文件不存在: {image_path}")
        sys.exit(1)
    
    print(f"处理图片: {image_path}")
    
    # 首先尝试Vision框架
    text = extract_text_with_vision(image_path)
    
    # 如果Vision失败，尝试系统OCR
    if not text:
        text = extract_text_with_system(image_path)
    
    if not text:
        print("无法从图片中提取文本。可能需要安装OCR引擎或图片不包含可识别文本。")
        
        # 提供图片基本信息
        img_info = subprocess.run(['file', image_path], 
                                 capture_output=True, text=True)
        print(f"\n图片信息: {img_info.stdout.strip()}")