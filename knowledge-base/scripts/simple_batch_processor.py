#!/usr/bin/env python3
"""
简化版批量处理器 - 先处理PDF文件，不依赖向量数据库
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from replay_parser import ReplayParser

class SimpleBatchProcessor:
    """简化版批量处理器"""
    
    def __init__(self, config_path: str = None):
        """初始化处理器"""
        self.parser = ReplayParser(config_path)
        
        # 配置
        self.config = {
            'input_dirs': [],
            'output_dir': 'raw/processed/replays',
            'knowledge_base_dir': 'raw/domains',
            'log_file': 'logs/simple_batch_process.log',
            'max_workers': 2,
            'chunk_size': 500
        }
        
        # 加载配置
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
    
    def load_config(self, config_path: str):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                self.config.update(user_config)
        except Exception as e:
            print(f"⚠️ 配置加载失败: {e}")
    
    def discover_files(self, input_dirs: List[str]) -> List[Dict]:
        """
        发现输入目录中的所有PDF文件
        
        Args:
            input_dirs: 输入目录列表
            
        Returns:
            文件信息列表
        """
        files = []
        
        for input_dir in input_dirs:
            input_path = Path(input_dir)
            if not input_path.exists():
                print(f"⚠️ 目录不存在: {input_dir}")
                continue
            
            # 查找PDF文件
            pdf_files = list(input_path.glob("**/*.pdf"))
            for pdf_file in pdf_files:
                files.append({
                    'path': str(pdf_file),
                    'type': 'pdf',
                    'size': pdf_file.stat().st_size,
                    'modified': pdf_file.stat().st_mtime,
                    'filename': pdf_file.name
                })
        
        # 按修改时间排序（最新的优先）
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        print(f"🔍 发现 {len(files)} 个PDF文件")
        return files
    
    def categorize_file(self, file_info: Dict) -> Dict:
        """
        根据文件名分类文件
        
        Args:
            file_info: 文件信息
            
        Returns:
            分类信息
        """
        file_name = file_info['filename'].lower()
        
        category = {
            'domain': 'unknown',
            'subdomain': 'unknown',
            'priority': 'medium',
            'tags': []
        }
        
        # 根据文件名判断领域
        if '复盘' in file_name:
            category['domain'] = 'trading'
            category['subdomain'] = 'market_analysis'
            category['tags'].append('复盘')
            
            # 判断复盘类型
            if '每日' in file_name or '日报' in file_name:
                category['subdomain'] = 'daily_replay'
                category['tags'].append('每日复盘')
            elif '周' in file_name:
                category['subdomain'] = 'weekly_replay'
                category['tags'].append('周复盘')
            elif '月' in file_name:
                category['subdomain'] = 'monthly_replay'
                category['tags'].append('月复盘')
            elif '深度' in file_name:
                category['subdomain'] = 'deep_analysis'
                category['tags'].append('深度分析')
        
        elif '框架' in file_name or '模板' in file_name:
            category['domain'] = 'methodology'
            category['subdomain'] = 'frameworks'
            category['tags'].append('框架')
        
        elif '思维' in file_name or '思考' in file_name:
            category['domain'] = 'personal'
            category['subdomain'] = 'thinking'
            category['tags'].append('思考')
        
        elif '策略' in file_name:
            category['domain'] = 'trading'
            category['subdomain'] = 'strategies'
            category['tags'].append('策略')
        
        elif '风险' in file_name:
            category['domain'] = 'trading'
            category['subdomain'] = 'risk_management'
            category['tags'].append('风险管理')
        
        # 判断优先级
        if '重要' in file_name or '核心' in file_name:
            category['priority'] = 'high'
        elif '草稿' in file_name or '临时' in file_name:
            category['priority'] = 'low'
        
        # 从文件名提取日期
        import re
        date_match = re.search(r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})', file_name)
        if date_match:
            category['date'] = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
            category['tags'].append(category['date'])
        
        return category
    
    def process_file(self, file_info: Dict, output_base: str) -> Optional[Dict]:
        """
        处理单个PDF文件
        
        Args:
            file_info: 文件信息
            output_base: 输出基础目录
            
        Returns:
            处理结果
        """
        file_path = file_info['path']
        
        try:
            # 分类文件
            category = self.categorize_file(file_info)
            
            # 创建输出目录
            output_dir = os.path.join(
                output_base,
                category['domain'],
                category['subdomain']
            )
            
            # 解析PDF文件
            print(f"📄 解析PDF: {file_info['filename']}")
            parsed_data = self.parser.parse_pdf(file_path)
            
            if 'error' in parsed_data:
                print(f"❌ 解析失败: {parsed_data['error']}")
                return None
            
            # 添加分类信息
            parsed_data['category'] = category
            
            # 保存为Markdown
            md_file = self.parser.save_to_markdown(parsed_data, output_dir)
            
            # 准备结果数据
            result = {
                'source_file': file_path,
                'processed_file': md_file,
                'category': category,
                'title': os.path.splitext(file_info['filename'])[0],
                'content': self._extract_main_content(parsed_data),
                'metadata': parsed_data.get('metadata', {}),
                'chunks': parsed_data.get('chunks', []),
                'page_count': parsed_data.get('page_count', 0),
                'text_length': len(parsed_data.get('raw_text', '')),
                'processed_time': datetime.now().isoformat(),
                'success': True
            }
            
            print(f"✅ 处理完成: {file_info['filename']} → {md_file}")
            return result
            
        except Exception as e:
            print(f"❌ 处理失败 {file_info['filename']}: {e}")
            import traceback
            traceback.print_exc()
            return {
                'source_file': file_path,
                'error': str(e),
                'success': False
            }
    
    def _extract_main_content(self, parsed_data: Dict) -> str:
        """提取主要内容"""
        # 优先使用结构化章节
        if 'sections' in parsed_data and parsed_data['sections']:
            # 合并所有章节
            sections = []
            for section_name, content in parsed_data['sections'].items():
                sections.append(f"## {section_name}\n{content}")
            return '\n\n'.join(sections)
        
        # 使用原始文本
        elif 'raw_text' in parsed_data and parsed_data['raw_text']:
            return parsed_data['raw_text']
        
        return ""
    
    def import_to_knowledge_base(self, result: Dict, kb_dir: str):
        """
        导入到知识库（文件系统）
        
        Args:
            result: 处理结果
            kb_dir: 知识库目录
        """
        try:
            domain = result['category']['domain']
            subdomain = result['category']['subdomain']
            
            kb_subdir = os.path.join(kb_dir, domain, subdomain)
            os.makedirs(kb_subdir, exist_ok=True)
            
            # 生成文件名
            title = result['title']
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            kb_file = os.path.join(kb_subdir, f"{safe_title}.md")
            
            # 写入知识库文件
            with open(kb_file, 'w', encoding='utf-8') as f:
                # 元数据头
                f.write("---\n")
                f.write(f"title: {title}\n")
                f.write(f"source: {result['source_file']}\n")
                f.write(f"category: {domain}/{subdomain}\n")
                f.write(f"tags: {', '.join(result['category']['tags'])}\n")
                f.write(f"date: {result['metadata'].get('inferred_date', '未知')}\n")
                f.write(f"processed: {result['processed_time']}\n")
                f.write(f"pages: {result.get('page_count', 0)}\n")
                f.write(f"text_length: {result.get('text_length', 0)}\n")
                f.write("---\n\n")
                
                # 内容
                f.write(result['content'])
            
            print(f"📚 导入知识库: {kb_file}")
            return kb_file
            
        except Exception as e:
            print(f"❌ 知识库导入失败: {e}")
            return None
    
    def run_batch(self, input_dirs: List[str], output_dir: str = None, 
                  kb_dir: str = None, limit: int = 5):
        """
        运行批量处理
        
        Args:
            input_dirs: 输入目录列表
            output_dir: 输出目录（可选）
            kb_dir: 知识库目录（可选）
            limit: 限制处理文件数量（可选）
        """
        print("🚀 开始简化版批量处理")
        print(f"输入目录: {input_dirs}")
        
        # 使用配置或参数
        if output_dir is None:
            output_dir = self.config['output_dir']
        if kb_dir is None:
            kb_dir = self.config['knowledge_base_dir']
        
        # 发现文件
        files = self.discover_files(input_dirs)
        if not files:
            print("⚠️ 未找到PDF文件")
            return
        
        # 限制文件数量
        if limit and limit > 0:
            files = files[:limit]
            print(f"限制处理前 {limit} 个文件")
        
        # 处理统计
        stats = {
            'total': len(files),
            'success': 0,
            'failed': 0,
            'processed_files': [],
            'kb_files': []
        }
        
        # 批量处理
        start_time = time.time()
        
        for i, file_info in enumerate(files, 1):
            print(f"\n📋 处理进度: {i}/{len(files)} - {file_info['filename']}")
            
            # 处理文件
            result = self.process_file(file_info, output_dir)
            
            if result and result.get('success', False):
                # 导入到知识库
                kb_file = self.import_to_knowledge_base(result, kb_dir)
                
                if kb_file:
                    stats['success'] += 1
                    stats['processed_files'].append(file_info['path'])
                    stats['kb_files'].append(kb_file)
                else:
                    stats['failed'] += 1
            else:
                stats['failed'] += 1
        
        # 计算耗时
        elapsed_time = time.time() - start_time
        
        # 生成报告
        report = self._generate_report(stats, elapsed_time)
        
        # 保存报告
        report_file = os.path.join(output_dir, f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 批量处理完成")
        print(f"报告已保存: {report_file}")
        
        return report
    
    def _generate_report(self, stats: Dict, elapsed_time: float) -> Dict:
        """生成处理报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'elapsed_seconds': round(elapsed_time, 2),
            'stats': stats,
            'summary': {
                'total_files': stats['total'],
                'success_rate': round(stats['success'] / stats['total'] * 100, 1) if stats['total'] > 0 else 0,
                'files_per_second': round(stats['total'] / elapsed_time, 2) if elapsed_time > 0 else 0,
                'average_time_per_file': round(elapsed_time / stats['total'], 2) if stats['total'] > 0 else 0
            }
        }
        
        return report

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='简化版批量处理复盘内容')
    parser.add_argument('input_dirs', nargs='+', help='输入目录（可多个）')
    parser.add_argument('--output-dir', '-o', help='输出目录')
    parser.add_argument('--kb-dir', '-k', help='知识库目录')
    parser.add_argument('--limit', '-l', type=int, default=5, help='限制处理文件数量（默认: 5）')
    parser.add_argument('--config', '-c', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 创建处理器
    processor = SimpleBatchProcessor(args.config)
    
    # 运行批量处理
    report = processor.run_batch(
        input_dirs=args.input_dirs,
        output_dir=args.output_dir,
        kb_dir=args.kb_dir,
        limit=args.limit
    )
    
    # 打印摘要
    if report:
        print("\n" + "="*50)
        print("批量处理摘要")
        print("="*50)
        print(f"总文件数: {report['stats']['total']}")
        print(f"成功: {report['stats']['success']}")
        print(f"失败: {report['stats']['failed']}")
        print(f"成功率: {report['summary']['success_rate']}%")
        print(f"总耗时: {report['elapsed_seconds']}秒")
        print(f"平均每个文件: {report['summary']['average_time_per_file']}秒")

if __name__ == "__main__":
    main()