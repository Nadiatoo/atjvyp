#!/usr/bin/env python3
"""
增强版向量数据库管理器 - 支持混合嵌入模型
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import hashlib
import json
import numpy as np

from config_loader import ConfigLoader
from local_embeddings import HybridEmbeddings

class EnhancedVectorDatabase:
    """增强版向量数据库管理器"""
    
    def __init__(self, config_dir: str = None):
        """初始化向量数据库"""
        self.config_loader = ConfigLoader(config_dir)
        self.config = self.config_loader.get_chroma_config()
        
        # 初始化嵌入模型
        self.embedding_model = self._init_embedding_model()
        
        # 初始化ChromaDB客户端
        self.client = self._init_chroma_client()
        
        # 获取或创建集合
        self.collection = self._get_or_create_collection()
        
        print(f"✅ 增强版向量数据库初始化完成")
        print(f"   集合: {self.collection.name}")
        print(f"   嵌入模型: {self.embedding_model.__class__.__name__}")
        print(f"   使用本地模型: {getattr(self.embedding_model, 'use_local', False)}")
        print(f"   文档数量: {self.collection.count()}")
    
    def _init_embedding_model(self) -> HybridEmbeddings:
        """初始化嵌入模型"""
        embedding_config = self.config.get("embedding", {})
        model_name = embedding_config.get("model", "all-MiniLM-L6-v2")
        
        return HybridEmbeddings(preferred_model=model_name)
    
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
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """生成文本嵌入向量"""
        return self.embedding_model.encode([text])[0]
    
    def add_document(self, file_path: str, content: str, metadata: Dict[str, Any], 
                    generate_vector: bool = True) -> str:
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
            "embedding_model": self.embedding_model.__class__.__name__,
            "embedding_local": str(getattr(self.embedding_model, 'use_local', False)),
            **metadata  # 添加其他元数据
        }
        
        # 添加文档
        try:
            if generate_vector:
                # 生成嵌入向量
                vector = self.generate_embedding(content).tolist()
                
                self.collection.add(
                    embeddings=[vector],
                    documents=[content[:10000]],  # 限制文档长度
                    metadatas=[full_metadata],
                    ids=[doc_id]
                )
                print(f"📝 添加文档(带向量): {file_path} (ID: {doc_id})")
            else:
                # 只添加文档，不生成向量
                self.collection.add(
                    documents=[content[:10000]],
                    metadatas=[full_metadata],
                    ids=[doc_id]
                )
                print(f"📝 添加文档(无向量): {file_path} (ID: {doc_id})")
            
            return doc_id
            
        except Exception as e:
            print(f"❌ 添加文档失败 {file_path}: {e}")
            return None
    
    def add_document_with_chunks(self, file_path: str, chunks: List[Dict], 
                                metadata: Dict[str, Any]) -> List[str]:
        """
        添加分块文档
        
        Args:
            file_path: 文件路径
            chunks: 分块列表，每个块包含text和其他信息
            metadata: 元数据
            
        Returns:
            文档ID列表
        """
        doc_ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_text = chunk.get('text', '')
            if not chunk_text:
                continue
            
            # 为每个块创建唯一ID
            chunk_hash = hashlib.md5(chunk_text.encode()).hexdigest()
            chunk_id = f"{file_path}:chunk{i}:{chunk_hash[:8]}"
            
            # 准备块元数据
            chunk_metadata = {
                **metadata,
                "chunk_id": i,
                "chunk_count": len(chunks),
                "chunk_start": chunk.get('start_word', 0),
                "chunk_end": chunk.get('end_word', 0),
                "is_chunk": True,
                "parent_file": file_path
            }
            
            # 添加块
            doc_id = self.add_document(
                file_path=chunk_id,
                content=chunk_text,
                metadata=chunk_metadata,
                generate_vector=True
            )
            
            if doc_id:
                doc_ids.append(doc_id)
        
        print(f"📚 添加分块文档: {file_path} → {len(doc_ids)}个块")
        return doc_ids
    
    def update_document(self, file_path: str, content: str, metadata: Dict[str, Any],
                       generate_vector: bool = True) -> str:
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
        return self.add_document(file_path, content, metadata, generate_vector)
    
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
    
    def search(self, query_text: str = None, query_vector: List[float] = None, 
               n_results: int = 10, where: Dict[str, Any] = None,
               include_documents: bool = True) -> Dict[str, Any]:
        """
        搜索相似文档
        
        Args:
            query_text: 查询文本（优先使用）
            query_vector: 查询向量（如果提供query_text则忽略）
            n_results: 返回结果数量
            where: 过滤条件
            include_documents: 是否包含文档内容
            
        Returns:
            搜索结果
        """
        search_config = self.config.get("search", {})
        n_results = min(n_results, search_config.get("max_limit", 100))
        
        # 生成查询向量
        if query_text:
            query_vector = self.generate_embedding(query_text).tolist()
        elif query_vector is None:
            raise ValueError("必须提供query_text或query_vector")
        
        try:
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances", "embeddings"]
            )
            
            # 格式化结果
            formatted_results = []
            if results["ids"] and len(results["ids"]) > 0:
                for i in range(len(results["ids"][0])):
                    result = {
                        "rank": i + 1,
                        "doc_id": results["ids"][0][i],
                        "score": 1 - results["distances"][0][i],  # 转换为相似度分数
                        "distance": results["distances"][0][i],
                        "metadata": results["metadatas"][0][i]
                    }
                    
                    # 包含文档内容
                    if include_documents and results["documents"]:
                        text = results["documents"][0][i]
                        result["text_preview"] = text[:200] + "..." if len(text) > 200 else text
                        result["text_length"] = len(text)
                    
                    # 包含向量（调试用）
                    if results["embeddings"]:
                        result["embedding_length"] = len(results["embeddings"][0][i])
                    
                    formatted_results.append(result)
            
            return {
                "query_type": "text" if query_text else "vector",
                "query_length": len(query_vector) if query_vector else 0,
                "results_count": len(formatted_results),
                "results": formatted_results
            }
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return {"results_count": 0, "results": [], "error": str(e)}
    
    def semantic_search(self, query: str, domain: str = None, category: str = None,
                       n_results: int = 10) -> Dict[str, Any]:
        """
        语义搜索（带过滤）
        
        Args:
            query: 查询文本
            domain: 限制领域
            category: 限制分类
            n_results: 返回结果数量
            
        Returns:
            搜索结果
        """
        # 构建过滤条件
        where = {}
        if domain:
            where["domain"] = domain
        if category:
            where["category"] = category
        
        return self.search(query_text=query, n_results=n_results, where=where)
    
    def find_similar_documents(self, document_id: str, n_results: int = 5) -> Dict[str, Any]:
        """
        查找相似文档
        
        Args:
            document_id: 文档ID
            n_results: 返回结果数量
            
        Returns:
            相似文档结果
        """
        try:
            # 获取文档的嵌入向量
            doc_result = self.collection.get(
                ids=[document_id],
                include=["embeddings"]
            )
            
            if not doc_result["embeddings"] or len(doc_result["embeddings"][0]) == 0:
                return {"error": "文档没有嵌入向量", "results_count": 0, "results": []}
            
            # 使用文档向量搜索
            doc_vector = doc_result["embeddings"][0][0]
            
            # 排除自身
            where = {"file_path": {"$ne": doc_result["metadatas"][0]["file_path"]}}
            
            return self.search(
                query_vector=doc_vector.tolist(),
                n_results=n_results,
                where=where
            )
            
        except Exception as e:
            print(f"❌ 查找相似文档失败: {e}")
            return {"error": str(e), "results_count": 0, "results": []}
    
    def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            count = self.collection.count()
            
            # 获取一些样本元数据
            sample = self.collection.get(limit=1, include=["metadatas"])
            
            # 获取领域分布
            all_docs = self.collection.get(limit=1000, include=["metadatas"])
            domain_dist = {}
            category_dist = {}
            
            for metadata in all_docs["metadatas"]:
                domain = metadata.get("domain", "unknown")
                category = metadata.get("category", "unknown")
                
                domain_dist[domain] = domain_dist.get(domain, 0) + 1
                category_dist[category] = category_dist.get(category, 0) + 1
            
            return {
                "collection_name": self.collection.name,
                "document_count": count,
                "embedding_model": self.embedding_model.__class__.__name__,
                "embedding_local": getattr(self.embedding_model, 'use_local', False),
                "embedding_dimension": self.embedding_model.embedding_dimension,
                "domain_distribution": domain_dist,
                "category_distribution": category_dist,
                "sample_metadata": sample["metadatas"][0] if sample["metadatas"] else None
            }
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
            return {}

if __name__ == "__main__":
    # 测试增强版向量数据库
    print("🧪 测试增强版向量数据库...")
    
    db = EnhancedVectorDatabase()
    
    # 获取统计信息
    stats = db.get_stats()
    print(f"📊 数据库统计:")
    print(f"  文档数量: {stats.get('document_count', 0)}")
    print(f"  集合名称: {stats.get('collection_name', 'N/A')}")
    print(f"  嵌入模型: {stats.get('embedding_model', 'N/A')}")
    print(f"  使用本地模型: {stats.get('embedding_local', False)}")
    
    # 测试添加文档
    test_content = """
    彪哥战法核心原则：
    1. 市场四季判断：春播、夏长、秋收、冬藏
    2. 庄稼人耕作节奏：根据季节调整操作频率
    3. 风险控制第一：永远把风险放在收益前面
    4. 概率思维：接受市场不确定性，用概率决策
    """
    
    test_metadata = {
        "file_path": "test/biage-core-principles.md",
        "timestamp": "2026-04-09",
        "domain": "trading",
        "category": "彪哥战法",
        "tags": ["核心原则", "交易策略", "风险控制", "概率思维"],
        "author": "老涂"
    }
    
    doc_id = db.add_document(
        file_path=test_metadata["file_path"],
        content=test_content,
        metadata=test_metadata,
        generate_vector=True
    )
    
    if doc_id:
        print(f"✅ 测试文档添加成功: {doc_id}")
        
        # 测试语义搜索
        print("\n🔍 测试语义搜索...")
        results = db.semantic_search(
            query="市场季节判断和风险控制",
            domain="trading",
            n_results=3
        )
        
        print(f"  搜索结果: {results['results_count']}个")
        for result in results['results']:
            print(f"  [{result['rank']}] 分数: {result['score']:.4f} - {result['metadata'].get('file_path', 'N/A')}")
        
        # 测试分块添加
        print("\n📚 测试分块添加...")
        chunks = [
            {"text": "市场四季判断是彪哥战法的核心", "start_word": 0, "end_word": 10},
            {"text": "春播季节适合建仓，夏长季节适合持有", "start_word": 10, "end_word": 20},
            {"text": "风险控制永远放在第一位，保护本金", "start_word": 20, "end_word": 30}
        ]
        
        chunk_ids = db.add_document_with_chunks(
            file_path="test/biage-chunks.md",
            chunks=chunks,
            metadata=test_metadata
        )
        print(f"  分块添加成功: {len(chunk_ids)}个块")
        
        # 测试查找相似文档
        print("\n🔄 测试查找相似文档...")
        if chunk_ids:
            similar = db.find_similar_documents(chunk_ids[0], n_results=2)
            print(f"  相似文档: {similar['results_count']}个")
        
        # 清理测试数据
        db.delete_document(test_metadata["file_path"])
        db.delete_document("test/biage-chunks.md")
        print(f"\n🗑️  测试文档已清理")
    
    print("\n✅ 增强版向量数据库测试完成")</