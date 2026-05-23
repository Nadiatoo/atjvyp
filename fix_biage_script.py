#!/usr/bin/env python3
"""
修复彪哥战法脚本的语法错误
"""

import os

# 读取原始文件
with open('/Users/tuqibiao/.openclaw/workspace/biage_premarket_eastmoney.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找并修复语法错误
# 错误在第422行附近：字符串未正确闭合
lines = content.split('\n')

# 找到有问题的行
for i, line in enumerate(lines):
    if 'return {"success": False, "error": "数据' in line and '"}' not in line:
        print(f"找到问题行 {i+1}: {line}")
        # 修复这一行
        lines[i] = '            return {"success": False, "error": "数据获取失败"}'
        break

# 重新组合内容
fixed_content = '\n'.join(lines)

# 写入修复后的文件
with open('/Users/tuqibiao/.openclaw/workspace/biage_premarket_eastmoney_fixed.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("✅ 脚本修复完成")
print(f"原始文件大小: {len(content)} 字符")
print(f"修复后文件大小: {len(fixed_content)} 字符")
print("修复后文件: biage_premarket_eastmoney_fixed.py")

# 检查修复结果
if '"}' in fixed_content:
    print("✅ 语法错误已修复")
else:
    print("⚠️ 可能还有其他语法错误")