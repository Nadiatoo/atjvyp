#!/usr/bin/env python3
"""
复盘内容解析器
专门解析老涂的复盘PDF和图片内容
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pdfplumber
from PIL import Image
import pytesseract
import markdownify

class ReplayParser:
    """复盘内容解析器"""
    
    def __init__(self, config_path: str = None):
        """初始化解析器"""
        self.section_patterns = {
            'market_overview': [r'市场概况', r'指数分析', r'大盘走势'],
            'technical_analysis': [r'技术面分析', r'技术分析', r'图表分析'],
            'emotion_analysis': [r'情绪分析', r'市场情绪', r'投资者心理'],
            'fund_flow': [r'资金流向', r'资金分析', r'北向资金'],
            'risk_warning': [r'风险提示', r'风险分析', r'注意事项'],
            'strategy': [r'操作策略', r'明日策略', r'投资建议'],
            'macro_analysis': [r'宏观分析', r'宏观环境', r'政策分析'],
            'sector_analysis': [r'板块分析', r'行业分析', r'题材分析']
        }
        
        # 从配置加载（如果存在）
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
    
    def load_config(self, config_path: str):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'section_patterns' in config:
                    self.section_patterns.update(config['section_patterns'])
        except Exception as e:
            print(f"⚠️ 配置加载失败: {e}")
    
    def parse_pdf(self, pdf_path: str) -> Dict:
        """
        解析PDF复盘文件
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            结构化数据字典
        """
        print(f"📄 开始解析PDF: {pdf_path}")
        
        result = {
            'file_path': pdf_path,
            'file_name': os.path.basename(pdf_path),
            'file_type': 'pdf',
            'sections': {},
            'metadata': self._extract_metadata(pdf_path),
            'raw_text': '',
            'chunks': []
        }
        
        try:
            # 使用pdfplumber提取文本
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                page_texts = []
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n\n"
                        page_texts.append({
                            'page': page_num,
                            'text': page_text
                        })
                
                result['raw_text'] = full_text
                result['page_count'] = len(pdf.pages)
                result['pages'] = page_texts
                
                # 提取表格数据
                tables = []
                for page_num, page in enumerate(pdf.pages, 1):
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table_num, table in enumerate(page_tables, 1):
                            tables.append({
                                'page': page_num,
                                'table_num': table_num,
                                'data': table
                            })
                
                result['tables'] = tables
            
            # 结构化解析
            result['sections'] = self._structure_text(full_text)
            
            # 分块处理（用于向量化）
            result['chunks'] = self._chunk_text(full_text)
            
            print(f"✅ PDF解析完成: {len(full_text)}字符, {len(result['sections'])}个章节")
            
        except Exception as e:
            print(f"❌ PDF解析失败: {e}")
            result['error'] = str(e)
        
        return result
    
    def parse_image(self, image_path: str) -> Dict:
        """
        解析图片内容（思维导图、图表、手写笔记等）
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            结构化数据字典
        """
        print(f"🖼️ 开始解析图片: {image_path}")
        
        result = {
            'file_path': image_path,
            'file_name': os.path.basename(image_path),
            'file_type': 'image',
            'content_type': self._detect_image_type(image_path),
            'metadata': self._extract_metadata(image_path),
            'ocr_text': '',
            'analysis': {}
        }
        
        try:
            # 1. 基础OCR提取文字
            ocr_text = self._extract_ocr_text(image_path)
            result['ocr_text'] = ocr_text
            
            # 2. 根据图片类型进行专门分析
            content_type = result['content_type']
            
            if content_type == 'text_dense':
                # 文字密集图片（如截图）
                result['analysis']['text_analysis'] = self._analyze_dense_text(ocr_text)
            
            elif content_type == 'chart':
                # 图表图片
                result['analysis']['chart_analysis'] = self._analyze_chart(image_path)
            
            elif content_type == 'mindmap':
                # 思维导图
                result['analysis']['mindmap_analysis'] = self._analyze_mindmap(image_path)
            
            elif content_type == 'handwritten':
                # 手写笔记
                result['analysis']['handwriting_analysis'] = self._analyze_handwriting(image_path)
            
            # 3. 转换为Markdown格式
            result['markdown'] = self._image_to_markdown(result)
            
            print(f"✅ 图片解析完成: {content_type}, {len(ocr_text)}字符")
            
        except Exception as e:
            print(f"❌ 图片解析失败: {e}")
            result['error'] = str(e)
        
        return result
    
    def _extract_metadata(self, file_path: str) -> Dict:
        """提取文件元数据"""
        file_stat = os.stat(file_path)
        file_name = os.path.basename(file_path)
        
        metadata = {
            'file_size': file_stat.st_size,
            'created_time': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
            'modified_time': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            'file_extension': os.path.splitext(file_name)[1].lower()
        }
        
        # 从文件名提取日期信息
        date_match = re.search(r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})', file_name)
        if date_match:
            metadata['inferred_date'] = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
        
        # 从文件名提取主题信息
        if '复盘' in file_name:
            metadata['content_type'] = 'replay'
        elif '框架' in file_name or '模板' in file_name:
            metadata['content_type'] = 'framework'
        elif '思维' in file_name or '思考' in file_name:
            metadata['content_type'] = 'thinking'
        
        return metadata
    
    def _structure_text(self, text: str) -> Dict:
        """将文本结构化为章节"""
        sections = {}
        current_section = 'unknown'
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是章节标题
            section_found = False
            for section_name, patterns in self.section_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line):
                        # 保存上一章节内容
                        if current_content:
                            sections[current_section] = '\n'.join(current_content)
                        
                        # 开始新章节
                        current_section = section_name
                        current_content = [line]
                        section_found = True
                        break
                
                if section_found:
                    break
            
            if not section_found:
                current_content.append(line)
        
        # 保存最后一章节
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
        """将文本分块（用于向量化）"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append({
                'chunk_id': len(chunks),
                'text': chunk_text,
                'word_count': len(chunk_words),
                'start_word': i,
                'end_word': i + len(chunk_words)
            })
        
        return chunks
    
    def _detect_image_type(self, image_path: str) -> str:
        """检测图片类型"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                aspect_ratio = width / height
                
                # 根据宽高比和内容初步判断
                if 0.8 <= aspect_ratio <= 1.2:
                    # 接近正方形，可能是思维导图或图表
                    return 'mindmap'
                elif aspect_ratio > 1.5:
                    # 宽屏，可能是截图或文档
                    return 'text_dense'
                else:
                    # 其他情况
                    return 'general'
        except:
            return 'unknown'
    
    def _extract_ocr_text(self, image_path: str) -> str:
        """使用OCR提取图片文字"""
        try:
            # 检查是否安装了tesseract
            pytesseract.get_tesseract_version()
            
            with Image.open(image_path) as img:
                # 预处理图片（提高OCR准确率）
                img = img.convert('L')  # 转为灰度
                
                # 提取文字
                text = pytesseract.image_to_string(img, lang='chi_sim+eng')
                return text.strip()
        
        except Exception as e:
            print(f"⚠️ OCR提取失败: {e}")
            return ""
    
    def _analyze_dense_text(self, text: str) -> Dict:
        """分析密集文字内容"""
        lines = text.split('\n')
        
        analysis = {
            'line_count': len(lines),
            'non_empty_lines': len([l for l in lines if l.strip()]),
            'estimated_topics': [],
            'key_phrases': []
        }
        
        # 提取关键词（简单实现）
        words = text.split()
        word_freq = {}
        for word in words:
            if len(word) > 1:  # 忽略单字
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 取频率最高的10个词
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        analysis['key_phrases'] = [word for word, freq in sorted_words[:10]]
        
        return analysis
    
    def _analyze_chart(self, image_path: str) -> Dict:
        """分析图表图片（基础实现）"""
        # 这里可以集成更复杂的图表识别算法
        # 目前返回基础信息
        return {
            'type': 'chart',
            'analysis_method': 'basic',
            'notes': '需要更复杂的图表识别算法'
        }
    
    def _analyze_mindmap(self, image_path: str) -> Dict:
        """分析思维导图（基础实现）"""
        return {
            'type': 'mindmap',
            'analysis_method': 'basic',
            'notes': '需要专门的思维导图识别算法'
        }
    
    def _analyze_handwriting(self, image_path: str) -> Dict:
        """分析手写笔记（基础实现）"""
        return {
            'type': 'handwritten',
            'analysis_method': 'basic',
            'notes': '手写识别需要专门模型'
        }
    
    def _image_to_markdown(self, image_data: Dict) -> str:
        """将图片分析结果转换为Markdown格式"""
        md_lines = []
        
        # 标题
        md_lines.append(f"# 图片分析: {image_data['file_name']}")
        md_lines.append("")
        
        # 元数据
        md_lines.append("## 元数据")
        md_lines.append(f"- **文件类型**: {image_data['file_type']}")
        md_lines.append(f"- **内容类型**: {image_data['content_type']}")
        md_lines.append(f"- **文件大小**: {image_data['metadata']['file_size']} bytes")
        md_lines.append("")
        
        # OCR文本
        if image_data['ocr_text']:
            md_lines.append("## OCR提取文本")
            md_lines.append("```")
            md_lines.append(image_data['ocr_text'][:500] + ("..." if len(image_data['ocr_text']) > 500 else ""))
            md_lines.append("```")
            md_lines.append("")
        
        # 分析结果
        if image_data['analysis']:
            md_lines.append("## 内容分析")
            for analysis_type, analysis_data in image_data['analysis'].items():
                md_lines.append(f"### {analysis_type.replace('_', ' ').title()}")
                for key, value in analysis_data.items():
                    if isinstance(value, list):
                        md_lines.append(f"- **{key}**: {', '.join(value[:5])}" + ("..." if len(value) > 5 else ""))
                    else:
                        md_lines.append(f"- **{key}**: {value}")
                md_lines.append("")
        
        # 原始文件信息
        md_lines.append("## 原始文件")
        md_lines.append(f"- **路径**: `{image_data['file_path']}`")
        md_lines.append(f"- **创建时间**: {image_data['metadata']['created_time']}")
        md_lines.append("")
        
        return '\n'.join(md_lines)
    
    def save_to_markdown(self, parsed_data: Dict, output_dir: str) -> str:
        """
        将解析结果保存为Markdown文件
        
        Args:
            parsed_data: 解析后的数据
            output_dir: 输出目录
            
        Returns:
            保存的文件路径
        """
        file_name = os.path.basename(parsed_data['file_path'])
        base_name = os.path.splitext(file_name)[0]
        output_path = os.path.join(output_dir, f"{base_name}.md")
        
        md_lines = []
        
        # 标题
        md_lines.append(f"# {base_name}")
        md_lines.append("")
        
        # 文件信息
        md_lines.append("## 文件信息")
        md_lines.append(f"- **原始文件**: `{parsed_data['file_path']}`")
        md_lines.append(f"- **文件类型**: {parsed_data['file_type']}")
        md_lines.append(f"- **解析时间**: {datetime.now().isoformat()}")
        md_lines.append("")
        
        # 元数据
        if 'metadata' in parsed_data:
            md_lines.append("## 元数据")
            for key, value in parsed_data['metadata'].items():
                md_lines.append(f"- **{key}**: {value}")
            md_lines.append("")
        
        # 章节内容（PDF特有）
        if 'sections' in parsed_data and parsed_data['sections']:
            md_lines.append("## 内容结构")
            for section_name, section_content in parsed_data['sections'].items():
                md_lines.append(f"### {section_name}")
                md_lines.append(section_content[:1000] + ("..." if len(section_content) > 1000 else ""))
                md_lines.append("")
        
        # OCR文本（图片特有）
        if 'ocr_text' in parsed_data and parsed_data['ocr_text']:
            md_lines.append("## OCR提取文本")
            md_lines.append("```")
            md_lines.append(parsed_data['ocr_text'])
            md_lines.append("```")
            md_lines.append("")
        
        # 原始文本（完整）
        if 'raw_text' in parsed_data and parsed_data['raw_text']:
            md_lines.append("## 完整文本")
            md_lines.append("<details>")
            md_lines.append("<summary>点击展开完整文本</summary>")
            md_lines.append("")
            md_lines.append("```")
            md_lines.append(parsed_data['raw_text'])
            md_lines.append("```")
            md_lines.append("")
            md_lines.append("</details>")
            md_lines.append("")
        
        # 写入文件
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))
        
        print(f"💾 已保存到: {output_path}")
        return output_path
    
    def batch_process(self, input_dir: str, output_dir: str, file_pattern: str = "*.pdf"):
        """
        批量处理文件
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            file_pattern: 文件匹配模式
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        # 确保输出目录存在
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 查找文件
        files = list(input_path.glob(file_pattern))
        print(f"🔍 找到 {len(files)} 个文件")
        
        results = []
        for file_path in files:
            print(f"\n📋 处理文件: {file_path.name}")
            
            if file_path.suffix.lower() == '.pdf':
                parsed_data = self.parse_pdf(str(file_path))
            elif file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                parsed_data = self.parse_image(str(file_path))
            else:
                print(f"⚠️ 跳过不支持的文件类型: {file_path.suffix}")
                continue
            
            # 保存结果
