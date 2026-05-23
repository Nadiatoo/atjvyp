#!/usr/bin/env python3
"""
本地嵌入模型备选方案
当无法连接huggingface时使用
"""

import numpy as np
from typing import List, Optional
import hashlib
import json
import os
from pathlib import Path

class LocalEmbeddings:
    """本地嵌入模型（轻量级备选方案）"""
    
    def __init__(self, model_name: str = "local", cache_dir: str = "vectors/embeddings"):
        """初始化本地嵌入模型"""
        self.model_name = model_name
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 简单词向量（用于演示，实际使用时可以加载预训练的小模型）
        self.word_vectors = self._create_simple_word_vectors()
        
        print(f"✅ 本地嵌入模型初始化: {model_name}")
    
    def _create_simple_word_vectors(self) -> dict:
        """创建简单的词向量（用于演示）"""
        # 这里可以替换为加载本地的小型预训练模型
        # 例如：加载本地的word2vec或fasttext模型
        
        # 临时使用随机向量（实际使用时应该加载真实模型）
        important_words = [
            '市场', '股票', '资金', '情绪', '技术', '分析', '复盘',
            '风险', '策略', '板块', '龙头', '趋势', '突破', '支撑',
            '压力', '成交量', '涨幅', '跌幅', '震荡', '反弹'
        ]
        
        vectors = {}
        np.random.seed(42)  # 固定随机种子
        
        for word in important_words:
            # 生成固定维度的随机向量（模拟）
            vectors[word] = np.random.randn(128).astype(np.float32)
        
        return vectors
    
    def encode(self, texts: List[str], **kwargs) -> np.ndarray:
        """
        编码文本为向量
        
        Args:
            texts: 文本列表
            **kwargs: 其他参数
            
        Returns:
            向量数组
        """
        embeddings = []
        
        for text in texts:
            # 检查缓存
            cached_embedding = self._get_cached_embedding(text)
            if cached_embedding is not None:
                embeddings.append(cached_embedding)
                continue
            
            # 生成新嵌入
            embedding = self._generate_embedding(text)
            
            # 缓存
            self._cache_embedding(text, embedding)
            
            embeddings.append(embedding)
        
        return np.array(embeddings)
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """生成文本嵌入"""
        # 简单实现：基于词向量的加权平均
        words = text.split()
        
        if not words:
            return np.zeros(128, dtype=np.float32)
        
        # 收集词向量
        word_embeddings = []
        for word in words:
            if word in self.word_vectors:
                word_embeddings.append(self.word_vectors[word])
            else:
                # 对于未知词，使用随机向量（基于词哈希）
                hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16)
                np.random.seed(hash_val % 10000)
                word_embeddings.append(np.random.randn(128).astype(np.float32))
        
        # 平均词向量
        if word_embeddings:
            embedding = np.mean(word_embeddings, axis=0)
        else:
            embedding = np.zeros(128, dtype=np.float32)
        
        # 归一化
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def _get_cached_embedding(self, text: str) -> Optional[np.ndarray]:
        """获取缓存的嵌入"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_file = self.cache_dir / f"{text_hash}.npy"
        
        if cache_file.exists():
            try:
                return np.load(cache_file)
            except:
                pass
        
        return None
    
    def _cache_embedding(self, text: str, embedding: np.ndarray):
        """缓存嵌入"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_file = self.cache_dir / f"{text_hash}.npy"
        
        try:
            np.save(cache_file, embedding)
        except:
            pass
    
    def get_sentence_embedding(self, sentence: str) -> np.ndarray:
        """获取句子嵌入（兼容sentence-transformers接口）"""
        return self.encode([sentence])[0]
    
    @property
    def max_seq_length(self) -> int:
        """最大序列长度"""
        return 512
    
    @property
    def embedding_dimension(self) -> int:
        """嵌入维度"""
        return 128

class HybridEmbeddings:
    """混合嵌入模型（优先使用真实模型，失败时使用本地模型）"""
    
    def __init__(self, preferred_model: str = "all-MiniLM-L6-v2"):
        """初始化混合嵌入模型"""
        self.preferred_model = preferred_model
        self.real_model = None
        self.local_model = LocalEmbeddings()
        self.use_local = False
        
        # 尝试加载真实模型
        self._try_load_real_model()
    
    def _try_load_real_model(self):
        """尝试加载真实模型"""
        try:
            from sentence_transformers import SentenceTransformer
            
            print(f"🔍 尝试加载模型: {self.preferred_model}")
            self.real_model = SentenceTransformer(self.preferred_model)
            print(f"✅ 真实模型加载成功: {self.preferred_model}")
            self.use_local = False
            
        except Exception as e:
            print(f"⚠️ 真实模型加载失败: {e}")
            print("🔄 切换到本地模型")
            self.use_local = True
    
    def encode(self, texts: List[str], **kwargs) -> np.ndarray:
        """编码文本"""
        if self.use_local or self.real_model is None:
            return self.local_model.encode(texts, **kwargs)
        else:
            return self.real_model.encode(texts, **kwargs)
    
    def get_sentence_embedding(self, sentence: str) -> np.ndarray:
        """获取句子嵌入"""
        return self.encode([sentence])[0]
    
    @property
    def max_seq_length(self) -> int:
        """最大序列长度"""
        if self.use_local or self.real_model is None:
            return self.local_model.max_seq_length
        else:
            return self.real_model.max_seq_length
    
    @property
    def embedding_dimension(self) -> int:
        """嵌入维度"""
        if self.use_local or self.real_model is None:
            return self.local_model.embedding_dimension
        else:
            return self.real_model.get_sentence_embedding_dimension()

# 测试函数
def test_embeddings():
    """测试嵌入模型"""
    print("🧪 测试嵌入模型...")
    
    # 创建混合模型
    model = HybridEmbeddings()
    
    # 测试文本
    test_texts = [
        "彪哥战法市场分析",
        "概率思维与逻辑验证",
        "资金流向和板块轮动"
    ]
    
    # 生成嵌入
    embeddings = model.encode(test_texts)
    
    print(f"✅ 嵌入生成成功")
    print(f"  模型类型: {'本地' if model.use_local else '真实'}")
    print(f"  文本数量: {len(test_texts)}")
    print(f"  嵌入维度: {embeddings.shape[1]}")
    print(f"  嵌入形状: {embeddings.shape}")
    
    # 计算相似度
    if len(test_texts) >= 2:
        from sklearn.metrics.pairwise import cosine_similarity
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        print(f"  相似度(文本1-2): {similarity:.4f}")
    
    return model

if __name__ == "__main__":
    test_embeddings()