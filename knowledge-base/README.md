# 🧠 彪哥战法知识库 - 混合架构版

## 📋 项目概述

基于 **文件系统 + ChromaDB向量数据库** 的混合架构知识库，实现：
- **文件系统**：原始知识存储，人类可读，版本控制友好
- **向量数据库**：语义搜索，快速检索，AI原生支持

## 🏗️ 架构设计

### 核心架构
```
原始知识文件 → 向量化处理 → ChromaDB索引 → 语义搜索
    ↓               ↓           ↓           ↓
Markdown/YAML   文本→向量   向量存储   自然语言查询
```

### 目录结构
```
knowledge-base/
├── raw/                    # 原始知识文件（权威源）
│   ├── domains/           # 知识领域分类
│   ├── entities/          # 实体定义
│   └── schemas/           # 数据模式
├── vectors/               # 向量数据库数据
│   ├── chroma/           # ChromaDB存储
│   ├── embeddings/       # 向量缓存
│   └── metadata/         # 元数据索引
├── scripts/              # 处理脚本
│   ├── sync.py          # 同步脚本
│   ├── search.py        # 搜索脚本
│   └── vectorize.py     # 向量化脚本
└── config/               # 配置文件
    ├── chroma.yaml      # ChromaDB配置
    └── embeddings.yaml  # 嵌入模型配置
```

## 🔄 工作流程

### 1. 知识录入流程
```
编辑Markdown文件 → 保存到raw/ → 触发同步 → 更新向量索引
```

### 2. 知识搜索流程
```
输入自然语言查询 → 向量化 → ChromaDB搜索 → 返回结果+原始文件链接
```

### 3. 系统维护流程
```
每日增量同步 → 每周全量验证 → 每月性能优化
```

## 🛠️ 技术栈

### 核心组件
- **文件系统**：Markdown/YAML格式，git版本控制
- **向量数据库**：ChromaDB（轻量级，Python原生）
- **嵌入模型**：sentence-transformers/all-MiniLM-L6-v2
- **同步引擎**：Python脚本，文件监控

### 开发环境
- Python 3.8+
- ChromaDB 0.4.0+
- sentence-transformers 2.2.0+
- 推荐：8GB+内存，SSD存储

## 🚀 快速开始

### 1. 环境准备
```bash
# 安装依赖
pip install chromadb sentence-transformers duckdb pandas numpy

# 验证安装
python -c "import chromadb; print('ChromaDB OK')"
python -c "from sentence_transformers import SentenceTransformer; print('Embeddings OK')"
```

### 2. 初始化知识库
```bash
# 创建测试数据
python scripts/init_test_data.py

# 首次向量化
python scripts/vectorize.py --full

# 测试搜索
python scripts/search.py "彪哥战法核心原则"
```

### 3. 日常使用
```bash
# 添加新知识
vim raw/domains/trading/new-knowledge.md

# 同步到向量数据库
python scripts/sync.py --incremental

# 搜索知识
python scripts/search.py "你的查询"
```

## 📁 文件格式规范

### Markdown知识文件
```markdown
# 标题

## 章节

### 子章节

- 列表项
- 另一个列表项

**重要概念**：解释...

---
*创建: YYYY-MM-DD*
*更新: YYYY-MM-DD*
*标签: [标签1, 标签2, 标签3]*
```

### YAML实体文件
```yaml
# entities/example.yaml
entities:
  - id: unique-id
    name: 实体名称
    type: 实体类型
    description: 描述
    properties:
      key1: value1
      key2: value2
    created: YYYY-MM-DD
    updated: YYYY-MM-DD
```

## 🔧 开发指南

### 添加新功能
1. 在`scripts/`目录创建新脚本
2. 遵循现有代码风格
3. 添加测试用例
4. 更新文档

### 修改配置
1. 编辑`config/`目录下的配置文件
2. 重启相关服务（如果需要）
3. 验证配置生效

### 调试问题
1. 检查日志文件
2. 验证数据同步状态
3. 测试各个组件
4. 查看监控指标

## 📊 性能指标

### 目标性能
- **查询响应**：< 100ms（简单查询），< 1s（复杂查询）
- **同步延迟**：< 10s（增量同步），< 5min（全量同步）
- **存储效率**：向量压缩率 > 50%
- **准确率**：搜索相关度 > 0.8

### 监控指标
- 知识文件数量
- 向量索引大小
- 搜索频率和响应时间
- 同步成功率和延迟

## 🔒 安全和备份

### 备份策略
```
实时备份：git提交
每日备份：数据库导出 + 文件打包
每周备份：异地存储
```

### 恢复流程
1. 从git恢复文件
2. 从备份恢复数据库
3. 重新同步数据
4. 验证完整性

## 🤝 贡献指南

### 代码贡献
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

### 知识贡献
1. 编辑知识文件
2. 遵循格式规范
3. 添加相关标签
4. 更新索引

## 📞 支持

### 常见问题
1. **同步失败**：检查文件权限和磁盘空间
2. **搜索不准确**：检查嵌入模型和向量质量
3. **性能问题**：优化配置和硬件资源

### 获取帮助
- 查看文档和示例
- 检查日志文件
- 提交Issue

---

**项目状态**：实施中  
**最后更新**：2026-04-08  
**版本**：1.0.0-alpha  
**维护者**：富富