#!/usr/bin/env python3
"""
配置加载器 - 加载和管理知识库配置
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_dir: str = None):
        """初始化配置加载器"""
        if config_dir is None:
            # 默认配置目录
            self.config_dir = Path(__file__).parent.parent / "config"
        else:
            self.config_dir = Path(config_dir)
        
        self.configs = {}
        self.load_all_configs()
    
    def load_all_configs(self):
        """加载所有配置文件"""
        config_files = [
            "chroma.yaml",
            "embeddings.yaml"
        ]
        
        for config_file in config_files:
            file_path = self.config_dir / config_file
            if file_path.exists():
                config_name = config_file.replace(".yaml", "")
                self.configs[config_name] = self.load_yaml(file_path)
                print(f"✅ 加载配置: {config_file}")
            else:
                print(f"⚠️  配置文件不存在: {config_file}")
    
    def load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """加载YAML配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ 加载配置文件失败 {file_path}: {e}")
            return {}
    
    def get_config(self, config_name: str, default: Any = None) -> Any:
        """获取配置"""
        return self.configs.get(config_name, default)
    
    def get_chroma_config(self) -> Dict[str, Any]:
        """获取ChromaDB配置"""
        return self.get_config("chroma", {}).get("chroma", {})
    
    def get_embeddings_config(self) -> Dict[str, Any]:
        """获取嵌入模型配置"""
        return self.get_config("embeddings", {}).get("embeddings", {})
    
    def print_summary(self):
        """打印配置摘要"""
        print("=" * 50)
        print("知识库配置摘要")
        print("=" * 50)
        
        chroma_config = self.get_chroma_config()
        if chroma_config:
            print(f"📊 ChromaDB配置:")
            print(f"  持久化目录: {chroma_config.get('persist_directory', 'N/A')}")
            print(f"  集合名称: {chroma_config.get('collection', {}).get('name', 'N/A')}")
            print(f"  向量维度: {chroma_config.get('embedding', {}).get('dimension', 'N/A')}")
        
        embeddings_config = self.get_embeddings_config()
        if embeddings_config:
            print(f"🤖 嵌入模型配置:")
            print(f"  模型名称: {embeddings_config.get('model', {}).get('name', 'N/A')}")
            print(f"  分块大小: {embeddings_config.get('text_processing', {}).get('chunk_size', 'N/A')}")
        
        print("=" * 50)

if __name__ == "__main__":
    # 测试配置加载器
    loader = ConfigLoader()
    loader.print_summary()