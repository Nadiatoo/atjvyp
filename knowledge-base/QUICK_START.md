# 🚀 彪哥战法知识库 - 快速开始指南

## ⏱️ 5分钟快速上手

### 第1步：检查环境（1分钟）
```bash
cd /Users/tuqibiao/.openclaw/workspace/knowledge-base

# 检查Python环境
python3 --version  # 需要Python 3.8+

# 检查依赖
python3 -c "import chromadb; print('✅ ChromaDB OK')"
```

### 第2步：添加你的知识（2分钟）
```bash
# 创建你的第一个知识文件
cat > raw/domains/trading/my-first-knowledge.md << 'EOF'
# 我的交易经验

## 重要教训
1. 不要追涨杀跌
2. 严格执行止损
3. 保持耐心，等待机会

## 成功模式
- 突破关键阻力位后买入
- 成交量配合的价格突破
- 板块轮动中的龙头股

---
*创建: $(date +%Y-%m-%d)*
*标签: [经验教训, 成功模式]*
EOF
```

### 第3步：同步到知识库（1分钟）
```bash
# 运行同步（首次建议全量同步）
python3 -c "
import sys
sys.path.append('scripts')
from sync_manager import SyncManager

sync_manager = SyncManager()
sync_manager.full_sync()
sync_manager.print_status()
"
```

### 第4步：搜索知识（1分钟）
```bash
# 搜索相关经验
python3 -c "
import sys
sys.path.append('scripts')

print('🔍 知识库搜索演示:')

# 注意：需要安装sentence-transformers才能使用语义搜索
# 当前使用简单文本匹配

from file_monitor import FileMonitor
monitor = FileMonitor()

files = monitor.get_all_files()
print(f'📚 知识库中有 {len(files)} 个文件:')
for file in files[:3]:  # 显示前3个
    print(f'  • {file[\"relative_path\"]}')
"
```

## 📋 完整使用流程

### 1. 日常知识管理
```bash
# 添加新知识
vim raw/domains/trading/new-insight.md

# 增量同步（推荐日常使用）
python3 scripts/main.py sync

# 查看状态
python3 scripts/main.py status
```

### 2. 批量知识导入
```bash
# 如果有多个Markdown文件
cp ~/your-knowledge/*.md raw/domains/trading/

# 全量同步
python3 scripts/main.py sync --full
```

### 3. 知识维护
```bash
# 编辑现有知识
vim raw/domains/trading/existing-knowledge.md

# 同步修改
python3 scripts/main.py sync

# 验证同步
python3 -c "
import sys
sys.path.append('scripts')
from sync_manager import SyncManager
sync_manager = SyncManager()
sync_manager.verify_sync()
"
```

## 🔧 常见问题解决

### Q1: sentence-transformers安装失败
```bash
# 尝试使用国内镜像
pip3 install sentence-transformers -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用轻量级替代
pip3 install transformers torch
```

### Q2: 同步失败
```bash
# 检查文件权限
ls -la raw/

# 检查磁盘空间
df -h .

# 重新初始化
rm -rf vectors/chroma/*
python3 scripts/main.py init
```

### Q3: 搜索不准确
```bash
# 确保嵌入模型已安装
python3 -c "import sentence_transformers; print('✅ 嵌入模型OK')"

# 重新同步所有文件
python3 scripts/main.py sync --full
```

## 🎯 最佳实践

### 文件命名规范
```
好的命名：biage-core-principles.md
差的命名：文档1.md

好的命名：risk-control-2026.md  
差的命名：新建文本文档.md
```

### 内容格式规范
```markdown
# 标题

## 章节标题

- 使用列表组织要点
- 保持段落简洁

**重要概念**：加粗强调

---
*创建: YYYY-MM-DD*
*更新: YYYY-MM-DD*
*标签: [标签1, 标签2, 标签3]*
```

### 同步时机
- **添加新知识后**：立即增量同步
- **每天结束时**：检查同步状态
- **每周一次**：运行全量同步验证

## 📊 监控和维护

### 每日检查
```bash
# 检查文件变化
python3 -c "
import sys
sys.path.append('scripts')
from file_monitor import FileMonitor
monitor = FileMonitor()
monitor.print_summary()
"

# 检查同步状态
python3 scripts/main.py status
```

### 每周维护
```bash
# 备份知识库
tar -czf knowledge-backup-$(date +%Y%m%d).tar.gz raw/ vectors/metadata/

# 验证数据一致性
python3 -c "
import sys
sys.path.append('scripts')
from sync_manager import SyncManager
sync_manager = SyncManager()
sync_manager.verify_sync()
"
```

## 🚀 高级功能（待实现）

### 语义搜索（需要嵌入模型）
```python
# 安装后可用
from vector_db import VectorDatabase
db = VectorDatabase()

# 自然语言搜索
results = db.search_semantic("市场下跌时怎么办")
```

### 知识推荐
```python
# 基于当前内容的推荐
related_knowledge = get_related_knowledge(current_content)
```

### 自动摘要
```python
# 长文档自动摘要
summary = generate_summary(long_document)
```

## 📞 获取帮助

### 查看详细文档
```bash
cat README.md          # 完整项目文档
cat IMPLEMENTATION_SUMMARY.md  # 实施总结
```

### 检查日志
```bash
# 查看同步日志
cat vectors/metadata/sync_state.json | python3 -m json.tool

# 查看文件状态
cat vectors/metadata/file_state.json | python3 -m json.tool
```

### 调试问题
```bash
# 启用详细日志
export PYTHONPATH=scripts:$PYTHONPATH
python3 -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

---

**快速开始完成！** 🎉

现在你可以：
1. ✅ 添加知识到 `raw/` 目录
2. ✅ 使用 `python3 scripts/main.py sync` 同步
3. ✅ 使用 `python3 scripts/main.py status` 查看状态

**下一步**：安装sentence-transformers启用语义搜索功能

---
*最后更新: 2026-04-08*
*版本: 1.0.0*