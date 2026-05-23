#!/bin/bash
# 临时测试iFinD连接

echo "🔐 设置iFinD环境变量..."
export IFIND_REFRESH_TOKEN="eyJzaWduX3RpbWUiOiIyMDI2LTA0LTIwIDE3OjQ2OjU2In0=.eyJ1aWQiOiI4NjI5MDAwNzMiLCJ1c2VyIjp7InJlZnJlc2hUb2tlbkV4cGlyZWRUaW1lIjoiMjAyNi0wNS0yMCAxNjozNzowMyIsInVzZXJJZCI6Ijg2MjkwMDA3MyJ9fQ==.3CF5C8F32F6F9B854BFFAF1DD4771664AE4EFBECB9EB6AA4B06EBBCAFC7B69D6"
export IFIND_ACCESS_TOKEN="a4d2c1699a51c951fffda4be589fe33809407b77.signs_ODYyOTAwMDcz"

echo "🚀 开始测试iFinD API连接..."
python3 /Users/tuqibiao/.openclaw/workspace/test_ifind_connection.py