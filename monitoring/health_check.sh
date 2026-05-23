#!/bin/bash
# 健康检查脚本

REPORT_DIR="/Users/tuqibiao/.openclaw/workspace/monitoring/health_reports"
REPORT_FILE="$REPORT_DIR/health_$(date +%Y%m%d_%H%M%S).txt"
LOG_FILE="/Users/tuqibiao/.openclaw/workspace/monitoring/health_check.log"

# 创建报告目录
mkdir -p $REPORT_DIR

echo "=== OpenClaw系统健康检查报告 ===" > $REPORT_FILE
echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 1. 系统基本信息
echo "1. 系统基本信息:" >> $REPORT_FILE
echo "   主机名: $(hostname)" >> $REPORT_FILE
echo "   当前用户: $(whoami)" >> $REPORT_FILE
echo "   检查时间: $(date)" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 2. 磁盘空间检查
echo "2. 磁盘空间检查:" >> $REPORT_FILE
df -h /Users/tuqibiao/.openclaw/workspace 2>/dev/null >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 3. 内存使用检查
echo "3. 内存使用检查:" >> $REPORT_FILE
if command -v free &> /dev/null; then
    free -h 2>/dev/null | head -2 >> $REPORT_FILE
else
    echo "   free命令不可用" >> $REPORT_FILE
fi
echo "" >> $REPORT_FILE

# 4. OpenClaw进程检查
echo "4. OpenClaw进程检查:" >> $REPORT_FILE
OPENCLAW_PROCESSES=$(ps aux | grep -i openclaw | grep -v grep | wc -l)
echo "   运行中的OpenClaw进程数: $OPENCLAW_PROCESSES" >> $REPORT_FILE
if [ $OPENCLAW_PROCESSES -gt 0 ]; then
    echo "   ✅ OpenClaw进程运行正常" >> $REPORT_FILE
else
    echo "   ⚠️ 未找到运行的OpenClaw进程" >> $REPORT_FILE
fi
echo "" >> $REPORT_FILE

# 5. 工作区文件检查
echo "5. 工作区关键文件检查:" >> $REPORT_FILE
check_file() {
    local file=$1
    local desc=$2
    if [ -f "$file" ]; then
        local size=$(du -h "$file" 2>/dev/null | cut -f1 || echo "未知")
        echo "   ✅ $desc: 存在 (大小: $size)" >> $REPORT_FILE
    else
        echo "   ⚠️ $desc: 不存在" >> $REPORT_FILE
    fi
}

check_file "/Users/tuqibiao/.openclaw/workspace/memory/2026-03-16.md" "今日记忆文件"
check_file "/Users/tuqibiao/.openclaw/workspace/agent_registry.json" "Agent注册表"
check_file "/Users/tuqibiao/.openclaw/workspace/紧急工作成果清单.md" "紧急工作清单"
echo "" >> $REPORT_FILE

# 6. 备份检查
echo "6. 备份检查:" >> $REPORT_FILE
BACKUP_COUNT=$(ls -1 /Users/tuqibiao/.openclaw/backups/workspace_backup_*.tar.gz 2>/dev/null | wc -l)
if [ $BACKUP_COUNT -gt 0 ]; then
    LATEST_BACKUP=$(ls -t /Users/tuqibiao/.openclaw/backups/workspace_backup_*.tar.gz 2>/dev/null | head -1)
    BACKUP_TIME=$(stat -f "%Sm" "$LATEST_BACKUP" 2>/dev/null || echo "未知时间")
    BACKUP_SIZE=$(du -h "$LATEST_BACKUP" 2>/dev/null | cut -f1 || echo "未知大小")
    echo "   ✅ 备份文件数: $BACKUP_COUNT" >> $REPORT_FILE
    echo "       最新备份: $(basename $LATEST_BACKUP)" >> $REPORT_FILE
    echo "       备份时间: $BACKUP_TIME" >> $REPORT_FILE
    echo "       备份大小: $BACKUP_SIZE" >> $REPORT_FILE
else
    echo "   ⚠️ 未找到备份文件" >> $REPORT_FILE
fi
echo "" >> $REPORT_FILE

# 7. 监控日志检查
echo "7. 监控日志检查:" >> $REPORT_FILE
if [ -f "/Users/tuqibiao/.openclaw/workspace/monitoring/context_simple.log" ]; then
    LOG_LINES=$(wc -l < /Users/tuqibiao/.openclaw/workspace/monitoring/context_simple.log)
    LAST_LOG_TIME=$(tail -1 /Users/tuqibiao/.openclaw/workspace/monitoring/context_simple.log 2>/dev/null | grep -o "2026-[0-9:-]*" || echo "未知")
    echo "   ✅ 监控日志行数: $LOG_LINES" >> $REPORT_FILE
    echo "       最后记录时间: $LAST_LOG_TIME" >> $REPORT_FILE
else
    echo "   ⚠️ 监控日志文件不存在" >> $REPORT_FILE
fi
echo "" >> $REPORT_FILE

# 8. 总体评估
echo "8. 总体评估:" >> $REPORT_FILE
ISSUES=0

# 检查问题
if [ $OPENCLAW_PROCESSES -eq 0 ]; then
    echo "   ⚠️ 问题: OpenClaw进程未运行" >> $REPORT_FILE
    ISSUES=$((ISSUES+1))
fi

if [ ! -f "/Users/tuqibiao/.openclaw/workspace/memory/2026-03-16.md" ]; then
    echo "   ⚠️ 问题: 今日记忆文件缺失" >> $REPORT_FILE
    ISSUES=$((ISSUES+1))
fi

if [ $BACKUP_COUNT -eq 0 ]; then
    echo "   ⚠️ 问题: 无备份文件" >> $REPORT_FILE
    ISSUES=$((ISSUES+1))
fi

if [ $ISSUES -eq 0 ]; then
    echo "   ✅ 系统状态良好，未发现问题" >> $REPORT_FILE
else
    echo "   ⚠️ 发现 $ISSUES 个问题，建议检查" >> $REPORT_FILE
fi
echo "" >> $REPORT_FILE

echo "=== 报告生成完成 ===" >> $REPORT_FILE
echo "报告文件: $REPORT_FILE" >> $REPORT_FILE

# 记录到日志
echo "$(date '+%Y-%m-%d %H:%M:%S') - 健康检查完成，报告: $(basename $REPORT_FILE)" >> $LOG_FILE

# 保留最近10个报告
cd $REPORT_DIR
ls -t health_*.txt 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true

echo "健康检查完成，报告已保存到: $REPORT_FILE"
