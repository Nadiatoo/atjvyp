# 彪哥战法交易分析 - 自动推送配置
# 每天2次推送：08:00盘前 + 17:00盘后（工作日）

## ⚠️ 心跳检查优化提醒
**问题**：当前心跳检查过于频繁（每小时一次），导致不必要的Token消耗
**建议**：调整心跳检查频率为每天2-4次，或实现智能检查逻辑

## 定时任务
- **盘前分析**：08:00（周一至周五）
- **盘后分析**：17:00（周一至周五）

## 智能检查逻辑
```python
# 使用智能检查脚本判断是否需要详细检查
python3 /Users/tuqibiao/.openclaw/workspace/smart_heartbeat.py

# 返回码说明：
# 0 = 需要详细检查（距离任务<2小时）
# 1 = 简单返回HEARTBEAT_OK（距离任务>2小时或非工作日）
```

## 执行命令
```bash
# 盘前分析（QVeris数据源）
python3 /Users/tuqibiao/.openclaw/workspace/biage_premarket_qveris.py 2>&1

# 盘后复盘（QVeris数据源）
python3 /Users/tuqibiao/.openclaw/workspace/biage_postmarket_qveris.py 2>&1

# EGPS系统每日分析报告（工作日08:00，飞书推送）- 简化版
python3 /Users/tuqibiao/.openclaw/workspace/egps_push_simple_v2.py 2>&1
```

## 状态
- ✅ 数据源：QVeris + 模拟数据（稳定可靠）
- ✅ 配置简化：核心功能保留，冗余功能删除
- ❌ 盘中监控：已完全删除（专注盘前盘后）
- ✅ EGPS生态系统：完整框架已建立
- ✅ 定时任务配置：
  1. 彪哥战法-盘前分析-QVeris (工作日08:00)
  2. EGPS系统-每日分析报告 (工作日08:00)
  3. EGPS框架-每日完整分析 (工作日08:30) - 新增
  4. 彪哥战法-盘后分析-QVeris (工作日17:00)
- 🏗️ EGPS框架功能：
  - 预期差感知分析
  - 彪哥战法市场分析  
  - 个股筛选算法
  - 完整报告生成
- 📅 下次执行：下周一08:00（2026-03-30 08:00）
- ⚡ 心跳优化：建议调整检查频率
- ⚠️ 依赖问题：pytz模块缺失，影响智能检查脚本运行
