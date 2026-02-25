# Skill: biage-premarket-analyzer v2.0

## 功能概述
板块阵型分析器 - 自动识别龙头和中军，评估板块健康度

## 核心能力
1. 龙头候选扫描与评分
2. 中军候选识别
3. 板块阵型健康度评估
4. 实时阵型报告生成

## 文件结构

```
skills/biage-premarket-analyzer/
├── SKILL.md                    # 本文件
├── formation_analyzer.py       # 主分析器
├── dragon_scanner.py          # 龙头扫描模块
├── general_scanner.py         # 中军扫描模块
├── formation_reporter.py      # 报告生成模块
├── templates/
│   └── alert_template.md      # 提醒模板
└── data/
    └── formation_cache/       # 缓存目录
```

## 快速开始

### 1. 运行每日扫描
```bash
python formation_analyzer.py --scan
```

### 2. 分析特定板块
```bash
python formation_analyzer.py --sector "AI" --date 20250224
```

### 3. 生成报告
```bash
python formation_analyzer.py --report
```

## 配置参数

### 龙头识别阈值
```python
DRAGON_CONFIG = {
    'market_cap_min': 30,      # 最小市值(亿)
    'market_cap_max': 500,     # 最大市值(亿)
    'optimal_cap_range': (50, 300),  # 最佳市值区间
    'min_turnover': 3,         # 最小换手率(%)
    'optimal_turnover': (5, 20),  # 最佳换手率区间
    'min_lianban': 2,          # 最小连板数
    'optimal_first_time': '10:00',  # 最佳首板时间
}
```

### 中军识别阈值
```python
GENERAL_CONFIG = {
    'min_market_cap': 500,     # 最小市值(亿)
    'optimal_market_cap': 1000,  # 最佳市值
    'max_daily_change': 9.5,   # 最大日涨幅(避免连板)
    'optimal_change_range': (3, 8),  # 最佳日涨幅区间
    'require_institution': True,  # 需要机构参与
}
```

### 阵型评分权重
```python
FORMATION_WEIGHTS = {
    'dragon': 0.40,      # 先锋权重
    'general': 0.35,     # 中军权重
    'followers': 0.25,   # 后排权重
}
```

## 输出格式

### 标准阵型报告
```markdown
【季节判断】XX期
【主线板块】XX板块

【板块阵型分析】

◆ 龙头候选:
  1. XXX（代码）
     - 市值：XX亿
     - 连板数：X板
     - 涨停时间：XX:XX
     - 换手率：X%
     - 龙虎榜：游资/量化/机构
     - 龙头潜力：高/中/低（原因）

◆ 中军候选:
  1. XXX（代码）
     - 市值：XX亿
     - 涨幅：X%
     - 龙虎榜：机构买入
     - 中军地位：核心/跟风

【阵型健康度】评分：XX/100
- 先锋：✓/✗（是否有连板龙头）
- 中军：✓/✗（是否有机构坐镇）
- 后排：✓/✗（是否有补涨跟随）
- 整体评价：进攻型/防守型/松散型

【操作建议】...
```

## API接口

### Python调用
```python
from formation_analyzer import FormationAnalyzer

# 初始化分析器
analyzer = FormationAnalyzer()

# 扫描龙头
dragons = analyzer.scan_dragon_candidates(sector_filter=['AI', '科技'])

# 扫描中军
generals = analyzer.scan_general_candidates(sector_filter=['AI', '科技'])

# 评估阵型
formation = analyzer.evaluate_formation(dragons, generals)

# 生成报告
report = analyzer.generate_report(sector="AI/科技")
print(report)
```

### 命令行调用
```bash
# 完整分析
python formation_analyzer.py --full --sector "AI" --output report.md

# 仅扫描龙头
python formation_analyzer.py --dragons-only

# 仅扫描中军
python formation_analyzer.py --generals-only

# 对比分析
python formation_analyzer.py --compare 20250220 20250224
```

## 数据依赖

### 必需数据
- 当日涨停股池 (ak.stock_zt_pool_em)
- A股实时行情 (ak.stock_zh_a_spot_em)
- 龙虎榜数据 (ak.stock_lhb_detail_daily_sina)

### 可选数据
- 板块资金流向
- 个股历史数据
- 机构持仓数据

## 注意事项

1. **数据时效性**: 确保数据为当日最新
2. **市场变化**: 阈值参数需根据市场风格调整
3. **风险控制**: 阵型分析仅供参考，不构成投资建议
4. **回测验证**: 建议先用历史数据验证有效性

## 更新日志

### v2.0 (2025-02)
- 新增龙头与中军识别体系
- 新增阵型健康度评估
- 新增实时提醒模板
- 优化评分算法

### v1.0 (2025-01)
- 基础涨停扫描功能
- 简单的板块分析

## 参考资料
- 《龙头与中军特征分析报告》
- 《庄稼人战法》
- AKShare文档
