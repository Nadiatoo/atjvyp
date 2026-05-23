#!/usr/bin/env python3
"""
知识库主入口脚本
"""

import argparse
import sys
from pathlib import Path

# 添加脚本目录到路径
sys.path.append(str(Path(__file__).parent))

from sync_manager import SyncManager
from file_monitor import FileMonitor
from vector_db import VectorDatabase
from config_loader import ConfigLoader

def init_knowledge_base():
    """初始化知识库"""
    print("🚀 初始化彪哥战法知识库...")
    
    # 加载配置
    config_loader = ConfigLoader()
    config_loader.print_summary()
    
    # 初始化向量数据库
    vector_db = VectorDatabase()
    
    # 初始化文件监控
    file_monitor = FileMonitor()
    file_monitor.print_summary()
    
    # 初始化同步管理器
    sync_manager = SyncManager()
    
    print("✅ 知识库初始化完成")
    return sync_manager

def cmd_sync(args):
    """同步命令"""
    sync_manager = SyncManager()
    
    if args.full:
        print("🔄 执行全量同步...")
        sync_manager.full_sync()
    else:
        print("🔄 执行增量同步...")
        sync_manager.incremental_sync()
    
    sync_manager.print_status()

def cmd_search(args):
    """搜索命令"""
    # 注意：这里需要嵌入模型，暂时使用简单搜索
    print(f"🔍 搜索: {args.query}")
    print("⚠️  搜索功能需要嵌入模型，当前使用简单文本匹配")
    
    # 这里应该调用实际的搜索功能
    # 暂时显示提示信息
    print("请先安装 sentence-transformers 并配置嵌入模型")
    print("安装命令: pip install sentence-transformers")

def cmd_status(args):
    """状态命令"""
    sync_manager = SyncManager()
    sync_manager.print_status()

def cmd_init(args):
    """初始化命令"""
    sync_manager = init_knowledge_base()
    
    # 创建示例数据
    if args.create_examples:
        create_example_data()
    
    # 运行首次同步
    if args.sync:
        sync_manager.full_sync()

def create_example_data():
    """创建示例数据"""
    print("📝 创建示例知识数据...")
    
    base_dir = Path(__file__).parent.parent / "raw"
    
    # 创建交易知识示例
    trading_dir = base_dir / "domains" / "trading"
    trading_dir.mkdir(parents=True, exist_ok=True)
    
    # 彪哥战法核心原则
    biage_content = """# 彪哥战法核心原则

## 三大核心
1. **市场四季判断** - 识别市场所处的季节阶段
2. **庄稼人耕作节奏** - 根据季节调整操作节奏  
3. **风险控制第一** - 永远把风险控制放在首位

## 四季战法要点
- **春季**：播种期，适合逐步建仓
- **夏季**：生长期，适合持有和加仓
- **秋季**：收获期，适合逐步减仓
- **冬季**：休眠期，适合空仓休息

## 风险控制原则
1. 单笔亏损不超过总资金的2%
2. 总仓位根据市场季节调整
3. 设置明确的止损和止盈点

---
*创建: 2026-04-08*
*更新: 2026-04-08*
*标签: [彪哥战法, 核心原则, 风险控制]*
"""
    
    with open(trading_dir / "biage-core-principles.md", 'w', encoding='utf-8') as f:
        f.write(biage_content)
    
    # 四季战法详解
    four_seasons_content = """# 四季战法详解

## 春季特征（播种期）
- 成交量温和放大
- 板块轮动开始
- 市场情绪从悲观转向谨慎乐观
- 适合策略：逐步建仓，分散投资

## 夏季特征（生长期）
- 成交量大幅放大
- 主线板块明确
- 市场情绪乐观
- 适合策略：持有核心仓位，适度加仓

## 秋季特征（收获期）
- 成交量开始萎缩
- 板块轮动加快
- 市场情绪从乐观转向谨慎
- 适合策略：逐步减仓，锁定利润

## 冬季特征（休眠期）
- 成交量低迷
- 市场缺乏明确主线
- 市场情绪悲观或观望
- 适合策略：空仓休息，等待春季信号

## 季节判断指标
1. 成交量变化趋势
2. 涨跌家数比例
3. 板块轮动情况
4. 市场情绪指标

---
*创建: 2026-04-08*
*更新: 2026-04-08*
*标签: [四季战法, 市场分析, 交易策略]*
"""
    
    with open(trading_dir / "four-seasons-detail.md", 'w', encoding='utf-8') as f:
        f.write(four_seasons_content)
    
    # 技术知识示例
    technical_dir = base_dir / "domains" / "technical"
    technical_dir.mkdir(parents=True, exist_ok=True)
    
    openclaw_content = """# OpenClaw系统配置指南

## 核心配置
- **模型设置**: DeepSeek V3 (deepseek/deepseek-chat)
- **上下文窗口**: 200k tokens
- **定时任务**: 盘前08:00，盘后17:00

## 技能管理
### 已安装核心技能
1. **彪哥战法相关**:
   - biage-market-analyzer (全市场分析)
   - biage-premarket-analyzer (盘前分析)
   - biage-report-generator (报告生成)

2. **系统管理**:
   - self-improving (自我提升)
   - openclaw-agent-optimize (Agent优化)

3. **数据处理**:
   - qveris-official (实时数据)
   - data-analyst (数据分析)

## 故障排查
### 常见问题
1. **API连接失败**: 检查网络和API密钥
2. **定时任务不执行**: 检查OpenClaw服务状态
3. **技能加载失败**: 检查技能依赖和配置

## 性能优化
### 内存优化
- 调整上下文保留策略
- 优化定时任务频率
- 清理不必要的日志

---
*创建: 2026-04-08*
*更新: 2026-04-08*
*标签: [OpenClaw, 系统配置, 故障排查]*
"""
    
    with open(technical_dir / "openclaw-config-guide.md", 'w', encoding='utf-8') as f:
        f.write(openclaw_content)
    
    print(f"✅ 创建了3个示例知识文件:")
    print(f"   1. {trading_dir / 'biage-core-principles.md'}")
    print(f"   2. {trading_dir / 'four-seasons-detail.md'}")
    print(f"   3. {technical_dir / 'openclaw-config-guide.md'}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="彪哥战法知识库管理系统")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # init命令
    init_parser = subparsers.add_parser("init", help="初始化知识库")
    init_parser.add_argument("--create-examples", action="store_true", help="创建示例数据")
    init_parser.add_argument("--sync", action="store_true", help="初始化后运行同步")
    
    # sync命令
    sync_parser = subparsers.add_parser("sync", help="同步文件系统和向量数据库")
    sync_parser.add_argument("--full", action="store_true", help="全量同步")
    
    # search命令
    search_parser = subparsers.add_parser("search", help="搜索知识")
    search_parser.add_argument("query", help="搜索查询")
    
    # status命令
    subparsers.add_parser("status", help="显示系统状态")
    
    # 如果没有提供命令，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    # 执行命令
    if args.command == "init":
        cmd_init(args)
    elif args.command == "sync":
        cmd_sync(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()