# 彪哥战法 × Qlib 融合项目

本项目将 **彪哥战法** (庄稼人战法进化版) 与 **微软Qlib量化平台** 进行融合，实现AI驱动的四季判断和量化回测。

---

## 📁 项目结构

```
qlib_biaoge/
├── README.md                      # 本文件
├── run_backtest.sh               # 一键运行脚本 ⭐
├── akshare_to_qlib.py            # 数据对接脚本 (选项A)
├── biaoge_season_model.py        # 四季判断模型 (选项B)
├── biaoge_backtest.py            # 简化版回测引擎 (选项C)
├── biaoge_qlib_workflow.py       # 完整Qlib工作流 (选项C)
├── biaoge_qlib_integration.py    # Qlib整合示例
├── workflow_config_biaoge.yaml   # Qlib工作流配置
└── biaoge_season_model.pkl       # 训练好的模型(自动生成)
```

---

## 🚀 快速开始 (三种方式)

### 方式一: 一键运行 (推荐)

```bash
# 进入项目目录
cd qlib_biaoge

# 运行简化版回测演示
./run_backtest.sh demo

# 训练四季判断模型
./run_backtest.sh season

# 准备完整回测数据
./run_backtest.sh prepare
```

### 方式二: 分步运行

#### 步骤1: 安装依赖

```bash
# 基础依赖
pip install akshare pandas numpy matplotlib scikit-learn joblib

# 如需完整Qlib功能 (可选)
pip install pyqlib
```

#### 步骤2: 数据对接 (选项A)

```bash
# 转换akshare数据到Qlib格式
python akshare_to_qlib.py --start 2020-01-01 --end 2026-03-01 --max-stocks 100
```

#### 步骤3: 训练四季判断模型 (选项B)

```bash
python biaoge_season_model.py
```

输出:
- 模型文件: `biaoge_season_model.pkl`
- 分析图表: `biaoge_season_analysis.png`

#### 步骤4: 运行回测 (选项C)

```bash
# 简化版回测 (无需完整Qlib)
python biaoge_backtest.py --action backtest --max-stocks 50 --topk 10

# 完整Qlib工作流 (需要安装pyqlib)
python biaoge_qlib_workflow.py --mode full
```

### 方式三: Python代码集成

```python
# 1. 导入模块
from biaoge_season_model import BiaogeSeasonModel
from biaoge_backtest import BiaogeBacktestEngine

# 2. 加载四季判断模型
model = BiaogeSeasonModel()
model.load('biaoge_season_model.pkl')

# 3. 预测当前季节
features = get_market_features()  # 获取市场特征
season = model.predict(features)
season_name = ['春播', '夏长', '秋收', '冬藏'][season[0]]
print(f"当前季节: {season_name}")

# 4. 运行回测
engine = BiaogeBacktestEngine()
result = engine.run_backtest_simple(
    start_date="2024-01-01",
    end_date="2026-03-01",
    topk=20
)
```

---

## 📊 四季判断模型详解

### 四季定义

| 季节 | 代码 | 市场特征 | 交易策略 | 建议仓位 |
|-----|------|---------|---------|---------|
| 春播 | 0 | 反弹初期, 放量上涨 | 逐步建仓 | 30-50% |
| 夏长 | 1 | 强势上涨, 量价齐升 | 重仓持股 | 70-90% |
| 秋收 | 2 | 高位震荡, 量能不济 | 逢高减仓 | 30-50% |
| 冬藏 | 3 | 下跌趋势, 量能萎缩 | 空仓观望 | 0-10% |

### 特征因子 (13个)

| 因子 | 说明 | 重要性 |
|-----|------|--------|
| `volume_ma20` | 20日量比 | ⭐⭐⭐⭐⭐ |
| `momentum_20` | 20日动量 | ⭐⭐⭐⭐ |
| `bb_position` | 布林带位置 | ⭐⭐⭐⭐ |
| `macd` | MACD指标 | ⭐⭐⭐ |
| `volume_ma5` | 5日量比 | ⭐⭐⭐ |
| `momentum_5` | 5日动量 | ⭐⭐⭐ |
| `ma20` | 20日均线位置 | ⭐⭐⭐ |
| `ma60` | 60日均线位置 | ⭐⭐ |
| `rsi` | RSI指标 | ⭐⭐ |
| `macd_signal` | MACD信号线 | ⭐⭐ |

### 运行结果示例

```
============================================================
彪哥战法 - AI四季判断模型原型
============================================================

【步骤1】数据准备
模拟数据生成完成: 1549 条样本
四季分布:
0.0     56   (春播)
1.0    419   (夏长)
2.0    390   (秋收)
3.0    684   (冬藏)

【步骤2】模型训练
模型训练完成, 测试集准确率: 0.9871

分类报告:
              precision    recall  f1-score   support
  春播         1.00       0.75      0.86        12
  夏长         1.00       0.99      0.99        67
  秋收         0.98       1.00      0.99        65
  冬藏         0.98       1.00      0.99       166

【步骤3】生成交易信号
最近10个交易日信号:
日期          季节    置信度    建议仓位
2026-02-27   冬藏    95.8%     0%
2026-02-26   冬藏    99.6%     0%
2026-02-20   冬藏    91.3%     0%
2026-02-18   春播    53.5%     40%
```

