#!/bin/bash
# 彪哥战法 - Qlib回测一键运行脚本

echo "=========================================="
echo "彪哥战法 × Qlib 回测系统"
echo "=========================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3"
    exit 1
fi

# 设置工作目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 解析参数
ACTION=${1:-demo}

case $ACTION in
    "demo")
        echo "【模式】简化版回测演示 (无需完整Qlib)"
        echo ""
        python3 biaoge_backtest.py --action backtest --max-stocks 50 --topk 10
        ;;
    
    "prepare")
        echo "【模式】准备回测数据"
        echo ""
        python3 biaoge_backtest.py --action prepare --max-stocks 100
        ;;
    
    "full")
        echo "【模式】完整Qlib工作流 (需要安装pyqlib)"
        echo ""
        python3 biaoge_qlib_workflow.py --mode full
        ;;
    
    "season")
        echo "【模式】训练四季判断模型"
        echo ""
        python3 biaoge_season_model.py
        ;;
    
    "convert")
        echo "【模式】数据格式转换测试"
        echo ""
        python3 akshare_to_qlib.py --start 2024-01-01 --end 2026-03-01 --max-stocks 20
        ;;
    
    *)
        echo "用法: ./run_backtest.sh [demo|prepare|full|season|convert]"
        echo ""
        echo "选项说明:"
        echo "  demo     - 简化版回测演示 (推荐初次使用)"
        echo "  prepare  - 准备回测数据 (下载股票数据)"
        echo "  full     - 完整Qlib工作流 (需要安装pyqlib)"
        echo "  season   - 训练四季判断模型"
        echo "  convert  - 测试数据格式转换"
        echo ""
        echo "示例:"
        echo "  ./run_backtest.sh demo"
        echo "  ./run_backtest.sh season"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "运行完成"
echo "=========================================="
