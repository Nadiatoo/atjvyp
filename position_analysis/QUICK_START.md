# 持仓分析系统 - 快速开始指南

## 🚀 安装与配置

### 1. 安装依赖
```bash
cd position_analysis
pip install -r requirements.txt
```

### 2. 安装可选依赖（PDF报告）
```bash
# 安装wkhtmltopdf（macOS）
brew install wkhtmltopdf

# 安装wkhtmltopdf（Ubuntu/Debian）
sudo apt-get install wkhtmltopdf

# 安装wkhtmltopdf（Windows）
# 从 https://wkhtmltopdf.org/downloads.html 下载安装
```

### 3. 配置API密钥（可选）
```bash
# 设置QVeris API密钥（备用数据源）
export QVERIS_API_KEY="your_api_key_here"
```

## 📊 快速开始

### 方式一：使用示例数据
```bash
cd position_analysis/src
python main.py ../data/sample_portfolio.csv --client-name "测试客户"
```

### 方式二：使用自定义数据
1. 准备持仓数据文件（CSV或Excel格式）
2. 运行分析：
```bash
cd position_analysis/src
python main.py /path/to/your/portfolio.xlsx --client-name "客户姓名" --output-format all
```

## 📁 数据文件格式

### CSV格式示例
```csv
股票代码,股票名称,持仓数量,成本价,行业分类,买入日期,备注
000001,平安银行,1000,15.20,银行,2026-01-15,核心持仓
600036,招商银行,800,32.50,银行,2026-02-20,价值投资
000858,五粮液,500,180.30,食品饮料,2026-03-10,消费龙头
```

### Excel格式要求
- 文件扩展名: .xlsx 或 .xls
- 必需列: 股票代码, 股票名称, 持仓数量, 成本价
- 可选列: 行业分类, 买入日期, 备注

## 🛠️ 命令行参数

```bash
# 基本用法
python main.py <输入文件> [选项]

# 常用选项
--client-name <姓名>      # 客户名称（默认: 客户）
--analyst <姓名>          # 分析师名称（默认: 智能投顾系统）
--output-format <格式>    # 输出格式: md, html, pdf, all（默认: md）
--update-market          # 更新市场数据
--export-all            # 导出所有结果
--verbose               # 详细输出

# 示例
python main.py portfolio.csv --client-name "张三" --output-format all --verbose
```

## 📈 输出文件

分析完成后，系统会生成以下文件：

### 1. 报告文件（outputs/reports/）
- `客户名_持仓分析报告_时间戳.md` - Markdown格式报告
- `客户名_持仓分析报告_时间戳.html` - HTML格式报告
- `客户名_持仓分析报告_时间戳.pdf` - PDF格式报告（如启用）

### 2. 图表文件（outputs/charts/）
- 行业分布饼图
- 前十大持仓图
- 风险雷达图
- 压力测试图等

### 3. 数据文件（outputs/）
- `客户名_分析结果_时间戳.json` - 完整分析结果
- `客户名_分析摘要_时间戳.txt` - 文本摘要
- `客户名_持仓数据_时间戳.csv` - 处理后的持仓数据

## 🔧 高级使用

### 1. 集成到其他Python程序
```python
from position_analysis.src.main import PortfolioAnalysisSystem

# 创建系统实例
system = PortfolioAnalysisSystem()

# 加载数据
system.load_portfolio_data("portfolio.csv", client_info={"name": "客户"})

# 更新市场数据
system.update_market_data()

# 执行分析
analysis_results = system.analyze_portfolio()

# 生成报告
report_files = system.generate_reports()
```

### 2. 自定义分析模块
```python
# 使用单独的分析模块
from position_analysis.src.industry_analysis import IndustryAnalyzer
from position_analysis.src.risk_assessment import RiskAssessor

analyzer = IndustryAnalyzer()
risk_assessor = RiskAssessor()

# 执行分析
industry_analysis = analyzer.analyze_portfolio_structure(portfolio_df)
risk_assessment = risk_assessor.assess_portfolio_risk(portfolio_df, industry_analysis)
```

## ⚠️ 常见问题

### Q1: 市场数据获取失败怎么办？
A: 系统会使用成本价作为替代，确保分析可以继续进行。

### Q2: 行业分类不正确怎么办？
A: 可以修改 `data/sw_industry.csv` 文件，或自定义行业映射。

### Q3: 如何生成PDF报告？
A: 需要先安装wkhtmltopdf，然后使用 `--output-format pdf` 参数。

### Q4: 数据文件格式错误？
A: 确保必需列存在，股票代码为6位数字，持仓数量和成本价为有效数值。

## 📞 技术支持

如有问题，请检查：
1. `outputs/analysis.log` 日志文件
2. 数据文件格式是否正确
3. 依赖包是否安装完整

或联系：富富（AI投顾助手）

---

**提示**: 首次使用建议先运行示例数据测试系统功能。