# 上下文管理优化计划
## 立即执行的工作流程改进

**目标**：减少上下文积累，防止系统崩溃  
**执行时间**：2026年3月16日 13:18  
**当前状态**：上下文使用率152%，压缩13次

---

## 一、立即实施的优化措施

### 1.1 工作模式优化
```python
# 优化前：长对话，大量上下文积累
def old_workflow():
    # 长时间对话，上下文不断积累
    conversation_history = load_all_history()  # 加载所有历史
    # ... 长时间工作 ...

# 优化后：模块化，定期清理
def optimized_workflow():
    # 模块1：独立任务，独立上下文
    task1_result = execute_task_with_fresh_context(task1)
    save_result(task1_result)
    
    # 模块2：独立任务，独立上下文  
    task2_result = execute_task_with_fresh_context(task2)
    save_result(task2_result)
    
    # 只保留结果，不保留完整对话历史
```

### 1.2 记忆管理策略
```
✅ 立即实施：
1. 每次重要操作后立即保存到记忆文件
2. 定期清理会话中的临时数据
3. 使用文件存储代替上下文存储
4. 建立记忆索引系统，按需加载
```

### 1.3 工具使用规范
| 工具 | 优化前 | 优化后 |
|------|--------|--------|
| `read` | 读取整个文件 | 使用offset/limit读取部分 |
| `exec` | 输出全部显示 | 只显示关键信息，保存到文件 |
| 模型调用 | 长对话 | 短任务，保存结果到文件 |
| 记忆管理 | 全部在上下文 | 主要在外存，按需加载 |

---

## 二、技术实现方案

### 2.1 上下文监控脚本
```bash
#!/bin/bash
# context_monitor.sh
# 实时监控上下文使用情况

while true; do
    # 获取当前上下文使用率
    context_usage=$(openclaw session status | grep "Context:" | awk '{print $2}')
    usage_percent=$(echo $context_usage | sed 's|/.*||' | sed 's/[^0-9]//g')
    limit=$(echo $context_usage | sed 's|.*/||' | sed 's/[^0-9]//g')
    
    # 计算百分比
    if [ -n "$usage_percent" ] && [ -n "$limit" ]; then
        percent=$((usage_percent * 100 / limit))
        
        # 告警逻辑
        if [ $percent -gt 80 ]; then
            echo "🚨 上下文使用率: ${percent}% (${usage_percent}/${limit})"
            echo "建议：立即保存工作并清理上下文"
            
            # 自动保存重要数据
            save_important_data
            
            if [ $percent -gt 120 ]; then
                echo "⚠️ 严重超限，建议重启会话"
            fi
        else
            echo "✅ 上下文使用率: ${percent}% (正常)"
        fi
    fi
    
    sleep 60  # 每分钟检查一次
done
```

### 2.2 自动保存机制
```python
# auto_save.py
import os
import json
from datetime import datetime

class AutoSaveManager:
    def __init__(self, workspace_path):
        self.workspace = workspace_path
        self.save_points = []
        
    def save_important_data(self, data_type, data):
        """自动保存重要数据到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_type}_{timestamp}.json"
        filepath = os.path.join(self.workspace, "auto_save", filename)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 保存数据
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": timestamp,
                "data_type": data_type,
                "data": data
            }, f, ensure_ascii=False, indent=2)
        
        # 记录保存点
        self.save_points.append({
            "time": timestamp,
            "type": data_type,
            "file": filename
        })
        
        # 清理旧的保存点（保留最近10个）
        if len(self.save_points) > 10:
            old_point = self.save_points.pop(0)
            old_file = os.path.join(self.workspace, "auto_save", old_point["file"])
            if os.path.exists(old_file):
                os.remove(old_file)
        
        return filepath
    
    def get_recovery_point(self):
        """获取最近的恢复点"""
        if self.save_points:
            return self.save_points[-1]
        return None
```

### 2.3 工作流优化模板
```python
# optimized_workflow_template.py
from contextlib import contextmanager

@contextmanager
def fresh_context_task(task_name, max_context_percent=70):
    """
    在新鲜上下文中执行任务的上下文管理器
    
    参数：
    - task_name: 任务名称
    - max_context_percent: 最大上下文使用率阈值
    """
    print(f"🚀 开始任务: {task_name}")
    
    try:
        # 检查当前上下文状态
        current_context = get_context_usage()
        if current_context > max_context_percent:
            print(f"⚠️ 上下文使用率较高: {current_context}%")
            print("建议先清理上下文或保存当前工作")
        
        # 执行任务
        yield
        
        # 任务完成后自动保存结果
        save_task_results(task_name)
        
        print(f"✅ 任务完成: {task_name}")
        
    except Exception as e:
        print(f"❌ 任务失败: {task_name}, 错误: {str(e)}")
        save_error_log(task_name, str(e))
        raise
```

