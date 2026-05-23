#!/usr/bin/env python3
"""
向量数据库管理器 - ChromaDB封装
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib
import json

from config_loader import ConfigLoader

class VectorDatabase:
    """向量数据库管理器"""
    
    def __init__(self, config_dir: str = None):
        """初始化向量数据库"""
        self.config_loader = ConfigLoader(config_dir)
        self.config = self.config_loader.get_chroma_config()
        
        # 初始化ChromaDB客户端
        self.client = self._init_chroma_client()
        
        # 获取或创建集合
        self.collection = self._get_or_create_collection()
        
        print(f"✅ 向量数据库初始化完成")
        print(f"   集合: {self.collection.name}")
        print(f"   文档数量: {self.collection.count()}")
    
    def _init_chroma_client(self) -> chromadb.Client:
        """初始化ChromaDB客户端"""
        persist_directory = self.config.get("persist_directory", "./vectors/chroma")
        
        # 确保目录存在
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # 创建客户端配置
        settings = Settings(
            chroma_db_impl=self.config.get("db_implementation", "duckdb+parquet"),
            persist_directory=persist_directory,
            anonymized_telemetry=False
        )
        
        return chromadb.Client(settings)
    
    def _get_or_create_collection(self) -> chromadb.Collection:
        """获取或创建集合"""
        collection_config = self.config.get("collection", {})
        collection_name = collection_config.get("name", "knowledge_base")
        collection_metadata = collection_config.get("metadata", {})
        
        try:
            # 尝试获取现有集合
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=None  # 我们使用自定义嵌入
            )
            print(f"📂 加载现有集合: {collection_name}")
            return collection
        except:
            # 创建新集合
            print(f"🆕 创建新集合: {collection_name}")
            return self.client.create_collection(
                name=collection_name,
                metadata=collection_metadata,
                embedding_function=None  # 我们使用自定义嵌入
            )
    
    def generate_doc_id(self, file_path: str, content_hash: str = None) -> str:
        """生成文档ID"""
        if content_hash:
            return f"{file_path}:{content_hash[:8]}"
        else:
            # 使用文件路径哈希
            return hashlib.md5(file_path.encode()).hexdigest()[:16]
    
    def add_document(self, file_path: str, content: str, metadata: Dict[str, Any], 
                    vector: List[float] = None) -> str:
        """添加文档到向量数据库"""
        
        # 生成内容哈希
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # 生成文档ID
        doc_id = self.generate_doc_id(file_path, content_hash)
        
        # 准备元数据
        full_metadata = {
            "file_path": file_path,
            "content_hash": content_hash,
            "content_length": len(content),
            "timestamp": metadata.get("timestamp", ""),
            "domain": metadata.get("domain", ""),
            "category": metadata.get("category", ""),
            "tags": json.dumps(metadata.get("tags", [])),
            **metadata  # 添加其他元数据
        }
        
        # 添加文档
        try:
            if vector:
                # 使用提供的向量
                self.collection.add(
                    embeddings=[vector],
                    documents=[content[:10000]],  # 限制文档长度
                    metadatas=[full_metadata],
                    ids=[doc_id]
                )
            else:
                # ChromaDB会自动向量化（如果配置了嵌入函数）
                self.collection.add(
                    documents=[content[:10000]],
                    metadatas=[full_metadata],
                    ids=[doc_id]
                )
            
            print(f"📝 添加文档: {file_path} (ID: {doc_id})")
            return doc_id
            
        except Exception as e:
            print(f"❌ 添加文档失败 {file_path}: {e}")
            return None
    
    def update_document(self, file_path: str, content: str, metadata: Dict[str, Any],
                       vector: List[float] = None) -> str:
        """更新文档（先删除后添加）"""
        # 查找现有文档
        existing_docs = self.collection.get(
            where={"file_path": file_path},
            include=["metadatas"]
        )
        
        # 删除所有匹配的文档
        if existing_docs["ids"]:
            self.collection.delete(ids=existing_docs["ids"])
            print(f"🗑️  删除旧版本: {file_path} ({len(existing_docs['ids'])}个)")
        
        # 添加新版本
        return self.add_document(file_path, content, metadata, vector)
    
    def delete_document(self, file_path: str) -> bool:
        """删除文档"""
        try:
            # 查找文档
            results = self.collection.get(
                where={"file_path": file_path},
                include=["metadatas"]
            )
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                print(f"🗑️  删除文档: {file_path} ({len(results['ids'])}个)")
                return True
            else:
                print(f"⚠️  文档不存在: {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ 删除文档失败 {file_path}: {e}")
            return False
    
    def search(self, query_vector: List[float], n_results: int = 10, 
               where: Dict[str, Any] = None) -> Dict[str, Any]:
        """搜索相似文档"""
        search_config = self.config.get("search", {})
        n_results = min(n_results, search_config.get("max_limit", 100))
        
        try:
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            # 格式化结果
            formatted_results = []
            if results["ids"] and len(results["ids"]) > 0:
                for i in range(len(results["ids"][0])):
                    formatted_results.append({
                        "rank": i + 1,
                        "doc_id": results["ids"][0][i],
                        "score": 1 - results["distances"][0][i],  # 转换为相似度分数
                        "text_preview": results["documents"][0][i][:200] + "..." if len(results["documents"][0][i]) > 200 else results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i]
                    })
            
            return {
                "query_vector_length": len(query_vector),
                "results_count": len(formatted_results),
                "results": formatted_results
            }
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return {"results_count": 0, "results": []}
    
    def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            count = self.collection.count()
            
            # 获取一些样本元数据
            sample = self.collection.get(limit=1, include=["metadatas"])
            
            return {
                "collection_name": self.collection.name,
                "document_count": count,
                "sample_metadata": sample["metadatas"][0] if sample["metadatas"] else None,
                "config": {
                    "persist_directory": self.config.get("persist_directory"),
                    "embedding_dimension": self.config.get("embedding", {}).get("dimension")
                }
            }
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
            return {}

if __name__ == "__main__":
    # 测试向量数据库
    print("🧪 测试向量数据库...")
    
    db = VectorDatabase()
    
    # 获取统计信息
    stats = db.get_stats()
    print(f"📊 数据库统计:")
    print(f"  文档数量: {stats.get('document_count', 0)}")
    print(f"  集合名称: {stats.get('collection_name', 'N/A')}")
    
    # 测试添加文档
    test_content = "彪哥战法核心原则：市场四季判断，庄稼人耕作节奏，风险控制第一。"
    test_metadata = {
        "file_path": "test/biage-method.md",
        "timestamp": "2026-04-08",
        "domain": "trading",
        "category": "彪哥战法",
        "tags": ["核心原则", "交易策略"]
    }
    
    doc_id = db.add_document(
        file_path=test_metadata["file_path"],
        content=test_content,
        metadata=test_metadata
    )
    
    if doc_id:
        print(f"✅ 测试文档添加成功: {doc_id}")
        
        # 测试搜索（使用简单向量）
        test_vector = [0.1] * 384  # 384维测试向量
        results = db.search(test_vector, n_results=3)
        print(f"🔍 测试搜索结果: {results['results_count']}个结果")
        
        # 测试删除
        db.delete_document(test_metadata["file_path"])
        print(f"🗑️  测试文档已删除")
    
    print("✅ 向量数据库测试完成")