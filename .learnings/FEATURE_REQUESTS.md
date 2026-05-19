# FEATURE_REQUESTS.md - 功能请求

## 使用说明
记录用户请求的功能、缺失的能力、改进建议等。

## 记录格式
```markdown
### [YYYY-MM-DD] 功能标题
**请求者**: [谁请求的]
**优先级**: critical | high | medium | low  
**描述**: [详细描述功能需求]
**使用场景**: [在什么情况下需要这个功能]
**预期效果**: [实现后能达到什么效果]
**相关技能**: [可能相关的现有技能]
**状态**: requested | planned | in_progress | completed | rejected
**完成时间**: [完成时间，如果已完成]
**备注**: [其他相关信息]
```

---

## 功能请求记录

### 2026-04-07 安装Agent-tools技能
**请求者**: 老涂  
**优先级**: high  
**描述**: 安装ai-agent-tools技能，增强AI代理能力
**使用场景**: 
1. 增强彪哥战法系统的自动化能力
2. 提供更多AI代理开发工具
3. 改进数据采集和分析流程
**预期效果**: 
1. 系统具备更强大的自动化工具
2. 提高市场数据分析效率
3. 增强系统自我改进能力
**相关技能**: agent-browser, self-improving-agent
**状态**: in_progress
**完成时间**: 
**备注**: 已安装agent-browser和self-improving-agent，继续寻找更多相关工具

### 2026-04-07 增强彪哥战法数据采集
**请求者**: 系统分析  
**优先级**: medium  
**描述**: 使用agent-browser增强市场数据采集能力
**使用场景**: 
1. 自动获取更多财经网站数据
2. 实时监控市场新闻和公告
3. 多源数据验证和整合
**预期效果**: 
1. 数据源更加丰富和可靠
2. 减少手动数据收集工作
3. 提高分析报告的全面性
**相关技能**: agent-browser, biage_premarket_eastmoney.py
**状态**: planned
**完成时间**: 
**备注**: 需要测试agent-browser与东方财富API的集成