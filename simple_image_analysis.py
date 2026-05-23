#!/usr/bin/env python3
import sys
import os
from PIL import Image
import numpy as np

def analyze_image(image_path):
    """分析图片基本信息"""
    try:
        # 打开图片
        img = Image.open(image_path)
        
        print("=== 图片基本信息 ===")
        print(f"格式: {img.format}")
        print(f"尺寸: {img.size} (宽x高)")
        print(f"模式: {img.mode}")
        print(f"信息: {img.info}")
        
        # 转换为numpy数组进行分析
        img_array = np.array(img)
        print(f"\n=== 像素分析 ===")
        print(f"数组形状: {img_array.shape}")
        print(f"数据类型: {img_array.dtype}")
        print(f"最小值: {img_array.min()}")
        print(f"最大值: {img_array.max()}")
        print(f"平均值: {img_array.mean():.2f}")
        print(f"标准差: {img_array.std():.2f}")
        
        # 检查是否是文本截图（通常有较高的对比度）
        if len(img_array.shape) == 3:  # RGB图像
            # 计算对比度（标准差）
            contrast = img_array.std()
            print(f"\n=== 对比度分析 ===")
            print(f"整体对比度: {contrast:.2f}")
            
            # 检查是否是深色背景浅色文字或反之
            avg_brightness = img_array.mean()
            print(f"平均亮度: {avg_brightness:.2f}")
            
            if avg_brightness < 128:
                print("推测: 可能是深色背景")
            else:
                print("推测: 可能是浅色背景")
        
        # 尝试简单的文本检测（基于边缘检测）
        print(f"\n=== 边缘检测 ===")
        if len(img_array.shape) == 3:
            # 转换为灰度
            gray = np.mean(img_array, axis=2).astype(np.uint8)
            
            # 简单的边缘检测（水平差分）
            horizontal_edges = np.abs(np.diff(gray, axis=1))
            vertical_edges = np.abs(np.diff(gray, axis=0))
            
            edge_strength = horizontal_edges.mean() + vertical_edges.mean()
            print(f"边缘强度: {edge_strength:.2f}")
            
            if edge_strength > 10:
                print("推测: 可能包含文本（边缘强度较高）")
            else:
                print("推测: 可能是平滑图像（边缘强度较低）")
        
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python3 simple_image_analysis.py <图片路径>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"文件不存在: {image_path}")
        sys.exit(1)
    
    analyze_image(image_path)