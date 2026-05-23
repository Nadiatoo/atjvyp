#!/bin/bash
# 简单备份脚本

BACKUP_DIR="/Users/tuqibiao/.openclaw/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="workspace_backup_${TIMESTAMP}.tar.gz"
LOG_FILE="/Users/tuqibiao/.openclaw/backups/backup_log.txt"

echo "开始备份工作区..."
echo "备份时间: $(date '+%Y-%m-%d %H:%M:%S')"

# 备份关键文件
BACKUP_FILES=(
    "/Users/tuqibiao/.openclaw/workspace/memory"
    "/Users/tuqibiao/.openclaw/workspace/agents"
    "/Users/tuqibiao/.openclaw/workspace/*.json"
    "/Users/tuqibiao/.openclaw/workspace/*.md"
)

# 创建备份
tar -czf $BACKUP_DIR/$BACKUP_NAME ${BACKUP_FILES[@]} 2>/dev/null

if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h $BACKUP_DIR/$BACKUP_NAME 2>/dev/null | cut -f1 || echo "未知")
    echo "✅ 备份成功: $BACKUP_NAME (大小: $BACKUP_SIZE)"
    
    # 记录日志
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 备份成功: $BACKUP_NAME ($BACKUP_SIZE)" >> $LOG_FILE
    
    # 保留最近5个备份
    cd $BACKUP_DIR
    ls -t workspace_backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true
else
    echo "❌ 备份失败"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 备份失败" >> $LOG_FILE
fi

echo "备份完成"
