#!/bin/bash
# Aider + Kimi 启动脚本

echo "🚀 启动 Aider + Kimi (月之暗面)"
echo "================================"

# 检查 API Key
if [ -z "$MOONSHOT_API_KEY" ]; then
    echo "❌ 错误: MOONSHOT_API_KEY 未设置"
    echo ""
    echo "请先设置环境变量:"
    echo "  export MOONSHOT_API_KEY='sk-你的key'"
    echo ""
    echo "或者添加到 ~/.zshrc:"
    echo "  echo 'export MOONSHOT_API_KEY=sk-你的key' >> ~/.zshrc"
    exit 1
fi

# 检查 aider
if command -v aider &> /dev/null; then
    AIDER_CMD="aider"
elif command -v python3 &> /dev/null; then
    # 尝试用 python -m 运行
    AIDER_CMD="python3 -m aider"
else
    echo "❌ 未找到 aider 或 python3"
    exit 1
fi

echo "✅ API Key 已配置"
echo "✅ Aider 命令: $AIDER_CMD"
echo ""

# 进入项目目录
cd /Users/tuqibiao/.openclaw/workspace/qlib_biaoge

echo "📁 工作目录: $(pwd)"
echo "🤖 模型: moonshot/kimi-k2.5"
echo ""
echo "启动中..."
echo ""

# 启动 Aider + Kimi
exec $AIDER_CMD --model moonshot/kimi-k2.5
