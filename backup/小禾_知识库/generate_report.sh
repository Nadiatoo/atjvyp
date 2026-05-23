#!/bin/bash
# 个股深度报告一键生成脚本
# 用法: ./generate_report.sh <股票代码>
# 示例: ./generate_report.sh 000001.SZ
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COLLECT_SCRIPT="$SCRIPT_DIR/collect_stock_data.py"
REPORT_SCRIPT="$SCRIPT_DIR/report_template.py"
DATA_DIR="$SCRIPT_DIR/data"
REPORT_DIR="$SCRIPT_DIR/reports"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ $# -lt 1 ]; then
    echo "用法: $0 <股票代码>"
    echo "示例: $0 000001.SZ"
    exit 1
fi

STOCK_CODE="$1"
# 格式化代码获取文件名
FMT_CODE=$(echo "$STOCK_CODE" | sed 's/\./_/g')
DATA_FILE="$DATA_DIR/${FMT_CODE}_data.json"
MD_FILE="$DATA_DIR/${FMT_CODE}_analysis.md"

echo -e "${GREEN}======================================"
echo "  个股深度报告生成系统"
echo -e "======================================${NC}"
echo ""

# Step 1: 数据采集
echo -e "${YELLOW}[1/3] 数据采集...${NC}"
python3 "$COLLECT_SCRIPT" "$STOCK_CODE"
echo ""

# Step 2: 提示编写分析内容
echo -e "${YELLOW}[2/3] 分析内容...${NC}"
AUTO_MODE="${AUTO_MODE:-0}"
if [ -f "$MD_FILE" ]; then
    echo "  已有分析文件: $MD_FILE"
    if [ "$AUTO_MODE" = "1" ]; then
        echo "  AUTO_MODE=1，跳过交互确认"
    else
        echo "  如需重新编写，请编辑该文件后按回车继续（30秒超时跳过）"
        read -r -t 30 || echo "  超时跳过，使用现有文件"
    fi
else
    echo "  请在以下文件中编写分析内容（Markdown格式）："
    echo "  $MD_FILE"
    echo ""
    cat > "$MD_FILE" << 'MDTEMPLATE'
## 核心业务分析


## 行业地位


## 盈利预测


## 投资要点


MDTEMPLATE
    echo "  模板已创建，请编辑该文件后按回车继续生成 PDF（30秒超时跳过）"
    read -r -t 30 || echo "  超时跳过，使用空模板继续"
fi
echo ""

# Step 3: 生成PDF
echo -e "${YELLOW}[3/3] 生成 PDF...${NC}"
python3 "$REPORT_SCRIPT" "$DATA_FILE" "$MD_FILE"
echo ""
echo -e "${GREEN}完成! PDF 报告已生成到 $REPORT_DIR/${NC}"
ls -la "$REPORT_DIR/"*.pdf 2>/dev/null | tail -1

