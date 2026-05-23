#!/bin/bash

echo "🔍 会话清理验证检查"
echo "========================"
echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 检查会话目录
echo "📁 会话目录状态:"
echo "----------------"
SESSION_DIR="/Users/tuqibiao/.openclaw/agents/main/sessions"
BACKUP_DIR="/Users/tuqibiao/.openclaw/workspace/session_backup_20260416"

SESSION_COUNT=$(ls -1 "$SESSION_DIR"/*.jsonl 2>/dev/null | wc -l)
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.jsonl 2>/dev/null | wc -l)

echo "当前会话文件数: $SESSION_COUNT 个"
echo "备份会话文件数: $BACKUP_COUNT 个"
echo ""

# 2. 检查文件大小分布
echo "📊 文件大小分布:"
echo "----------------"
echo "当前会话目录:"
du -sh "$SESSION_DIR"
echo ""
echo "备份目录:"
du -sh "$BACKUP_DIR"
echo ""

# 3. 检查最近文件
echo "🕒 最近修改的文件:"
echo "----------------"
find "$SESSION_DIR" -name "*.jsonl" -mtime -7 | wc -l | xargs echo "最近7天内文件:"
find "$SESSION_DIR" -name "*.jsonl" -size +100k | wc -l | xargs echo "大于100KB的重要文件:"
echo ""

# 4. 检查服务状态
echo "⚙️ 服务状态检查:"
echo "----------------"
if pgrep -f "openclaw-gateway" > /dev/null; then
    echo "✅ OpenClaw网关服务: 运行中"
else
    echo "❌ OpenClaw网关服务: 未运行"
fi

# 5. 检查清理报告
echo ""
echo "📋 清理报告检查:"
echo "----------------"
if [ -f "$BACKUP_DIR/cleanup_report.md" ]; then
    echo "✅ 清理报告存在: $BACKUP_DIR/cleanup_report.md"
    echo "   报告摘要:"
    grep -A5 "## 清理统计" "$BACKUP_DIR/cleanup_report.md" | tail -5
else
    echo "❌ 清理报告不存在"
fi

echo ""
echo "========================"
echo "✅ 验证检查完成"
echo "建议: 每月执行一次类似清理，保持系统性能"