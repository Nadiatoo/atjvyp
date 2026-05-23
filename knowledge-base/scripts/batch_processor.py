#!/usr/bin/env python3
"""
批量处理工具 - 将复盘内容导入知识库
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import argparse

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from replay_parser import ReplayParser
from sync_manager import SyncManager

class BatchProcessor:
    """批量处理器"""
    
    def __init__(self, config_path: str = None):
        """初始化处理器"""
        self.parser = ReplayParser(config_path)
        self.sync_manager = SyncManager()
        
        # 配置
        self.config = {
            'input_dirs': [],
            'output_dir': 'raw/processed',
            'knowledge_base_dir': 'raw/domains',
            'log_file': 'logs/batch_process.log',
            'max_workers': 4,
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
    
    def setup_logging(self):
        """设置日志"""
        log_dir = os.path.dirname(self.config['log_file'])
        os.makedirs(log_dir, exist_ok=True)
        
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config['log_file'], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def discover_files(self, input_dirs: List[str]) -> List[Dict]:
        """
        发现输入目录中的所有文件
        
        Args:
            input_dirs: 输入目录列表
            
        Returns:
            文件信息列表
        """
        files = []
        
        for input_dir in input_dirs:
            input_path = Path(input_dir)
            if not input_path.exists():
                self.logger.warning(f"目录不存在: {input_dir}")
                continue
            
            # 查找PDF文件
            pdf_files = list(input_path.glob("**/*.pdf"))
            for pdf_file in pdf_files:
                files.append({
                    'path': str(pdf_file),
                    'type': 'pdf',
                    'size': pdf_file.stat().st_size,
                    'modified': pdf_file.stat().st_mtime
                })
            
            # 查找图片文件
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
            for ext in image_extensions:
                image_files = list(input_path.glob(f"**/*{ext}"))
                for image_file in image_files:
                    files.append({
                        'path': str(image_file),
                        'type': 'image',
                        'size': image_file.stat().st_size,
                        'modified': image_file.stat().st_mtime
                    })
        
        # 按修改时间排序（最新的优先）
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        self.logger.info(f"发现 {len(files)} 个文件")
        return files
    
    def categorize_file(self, file_info: Dict) -> Dict:
        """
        根据文件名和内容分类文件
        
        Args:
            file_info: 文件信息
            
        Returns:
            分类信息
        """
        file_path = file_info['path']
        file_name = os.path.basename(file_path).lower()
        
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
            
            if '概率' in file_name:
                category['subdomain'] = 'probability_thinking'
                category['tags'].append('概率思维')
            elif '系统' in file_name or '网络' in file_name:
                category['subdomain'] = 'system_thinking'
                category['tags'].append('系统思维')
            elif '数据' in file_name:
                category['subdomain'] = 'data_analysis'
                category['tags'].append('数据分析')
        
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
        处理单个文件
        
        Args:
            file_info: 文件信息
            output_base: 输出基础目录
            
        Returns:
            处理结果
        """
        file_path = file_info['path']
        file_type = file_info['type']
        
        try:
            # 分类文件
            category = self.categorize_file(file_info)
            
            # 创建输出目录
            output_dir = os.path.join(
                output_base,
                category['domain'],
                category['subdomain']
            )
            
            # 解析文件
            if file_type == 'pdf':
                parsed_data = self.parser.parse_pdf(file_path)
            elif file_type == 'image':
                parsed_data = self.parser.parse_image(file_path)
            else:
                self.logger.warning(f"不支持的文件类型: {file_type}")
                return None
            
            # 添加分类信息
            parsed_data['category'] = category
            
            # 保存为Markdown
            md_file = self.parser.save_to_markdown(parsed_data, output_dir)
            
            # 准备知识库导入数据
            kb_data = {
                'source_file': file_path,
                'processed_file': md_file,
                'category': category,
                'title': os.path.splitext(os.path.basename(file_path))[0],
                'content': self._extract_main_content(parsed_data),
                'metadata': parsed_data.get('metadata', {}),
                'chunks': parsed_data.get('chunks', []),
                'processed_time': datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ 处理完成: {file_path} → {md_file}")
            return kb_data
            
        except Exception as e:
            self.logger.error(f"❌ 处理失败 {file_path}: {e}")
            return None
    
    def _extract_main_content(self, parsed_data: Dict) -> str:
        """提取主要内容"""
        # 优先使用结构化章节
        if 'sections' in parsed_data and parsed_data['sections']:
            # 合并所有章节
            sections = []
            for section_name, content in parsed_data['sections'].items():
                sections.append(f"## {section_name}\n{content}")
            return '\n\n'.join(sections)
        
        # 其次使用OCR文本
        elif 'ocr_text' in parsed_data and parsed_data['ocr_text']:
            return parsed_data['ocr_text']
        
        # 最后使用原始文本
        elif 'raw_text' in parsed_data and parsed_data['raw_text']:
            return parsed_data['raw_text']
        
        return ""
    
    def import_to_knowledge_base(self, kb_data: Dict, kb_dir: str):
        """
        导入到知识库
        
        Args:
            kb_data: 知识库数据
            kb_dir: 知识库目录
        """
        try:
            # 创建知识库文件
            domain = kb_data['category']['domain']
            subdomain = kb_data['category']['subdomain']
            
            kb_subdir = os.path.join(kb_dir, domain, subdomain)
            os.makedirs(kb_subdir, exist_ok=True)
            
            # 生成文件名
            title = kb_data['title']
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            kb_file = os.path.join(kb_subdir, f"{safe_title}.md")
            
            # 写入知识库文件
            with open(kb_file, 'w', encoding='utf-8') as f:
                # 元数据头
                f.write("---\n")
                f.write(f"title: {title}\n")
                f.write(f"source: {kb_data['source_file']}\n")
                f.write(f"category: {domain}/{subdomain}\n")
                f.write(f"tags: {', '.join(kb_data['category']['tags'])}\n")
                f.write(f"date: {kb_data['metadata'].get('inferred_date', '未知')}\n")
                f.write(f"processed: {kb_data['processed_time']}\n")
                f.write("---\n\n")
                
                # 内容
                f.write(kb_data['content'])
            
            self.logger.info(f"📚 导入知识库: {kb_file}")
            return kb_file
            
        except Exception as e:
            self.logger.error(f"❌ 知识库导入失败: {e}")
            return None
    
    def run_batch(self, input_dirs: List[str], output_dir: str = None, 
                  kb_dir: str = None, limit: int = None):
        """
        运行批量处理
        
        Args:
            input_dirs: 输入目录列表
            output_dir: 输出目录（可选）
            kb_dir: 知识库目录（可选）
            limit: 限制处理文件数量（可选）
        """
        # 设置日志
        self.setup_logging()
        
        # 使用配置或参数
        if output_dir is None:
            output_dir = self.config['output_dir']
        if kb_dir is None:
            kb_dir = self.config['knowledge_base_dir']
        
        self.logger.info("🚀 开始批量处理")
        self.logger.info(f"输入目录: {input_dirs}")
        self.logger.info(f"输出目录: {output_dir}")
        self.logger.info(f"知识库目录: {kb_dir}")
        
        # 发现文件
        files = self.discover_files(input_dirs)
        if not files:
            self.logger.warning("未找到文件")
            return
        
        # 限制文件数量
        if limit and limit > 0:
            files = files[:limit]
            self.logger.info(f"限制处理前 {limit} 个文件")
        
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
            self.logger.info(f"📋 处理进度: {i}/{len(files)} - {file_info['path']}")
            
            # 处理文件
            kb_data = self.process_file(file_info, output_dir)
            
            if kb_data:
                # 导入到知识库
                kb_file = self.import_to_knowledge_base(kb_data, kb_dir)
                
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
        
        self.logger.info(f"📊 批量处理完成")
        self.logger.info(f"报告已保存: {report_file}")
        
        # 触发知识库同步
        self.logger.info("🔄 触发知识库同步...")
        try:
            self.sync_manager.sync_all()
            self.logger.info("✅ 知识库同步完成")
        except Exception as e:
            self.logger.error(f"❌ 知识库同步失败: {e}")
        
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
        
        # 分类统计
        categories = {}
        for file_path in stats['processed_files']:
            file_name = os.path.basename(file_path).lower()
            
            if '复盘' in file_name:
                categories.setdefault('replay', 0)
                categories['replay'] += 1
            elif '框架' in file_name:
                categories.setdefault('framework', 0)
                categories['framework'] += 1
            elif '思维' in file_name:
                categories.setdefault('thinking', 0)
                categories['thinking'] += 1
        
        report['categories'] = categories
        
        return report

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='批量处理复盘内容')
    parser.add_argument('input_dirs', nargs='+', help='输入目录（可多个）')
    parser.add_argument('--output-dir', '-o', help='输出目录')
    parser.add_argument('--kb-dir', '-k', help='知识库目录')
    parser.add_argument('--limit', '-l', type=int, help='限制处理文件数量')
    parser.add_argument('--config', '-c', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 创建处理器
    processor = BatchProcessor(args.config)
    
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
        
        if 'categories' in report:
            print("\n分类统计:")
            for category, count in report['categories'].items():
                print(f"  {category}: {count}个")

if __name__ == "__main__":
    main()