---

## 三、立即执行的优化操作

### 3.1 创建监控目录结构
```bash
# 创建自动保存和监控目录
mkdir -p /Users/tuqibiao/.openclaw/workspace/auto_save
mkdir -p /Users/tuqibiao/.openclaw/workspace/monitoring
mkdir -p /Users/tuqibiao/.openclaw/workspace/optimized_workflows
```

### 3.2 设置上下文监控
```bash
# 创建监控脚本
cat > /Users/tuqibiao/.openclaw/workspace/monitoring/context_monitor.sh << 'EOF'
#!/bin/bash
# 上下文监控脚本

LOG_FILE="/Users/tuqibiao/.openclaw/workspace/monitoring/context_log.txt"
ALERT_THRESHOLD=80
CRITICAL_THRESHOLD=120

while true; do
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    
    # 获取上下文信息（简化版本）
    # 实际实现需要解析openclaw session status输出
    CONTEXT_INFO="当前无法获取准确上下文信息"
    
    # 记录到日志
    echo "[$TIMESTAMP] $CONTEXT_INFO" >> $LOG_FILE
    
    # 检查日志文件大小
    LOG_SIZE=$(wc -l < $LOG_FILE)
    if [ $LOG_SIZE -gt 1000 ]; then
        # 保留最近1000行
        tail -n 1000 $LOG_FILE > $LOG_FILE.tmp
        mv $LOG_FILE.tmp $LOG_FILE
    fi
    
    sleep 300  # 每5分钟检查一次
done
EOF

chmod +x /Users/tuqibiao/.openclaw/workspace/monitoring/context_monitor.sh
```

### 3.3 优化当前工作模式
```bash
# 立即清理不必要的上下文
echo "开始优化当前工作模式..."

# 1. 保存当前重要状态
echo "保存当前Agent配置状态..."
cp -r /Users/tuqibiao/.openclaw/workspace/agents/ /tmp/agents_backup_$(date +%Y%m%d_%H%M%S)

# 2. 清理临时文件
echo "清理临时文件..."
find /tmp -name "openclaw_*" -mtime +1 -delete 2>/dev/null || true

# 3. 优化记忆文件结构
echo "优化记忆文件结构..."
# 将今天的记忆文件备份
cp /Users/tuqibiao/.openclaw/workspace/memory/2026-03-16.md /tmp/memory_backup_$(date +%Y%m%d).md
```

---

## 四、监控告警设置

### 4.1 创建健康检查脚本
```bash
cat > /Users/tuqibiao/.openclaw/workspace/monitoring/health_check.sh << 'EOF'
#!/bin/bash
# 系统健康检查脚本

CHECK_TIME=$(date "+%Y-%m-%d %H:%M:%S")
REPORT_FILE="/Users/tuqibiao/.openclaw/workspace/monitoring/health_report.txt"

echo "=== 系统健康检查报告 ===" > $REPORT_FILE
echo "检查时间: $CHECK_TIME" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 1. 检查磁盘空间
echo "1. 磁盘空间检查:" >> $REPORT_FILE
df -h /Users/tuqibiao/.openclaw/workspace >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 2. 检查内存使用
echo "2. 内存使用检查:" >> $REPORT_FILE
free -h >> $REPORT_FILE 2>/dev/null || echo "内存信息不可用" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 3. 检查进程状态
echo "3. OpenClaw进程检查:" >> $REPORT_FILE
ps aux | grep -i openclaw | grep -v grep >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 4. 检查定时任务
echo "4. 定时任务检查:" >> $REPORT_FILE
openclaw cron list 2>/dev/null | head -20 >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 5. 检查工作区文件
echo "5. 工作区关键文件检查:" >> $REPORT_FILE
ls -la /Users/tuqibiao/.openclaw/workspace/memory/2026-03-16.md >> $REPORT_FILE
ls -la /Users/tuqibiao/.openclaw/workspace/agent_registry.json >> $REPORT_FILE
echo "" >> $REPORT_FILE

echo "=== 检查完成 ===" >> $REPORT_FILE

# 发送通知（如果配置了通知渠道）
if [ -f "/Users/tuqibiao/.openclaw/workspace/monitoring/send_alert.sh" ]; then
    /Users/tuqibiao/.openclaw/workspace/monitoring/send_alert.sh "系统健康检查完成"
fi

echo "健康检查报告已保存到: $REPORT_FILE"
EOF

chmod +x /Users/tuqibiao/.openclaw/workspace/monitoring/health_check.sh
```

