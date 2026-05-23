#!/usr/bin/env python3
"""
同花顺数据深度分析工具
用于研究Mac版同花顺的数据文件结构
"""

import plistlib
import os
from pathlib import Path
from typing import Dict, List, Any, Set, Optional
import json


class THSDataAnalyzer:
    """同花顺数据文件深度分析器"""
    
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            self.data_dir = Path.home() / "Library/Containers/cn.com.10jqka.macstockPro/Data"
        else:
            self.data_dir = Path(data_dir)
        
        self.market_data_file = self.data_dir / "Documents/MarketData/MarketDataFile"
    
    def analyze_plist_structure(self, plist_path: Path, max_depth: int = 5) -> Dict:
        """
        深度分析plist文件结构
        
        Args:
            plist_path: plist文件路径
            max_depth: 最大解析深度
            
        Returns:
            结构分析报告
        """
        with open(plist_path, 'rb') as f:
            plist_data = plistlib.load(f)
        
        objects = plist_data.get('$objects', [])
        top = plist_data.get('$top', {})
        
        report = {
            'file': str(plist_path),
            'total_objects': len(objects),
            'top_keys': list(top.keys()),
            'object_types': {},
            'string_samples': [],
            'dictionary_samples': [],
            'top_structure': {}
        }
        
        # 统计对象类型
        type_counts = {}
        for obj in objects:
            obj_type = type(obj).__name__
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
        report['object_types'] = type_counts
        
        # 收集字符串样本（可能是股票代码或名称）
        strings = [obj for obj in objects if isinstance(obj, str) and len(obj) < 20]
        report['string_samples'] = strings[:50]  # 前50个字符串
        
        # 收集字典样本
        dicts = [(i, obj) for i, obj in enumerate(objects) if isinstance(obj, dict)]
        for idx, d in dicts[:10]:
            sample = {
                'index': idx,
                'keys': list(d.keys()),
                'has_classname': '$classname' in d
            }
            if '$classname' in d:
                sample['classname'] = d['$classname']
            report['dictionary_samples'].append(sample)
        
        # 解析顶层结构
        def resolve_and_describe(ref, depth=0):
            if depth > max_depth:
                return "<max depth>"
            
            if isinstance(ref, dict) and 'CF$UID' in ref:
                idx = ref['CF$UID']
                if idx >= len(objects):
                    return f"<invalid ref #{idx}>"
                obj = objects[idx]
                
                if isinstance(obj, dict):
                    if '$classname' in obj:
                        return f"<Class:{obj['$classname']}>"
                    
                    result = {}
                    for k, v in obj.items():
                        if k == '$class':
                            continue
                        if isinstance(v, dict) and 'CF$UID' in v:
                            if depth < max_depth:
                                result[k] = resolve_and_describe(v, depth + 1)
                            else:
                                result[k] = f"<ref #{v['CF$UID']}>"
                        else:
                            result[k] = v
                    return result
                elif isinstance(obj, (list, tuple)):
                    return f"<array length={len(obj)}>"
                else:
                    return obj
            
            return ref
        
        for key, ref in top.items():
            report['top_structure'][key] = resolve_and_describe(ref)
        
        return report
    
    def extract_all_strings(self, plist_path: Path) -> List[str]:
        """提取plist中所有字符串（用于查找股票代码）"""
        with open(plist_path, 'rb') as f:
            plist_data = plistlib.load(f)
        
        objects = plist_data.get('$objects', [])
        
        strings = []
        for obj in objects:
            if isinstance(obj, str):
                strings.append(obj)
        
        return strings
    
    def find_stock_codes(self, plist_path: Path) -> List[str]:
        """尝试从plist中查找股票代码"""
        strings = self.extract_all_strings(plist_path)
        
        # 股票代码模式：6位数字（A股）或特定前缀
        import re
        stock_patterns = [
            r'^(sh|sz|bj)\d{6}$',  # sh600000, sz000001 格式
            r'^\d{6}$',  # 纯6位数字
        ]
        
        stock_codes = []
        for s in strings:
            for pattern in stock_patterns:
                if re.match(pattern, s, re.IGNORECASE):
                    stock_codes.append(s)
                    break
        
        return stock_codes
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        生成完整的分析报告
        
        Args:
            output_file: 输出文件路径，如果为None则打印到控制台
            
        Returns:
            报告文本
        """
        lines = []
        lines.append("=" * 80)
        lines.append("同花顺数据文件深度分析报告")
        lines.append("=" * 80)
        lines.append("")
        
        # 分析MarketDataFile
        if self.market_data_file.exists():
            lines.append(f"分析文件: {self.market_data_file}")
            lines.append("")
            
            analysis = self.analyze_plist_structure(self.market_data_file)
            
            lines.append(f"总对象数: {analysis['total_objects']}")
            lines.append("")
            
            lines.append("对象类型分布:")
            for obj_type, count in analysis['object_types'].items():
                lines.append(f"  {obj_type}: {count}")
            lines.append("")
            
            lines.append("顶层键:")
            for key in analysis['top_keys']:
                lines.append(f"  - {key}")
            lines.append("")
            
            lines.append("字符串样本 (可能是股票代码/名称):")
            for i, s in enumerate(analysis['string_samples'][:30], 1):
                lines.append(f"  {i}. {s}")
            lines.append("")
            
            lines.append("字典样本:")
            for sample in analysis['dictionary_samples']:
                lines.append(f"  [{sample['index']}] 类: {sample.get('classname', 'N/A')}")
                lines.append(f"       键: {sample['keys']}")
            lines.append("")
            
            lines.append("顶层结构:")
            lines.append(json.dumps(analysis['top_structure'], indent=2, default=str))
            lines.append("")
            
            # 查找股票代码
            lines.append("查找股票代码...")
            stock_codes = self.find_stock_codes(self.market_data_file)
            if stock_codes:
                lines.append(f"找到 {len(stock_codes)} 个可能的股票代码:")
                for code in stock_codes[:50]:
                    lines.append(f"  {code}")
            else:
                lines.append("未找到符合格式的股票代码")
            
        else:
            lines.append(f"文件不存在: {self.market_data_file}")
        
        report_text = "\n".join(lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"报告已保存到: {output_file}")
        
        return report_text


def main():
    """主函数"""
    import sys
    
    analyzer = THSDataAnalyzer()
    
    # 生成报告
    output_path = Path.home() / ".openclaw/workspace/ths-data-parser/analysis_report.txt"
    report = analyzer.generate_report(str(output_path))
    
    print(report)


if __name__ == "__main__":
    main()