---

## 🔄 Qlib回测工作流详解

### 数据流

```
akshare 实时数据
      ↓
akshare_to_qlib.py (数据转换)
      ↓
Qlib格式数据 (.bin)
      ↓
BiaogeSeasonModel (四季判断)
      ↓
Alpha158 因子数据集
      ↓
LightGBM 模型训练
      ↓
TopkDropout 策略
      ↓
回测引擎
      ↓
绩效分析报告
```

### 工作流配置

```yaml
# workflow_config_biaoge.yaml
qlib_init:
  provider_uri: "~/.qlib/qlib_data/cn_data"
  region: cn

task:
  model:
    class: LGBModel
    kwargs:
      loss: mse
      learning_rate: 0.0421
      max_depth: 8
      
  dataset:
    class: DatasetH
    kwargs:
      handler:
        class: Alpha158  # 158个Alpha因子
      segments:
        train: ["2020-01-01", "2023-12-31"]
        valid: ["2024-01-01", "2024-06-30"]
        test: ["2024-07-01", "2026-03-01"]
        
  record:
    - class: SignalRecord      # 信号分析
    - class: PortAnaRecord     # 组合分析
```

### 四季调整策略

不同季节使用不同的策略参数:

```python
season_config = {
    'spring': {'topk': 30, 'n_drop': 3},  # 春播: 精选,少换仓
    'summer': {'topk': 50, 'n_drop': 5},  # 夏长: 激进,高换仓
    'autumn': {'topk': 20, 'n_drop': 2},  # 秋收: 保守,少换仓
    'winter': {'topk': 0, 'n_drop': 0},   # 冬藏: 空仓
}
```

---

## 📈 回测绩效指标

运行回测后会输出:

| 指标 | 说明 |
|-----|------|
| **总收益率** | 回测期间累计收益 |
| **年化收益** | 按252交易日年化 |
| **夏普比率** | 风险调整后收益 |
| **最大回撤** | 最大亏损幅度 |
| **信息比率** | 相对基准超额收益 |
| **胜率** | 盈利交易占比 |

---

## 🎯 与现有彪哥战法的衔接

### 人工验证流程

```
┌─────────────────────────────────────────────┐
│  Step 1: AI判断                               │
│  模型输出当前季节 + 置信度                     │
│  例: 冬藏期 (置信度 95.8%)                    │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  Step 2: 人工复核                             │
│  结合市场情绪、板块轮动、消息面验证            │
│  例: 确认近期确实情绪低迷、跌停增多           │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  Step 3: 策略调整                             │
│  根据季节确定仓位和选股策略                    │
│  例: 冬藏期 → 空仓观望                        │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  Step 4: 执行交易                             │
│  按战法规则买卖，严格执行纪律                  │
└─────────────────────────────────────────────┘
```

---

## ⚠️ 注意事项

1. **数据质量**: akshare数据可能存在延迟，实盘前请验证
2. **模型过拟合**: 历史回测不代表未来表现，需持续优化
3. **季节标注**: 自动标注基于规则，建议人工校验修正
4. **参数调优**: 根据实际交易情况调整模型参数
5. **市场环境**: 模型在极端行情(如2015年股灾)可能失效

---

## 📚 参考文档

- [Qlib官方文档](https://qlib.readthedocs.io/)
- [Qlib GitHub](https://github.com/microsoft/qlib)
- [Akshare数据接口](https://www.akshare.xyz/)
- [LightGBM文档](https://lightgbm.readthedocs.io/)

---

## 🚀 后续优化方向

### 短期 (1-2周)
- [ ] 接入涨停跌停数据，完善情绪因子
- [ ] 添加板块轮动速度计算
- [ ] 优化四季标注规则

### 中期 (1-2月)
- [ ] 训练真实历史数据 (2020-2026)
- [ ] 添加行业/概念因子
- [ ] 实现实时数据流接入

### 长期 (3-6月)
- [ ] 强化学习端到端优化
- [ ] 多模型集成 (RF + LGB + NN)
- [ ] 实盘交易接入

---

## 📝 更新日志

**2026-03-01** - v1.0 初始版本
- ✅ 完成数据对接脚本 (akshare_to_qlib.py)
- ✅ 完成四季判断模型原型 (biaoge_season_model.py)
- ✅ 完成简化版回测引擎 (biaoge_backtest.py)
- ✅ 完成完整Qlib工作流 (biaoge_qlib_workflow.py)
- ✅ 完成一键运行脚本 (run_backtest.sh)
- ✅ 13个市场特征因子
- ✅ RandomForest分类模型
- ✅ 可视化分析报告

---

有问题随时问! 💪
