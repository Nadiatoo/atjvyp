#!/usr/bin/env python3
"""
文件系统监控器 - 监控知识文件变化
"""

import os
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
import json

class FileMonitor:
    """文件系统监控器"""
    
    def __init__(self, base_dir: str = None):
        """初始化文件监控器"""
        if base_dir is None:
            self.base_dir = Path(__file__).parent.parent / "raw"
        else:
            self.base_dir = Path(base_dir)
        
        # 状态文件路径
        self.state_file = self.base_dir.parent / "vectors" / "metadata" / "file_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载状态
        self.file_states = self._load_state()
        
        print(f"📁 监控目录: {self.base_dir}")
        print(f"📊 已跟踪文件: {len(self.file_states)}个")
    
    def _load_state(self) -> Dict[str, Dict[str, any]]:
        """加载文件状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ 加载状态文件失败: {e}")
                return {}
        else:
            return {}
    
    def _save_state(self):
        """保存文件状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.file_states, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存状态文件失败: {e}")
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"❌ 计算文件哈希失败 {file_path}: {e}")
            return ""
    
    def get_file_metadata(self, file_path: Path) -> Dict[str, any]:
        """获取文件元数据"""
        try:
            stat = file_path.stat()
            
            # 读取文件内容（用于提取元数据）
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取领域和类别（从路径推断）
            relative_path = str(file_path.relative_to(self.base_dir))
            domain = self._extract_domain(relative_path)
            category = self._extract_category(relative_path)
            
            # 提取标签（从内容中）
            tags = self._extract_tags(content)
            
            return {
                "file_path": str(file_path),
                "relative_path": relative_path,
                "size": stat.st_size,
                "modified_time": stat.st_mtime,
                "created_time": stat.st_ctime,
                "content_hash": self.calculate_file_hash(file_path),
                "domain": domain,
                "category": category,
                "tags": tags,
                "content_length": len(content),
                "timestamp": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
        except Exception as e:
            print(f"❌ 获取文件元数据失败 {file_path}: {e}")
            return {}
    
    def _extract_domain(self, file_path: str) -> str:
        """从文件路径提取领域"""
        parts = file_path.split('/')
        if len(parts) > 0:
            if parts[0] == "domains":
                return parts[1] if len(parts) > 1 else "unknown"
            elif parts[0] == "entities":
                return "entities"
            elif parts[0] == "schemas":
                return "schemas"
        return "unknown"
    
    def _extract_category(self, file_path: str) -> str:
        """从文件路径提取类别"""
        # 从文件名推断类别
        filename = Path(file_path).stem.lower()
        
        # 常见类别映射
        category_map = {
            "biage": "彪哥战法",
            "four": "四季战法", 
            "risk": "风险控制",
            "technical": "技术分析",
            "fundamental": "基本面分析",
            "strategy": "交易策略",
            "pattern": "市场模式",
            "lesson": "经验教训"
        }
        
        for key, category in category_map.items():
            if key in filename:
                return category
        
        return "其他"
    
    def _extract_tags(self, content: str) -> List[str]:
        """从内容提取标签"""
        tags = []
        
        # 常见标签
        common_tags = [
            "彪哥战法", "四季战法", "庄稼人战法", "风险控制",
            "市场分析", "技术分析", "基本面分析", "资金面分析",
            "交易策略", "仓位管理", "止损", "止盈",
            "OpenClaw", "Python", "自动化", "数据源",
            "AI工具", "向量数据库", "知识库"
        ]
        
        # 检查内容中是否包含这些标签
        for tag in common_tags:
            if tag in content:
                tags.append(tag)
        
        # 限制标签数量
        return tags[:10]
    
    def scan_files(self) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """扫描文件系统，返回变化"""
        current_files = {}
        
        # 扫描所有支持的文件
        supported_extensions = {'.md', '.yaml', '.yml', '.txt', '.json'}
        
        for ext in supported_extensions:
            for file_path in self.base_dir.rglob(f"*{ext}"):
                if file_path.is_file():
                    relative_path = str(file_path.relative_to(self.base_dir))
                    metadata = self.get_file_metadata(file_path)
                    current_files[relative_path] = metadata
        
        # 比较变化
        added = []
        modified = []
        deleted = []
        
        # 检查新增和修改的文件
        for relative_path, metadata in current_files.items():
            if relative_path not in self.file_states:
                # 新增文件
                added.append(metadata)
            else:
                old_state = self.file_states[relative_path]
                if (metadata["content_hash"] != old_state.get("content_hash") or
                    metadata["size"] != old_state.get("size")):
                    # 修改的文件
                    modified.append(metadata)
        
        # 检查删除的文件
        for relative_path in list(self.file_states.keys()):
            if relative_path not in current_files:
                deleted.append({
                    "file_path": str(self.base_dir / relative_path),
                    "relative_path": relative_path,
                    "timestamp": datetime.now().isoformat()
                })
        
        # 更新状态
        self.file_states = {
            relative_path: {
                "content_hash": metadata["content_hash"],
                "size": metadata["size"],
                "modified_time": metadata["modified_time"],
                "last_checked": datetime.now().timestamp()
            }
            for relative_path, metadata in current_files.items()
        }
        
        self._save_state()
        
        return added, modified, deleted
    
    def get_file_content(self, file_path: str) -> str:
        """获取文件内容"""
        try:
            full_path = self.base_dir / file_path
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ 读取文件失败 {file_path}: {e}")
            return ""
    
    def get_all_files(self) -> List[Dict[str, any]]:
        """获取所有文件信息"""
        files = []
        
        for ext in ['.md', '.yaml', '.yml', '.txt', '.json']:
            for file_path in self.base_dir.rglob(f"*{ext}"):
                if file_path.is_file():
                    metadata = self.get_file_metadata(file_path)
                    files.append(metadata)
        
        return files
    
    def print_summary(self):
        """打印监控摘要"""
        added, modified, deleted = self.scan_files()
        
        print("=" * 50)
        print("文件系统监控摘要")
        print("=" * 50)
        print(f"📁 监控目录: {self.base_dir}")
        print(f"📊 总文件数: {len(self.file_states)}")
        print(f"🆕 新增文件: {len(added)}")
        print(f"✏️  修改文件: {len(modified)}")
        print(f"🗑️  删除文件: {len(deleted)}")
        
        if added:
            print("\n新增文件:")
            for file in added[:5]:  # 只显示前5个
                print(f"  • {file['relative_path']}")
            if len(added) > 5:
                print(f"  ... 还有 {len(added) - 5} 个")
        
        if modified:
            print("\n修改文件:")
            for file in modified[:5]:
                print(f"  • {file['relative_path']}")
            if len(modified) > 5:
                print(f"  ... 还有 {len(modified) - 5} 个")
        
        print("=" * 50)

if __name__ == "__main__":
    # 测试文件监控器
    print("🧪 测试文件监控器...")
    
    monitor = FileMonitor()
    monitor.print_summary()
    
    # 测试获取文件内容
    test_files = monitor.get_all_files()
    if test_files:
        print(f"\n📄 找到 {len(test_files)} 个文件")
        for i, file_info in enumerate(test_files[:3]):  # 显示前3个
            print(f"{i+1}. {file_info['relative_path']} ({file_info['domain']}/{file_info['category']})")
    else:
        print("📁 目录为空，创建测试文件...")
        
        # 创建测试目录和文件
        test_dir = monitor.base_dir / "domains" / "trading"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        test_file = test_dir / "biage-method-test.md"
        test_content = """# 彪哥战法测试文档

## 核心原则
1. 市场四季判断
2. 庄稼人耕作节奏  
3. 风险控制第一

## 标签
- 彪哥战法
- 交易策略
- 风险控制

---
*创建: 2026-04-08*
*更新: 2026-04-08*
"""
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"✅ 创建测试文件: {test_file}")
        
        # 重新扫描
        monitor.scan_files()
        monitor.print_summary()
    
    print("✅ 文件监控器测试完成")