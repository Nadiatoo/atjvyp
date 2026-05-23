# Skill注册表系统使用指南

## 概述

Skill注册表系统是一个仿操作系统的注册表功能，用于管理所有已安装和可用的skill。它提供了skill的发现、调用、状态监控和统计功能，可以大幅优化工作流程并节省Token使用。

## 核心功能

### 1. Skill自动扫描与注册
- 自动扫描用户安装的skill (`~/.openclaw/skills/`)
- 自动扫描系统自带的skill (`/opt/homebrew/lib/node_modules/openclaw/skills/`)
- 自动解析SKILL.md文件提取skill信息
- 智能分类（金融、系统、数据、AI等）

### 2. Skill发现与搜索
- 支持关键词搜索（名称、描述、标签）
- 支持分类过滤
- 支持来源过滤（用户/系统）
- 按使用频率排序

### 3. 使用统计与监控
- 记录每个skill的使用次数
- 记录最后使用时间
- 活跃/非活跃状态监控
- 生成使用报告

### 4. 快速调用接口
- 提供统一的skill调用接口
- 自动更新使用统计
- 支持skill依赖管理

## 文件结构

```
~/.openclaw/workspace/
├── skill_registry.json          # 注册表数据库
├── scripts/
│   └── skill_registry_manager.py # 注册表管理工具
├── docs/
│   └── skill_registry_guide.md  # 使用指南
└── skill_registry_report.md     # 自动生成的报告
```

## 快速开始

### 1. 初始化注册表

```bash
# 扫描所有skill并创建注册表
python3 ~/.openclaw/workspace/scripts/skill_registry_manager.py scan
```

### 2. 查看所有skill

```bash
# 列出所有skill
python3 ~/.openclaw/workspace/scripts/skill_registry_manager.py list

# 按分类列出
python3 ~/.openclaw/workspace/scripts/skill_registry_manager.py list --category finance

# 按来源列出
python3 ~/.openclaw/workspace/scripts/skill_registry_manager.py list --source user
```

### 3. 搜索skill

```bash
# 搜索包含关键词的skill
python3 ~/.openclaw/workspace/scripts/skill_registry_manager.py find --query "市场"
python3 ~/.openclaw/workspace/scripts/skill_registry_manager.py find --query "分析"
```

### 4. 生成报告

```bash
# 生成详细的使用报告
python3 ~/.openclaw/workspace/scripts/skill_registry_manager.py report
```

## 在OpenClaw中使用

### 1. 项目开始前检查可用skill

在执行任何项目前，先检查注册表中是否有现成的skill可用：

```python
# 伪代码示例
def check_available_skills(project_type):
    registry = SkillRegistry()
    
    # 根据项目类型搜索相关skill
    if project_type == "金融分析":
        skills = registry.find_skill("市场", "finance")
        skills.extend(registry.find_skill("股票", "finance"))
    elif project_type == "数据处理":
        skills = registry.find_skill("数据", "data")
    
    return skills
```

### 2. 调用skill时自动更新统计

```python
def execute_skill(skill_id, params):
    registry = SkillRegistry()
    skill_info = registry.get_skill(skill_id)
    
    if skill_info:
        # 更新使用统计
        registry.update_skill_usage(skill_id)
        
        # 执行skill
        result = call_skill(skill_info["location"], params)
        return result
    else:
        print(f"Skill {skill_id} 未找到")
        return None
```

### 3. 定期维护注册表

建议每周运行一次扫描和报告生成：

```bash
# 每周扫描新skill
python3 ~/.openclaw/workspace/scripts/skill_registry_manager.py scan

# 生成周报
python3 ~/.openclaw/workspace/scripts/skill_registry_manager.py report
```

## 分类系统

注册表使用以下分类：

| 分类 | 说明 | 示例skill |
|------|------|-----------|
| **system** | 系统管理类 | skill_registry_manager, healthcheck |
| **finance** | 金融交易类 | biage-market-analyzer, tushare-finance |
| **data** | 数据处理类 | biage-premarket-analyzer |
| **communication** | 通讯工具类 | feishu-doc, feishu-drive |
| **productivity** | 生产力工具类 | biage-report-generator |
| **development** | 开发工具类 | skill-creator |
| **media** | 媒体处理类 | - |
| **ai** | 人工智能类 | self-improving |

## 节省Token的策略

### 1. 避免重复开发
- 执行项目前先搜索注册表
- 重用现有skill而不是重新开发
- 积累可复用的skill库

### 2. 优化skill调用
- 使用注册表快速找到最合适的skill
- 记录skill使用频率，优先调用高频skill
- 避免调用不必要或功能重叠的skill

### 3. 智能skill推荐
- 根据项目类型自动推荐相关skill
- 根据历史使用记录推荐skill
- 根据skill评分和质量推荐

## 扩展功能

### 1. Skill评分系统
可以扩展为包含：
- 用户评分（1-5星）
- 成功率统计
- 执行效率评分
- 资源消耗评分

### 2. Skill依赖管理
- 自动检测skill依赖关系
- 依赖冲突解决
- 版本兼容性检查

### 3. Skill市场集成
- 从ClawHub自动发现新skill
- 一键安装和注册
- 更新通知和版本管理

## 最佳实践

1. **定期扫描**：每周至少扫描一次新skill
2. **及时注册**：新安装skill后立即注册
3. **使用统计**：关注高频使用的skill，优化其性能
4. **清理无用skill**：定期清理不再使用的skill
5. **备份注册表**：定期备份skill_registry.json文件

## 故障排除

### 常见问题

1. **扫描不到skill**
   - 检查skill目录权限
   - 确认SKILL.md文件存在
   - 检查文件编码（应为UTF-8）

2. **分类不正确**
   - 手动修改skill_registry.json中的category字段
   - 更新解析逻辑

3. **使用统计不更新**
   - 检查文件写入权限
   - 确认注册表文件未被锁定

### 手动修复

```bash
# 强制重新扫描
python3 ~/.openclaw/workspace/scripts/skill_registry_manager.py scan --force

# 手动编辑注册表
vim ~/.openclaw/workspace/skill_registry.json
```

## 未来规划

1. **Web界面**：提供可视化的skill管理界面
2. **API服务**：提供REST API供其他工具调用
3. **智能推荐**：基于AI的skill推荐引擎
4. **性能监控**：实时监控skill执行性能
5. **安全审计**：skill安全性和权限审计

---

**创建时间**: 2026-03-14  
**版本**: 1.0  
**维护者**: 富富 (OpenClaw Assistant)