#!/bin/bash
# iFinD API环境变量设置脚本
# 安全提示：请勿在版本控制中提交此文件

echo "🔐 iFinD API环境变量设置"
echo "=========================="

# 设置环境变量（临时，仅当前会话有效）
read -p "请输入iFinD Refresh Token: " refresh_token
read -p "请输入iFinD Access Token（如无可留空）: " access_token

# 设置环境变量
export IFIND_REFRESH_TOKEN="$refresh_token"
export IFIND_ACCESS_TOKEN="$access_token"

echo ""
echo "✅ 环境变量已设置（仅当前会话有效）"
echo ""
echo "永久设置方法："
echo "1. 将以下内容添加到 ~/.zshrc 或 ~/.bashrc:"
echo "   export IFIND_REFRESH_TOKEN='your_refresh_token'"
echo "   export IFIND_ACCESS_TOKEN='your_access_token'"
echo ""
echo "2. 然后执行: source ~/.zshrc"
echo ""
echo "测试连接: python3 /Users/tuqibiao/.openclaw/workspace/test_ifind_connection.py"
echo "注意：Token会自动从环境变量读取"