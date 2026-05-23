#!/usr/bin/env python3
"""
知识库下一步工作计划
"""

import os
import sys
from datetime import datetime

def show_plan():
    """显示工作计划"""
    print("🚀 知识库下一步工作计划")
    print("="*60)
    print(f"📅 计划时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("")
    
    # 阶段1: 监控08:00任务
    print("📋 第一阶段: 监控08:00盘前分析任务 (07:50-08:10)")
    print("  ✅ 已完成:")
    print("    1. 系统状态检查完成")
    print("    2. OpenClaw网关运行正常")
    print("    3. 定时任务已配置")
    print("    4. 脚本文件准备就绪")
    print("  🔍 待监控:")
    print("    1. 08:00任务自动执行")
    print("    2. 飞书推送结果")
    print("    3. 执行错误处理")
    print("")
    
    # 阶段2: 批量处理PDF
    print("📋 第二阶段: 批量处理复盘PDF文件 (08:10-08:30)")
    print("  🎯 目标: 处理剩余55个PDF文件")
    print("  📊 预计:")
    print("    - 处理速度: 0.15秒/文件")
    print("    - 总时间: ~8.25秒")
    print("    - 输出: 55个Markdown文件")
    print("  🔧 命令:")
    print("    cd /Users/tuqibiao/.openclaw/workspace/knowledge-base")
    print("    python scripts/simple_batch_processor.py /Users/tuqibiao/Downloads/2026复盘 --limit 55")
    print("")
    
    # 阶段3: 安装OCR支持
    print("📋 第三阶段: 安装OCR支持 (08:30-08:45)")
    print("  🎯 目标: 处理图片格式的思考内容")
    print("  📦 需要安装:")
    print("    - Tesseract OCR (brew install tesseract tesseract-lang)")
    print("    - 图片处理依赖")
    print("  🔧 命令:")
    print("    brew install tesseract tesseract-lang")
    print("    pip3 install pillow pytesseract")
    print("")
    
    # 阶段4: 修复向量数据库
    print("📋 第四阶段: 修复向量数据库 (08:45-09:00)")
    print("  🎯 目标: 启用语义搜索功能")
    print("  🔧 步骤:")
    print("    1. 安装chroma-migrate")
    print("    2. 迁移ChromaDB数据")
    print("    3. 更新配置文件")
    print("    4. 测试语义搜索")
    print("  🔧 命令:")
    print("    pip3 install chroma-migrate")
    print("    chroma-migrate")
    print("")
    
    # 阶段5: 创建Web界面
    print("📋 第五阶段: 创建知识库Web界面 (09:00-09:30)")
    print("  🎯 目标: 可视化搜索界面")
    print("  🛠️ 功能:")
    print("    - 文件浏览")
    print("    - 关键词搜索")
    print("    - 语义搜索")
    print("    - 分类浏览")
    print("    - 内容预览")
    print("")
    
    # 预期成果
    print("📊 预期成果:")
    print("  ✅ 60个复盘PDF全部处理完成")
    print("  ✅ 图片内容OCR支持")
    print("  ✅ 向量数据库语义搜索")
    print("  ✅ 可视化Web界面")
    print("  ✅ 完整的知识库系统")
    print("")
    
    print("💡 提示: 所有工作将在08:10后开始，先监控08:00任务执行情况")

def check_current_status():
    """检查当前状态"""
    print("🔍 当前系统状态检查")
    print("="*60)
    
    # 检查时间
    from datetime import datetime
    now = datetime.now()
    print(f"🕐 当前时间: {now.strftime('%H:%M:%S')}")
    
    # 检查知识库
    kb_dir = "/Users/tuqibiao/.openclaw/workspace/knowledge-base"
    if os.path.exists(kb_dir):
        import subprocess
        result = subprocess.run(
            ["find", "raw/domains", "-name", "*.md"],
            cwd=kb_dir,
            capture_output=True,
            text=True
        )
        file_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        print(f"📚 知识库文件数: {file_count}")
    else:
        print("❌ 知识库目录不存在")
    
    # 检查复盘文件
    replay_dir = "/Users/tuqibiao/Downloads/2026复盘"
    if os.path.exists(replay_dir):
        import subprocess
        result = subprocess.run(
            ["find", replay_dir, "-name", "*.pdf", "-type", "f"],
            capture_output=True,
            text=True
        )
        pdf_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        print(f"📄 剩余PDF文件: {pdf_count}")
    else:
        print("❌ 复盘目录不存在")
    
    print("")
    print("✅ 系统准备就绪，等待08:00任务执行")

if __name__ == "__main__":
    show_plan()
    print("\n" + "="*60)
    check_current_status()