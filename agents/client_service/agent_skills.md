# 客户服务Agent技能配置

## 可用技能列表

### 核心分析技能
1. **stock-watcher**
   - **功能**: 股票观察列表管理，持仓跟踪
   - **权限**: 已授权
   - **使用频率**: 高频
   - **配置状态**: 已安装，可用
   - **主要用途**: 客户持仓跟踪、表现监控

2. **stock-analysis**
   - **功能**: 股票深度分析，8维度评分
   - **权限**: 已授权
   - **使用频率**: 高频
   - **配置状态**: 已安装，可用
   - **主要用途**: 持仓股票基本面+技术面分析

3. **data-analyst**
   - **功能**: 数据分析与可视化，报告生成
   - **权限**: 已授权
   - **使用频率**: 高频
   - **配置状态**: 已安装，可用
   - **主要用途**: 投资组合分析、报告图表制作

### 数据支持技能
4. **qveris-official**
   - **功能**: 多市场实时数据查询
   - **权限**: 已授权
   - **使用频率**: 中频
   - **配置状态**: 已安装，需验证API Key
   - **主要用途**: 获取实时行情、财务数据

### 报告生成技能
5. **feishu-doc** (通过message工具)
   - **功能**: 飞书文档创建与编辑
   - **权限**: 已授权
   - **使用频率**: 高频
   - **配置状态**: 已配置，可用
   - **主要用途**: 投资报告生成与推送

### 协作技能
6. **sessions_send** (通过subagent工具)
   - **功能**: 与其他Agent通信协作
   - **权限**: 已授权
   - **使用频率**: 中频
   - **配置状态**: 已配置，可用
   - **主要用途**: 请求专业Agent支持

## 技能使用规范

### 持仓分析工作流
```
1. 获取持仓数据 → stock-watcher
2. 个股深度分析 → stock-analysis  
3. 组合风险评估 → data-analyst
4. 实时数据更新 → qveris-official
5. 报告生成交付 → feishu-doc + data-analyst
```

### 资产配置工作流
```
1. 客户风险测评 → data-analyst (问卷分析)
2. 市场环境分析 → 请求市场分析Agent支持
3. 配置方案设计 → data-analyst + 专业模型
4. 方案演示说明 → feishu-doc + 可视化图表
```

### 报告生成标准
1. **格式标准**: 使用飞书文档模板
2. **内容结构**: 概览→分析→建议→展望
3. **数据要求**: 使用最新可用数据
4. **交付时效**: 按约定时间准时交付
5. **质量控制**: 通过质量评审Agent审核

## 技能调用示例

### 持仓分析示例
```python
# 使用stock-watcher跟踪持仓
from stock_watcher import PortfolioTracker
tracker = PortfolioTracker()
portfolio = tracker.get_portfolio("client_001")
performance = tracker.analyze_performance(portfolio)

# 使用stock-analysis进行深度分析
from stock_analysis import StockAnalyzer
analyzer = StockAnalyzer()
for stock in portfolio.holdings:
    analysis = analyzer.analyze(stock.code)
    risk_score = analyzer.calculate_risk_score(analysis)
```

### 报告生成示例
```python
# 使用data-analyst生成报告
from data_analyst import ReportGenerator
generator = ReportGenerator()
report = generator.create_portfolio_report(
    portfolio=portfolio,
    analysis=analysis,
    period="monthly"
)

# 使用feishu-doc推送报告
from feishu_doc import FeishuClient
client = FeishuClient()
doc_url = client.create_document(
    title=f"持仓分析报告-{datetime.now().strftime('%Y%m%d')}",
    content=report.to_markdown()
)
```

## 权限配置
- **数据访问**: 可读取客户持仓数据（需授权）
- **技能调用**: 允许调用上述所有技能
- **文档创建**: 允许创建飞书文档
- **Agent协作**: 允许与其他Agent通信
- **限制**: 不可修改客户核心数据，不可创建新skill

## 监控指标
- **技能调用成功率**: 目标≥99%
- **报告生成时效**: 目标≤约定时间的90%
- **数据准确性**: 目标≥98%
- **协作效率**: 跨Agent请求响应时间≤15分钟