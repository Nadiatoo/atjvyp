#!/bin/bash
# Aider + Kimi 完整安装脚本
# 如果 pip 安装失败，用二进制方式

echo "🚀 Aider + Kimi 安装器"
echo "======================"

# 检查 API Key
if [ -z "$MOONSHOT_API_KEY" ]; then
    export MOONSHOT_API_KEY="sk-t2zL1sYnEI50wPCWJL9fbvQvwk0IQMJHv6XMDU7k1UaiFjMO"
    echo "✅ API Key 已设置"
fi

# 方法1: 尝试用 brew 安装
echo ""
echo "📦 方法1: 尝试 Homebrew 安装..."
if command -v brew &> /dev/null; then
    brew install aider 2>&1 | tail -5
    if command -v aider &> /dev/null; then
        echo "✅ Brew 安装成功"
        exit 0
    fi
fi

# 方法2: 下载预编译二进制
echo ""
echo "📦 方法2: 下载预编译二进制..."
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    URL="https://github.com/paul-gauthier/aider/releases/download/v0.72.3/aider-macos-arm64"
else
    URL="https://github.com/paul-gauthier/aider/releases/download/v0.72.3/aider-macos-x86_64"
fi

cd /usr/local/bin
curl -L -o aider "$URL" 2>&1 | tail -3
chmod +x aider 2>&1

if command -v aider &> /dev/null; then
    echo "✅ 二进制安装成功"
    aider --version
else
    echo "⚠️ 二进制安装失败，尝试方法3..."
fi

# 方法3: Python 虚拟环境
echo ""
echo "📦 方法3: Python 虚拟环境安装..."
python3 -m venv ~/.aider-venv
source ~/.aider-venv/bin/activate
pip install aider-chat 2>&1 | tail -5

if command -v aider &> /dev/null; then
    echo "✅ 虚拟环境安装成功"
    echo "alias aider='~/.aider-venv/bin/aider'" >> ~/.zshrc
    echo "请运行: source ~/.zshrc"
else
    echo "❌ 所有方法都失败了"
fi

echo ""
echo "======================"
echo "安装完成！"
