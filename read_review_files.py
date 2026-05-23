#!/usr/bin/env python3
"""
读取复盘文件内容脚本
读取2026年4月15日到当前日期的复盘文件
"""

import os
import subprocess
from datetime import datetime

def pdf_to_text(pdf_path):
    """将PDF文件转换为文本"""
    try:
        # 使用pdftotext工具
        result = subprocess.run(
            ['pdftotext', pdf_path, '-'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"警告: pdftotext失败, 返回码: {result.returncode}")
            print(f"错误输出: {result.stderr}")
            return None
    except FileNotFoundError:
        print("错误: pdftotext工具未安装")
        return None
    except Exception as e:
        print(f"错误: 读取PDF文件时出错: {e}")
        return None

def main():
    # 复盘文件夹路径
    review_dir = "/Users/tuqibiao/Downloads/2026复盘"
    
    # 需要读取的文件列表 (4月15日到4月21日)
    target_files = [
        "4.15复盘.pdf",
        "4.16复盘.pdf", 
        "4.19周末复盘.pdf",
        "4.20复盘.pdf",
        "4.21复盘.pdf"
    ]
    
    print("=" * 60)
    print("复盘文件内容读取汇总 (2026年4月15日-4月21日)")
    print("=" * 60)
    
    all_content = []
    
    for filename in target_files:
        filepath = os.path.join(review_dir, filename)
        
        print(f"\n📄 正在读取: {filename}")
        print("-" * 40)
        
        if not os.path.exists(filepath):
            print(f"❌ 文件不存在: {filepath}")
            continue
            
        # 获取文件大小
        file_size = os.path.getsize(filepath)
        print(f"文件大小: {file_size:,} 字节")
        
        # 读取PDF内容
        text_content = pdf_to_text(filepath)
        
        if text_content:
            # 统计基本信息
            lines = text_content.strip().split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            print(f"总行数: {len(lines)}")
            print(f"非空行数: {len(non_empty_lines)}")
            print(f"总字符数: {len(text_content)}")
            
            # 提取前5行作为摘要
            print("\n📝 内容摘要:")
            print("-" * 20)
            for i, line in enumerate(non_empty_lines[:10]):
                if line.strip():
                    print(f"{i+1}. {line.strip()[:100]}{'...' if len(line.strip()) > 100 else ''}")
            
            # 保存内容
            file_info = {
                'filename': filename,
                'content': text_content,
                'line_count': len(lines),
                'char_count': len(text_content)
            }
            all_content.append(file_info)
        else:
            print("❌ 无法读取文件内容")
    
    # 生成汇总报告
    print("\n" + "=" * 60)
    print("📊 汇总报告")
    print("=" * 60)
    
    total_lines = sum(item['line_count'] for item in all_content)
    total_chars = sum(item['char_count'] for item in all_content)
    
    print(f"读取文件数量: {len(all_content)}/{len(target_files)}")
    print(f"总行数: {total_lines:,}")
    print(f"总字符数: {total_chars:,}")
    
    # 按日期排序
    sorted_content = sorted(all_content, key=lambda x: x['filename'])
    
    print("\n📅 文件列表:")
    for item in sorted_content:
        print(f"  • {item['filename']}: {item['line_count']:,} 行, {item['char_count']:,} 字符")
    
    # 保存完整内容到文件
    output_file = "/Users/tuqibiao/.openclaw/workspace/review_summary_2026_04_15_21.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 复盘文件内容汇总 (2026年4月15日-4月21日)\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"读取文件数: {len(all_content)}\n")
        f.write(f"总行数: {total_lines:,}\n")
        f.write(f"总字符数: {total_chars:,}\n\n")
        
        for item in sorted_content:
            f.write(f"## {item['filename']}\n\n")
            f.write(f"行数: {item['line_count']:,} | 字符数: {item['char_count']:,}\n\n")
            f.write("```\n")
            # 只保存前500行以避免文件过大
            lines = item['content'].split('\n')
            for line in lines[:500]:
                f.write(line + '\n')
            if len(lines) > 500:
                f.write(f"\n... 省略 {len(lines)-500} 行 ...\n")
            f.write("```\n\n")
    
    print(f"\n✅ 完整内容已保存到: {output_file}")
    
    # 显示关键主题分析
    print("\n🔍 关键主题分析:")
    print("-" * 40)
    
    # 提取常见关键词
    keywords = [
        "指数", "情绪", "板块", "涨停", "跌停",
        "资金", "机构", "技术", "压力", "风险"
    ]
    
    for keyword in keywords:
        count = sum(item['content'].lower().count(keyword.lower()) for item in all_content)
        if count > 0:
            print(f"  {keyword}: {count} 次提到")

if __name__ == "__main__":
    main()