#!/usr/bin/env python3
"""
同花顺Mac版数据解析器
读取 ~/Library/Containers/cn.com.10jqka.macstockPro/ 下的本地数据文件
"""

import plistlib
import struct
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd


class THSDataParser:
    """同花顺Mac版本地数据解析器"""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        初始化解析器
        
        Args:
            data_dir: 同花顺数据目录，默认使用Mac版标准路径
        """
        if data_dir is None:
            self.data_dir = Path.home() / "Library/Containers/cn.com.10jqka.macstockPro/Data"
        else:
            self.data_dir = Path(data_dir)
        
        self.market_data_file = self.data_dir / "Documents/MarketData/MarketDataFile"
        self.cache_dir = Path.home() / ".ths_data_cache"
        self.cache_dir.mkdir(exist_ok=True)
        
    def _parse_nskeyedarchiver(self, plist_path: Path) -> Dict:
        """
        解析NSKeyedArchiver格式的plist文件
        
        Args:
            plist_path: plist文件路径
            
        Returns:
            解析后的字典数据
        """
        with open(plist_path, 'rb') as f:
            plist_data = plistlib.load(f)
        
        objects = plist_data.get('$objects', [])
        top = plist_data.get('$top', {})
        
        def resolve_ref(ref):
            """解析引用对象"""
            if isinstance(ref, dict) and 'CF$UID' in ref:
                idx = ref['CF$UID']
                if 0 <= idx < len(objects):
                    return objects[idx]
            return ref
        
        def parse_object(obj_idx, visited=None):
            """递归解析对象"""
            if visited is None:
                visited = set()
            
            if obj_idx in visited:
                return f"<circular ref #{obj_idx}>"
            visited.add(obj_idx)
            
            if obj_idx >= len(objects):
                return None
            
            obj = objects[obj_idx]
            
            # 基础类型直接返回
            if isinstance(obj, (str, int, float, bool, bytes)):
                return obj
            
            if isinstance(obj, dict):
                # 跳过类定义
                if '$classname' in obj:
                    return f"<Class:{obj.get('$classname')}>"
                
                result = {}
                for k, v in obj.items():
                    if k == '$class':
                        continue
                    if k in ['NS.keys', 'NS.objects']:
                        # NSDictionary的内部结构
                        ref_v = resolve_ref(v)
                        if isinstance(ref_v, dict) and 'NS.objects' in ref_v:
                            items = []
                            for item_ref in ref_v['NS.objects']:
                                if isinstance(item_ref, dict) and 'CF$UID' in item_ref:
                                    items.append(parse_object(item_ref['CF$UID'], visited.copy()))
                                else:
                                    items.append(item_ref)
                            result[k] = items
                        else:
                            result[k] = ref_v
                    elif isinstance(v, dict) and 'CF$UID' in v:
                        result[k] = parse_object(v['CF$UID'], visited.copy())
                    else:
                        result[k] = v
                return result
            
            return obj
        
        # 解析顶层对象
        result = {}
        for key, ref in top.items():
            if isinstance(ref, dict) and 'CF$UID' in ref:
                result[key] = parse_object(ref['CF$UID'])
            else:
                result[key] = ref
        
        return result
    
    def parse_market_data(self) -> Optional[pd.DataFrame]:
        """
        解析市场数据文件
        
        Returns:
            包含市场数据的DataFrame，如果解析失败返回None
        """
        if not self.market_data_file.exists():
            print(f"市场数据文件不存在: {self.market_data_file}")
            return None
        
        try:
            data = self._parse_nskeyedarchiver(self.market_data_file)
            print(f"解析成功，顶层键: {list(data.keys())}")
            
            # 进一步解析市场数据结构
            market_data = data.get('MarketDataDecodeKey', {})
            print(f"市场数据结构: {type(market_data)}")
            
            if isinstance(market_data, dict):
                # 提取股票数据
                stocks = self._extract_stocks_from_market_data(market_data)
                if stocks:
                    return pd.DataFrame(stocks)
            
            return None
            
        except Exception as e:
            print(f"解析市场数据失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_stocks_from_market_data(self, market_data: Dict) -> List[Dict]:
        """
        从市场数据中提取股票信息
        
        Args:
            market_data: 解析后的市场数据字典
            
        Returns:
            股票信息列表
        """
        stocks = []
        
        # NSKeyedArchiver中的NSDictionary会被解析为包含NS.keys和NS.objects的结构
        # 需要进一步分析实际数据结构
        print(f"市场数据键: {list(market_data.keys()) if isinstance(market_data, dict) else 'N/A'}")
        
        # TODO: 根据实际数据结构提取股票信息
        # 这里需要根据进一步分析的结果来实现
        
        return stocks
    
    def list_available_data_files(self) -> List[Path]:
        """
        列出同花顺数据目录中所有可用的数据文件
        
        Returns:
            数据文件路径列表
        """
        data_files = []
        
        # 扫描Documents目录下的数据文件
        docs_dir = self.data_dir / "Documents"
        if docs_dir.exists():
            for path in docs_dir.rglob("*"):
                if path.is_file() and path.stat().st_size > 1000:  # 排除小文件
                    data_files.append(path)
        
        return sorted(data_files, key=lambda p: p.stat().st_size, reverse=True)
    
    def inspect_data_file(self, file_path: Path) -> Dict:
        """
        检查数据文件的内容和结构
        
        Args:
            file_path: 数据文件路径
            
        Returns:
            文件信息字典
        """
        info = {
            'path': str(file_path),
            'size': file_path.stat().st_size,
            'type': 'unknown'
        }
        
        # 尝试作为plist解析
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
                if header.startswith(b'bplist'):
                    info['type'] = 'plist/bplist'
                    # 尝试解析
                    f.seek(0)
                    plist_data = plistlib.load(f)
                    info['plist_keys'] = list(plist_data.keys()) if isinstance(plist_data, dict) else 'N/A'
                    if '$objects' in plist_data:
                        info['object_count'] = len(plist_data['$objects'])
        except:
            pass
        
        return info


def main():
    """主函数 - 测试解析器"""
    print("=" * 60)
    print("同花顺Mac版数据解析器")
    print("=" * 60)
    
    parser = THSDataParser()
    
    # 列出可用的数据文件
    print("\n扫描数据文件...")
    data_files = parser.list_available_data_files()
    print(f"找到 {len(data_files)} 个数据文件")
    
    # 显示前10个最大的文件
    print("\n最大的10个数据文件:")
    for i, f in enumerate(data_files[:10], 1):
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {i}. {f.name}: {size_mb:.2f} MB")
    
    # 检查MarketDataFile
    print(f"\n检查市场数据文件: {parser.market_data_file}")
    if parser.market_data_file.exists():
        info = parser.inspect_data_file(parser.market_data_file)
        print(f"  文件大小: {info.get('size', 0) / 1024:.2f} KB")
        print(f"  文件类型: {info.get('type', 'unknown')}")
        if 'plist_keys' in info:
            print(f"  Plist键: {info['plist_keys']}")
        if 'object_count' in info:
            print(f"  对象数量: {info['object_count']}")
        
        # 尝试解析
        print("\n尝试解析市场数据...")
        df = parser.parse_market_data()
        if df is not None:
            print(f"解析成功！数据行数: {len(df)}")
            print(df.head())
        else:
            print("解析结果为空，需要进一步分析数据结构")
    else:
        print("  文件不存在!")


if __name__ == "__main__":
    main()
