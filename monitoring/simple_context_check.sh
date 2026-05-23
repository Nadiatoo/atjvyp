#!/bin/bash
# 简单上下文检查脚本

LOG_FILE="/Users/tuqibiao/.openclaw/workspace/monitoring/context_simple.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# 记录基本系统信息
echo "=== 系统检查 $TIMESTAMP ===" >> $LOG_FILE
echo "当前时间: $TIMESTAMP" >> $LOG_FILE
echo "工作目录: $(pwd)" >> $LOG_FILE
echo "用户: $(whoami)" >> $LOG_FILE
echo "" >> $LOG_FILE

# 检查磁盘空间
echo "磁盘空间:" >> $LOG_FILE
df -h /Users/tuqibiao/.openclaw/workspace 2>/dev/null | tail -1 >> $LOG_FILE
echo "" >> $LOG_FILE

# 检查内存使用（如果可用）
if command -v free &> /dev/null; then
    echo "内存使用:" >> $LOG_FILE
    free -h 2>/dev/null | head -2 >> $LOG_FILE
    echo "" >> $LOG_FILE
fi

# 检查OpenClaw进程
echo "OpenClaw进程:" >> $LOG_FILE
ps aux | grep -i openclaw | grep -v grep | wc -l >> $LOG_FILE
echo "" >> $LOG_FILE

echo "=== 检查完成 ===" >> $LOG_FILE

# 限制日志文件大小
if [ $(wc -l < $LOG_FILE) -gt 100 ]; then
    tail -n 50 $LOG_FILE > $LOG_FILE.tmp
    mv $LOG_FILE.tmp $LOG_FILE
fi

echo "监控日志已更新: $LOG_FILE"
