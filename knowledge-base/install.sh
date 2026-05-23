#!/bin/bash
# 知识库系统安装脚本

set -e  # 遇到错误退出

echo "🚀 开始安装彪哥战法知识库系统..."

# 检查Python版本
echo "🔍 检查Python环境..."
python3 --version

# 创建虚拟环境（可选）
read -p "是否创建Python虚拟环境？(y/n): " create_venv
if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
fi

# 安装核心依赖
echo "📦 安装核心依赖..."
echo "  1. 安装ChromaDB..."
pip3 install chromadb --index-url https://pypi.tuna.tsinghua.edu.cn/simple

echo "  2. 安装数据处理库..."
pip3 install pandas numpy --index-url https://pypi.tuna.tsinghua.edu.cn/simple

echo "  3. 安装YAML处理库..."
pip3 install pyyaml --index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 尝试安装sentence-transformers
echo "  4. 尝试安装sentence-transformers..."
if pip3 install sentence-transformers --index-url https://pypi.tuna.tsinghua.edu.cn/simple; then
    echo "✅ sentence-transformers 安装成功"
else
    echo "⚠️  sentence-transformers 安装失败，使用备用方案"
    echo "   安装轻量级替代方案..."
    pip3 install transformers torch --index-url https://pypi.tuna.tsinghua.edu.cn/simple
fi

# 验证安装
echo "🔍 验证安装..."
python3 -c "
import importlib

packages = ['chromadb', 'pandas', 'numpy', 'yaml']
for pkg in packages:
    try:
        importlib.import_module(pkg)
        print(f'✅ {pkg}: 已安装')
    except ImportError as e:
        print(f'❌ {pkg}: 未安装')

# 检查嵌入模型
try:
    import sentence_transformers
    print('✅ sentence-transformers: 已安装')
except:
    try:
        import transformers
        print('✅ transformers: 已安装 (sentence-transformers替代)')
    except:
        print('❌ 嵌入模型库未安装，搜索功能将受限')
"

# 创建目录结构
echo "📁 创建目录结构..."
mkdir -p vectors/{chroma,embeddings,metadata}
mkdir -p raw/domains/{trading,technical,workflow}
mkdir -p raw/{entities,schemas}
mkdir -p scripts config

echo "📝 创建示例数据..."
cat > raw/domains/trading/quick-start.md << 'EOF'
# 彪哥战法快速入门

## 核心概念
1. **市场四季**：春播、夏长、秋收、冬藏
2. **庄稼人节奏**：根据季节调整耕作节奏
3. **风险控制**：永远把风险放在第一位

## 快速开始
1. 判断当前市场季节
2. 根据季节选择策略
3. 严格执行风险控制

---
*创建: 2026-04-08*
*标签: [快速入门, 彪哥战法]*
EOF

echo "✅ 示例文件已创建: raw/domains/trading/quick-start.md"

# 创建测试脚本
echo "📜 创建测试脚本..."
cat > test_system.py << 'EOF'
#!/usr/bin/env python3
"""
测试知识库系统
"""

import sys
from pathlib import Path

# 添加脚本目录
sys.path.append(str(Path(__file__).parent / "scripts"))

try:
    from config_loader import ConfigLoader
    print("✅ 配置加载器测试通过")
except Exception as e:
    print(f"❌ 配置加载器测试失败: {e}")

try:
    # 测试文件监控
    from file_monitor import FileMonitor
    monitor = FileMonitor()
    print(f"✅ 文件监控器测试通过，监控目录: {monitor.base_dir}")
except Exception as e:
    print(f"❌ 文件监控器测试失败: {e}")

try:
    # 测试向量数据库
    from vector_db import VectorDatabase
    db = VectorDatabase()
    print(f"✅ 向量数据库测试通过，集合: {db.collection.name}")
except Exception as e:
    print(f"❌ 向量数据库测试失败: {e}")

print("\n🎉 系统测试完成！")
EOF

# 运行测试
echo "🧪 运行系统测试..."
python3 test_system.py

echo ""
echo "=========================================="
echo "🎉 彪哥战法知识库系统安装完成！"
echo "=========================================="
echo ""
echo "📋 下一步操作："
echo "1. 查看目录结构: ls -la"
echo "2. 运行知识库管理: python3 scripts/main.py --help"
echo "3. 添加知识文件到 raw/domains/ 目录"
echo "4. 运行同步: python3 scripts/main.py sync"
echo ""
echo "🔧 故障排除："
echo "  如果嵌入模型安装失败，可以："
echo "  - 手动安装: pip3 install sentence-transformers"
echo "  - 或使用备用模型"
echo ""
echo "📞 更多帮助请查看 README.md"
echo "=========================================="