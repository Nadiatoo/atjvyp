#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pdfplumber
import os
import sys
from datetime import datetime

def extract_pdf_content(pdf_path):
    """提取PDF文件中的文字内容"""
    print(f"正在提取: {pdf_path}")
    
    try:
        content = []
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"  总页数: {total_pages}")
            
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    content.append(f"=== 第{i}页 ===")
                    content.append(text.strip())
                    content.append("")  # 空行分隔
                else:
                    content.append(f"=== 第{i}页 (无文字内容) ===")
                    content.append("")
        
        return "\n".join(content)
    
    except Exception as e:
        return f"提取PDF时出错: {str(e)}"

def summarize_content(content, pdf_name):
    """总结PDF内容的核心要点"""
    print(f"正在总结: {pdf_name}")
    
    # 提取关键信息
    lines = content.split('\n')
    
    # 寻找常见的关键部分
    summary = []
    summary.append(f"# {pdf_name} 核心要点总结")
    summary.append(f"提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append("")
    
    # 分析内容结构
    sections = []
    current_section = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 检测标题或关键部分
        if (line.startswith("===") or 
            "复盘" in line or 
            "总结" in line or 
            "要点" in line or
            "分析" in line or
            "操作" in line or
            "策略" in line or
            "市场" in line or
            "板块" in line or
            "个股" in line or
            len(line) < 50 and (line.endswith(":") or "：" in line)):
            
            if current_section:
                sections.append("\n".join(current_section))
                current_section = []
            
            current_section.append(f"## {line}")
        else:
            current_section.append(line)
    
    if current_section:
        sections.append("\n".join(current_section))
    
    # 如果自动检测的段落太少，尝试其他方法
    if len(sections) < 3:
        # 按段落分组
        paragraphs = []
        current_para = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_para:
                    paragraphs.append(" ".join(current_para))
                    current_para = []
            else:
                current_para.append(line)
        
        if current_para:
            paragraphs.append(" ".join(current_para))
        
        # 选择最重要的段落（较长的段落通常包含更多信息）
        paragraphs.sort(key=len, reverse=True)
        important_paragraphs = paragraphs[:5]  # 取前5个最重要的段落
        
        summary.append("## 主要内容摘要")
        for i, para in enumerate(important_paragraphs, 1):
            if len(para) > 50:  # 只包含有意义的段落
                summary.append(f"{i}. {para[:200]}..." if len(para) > 200 else f"{i}. {para}")
        summary.append("")
    
    else:
        # 使用检测到的章节
        summary.append("## 主要内容结构")
        for i, section in enumerate(sections[:8], 1):  # 最多显示8个章节
            # 提取章节标题
            lines_in_section = section.split('\n')
            if lines_in_section:
                title = lines_in_section[0].replace("## ", "")
                summary.append(f"{i}. **{title}**")
                
                # 添加章节内容的前100个字符作为摘要
                content_text = " ".join(lines_in_section[1:])[:150]
                if content_text:
                    summary.append(f"   {content_text}...")
        summary.append("")
    
    # 提取关键词
    keywords = []
    all_text = content.lower()
    
    # 常见复盘关键词
    common_keywords = [
        "上涨", "下跌", "涨幅", "跌幅", "成交量", "资金", "流入", "流出",
        "板块", "行业", "个股", "龙头", "涨停", "跌停", "反弹", "回调",
        "趋势", "支撑", "压力", "突破", "回踩", "仓位", "止损", "止盈",
        "风险", "机会", "策略", "操作", "建议", "关注", "回避", "持有"
    ]
    
    for keyword in common_keywords:
        if keyword in all_text:
            keywords.append(keyword)
    
    if keywords:
        summary.append("## 关键词")
        summary.append(", ".join(keywords[:10]))  # 最多显示10个关键词
        summary.append("")
    
    # 统计基本信息
    char_count = len(content)
    line_count = len(lines)
    non_empty_lines = len([l for l in lines if l.strip()])
    
    summary.append("## 文档统计")
    summary.append(f"- 总字符数: {char_count}")
    summary.append(f"- 总行数: {line_count}")
    summary.append(f"- 非空行数: {non_empty_lines}")
    summary.append(f"- 检测到的章节数: {len(sections)}")
    
    return "\n".join(summary)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 extract_pdf_summary.py <pdf文件1> [pdf文件2 ...]")
        sys.exit(1)
    
    pdf_files = sys.argv[1:]
    
    all_results = []
    
    for pdf_file in pdf_files:
        if not os.path.exists(pdf_file):
            print(f"错误: 文件不存在 - {pdf_file}")
            continue
        
        pdf_name = os.path.basename(pdf_file)
        print(f"\n{'='*60}")
        print(f"处理文件: {pdf_name}")
        print(f"{'='*60}")
        
        # 提取内容
        content = extract_pdf_content(pdf_file)
        
        # 保存原始内容
        output_file = f"{os.path.splitext(pdf_name)[0]}_内容.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"原始内容已保存到: {output_file}")
        
        # 生成总结
        summary = summarize_content(content, pdf_name)
        
        # 保存总结
        summary_file = f"{os.path.splitext(pdf_name)[0]}_总结.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"核心要点总结已保存到: {summary_file}")
        
        all_results.append({
            'file': pdf_name,
            'content': content,
            'summary': summary
        })
    
    # 生成综合报告
    if len(all_results) > 1:
        print(f"\n{'='*60}")
        print("生成综合报告")
        print(f"{'='*60}")
        
        combined_summary = []
        combined_summary.append("# PDF复盘文件综合报告")
        combined_summary.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        combined_summary.append(f"处理文件数: {len(all_results)}")
        combined_summary.append("")
        
        for result in all_results:
            combined_summary.append(f"## {result['file']}")
            combined_summary.append("")
            
            # 提取总结中的关键部分
            summary_lines = result['summary'].split('\n')
            for line in summary_lines:
                if line.startswith("## ") or line.startswith("- ") or line.startswith("1. "):
                    combined_summary.append(line)
            
            combined_summary.append("")
        
        combined_file = "复盘文件综合报告.md"
        with open(combined_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(combined_summary))
        
        print(f"综合报告已保存到: {combined_file}")
    
    print(f"\n{'='*60}")
    print("处理完成!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()