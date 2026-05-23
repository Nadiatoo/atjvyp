---
name: mem0
description: 专业的长期记忆管理系统 - 为AI Agent提供向量化记忆存储和智能检索
metadata:
  openclaw:
    emoji: "🧠"
    requires:
      bins: ["python3", "pip"]
    install:
      - id: "install-mem0ai"
        kind: "pip"
        package: "mem0ai"
        label: "安装mem0ai Python包"
      - id: "install-optional-deps"
        kind: "pip"
        package: "mem0ai[all]"
        label: "安装mem0ai完整依赖（可选）"
---

# mem0 - 专业记忆管理系统

mem0是一个开源的长期记忆管理系统，专门为AI Agent设计。它提供了向量化记忆存储、智能检索、记忆策略管理等功能。

## 项目信息

- **GitHub**: https://github.com/mem0ai/mem0
- **PyPI**: https://pypi.org/project/mem0ai/
- **文档**: https://docs.mem0.ai/

## 核心功能

### 1. 记忆存储
- 向量化记忆存储
- 支持多种向量数据库（Chroma、Pinecone、LanceDB等）
- 记忆元数据管理

### 2. 智能检索
- 基于上下文的语义搜索
- 记忆相关性排序
- 多条件过滤

### 3. 记忆策略
- 可配置的记忆保留策略
- 记忆优先级管理
- 自动记忆整理

### 4. 集成支持
- REST API
- Python SDK
- LangChain集成
- LlamaIndex集成

## 安装方式

### 方式1: Python包安装
```bash
pip install mem0ai
```

### 方式2: 完整安装（包含所有可选依赖）
```bash
pip install "mem0ai[all]"
```

### 方式3: Docker部署（作为独立服务）
```bash
docker run -p 8080:8080 mem0ai/mem0
```

## 基本使用

### 初始化客户端
```python
from mem0 import Memory

# 使用默认配置（需要OpenAI API Key）
memory = Memory()

# 或者设置环境变量
import os
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
memory = Memory()
```

### 存储记忆
```python
# mem0使用messages参数存储对话记忆
memory_id = memory.add(
    messages=[
        {"role": "user", "content": "用户喜欢喝咖啡，每天早上一杯"},
        {"role": "assistant", "content": "好的，已记录用户喜欢喝咖啡"}
    ],
    metadata={
        "user_id": "123",
        "category": "preference",
        "timestamp": "2026-04-03"
    }
)

# 存储项目相关记忆
memory.add(
    messages=[
        {"role": "user", "content": "EGPS系统在2026-03-29完成了框架升级"},
        {"role": "assistant", "content": "这是一个重要的系统里程碑"}
    ],
    metadata={
        "project": "EGPS",
        "date": "2026-03-29",
        "type": "system_upgrade",
        "importance": "high"
    }
)
```

### 检索记忆
```python
# 基于查询检索相关记忆
results = memory.search("用户喜欢喝什么？", top_k=3)

# 基于元数据过滤
results = memory.search(
    query="系统升级",
    metadata_filter={"project": "EGPS"},
    top_k=5
)
```

### 记忆管理
```python
# 获取所有记忆
all_memories = memory.get_all()

# 删除特定记忆
memory.delete(memory_id="some-id")

# 更新记忆
memory.update(
    memory_id="some-id",
    text="更新后的记忆内容",
    metadata={"updated": True}
)
```

## 与OpenClaw集成

### 集成方案1: 作为记忆服务
```python
# 在OpenClaw技能中使用mem0
from mem0 import Memory

class Mem0Skill:
    def __init__(self):
        self.memory = Memory()
    
    def remember(self, text, metadata=None):
        """存储重要信息到mem0"""
        return self.memory.add(text=text, metadata=metadata)
    
    def recall(self, query, top_k=5):
        """从mem0检索相关记忆"""
        return self.memory.search(query=query, top_k=top_k)
```

### 集成方案2: 作为智能知识中枢组件
```python
# 将mem0作为智能知识中枢（IKH）的记忆模块
class IntelligentKnowledgeHub:
    def __init__(self):
        self.memory_system = Memory()
        self.knowledge_base = None  # 其他知识库组件
    
    def store_knowledge(self, content, source, importance=0.5):
        """存储知识到记忆系统"""
        return self.memory_system.add(
            text=content,
            metadata={
                "source": source,
                "importance": importance,
                "timestamp": datetime.now().isoformat()
            }
        )
```

## 配置选项

### 向量存储配置
```python
# ChromaDB配置
memory = Memory(
    vector_store="chroma",
    chroma_db_path="./chroma_db"
)

# Pinecone配置
memory = Memory(
    vector_store="pinecone",
    pinecone_api_key="your-key",
    pinecone_index="mem0-index"
)

# LanceDB配置
memory = Memory(
    vector_store="lancedb",
    lancedb_uri="./lancedb_data"
)
```

### Embedding模型配置
```python
# OpenAI Embeddings
memory = Memory(
    embedding_model="text-embedding-3-small",
    openai_api_key="your-key"
)

# 本地模型（如sentence-transformers）
memory = Memory(
    embedding_model="all-MiniLM-L6-v2",
    local_embedding=True
)
```

## 使用场景

### 场景1: AI助手长期记忆
```python
# 记录用户偏好
memory.add("用户是投资顾问，主要关注A股市场", 
           metadata={"user_type": "investment_advisor", "market": "A股"})

# 在后续对话中回忆
preferences = memory.search("用户的职业是什么？")
```

### 场景2: 项目知识管理
```python
# 存储项目经验
memory.add("EGPS系统在滞涨分析中表现优秀",
           metadata={"project": "EGPS", "analysis_type": "滞涨"})

# 检索相关项目经验
egps_experiences = memory.search("滞涨分析", 
                                 metadata_filter={"project": "EGPS"})
```

### 场景3: 工作流程记忆
```python
# 记录工作流程
memory.add("每日08:00执行彪哥战法盘前分析",
           metadata={"task": "盘前分析", "time": "08:00", "system": "彪哥战法"})

# 检索工作计划
daily_tasks = memory.search("今天要执行什么任务？")
```

## 性能优化

### 批量操作
```python
# 批量添加记忆
memories = [
    {"text": "记忆1", "metadata": {"id": 1}},
    {"text": "记忆2", "metadata": {"id": 2}},
]
memory.add_batch(memories)
```

### 缓存策略
```python
# 启用缓存
memory = Memory(
    use_cache=True,
    cache_ttl=3600  # 缓存1小时
)
```

### 异步操作
```python
import asyncio
from mem0 import AsyncMemory

async def async_operations():
    memory = AsyncMemory()
    await memory.add("异步存储的记忆")
    results = await memory.search("查询")
```

## 故障排除

### 常见问题
1. **安装失败**: 检查Python版本（需要3.8+）和网络连接
2. **向量数据库连接失败**: 检查数据库配置和网络
3. **Embedding模型加载失败**: 检查API密钥或本地模型文件

### 调试模式
```python
memory = Memory(debug=True)
# 启用调试日志
```

## 相关资源

- [mem0官方文档](https://docs.mem0.ai/)
- [GitHub示例](https://github.com/mem0ai/mem0/tree/main/examples)
- [API参考](https://docs.mem0.ai/api-reference)
- [社区讨论](https://github.com/mem0ai/mem0/discussions)

## 更新日志

### v1.0.0 (2024-12-01)
- 初始版本发布
- 基础记忆存储和检索功能
- 支持多种向量数据库
- Python SDK和REST API

---

**注意**: 本skill提供了mem0的基本集成指南。实际使用时可能需要根据具体需求进行调整和扩展。