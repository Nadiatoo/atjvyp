#!/usr/bin/env python3
"""
Aider + Kimi 启动器
如果 aider 命令行安装失败，用 Python 直接调用
"""

import os
import sys
import subprocess
from pathlib import Path

def check_api_key():
    """检查 API Key"""
    api_key = os.environ.get('MOONSHOT_API_KEY')
    if not api_key:
        print("❌ 错误: MOONSHOT_API_KEY 未设置")
        print()
        print("请先设置环境变量:")
        print("  export MOONSHOT_API_KEY='sk-你的key'")
        print()
        print("你的 API Key 已在 ~/.zshrc 中:")
        try:
            with open(os.path.expanduser('~/.zshrc')) as f:
                for line in f:
                    if 'MOONSHOT_API_KEY' in line and 'export' in line:
                        print(f"  {line.strip()}")
        except:
            pass
        return False
    
    # 隐藏显示
    masked = api_key[:10] + "..." + api_key[-4:]
    print(f"✅ API Key 已配置: {masked}")
    return True

def start_aider():
    """启动 Aider"""
    
    if not check_api_key():
        sys.exit(1)
    
    # 项目目录
    project_dir = Path("/Users/tuqibiao/.openclaw/workspace/qlib_biaoge")
    project_dir.mkdir(exist_ok=True)
    
    print(f"📁 工作目录: {project_dir}")
    print("🤖 模型: moonshot/kimi-k2.5")
    print()
    
    # 尝试启动 aider
    try:
        # 先尝试直接运行
        result = subprocess.run(['aider', '--version'], 
                              capture_output=True, text=True, timeout=5)
        aider_cmd = ['aider']
        print("✅ 使用系统 aider")
    except:
        # 尝试用 python -m
        try:
            result = subprocess.run([sys.executable, '-m', 'aider', '--version'],
                                  capture_output=True, text=True, timeout=5)
            aider_cmd = [sys.executable, '-m', 'aider']
            print("✅ 使用 Python module aider")
        except:
            print("❌ 未找到 aider，尝试安装...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 
                          'aider-chat', '--break-system-packages', '-q'])
            aider_cmd = [sys.executable, '-m', 'aider']
    
    print()
    print("🚀 启动 Aider + Kimi...")
    print("=" * 60)
    print()
    print("💡 使用提示:")
    print("  - 直接输入需求，如: 帮我优化四季判断模型")
    print("  - 按 Ctrl+C 退出")
    print("  - 输入 /help 查看所有命令")
    print()
    
    # 启动
    os.chdir(project_dir)
    subprocess.run(aider_cmd + ['--model', 'moonshot/kimi-k2.5'])

if __name__ == '__main__':
    start_aider()