### 4.2 设置定时健康检查
```bash
# 创建cron任务进行定期健康检查
cat > /Users/tuqibiao/.openclaw/workspace/monitoring/setup_cron.sh << 'EOF'
#!/bin/bash
# 设置定时健康检查

CRON_JOB="0 */2 * * * /Users/tuqibiao/.openclaw/workspace/monitoring/health_check.sh"

# 添加到当前用户的crontab
(crontab -l 2>/dev/null | grep -v "health_check.sh"; echo "$CRON_JOB") | crontab -

echo "定时健康检查已设置：每2小时执行一次"
echo "当前crontab内容："
crontab -l
EOF

chmod +x /Users/tuqibiao/.openclaw/workspace/monitoring/setup_cron.sh
```

---

## 五、备份机制完善

### 5.1 创建自动备份脚本
```bash
cat > /Users/tuqibiao/.openclaw/workspace/monitoring/auto_backup.sh << 'EOF'
#!/bin/bash
# 自动备份脚本

BACKUP_DIR="/Users/tuqibiao/.openclaw/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="openclaw_backup_${TIMESTAMP}.tar.gz"

# 创建备份目录
mkdir -p $BACKUP_DIR

echo "开始备份OpenClaw工作区..."
echo "备份时间: $(date)"

# 备份关键目录
tar -czf $BACKUP_DIR/$BACKUP_NAME \
    /Users/tuqibiao/.openclaw/workspace \
    /Users/tuqibiao/.openclaw/config \
    /Users/tuqibiao/.openclaw/cron 2>/dev/null

# 检查备份是否成功
if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h $BACKUP_DIR/$BACKUP_NAME | cut -f1)
    echo "✅ 备份成功: $BACKUP_NAME (大小: $BACKUP_SIZE)"
    
    # 保留最近7天的备份
    find $BACKUP_DIR -name "openclaw_backup_*.tar.gz" -mtime +7 -delete
    
    # 记录备份日志
    echo "$(date): 备份成功 - $BACKUP_NAME ($BACKUP_SIZE)" >> $BACKUP_DIR/backup_log.txt
else
    echo "❌ 备份失败"
    echo "$(date): 备份失败" >> $BACKUP_DIR/backup_log.txt
fi
EOF

chmod +x /Users/tuqibiao/.openclaw/workspace/monitoring/auto_backup.sh
```

### 5.2 设置每日自动备份
```bash
# 创建每日备份cron任务
cat > /Users/tuqibao/.openclaw/workspace/monitoring/setup_backup_cron.sh << 'EOF'
#!/bin/bash
# 设置每日自动备份

CRON_JOB="0 2 * * * /Users/tuqibiao/.openclaw/workspace/monitoring/auto_backup.sh"

# 添加到当前用户的crontab
(crontab -l 2>/dev/null | grep -v "auto_backup.sh"; echo "$CRON_JOB") | crontab -

echo "每日自动备份已设置：每天凌晨2点执行"
echo "当前crontab内容："
crontab -l
EOF

chmod +x /Users/tuqibiao/.openclaw/workspace/monitoring/setup_backup_cron.sh
```

---

## 六、立即执行清单

### ✅ 已完成
1. [x] 创建上下文管理优化计划文档
2. [x] 创建监控目录结构
3. [x] 创建上下文监控脚本框架
4. [x] 创建健康检查脚本
5. [x] 创建自动备份脚本

### ⏳ 进行中
6. [ ] 更新Command Line Tools（brew update正在运行）
7. [ ] 执行优化当前工作模式操作
8. [ ] 设置定时健康检查cron任务
9. [ ] 设置每日自动备份cron任务

### 📋 待执行
10. [ ] 测试监控脚本功能
11. [ ] 验证备份恢复流程
12. [ ] 优化Agent工作流程以减少上下文
13. [ ] 建立实时告警通知机制

---

## 七、预期效果

### 短期效果（今日内）
1. 上下文使用率得到控制
2. 系统稳定性提升
3. 建立基础监控和备份机制

### 中期效果（一周内）
1. 工作流程优化，减少上下文积累
2. 自动监控告警系统运行
3. 定期备份机制完善

### 长期效果（一月内）
1. 系统稳定性大幅提升
2. 工作效率提高
3. 数据安全有保障
4. 可应对更高复杂度任务

---

## 八、风险控制

### 实施风险
1. **脚本错误**：所有脚本先测试再部署
2. **cron任务冲突**：检查现有cron任务避免冲突
3. **磁盘空间**：监控备份文件大小
4. **系统负载**：监控脚本执行对系统的影响

### 应对措施
1. **逐步实施**：先测试，再小范围部署，最后全面实施
2. **监控反馈**：实施后密切监控系统状态
3. **回滚计划**：准备快速回滚方案
4. **用户通知**：重要变更前通知用户

---

**执行状态**：优化计划已制定，立即开始实施  
**预计完成时间**：今日内完成核心优化  
**监控指标**：上下文使用率、系统稳定性、备份完整性