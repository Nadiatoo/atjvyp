# 投资组合分析报告

## 📋 报告信息
- **客户名称**: {{ client_name }}
- **分析日期**: {{ analysis_date }}
- **报告版本**: {{ report_version }}
- **分析人员**: {{ analyst_name }}

---

## 📊 一、组合概览

### 1.1 基本信息
{% if portfolio_summary %}
- **总市值**: {{ portfolio_summary.total_market_value|format_number }}元
- **股票数量**: {{ portfolio_summary.total_stocks }}只
- **行业数量**: {{ portfolio_summary.unique_industries }}个
- **平均持仓**: {{ portfolio_summary.avg_position_size|format_number }}元
{% endif %}

### 1.2 盈亏概况
{% if portfolio_summary %}
- **平均盈亏比例**: {{ portfolio_summary.avg_pnl_ratio|format_percent }}%
- **盈利股票数量**: {{ portfolio_summary.profit_stocks }}只
- **亏损股票数量**: {{ portfolio_summary.loss_stocks }}只
- **盈亏平衡点**: {{ portfolio_summary.break_even_point|format_percent }}%
{% endif %}

---

## 📈 二、持仓结构分析

### 2.1 行业分布
{% for industry in industry_distribution %}
#### {{ industry.industry_name }} ({{ industry.holding_percentage|format_percent }}%)
- **持仓市值**: {{ industry.market_value|format_number }}元
- **股票数量**: {{ industry.stock_count }}只
- **平均仓位**: {{ industry.avg_position|format_number }}元
- **最大持仓**: {{ industry.max_stock_name }} ({{ industry.max_stock_value|format_number }}元)

{% if industry.stock_details %}
主要股票:
{% for stock in industry.stock_details[:3] %}
  - {{ stock.stock_name }}({{ stock.stock_code }}): {{ stock.holding_percentage|format_percent }}% ({{ stock.pnl_ratio|format_percent }}%)
{% endfor %}
{% endif %}
{% endfor %}

### 2.2 前十大持仓
| 排名 | 股票代码 | 股票名称 | 行业 | 持仓比例 | 盈亏比例 |
|------|----------|----------|------|----------|----------|
{% for holding in top_holdings %}
| {{ loop.index }} | {{ holding.stock_code }} | {{ holding.stock_name }} | {{ holding.industry }} | {{ holding.holding_percentage|format_percent }}% | {{ holding.pnl_ratio|format_percent }}% |
{% endfor %}

### 2.3 集中度分析
{% if concentration_analysis %}
- **HHI指数**: {{ concentration_analysis.hhi_index|format_number(2) }}
- **前十大持仓集中度**: {{ concentration_analysis.top_10_concentration|format_percent }}%
- **最大个股暴露**: {{ concentration_analysis.max_stock_exposure|format_percent }}%
- **集中度风险等级**: {{ concentration_analysis.concentration_risk_level }}
{% endif %}

---

## 🔄 三、行业轮动分析

### 3.1 行业配置趋势
{% if rotation_trends %}
| 行业 | 当前权重 | 1个月前 | 3个月前 | 6个月前 | 趋势方向 |
|------|----------|---------|---------|---------|----------|
{% for trend in rotation_trends %}
| {{ trend.industry_name }} | {{ trend.current_weight|format_percent }}% | {{ trend.historical_weights['1个月前']|format_percent }}% | {{ trend.historical_weights['3个月前']|format_percent }}% | {{ trend.historical_weights['6个月前']|format_percent }}% | {{ trend.short_term_trend }} |
{% endfor %}
{% endif %}

### 3.2 行业轮动建议
{% if rotation_recommendations %}
{% for rec in rotation_recommendations %}
#### {{ rec.industry_name }}
- **建议方向**: {{ rec.recommendation_direction }}
- **建议幅度**: {{ rec.suggested_change|format_percent }}%
- **理由**: {{ rec.rationale }}
- **优先级**: {{ rec.priority }}
{% endfor %}
{% endif %}

---

## ⚠️ 四、风险评估

### 4.1 风险指标概览
{% if overall_risk %}
- **整体风险等级**: {{ overall_risk.overall_risk_level }}
- **风险分数**: {{ overall_risk.overall_risk_score|format_number(1) }}/100
- **风险容忍匹配**: {{ overall_risk.risk_tolerance_match }}
- **建议监控频率**: {{ overall_risk.risk_monitoring_frequency }}
{% endif %}

