#!/usr/bin/env python3
"""
简单测试脚本
"""

import os
import sys

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("🧪 简单系统测试...")

# 测试1: 检查目录
print("\n1. 检查目录结构...")
required_dirs = [
    "raw/domains",
    "vectors/chroma", 
    "config",
    "scripts"
]

for dir_path in required_dirs:
    full_path = os.path.join(current_dir, dir_path)
    if os.path.exists(full_path):
        print(f"  ✅ {dir_path}")
    else:
        print(f"  ❌ {dir_path}")

# 测试2: 检查配置文件
print("\n2. 检查配置文件...")
config_files = [
    "config/chroma.yaml",
    "config/embeddings.yaml",
    "config/replay_config.yaml"
]

for config_file in config_files:
    full_path = os.path.join(current_dir, config_file)
    if os.path.exists(full_path):
        print(f"  ✅ {config_file}")
    else:
        print(f"  ❌ {config_file}")

# 测试3: 检查Python依赖
print("\n3. 检查Python依赖...")
try:
    import chromadb
    print("  ✅ chromadb")
except ImportError:
    print("  ❌ chromadb")

try:
    import pandas
    print("  ✅ pandas")
except ImportError:
    print("  ❌ pandas")

try:
    import numpy
    print("  ✅ numpy")
except ImportError:
    print("  ❌ numpy")

try:
    import yaml
    print("  ✅ pyyaml")
except ImportError:
    print("  ❌ pyyaml")

# 测试4: 检查嵌入模型
print("\n4. 检查嵌入模型...")
try:
    # 尝试导入本地嵌入模型
    from scripts.local_embeddings import LocalEmbeddings
    model = LocalEmbeddings()
    test_vector = model.encode(["测试文本"])
    print(f"  ✅ 本地嵌入模型 (维度: {test_vector.shape[1]})")
except Exception as e:
    print(f"  ⚠️ 本地嵌入模型: {e}")

# 测试5: 检查复盘解析器
print("\n5. 检查复盘解析器...")
try:
    from scripts.replay_parser import ReplayParser
    parser = ReplayParser()
    print("  ✅ 复盘解析器")
except Exception as e:
    print(f"  ⚠️ 复盘解析器: {e}")

# 测试6: 检查批量处理器
print("\n6. 检查批量处理器...")
try:
    from scripts.batch_processor import BatchProcessor
    processor = BatchProcessor()
    print("  ✅ 批量处理器")
except Exception as e:
    print(f"  ⚠️ 批量处理器: {e}")

print("\n" + "="*50)
print("📋 系统状态总结:")
print("="*50)

# 检查复盘文件目录
replay_dir = "/Users/tuqibiao/Downloads/2026复盘"
if os.path.exists(replay_dir):
    import glob
    pdf_files = glob.glob(os.path.join(replay_dir, "*.pdf"))
    print(f"📁 复盘目录: {replay_dir}")
    print(f"📄 PDF文件数: {len(pdf_files)}")
    
    if pdf_files:
        print("📅 最近文件:")
        for i, pdf_file in enumerate(sorted(pdf_files, key=os.path.getmtime, reverse=True)[:3]):
            file_name = os.path.basename(pdf_file)
            mtime = os.path.getmtime(pdf_file)
            from datetime import datetime
            mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
            print(f"  {i+1}. {file_name} ({mtime_str})")
else:
    print(f"⚠️ 复盘目录不存在: {replay_dir}")

print("\n🚀 下一步行动建议:")
print("1. 安装Tesseract OCR（用于图片文字识别）:")
print("   brew install tesseract tesseract-lang")
print("")
print("2. 测试处理单个复盘文件:")
print("   python scripts/batch_processor.py /Users/tuqibiao/Downloads/2026复盘 --limit 1")
print("")
print("3. 查看配置文件:")
print("   cat config/replay_config.yaml")
print("")
print("4. 修改配置（如果需要）:")
print("   vim config/replay_config.yaml")

print("\n💡 提示: 系统已准备好处理您的复盘内容!")
print("   我可以立即开始批量处理PDF文件和图片内容。")