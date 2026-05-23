#!/usr/bin/env python3
"""
快速修复彪哥战法脚本语法错误
"""

# 读取文件
with open('/Users/tuqibiao/.openclaw/workspace/biage_premarket_eastmoney.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 查找并修复第422行附近的语法错误
fixed = False
for i in range(len(lines)):
    if 'return {"success": False, "error": "数据' in lines[i] and '"}' not in lines[i]:
        print(f"🔧 修复第{i+1}行语法错误")
        print(f"修复前: {lines[i].strip()}")
        
        # 修复这一行
        lines[i] = '            return {"success": False, "error": "数据获取失败"}\n'
        fixed = True
        
        print(f"修复后: {lines[i].strip()}")
        break

if fixed:
    # 写入修复后的文件
    with open('/Users/tuqibiao/.openclaw/workspace/biage_premarket_eastmoney.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ 语法错误修复完成")
    
    # 验证修复
    with open('/Users/tuqibiao/.openclaw/workspace/biage_premarket_eastmoney.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if '"数据获取失败"}' in content:
            print("✅ 验证通过：字符串已正确闭合")
        else:
            print("⚠️ 验证失败：可能还有其他语法错误")
else:
    print("❌ 未找到需要修复的行")
    print("可能错误位置有变化，让我检查文件内容...")
    
    # 显示文件最后20行
    print("\n📋 文件最后20行：")
    for j in range(max(0, len(lines)-20), len(lines)):
        print(f"{j+1:4d}: {lines[j].rstrip()}")