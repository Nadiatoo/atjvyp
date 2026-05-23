#!/usr/bin/env python3
"""
快速启动脚本 - 开始处理复盘内容
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# 添加脚本目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_directories():
    """设置目录结构"""
    directories = [
        "raw/processed/replays",
        "raw/domains/trading",
        "raw/domains/methodology", 
        "raw/domains/personal",
        "vectors/chroma",
        "vectors/embeddings",
        "logs",
        "backups/replays"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 创建目录: {directory}")
    
    print("✅ 目录结构设置完成")

def test_system():
    """测试系统组件"""
    print("\n🧪 测试系统组件...")
    
    tests = []
    
    # 测试1: 嵌入模型
    try:
        from local_embeddings import HybridEmbeddings
        model = HybridEmbeddings()
        test_vector = model.encode(["测试文本"])
        tests.append(("嵌入模型", True, f"维度: {test_vector.shape[1]}"))
    except Exception as e:
        tests.append(("嵌入模型", False, str(e)))
    
    # 测试2: PDF解析器
    try:
        from replay_parser import ReplayParser
        parser = ReplayParser()
        tests.append(("PDF解析器", True, "初始化成功"))
    except Exception as e:
        tests.append(("PDF解析器", False, str(e)))
    
    # 测试3: 向量数据库
    try:
        from vector_db_enhanced import EnhancedVectorDatabase
        db = EnhancedVectorDatabase()
        stats = db.get_stats()
        tests.append(("向量数据库", True, f"文档数: {stats.get('document_count', 0)}"))
    except Exception as e:
        tests.append(("向量数据库", False, str(e)))
    
    # 打印测试结果
    print("\n📊 测试结果:")
    for name, success, message in tests:
        status = "✅" if success else "❌"
        print(f"  {status} {name}: {message}")
    
    return all(success for _, success, _ in tests)

def create_sample_data():
    """创建示例数据"""
    print("\n📝 创建示例数据...")
    
    # 创建示例复盘文件
    sample_dir = "raw/domains/trading/sample"
    Path(sample_dir).mkdir(parents=True, exist_ok=True)
    
    sample_content = """# 示例复盘 - 2026-04-09

## 市场概况
今日市场震荡上行，成交量温和放大。

## 技术分析
上证指数在4000点附近获得支撑，技术指标显示超卖反弹。

## 情绪分析
市场情绪从冰点修复，赚钱效应有所改善。

## 资金流向
北向资金净流入45亿元，主要流入科技板块。

## 风险提示
注意外围市场波动风险，控制仓位。

## 操作策略
建议逢低布局优质科技股，仓位控制在50%左右。

---
*创建: 2026-04-09*
*标签: [示例, 复盘, 市场分析]*
"""
    
    sample_file = os.path.join(sample_dir, "sample-replay-20260409.md")
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    print(f"✅ 示例文件已创建: {sample_file}")
    return sample_file

def process_single_file(file_path: str):
    """处理单个文件（测试用）"""
    print(f"\n🔧 测试处理文件: {file_path}")
    
    try:
        from replay_parser import ReplayParser
        from vector_db_enhanced import EnhancedVectorDatabase
        
        # 初始化
        parser = ReplayParser()
        db = EnhancedVectorDatabase()
        
        # 解析文件
        if file_path.endswith('.pdf'):
            parsed_data = parser.parse_pdf(file_path)
        elif file_path.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            parsed_data = parser.parse_image(file_path)
        else:
            print(f"⚠️ 不支持的文件类型: {file_path}")
            return False
        
        if 'error' in parsed_data:
            print(f"❌ 解析失败: {parsed_data['error']}")
            return False
        
        # 保存为Markdown
        output_dir = "raw/processed/test"
        md_file = parser.save_to_markdown(parsed_data, output_dir)
        
        # 导入到知识库
        kb_data = {
            'source_file': file_path,
            'processed_file': md_file,
            'category': {
                'domain': 'trading',
                'subdomain': 'test',
                'tags': ['测试']
            },
            'title': os.path.splitext(os.path.basename(file_path))[0],
            'content': parsed_data.get('raw_text', parsed_data.get('ocr_text', '')),
            'metadata': parsed_data.get('metadata', {}),
            'chunks': parsed_data.get('chunks', [])
        }
        
        # 添加完整文档
        doc_id = db.add_document(
            file_path=file_path,
            content=kb_data['content'],
            metadata={
                'file_path': file_path,
                'timestamp': datetime.now().isoformat(),
                'domain': 'trading',
                'category': 'test',
                'tags': ['测试', '示例']
            },
            generate_vector=True
        )
        
        # 添加分块文档
        if kb_data['chunks']:
            chunk_ids = db.add_document_with_chunks(
                file_path=f"{file_path}_chunks",
                chunks=kb_data['chunks'],
                metadata={
                    'file_path': file_path,
                    'timestamp': datetime.now().isoformat(),
                    'domain': 'trading',
                    'category': 'test',
                    'tags': ['测试', '分块']
                }
            )
            print(f"📚 分块添加: {len(chunk_ids)}个块")
        
        print(f"✅ 文件处理完成: {file_path} → {doc_id}")
        return True
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 彪哥战法知识库 - 快速启动")
    print("=" * 50)
    
    # 1. 设置目录
    setup_directories()
    
    # 2. 测试系统
    if not test_system():
        print("\n⚠️ 系统测试失败，请检查依赖")
        return
    
    # 3. 创建示例数据
    sample_file = create_sample_data()
    
    # 4. 处理示例数据
    success = process_single_file(sample_file)
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 快速启动完成！")
        print("=" * 50)
        print("\n📋 下一步操作:")
        print("1. 批量处理复盘文件:")
        print("   python scripts/batch_processor.py /Users/tuqibiao/Downloads/2026复盘")
        print("")
        print("2. 搜索知识库:")
        print("   python scripts/main.py search '市场分析'")
        print("")
        print("3. 查看系统状态:")
        print("   python scripts/main.py status")
        print("")
        print("4. 同步知识库:")
        print("   python scripts/main.py sync")
        print("")
        print("🔧 配置文件:")
        print("   - config/replay_config.yaml: 复盘处理配置")
        print("   - config/chroma.yaml: 向量数据库配置")
        print("   - config/embeddings.yaml: 嵌入模型配置")
        print("")
        print("💡 提示:")
        print("   - 首次批量处理建议使用 --limit 参数限制文件数量")
        print("   - 图片处理需要安装Tesseract OCR")
        print("   - 网络问题可能导致嵌入模型下载失败，已启用本地备选方案")
    else:
        print("\n❌ 快速启动失败，请检查错误信息")

if __name__ == "__main__":
    main()