### 4.2 压力测试结果
{% if stress_tests %}
| 压力场景 | 损失比例 | 幸存率 | 资本充足性 |
|----------|----------|--------|------------|
{% for key, test in stress_tests.items() if key != 'summary' %}
| {{ test.scenario_name }} | {{ test.loss_percentage|format_percent(1) }}% | {{ test.survival_rate|format_percent(1) }}% | {{ test.capital_adequacy }} |
{% endfor %}

**最坏情况**: {{ stress_tests.summary.worst_case_scenario }} (损失{{ stress_tests.summary.worst_case_loss|format_percent(1) }}%)
**整体韧性**: {{ stress_tests.summary.overall_resilience }}
{% endif %}

### 4.3 风险价值分析
{% if value_at_risk %}
- **95%置信度，1天VaR**: {{ value_at_risk.var_estimates_percentage.var_95_1d|format_percent(1) }}%
- **99%置信度，1天VaR**: {{ value_at_risk.var_estimates_percentage.var_99_1d|format_percent(1) }}%
- **条件VaR(95%)**: {{ value_at_risk.var_estimates_percentage.conditional_var_95|format_percent(1) }}%
- **VaR模型充分性**: {{ value_at_risk.var_model_adequacy }}
{% endif %}

### 4.4 风险警告
{% if risk_warnings %}
{% for warning in risk_warnings %}
- ⚠️ {{ warning }}
{% endfor %}
{% endif %}

---

## 💡 五、投资建议

### 5.1 整体建议
{% if overall_recommendations %}
{% for rec in overall_recommendations %}
- **{{ rec.type }}**: {{ rec.action }} - {{ rec.target }}
{% endfor %}
{% endif %}

### 5.2 具体操作建议
1. **仓位调整**:
   - 建议整体仓位: {{ position_adjustment.suggested_position|format_percent }}%
   - 现金比例: {{ position_adjustment.cash_ratio|format_percent }}%
   - 调整幅度: {{ position_adjustment.adjustment_range }}

2. **行业配置**:
   - 增配行业: {{ industry_adjustment.increase_industries|join(', ') if industry_adjustment.increase_industries else '无' }}
   - 减配行业: {{ industry_adjustment.decrease_industries|join(', ') if industry_adjustment.decrease_industries else '无' }}
   - 关注行业: {{ industry_adjustment.watch_industries|join(', ') if industry_adjustment.watch_industries else '无' }}

3. **风险控制**:
   - 止损设置: {{ risk_control.stop_loss_level|format_percent }}%
   - 最大回撤控制: {{ risk_control.max_drawdown_control|format_percent }}%
   - 仓位限制: 单股不超过{{ risk_control.single_stock_limit|format_percent }}%

---

## 📋 六、附录

### 6.1 详细持仓列表
| 股票代码 | 股票名称 | 行业 | 持仓数量 | 成本价 | 最新价 | 持仓市值 | 盈亏比例 |
|----------|----------|------|----------|--------|--------|----------|----------|
{% for stock in detailed_holdings %}
| {{ stock.stock_code }} | {{ stock.stock_name }} | {{ stock.industry }} | {{ stock.holding_quantity|format_number }} | {{ stock.cost_price|format_number(2) }} | {{ stock.current_price|format_number(2) }} | {{ stock.market_value|format_number }} | {{ stock.pnl_ratio|format_percent }}% |
{% endfor %}

### 6.2 图表说明
{% if chart_files %}
{% for chart_type, chart_path in chart_files.items() %}
- {{ chart_type }}: {{ chart_path }}
{% endfor %}
{% endif %}

### 6.3 数据说明
- 数据来源: {{ data_sources|join(', ') }}
- 分析模型: {{ analysis_models|join(', ') }}
- 更新频率: {{ update_frequency }}
- 免责声明: {{ disclaimer }}

---

## 📞 联系方式
- **分析团队**: {{ contact_info.team_name }}
- **联系电话**: {{ contact_info.phone }}
- **电子邮箱**: {{ contact_info.email }}
- **报告生成时间**: {{ contact_info.report_generation_time }}

---
*报告结束*
