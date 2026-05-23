#!/bin/bash
# 设置定时监控和备份任务

echo "当前crontab内容:"
crontab -l 2>/dev/null || echo "暂无crontab任务"

echo ""
echo "添加新的定时任务..."

# 创建临时crontab文件
TEMP_CRON=$(mktemp)

# 保留现有任务
crontab -l 2>/dev/null > $TEMP_CRON

# 添加新任务
echo "# OpenClaw监控任务 - 添加于 $(date '+%Y-%m-%d %H:%M:%S')" >> $TEMP_CRON
echo "*/30 * * * * /Users/tuqibiao/.openclaw/workspace/monitoring/simple_context_check.sh >/dev/null 2>&1" >> $TEMP_CRON
echo "0 2 * * * /Users/tuqibiao/.openclaw/workspace/monitoring/simple_backup.sh >/dev/null 2>&1" >> $TEMP_CRON
echo "0 9,17 * * 1-5 /Users/tuqibiao/.openclaw/workspace/monitoring/health_check.sh >/dev/null 2>&1" >> $TEMP_CRON

# 安装新的crontab
crontab $TEMP_CRON
rm -f $TEMP_CRON

echo ""
echo "新的crontab内容:"
crontab -l

echo ""
echo "定时任务设置完成:"
echo "1. 每30分钟执行上下文检查"
echo "2. 每天凌晨2点执行备份"
echo "3. 交易日9点和17点执行健康检查"
