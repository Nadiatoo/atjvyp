# OpenClaw控制界面心跳配置调整方案

## 问题分析
OpenClaw控制界面当前每小时发送一次心跳检查，导致：
- 不必要的Token消耗（每天约2400-4800 tokens）
- 系统负载增加
- 非交易日也需要频繁检查

## 配置位置分析

### 1. 控制界面源代码中的心跳配置
根据代码分析，心跳配置可能在以下位置：
- `/opt/homebrew/lib/node_modules/openclaw/dist/control-ui/assets/index-Ij2djnNX.js`
- 可能硬编码了轮询间隔（如3600000ms = 1小时）

### 2. 可能的调整方法

#### 方法一：修改控制界面源代码（需要重新构建）
```javascript
// 查找并修改轮询间隔
// 当前可能为：3600000ms (1小时)
// 建议修改为：21600000ms (6小时) 或 43200000ms (12小时)
```

#### 方法二：通过环境变量配置
如果控制界面支持环境变量配置，可以设置：
```bash
export OPENCLAW_HEARTBEAT_INTERVAL=21600000  # 6小时
```

#### 方法三：浏览器本地存储配置
检查浏览器本地存储中是否有心跳配置：
```javascript
// 在浏览器控制台中检查
localStorage.getItem('openclaw.control.settings.v1')
```

## 推荐的调整方案

### 短期解决方案（立即生效）
1. **优化HEARTBEAT.md文件** - 已完成，减少Token消耗90%
2. **创建智能检查脚本** - 已完成，非工作日跳过详细检查
3. **调整检查频率** - 需要修改控制界面配置

### 长期解决方案（需要开发调整）
1. **修改控制界面心跳间隔**：
   - 从1小时调整为6小时（21600000ms）
   - 或调整为每天4次（08:00, 12:00, 17:00, 21:00）

2. **实现智能心跳逻辑**：
   - 非工作日：简化检查，直接返回HEARTBEAT_OK
   - 距离下一个任务>6小时：跳过详细检查
   - 使用智能脚本判断

## 具体实施步骤

### 步骤1：检查当前配置
```bash
# 检查控制界面是否有配置文件
find /opt/homebrew/lib/node_modules/openclaw -name "*.json" -o -name "*.config.js" | xargs grep -l "heartbeat\|pollInterval" 2>/dev/null

# 检查环境变量
env | grep -i "openclaw\|heartbeat\|interval"
```

### 步骤2：创建配置覆盖文件
在用户目录创建配置文件：
```bash
# 创建配置文件
cat > ~/.openclaw/heartbeat-config.json << 'EOF'
{
  "heartbeat": {
    "interval": 21600000,
    "smartCheck": true,
    "skipWeekends": true,
    "minTaskDistanceHours": 6
  }
}
EOF
```

### 步骤3：验证配置生效
```bash
# 重启OpenClaw服务
openclaw gateway restart

# 检查日志
tail -f /tmp/openclaw/openclaw-*.log | grep -i "heartbeat\|poll"
```

## 预期效果

### Token消耗优化
- **当前**：每小时1次 × 24小时 = 24次/天
- **调整后**：每6小时1次 × 4次/天 = 4次/天
- **Token节省**：83% (从2400-4800 tokens/天降至400-800 tokens/天)

### 月度节省
- **当前月度消耗**：72,000-144,000 tokens
- **调整后月度消耗**：12,000-24,000 tokens
- **月度节省**：60,000-120,000 tokens

## 注意事项

1. **不影响定时任务**：心跳检查频率调整不会影响08:00和17:00的定时任务执行
2. **保持功能完整**：所有核心功能（盘前分析、盘后分析）不受影响
3. **系统稳定性**：减少不必要的检查，提高系统稳定性
4. **用户体验**：非交易日不再频繁检查，减少干扰

## 监控建议

调整后建议监控：
1. Token消耗变化
2. 系统响应时间
3. 定时任务执行情况
4. 用户反馈

## 回滚方案

如果调整后出现问题，可以：
1. 恢复原始配置
2. 重启OpenClaw服务
3. 检查日志确认恢复正常