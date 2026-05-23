#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成模块
应用层：报告生成、格式输出、文件保存
"""

import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json
import jinja2
import markdown

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, template_dir="../templates", output_dir="../outputs/reports"):
        """
        初始化报告生成器
        
        Args:
            template_dir (str): 模板目录
            output_dir (str): 输出目录
        """
        self.template_dir = template_dir
        self.output_dir = output_dir
        
        # 创建目录
        os.makedirs(template_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # 初始化Jinja2环境
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # 创建默认模板（如果不存在）
        self._create_default_templates()
    
    def _create_default_templates(self):
        """创建默认模板"""
        # Markdown报告模板
        md_template_path = os.path.join(self.template_dir, "report_template.md")
        if not os.path.exists(md_template_path):
            md_template = """# 投资组合分析报告

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
"""
            with open(md_template_path, 'w', encoding='utf-8') as f:
                f.write(md_template)
            logger.info(f"创建Markdown模板: {md_template_path}")
        
        # HTML报告模板（可选）
        html_template_path = os.path.join(self.template_dir, "html_report_template.html")
        if not os.path.exists(html_template_path):
            html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>投资组合分析报告 - {{ client_name }}</title>
    <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .section { background: white; padding: 25px; margin-bottom: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1, h2, h3 { color: #2c3e50; }
        .highlight { background: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; margin: 15px 0; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f2f2f2; font-weight: bold; }
        .warning { background: #fff3cd; border-left: 4px solid #ffc107; }
        .success { background: #d4edda; border-left: 4px solid #28a745; }
        .chart-container { text-align: center; margin: 20px 0; }
        .chart-container img { max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 5px; }
        .footer { text-align: center; margin-top: 50px; padding: 20px; color: #666; font-size: 0.9em; border-top: 1px solid #ddd; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>投资组合分析报告</h1>
            <p>客户: {{ client_name }} | 分析日期: {{ analysis_date }} | 报告版本: {{ report_version }}</p>
        </div>
        
        {% for section in sections %}
        <div class="section">
            <h2>{{ section.title }}</h2>
            {{ section.content|safe }}
        </div>
        {% endfor %}
        
        <div class="footer">
            <p>报告生成时间: {{ generation_time }} | 分析团队: {{ team_name }} | 免责声明: 本报告仅供参考，不构成投资建议</p>
        </div>
    </div>
</body>
</html>"""
            with open(html_template_path, 'w', encoding='utf-8') as f:
                f.write(html_template)
            logger.info(f"创建HTML模板: {html_template_path}")
    
    def generate_markdown_report(self, analysis_data: Dict, 
                                client_info: Dict, 
                                chart_files: Dict = None) -> str:
        """
        生成Markdown格式报告
        
        Args:
            analysis_data (Dict): 分析数据
            client_info (Dict): 客户信息
            chart_files (Dict, optional): 图表文件路径
            
        Returns:
            str: Markdown报告内容
        """
        logger.info(f"开始生成Markdown报告，客户: {client_info.get('name', '未知')}")
        
        try:
            # 准备模板数据
            template_data = self._prepare_template_data(analysis_data, client_info, chart_files)
            
            # 加载模板
            template = self.jinja_env.get_template("report_template.md")
            
            # 添加自定义过滤器
            self.jinja_env.filters['format_number'] = self._format_number
            self.jinja_env.filters['format_percent'] = self._format_percent
            
            # 渲染模板
            report_content = template.render(**template_data)
            
            # 保存报告
            report_filename = self._save_report(report_content, client_info, "md")
            
            logger.info(f"Markdown报告生成成功: {report_filename}")
            return report_content
            
        except Exception as e:
            logger.error(f"生成Markdown报告失败: {str(e)}")
            return f"报告生成失败: {str(e)}"
    
    def generate_html_report(self, analysis_data: Dict, 
                            client_info: Dict, 
                            chart_files: Dict = None) -> str:
        """
        生成HTML格式报告
        
        Args:
            analysis_data (Dict): 分析数据
            client_info (Dict): 客户信息
            chart_files (Dict, optional): 图表文件路径
            
        Returns:
            str: HTML报告内容
        """
        logger.info(f"开始生成HTML报告，客户: {client_info.get('name', '未知')}")
        
        try:
            # 准备模板数据
            template_data = self._prepare_template_data(analysis_data, client_info, chart_files)
            
            # 转换为HTML格式
            html_sections = self._convert_to_html_sections(analysis_data)
            
            # 添加HTML特定数据
            template_data.update({
                'sections': html_sections,
                'generation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'team_name': '智能投顾分析团队'
            })
            
            # 加载模板
            template = self.jinja_env.get_template("html_report_template.html")
            
            # 渲染模板
            html_content = template.render(**template_data)
            
            # 保存报告
            report_filename = self._save_report(html_content, client_info, "html")
            
            logger.info(f"HTML报告生成成功: {report_filename}")
            return html_content
            
        except Exception as e:
            logger.error(f"生成HTML报告失败: {str(e)}")
            return f"<html><body><h1>报告生成失败</h1><p>{str(e)}</p></body></html>"
    
    def generate_pdf_report(self, analysis_data: Dict, 
                           client_info: Dict, 
                           chart_files: Dict = None) -> Optional[str]:
        """
        生成PDF格式报告（需要wkhtmltopdf）
        
        Args:
            analysis_data (Dict): 分析数据
            client_info (Dict): 客户信息
            chart_files (Dict, optional): 图表文件路径
            
        Returns:
            str or None: PDF文件路径
        """
        logger.info(f"开始生成PDF报告，客户: {client_info.get('name', '未知')}")
        
        try:
            # 先生成HTML报告
            html_content = self.generate_html_report(analysis_data, client_info, chart_files)
            
            # 检查wkhtmltopdf是否可用
            try:
                import pdfkit
                
                # 配置PDF选项
                options = {
                    'page-size': 'A4',
                    'margin-top': '15mm',
                    'margin-right': '15mm',
                    'margin-bottom': '15mm',
                    'margin-left': '15mm',
                    'encoding': "UTF-8",
                    'no-outline': None,
                    'enable-local-file-access': None,
                }
                
                # 生成PDF文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                client_name = client_info.get('name', '未知客户').replace(' ', '_')
                pdf_filename = f"{client_name}_持仓分析报告_{timestamp}.pdf"
                pdf_path = os.path.join(self.output_dir, pdf_filename)
                
                # 生成PDF
                pdfkit.from_string(html_content, pdf_path, options=options)
                
                logger.info(f"PDF报告生成成功: {pdf_path}")
                return pdf_path
                
            except ImportError:
                logger.warning("pdfkit未安装，无法生成PDF报告")
                return None
            except Exception as e:
                logger.error(f"PDF生成失败: {str(e)}")
                return None
                
        except Exception as e:
            logger.error(f"生成PDF报告失败: {str(e)}")
            return None
    
    def _prepare_template_data(self, analysis_data: Dict, 
                              client_info: Dict, 
                              chart_files: Dict = None) -> Dict:
        """
        准备模板数据
        
        Args:
            analysis_data (Dict): 分析数据
            client_info (Dict): 客户信息
            chart_files (Dict, optional): 图表文件路径
            
        Returns:
            Dict: 模板数据
        """
        # 基本信息
        template_data = {
            'client_name': client_info.get('name', '未知客户'),
            'analysis_date': datetime.now().strftime("%Y-%m-%d"),
            'report_version': '1.0',
            'analyst_name': client_info.get('analyst', '智能投顾系统'),
            'chart_files': chart_files or {},
            'data_sources': ['东方财富API', 'QVeris API', '本地数据'],
            'analysis_models': ['行业分析模型', '风险评估模型', '轮动分析模型'],
            'update_frequency': '每日更新',
            'disclaimer': '本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。',
            'contact_info': {
                'team_name': '智能投顾分析团队',
                'phone': client_info.get('phone', '400-xxx-xxxx'),
                'email': client_info.get('email', 'analysis@investment.com'),
                'report_generation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        # 从分析数据中提取信息
        portfolio_summary = analysis_data.get('portfolio_summary', {})
        industry_analysis = analysis_data.get('industry_analysis', {})
        risk_assessment = analysis_data.get('risk_assessment', {})
        rotation_analysis = analysis_data.get('rotation_analysis', {})
        
        # 组合概览
        template_data['portfolio_summary'] = {
            'total_market_value': portfolio_summary.get('total_market_value', 0),
            'total_stocks': portfolio_summary.get('total_stocks', 0),
            'unique_industries': portfolio_summary.get('unique_industries', 0),
            'avg_position_size': portfolio_summary.get('avg_position_size', 0),
            'avg_pnl_ratio': portfolio_summary.get('avg_pnl_ratio', 0),
            'profit_stocks': portfolio_summary.get('profit_stocks', 0),
            'loss_stocks': portfolio_summary.get('loss_stocks', 0),
            'break_even_point': portfolio_summary.get('break_even_point', 0),
        }
        
        # 行业分布
        industry_distribution = []
        if 'industry_distribution' in industry_analysis:
            for industry in industry_analysis['industry_distribution'][:10]:  # 最多10个行业
                industry_distribution.append({
                    'industry_name': industry.get('行业名称', ''),
                    'holding_percentage': industry.get('持仓占比', 0),
                    'market_value': industry.get('持仓市值', 0),
                    'stock_count': industry.get('股票数量', 0),
                    'avg_position': industry.get('平均持仓市值', 0),
                    'max_stock_name': industry.get('最大持仓股票', ''),
                    'max_stock_value': industry.get('最大持仓市值', 0),
                    'stock_details': industry.get('股票明细', [])
                })
        template_data['industry_distribution'] = industry_distribution
        
        # 前十大持仓
        top_holdings = []
        if 'top_holdings' in industry_analysis:
            for holding in industry_analysis['top_holdings'][:10]:
                top_holdings.append({
                    'stock_code': holding.get('股票代码', ''),
                    'stock_name': holding.get('股票名称', ''),
                    'industry': holding.get('行业分类', ''),
                    'holding_percentage': holding.get('持仓占比', 0),
                    'pnl_ratio': holding.get('盈亏比例', 0)
                })
        template_data['top_holdings'] = top_holdings
        
        # 集中度分析
        if 'concentration_analysis' in industry_analysis:
            template_data['concentration_analysis'] = {
                'hhi_index': industry_analysis['concentration_analysis'].get('hhi_index', 0),
                'top_10_concentration': industry_analysis['concentration_analysis'].get('top_10_concentration', 0),
                'max_stock_exposure': industry_analysis['concentration_analysis'].get('max_stock_exposure', 0),
                'concentration_risk_level': industry_analysis['concentration_analysis'].get('concentration_risk_level', '')
            }
        
        # 行业轮动趋势
        rotation_trends = []
        if 'rotation_trends' in rotation_analysis:
            for trend in rotation_analysis['rotation_trends'][:8]:
                rotation_trends.append({
                    'industry_name': trend.get('行业名称', ''),
                    'current_weight': trend.get('当前权重', 0),
                    'historical_weights': trend.get('历史权重', {}),
                    'short_term_trend': trend.get('短期趋势', '')
                })
        template_data['rotation_trends'] = rotation_trends
        
        # 行业轮动建议
        rotation_recommendations = []
        if 'recommendations' in rotation_analysis:
            for rec in rotation_analysis['recommendations']:
                rotation_recommendations.append({
                    'industry_name': rec.get('行业名称', ''),
                    'recommendation_direction': rec.get('建议方向', ''),
                    'suggested_change': rec.get('建议幅度', 0),
                    'rationale': rec.get('理由', ''),
                    'priority': rec.get('优先级', '')
                })
        template_data['rotation_recommendations'] = rotation_recommendations
        
        # 整体风险评估
        if 'overall_risk' in risk_assessment:
            template_data['overall_risk'] = {
                'overall_risk_level': risk_assessment['overall_risk'].get('overall_risk_level', ''),
                'overall_risk_score': risk_assessment['overall_risk'].get('overall_risk_score', 0),
                'risk_tolerance_match': risk_assessment['overall_risk'].get('risk_tolerance_match', ''),
                'risk_monitoring_frequency': risk_assessment['overall_risk'].get('risk_monitoring_frequency', '')
            }
        
        # 压力测试结果
        if 'stress_tests' in risk_assessment:
            template_data['stress_tests'] = risk_assessment['stress_tests']
        
        # 风险价值分析
        if 'value_at_risk' in risk_assessment:
            template_data['value_at_risk'] = risk_assessment['value_at_risk']
        
        # 风险警告
        if 'risk_warnings' in risk_assessment:
            template_data['risk_warnings'] = risk_assessment['risk_warnings']
        
        # 投资建议（从风险建议中提取）
        overall_recommendations = []
        if 'recommendations' in risk_assessment:
            for rec in risk_assessment['recommendations'][:5]:
                overall_recommendations.append({
                    'type': rec.get('type', ''),
                    'action': rec.get('action', ''),
                    'target': rec.get('target', '')
                })
        template_data['overall_recommendations'] = overall_recommendations
        
        # 具体操作建议（模拟数据）
        template_data['position_adjustment'] = {
            'suggested_position': 70,
            'cash_ratio': 30,
            'adjustment_range': '±5%'
        }
        
        template_data['industry_adjustment'] = {
            'increase_industries': ['计算机', '医药生物'],
            'decrease_industries': ['食品饮料'],
            'watch_industries': ['电子', '新能源']
        }
        
        template_data['risk_control'] = {
            'stop_loss_level': -8,
            'max_drawdown_control': -15,
            'single_stock_limit': 10
        }
        
        # 详细持仓列表（从原始数据中提取）
        detailed_holdings = []
        portfolio_df = analysis_data.get('portfolio_data')
        if portfolio_df is not None and not portfolio_df.empty:
            for _, row in portfolio_df.iterrows():
                detailed_holdings.append({
                    'stock_code': row.get('股票代码', ''),
                    'stock_name': row.get('股票名称', ''),
                    'industry': row.get('行业分类', ''),
                    'holding_quantity': row.get('持仓数量', 0),
                    'cost_price': row.get('成本价', 0),
                    'current_price': row.get('最新价', 0),
                    'market_value': row.get('持仓市值', 0),
                    'pnl_ratio': row.get('盈亏比例', 0)
                })
        template_data['detailed_holdings'] = detailed_holdings
        
        return template_data
    
    def _convert_to_html_sections(self, analysis_data: Dict) -> List[Dict]:
        """
        将分析数据转换为HTML部分
        
        Args:
            analysis_data (Dict): 分析数据
            
        Returns:
            List[Dict]: HTML部分列表
        """
        sections = []
        
        # 1. 组合概览
        portfolio_summary = analysis_data.get('portfolio_summary', {})
        overview_html = f"""
        <div class="highlight">
            <p><strong>总市值:</strong> {self._format_number(portfolio_summary.get('total_market_value', 0))}元</p>
            <p><strong>股票数量:</strong> {portfolio_summary.get('total_stocks', 0)}只</p>
            <p><strong>行业数量:</strong> {portfolio_summary.get('unique_industries', 0)}个</p>
            <p><strong>平均盈亏:</strong> {self._format_percent(portfolio_summary.get('avg_pnl_ratio', 0))}%</p>
        </div>
        """
        sections.append({'title': '一、组合概览', 'content': overview_html})
        
        # 2. 行业分布
        industry_html = "<h3>行业分布</h3>"
        industry_analysis = analysis_data.get('industry_analysis', {})
        if 'industry_distribution' in industry_analysis:
            industry_html += "<table><tr><th>行业</th><th>持仓比例</th><th>持仓市值</th><th>股票数量</th></tr>"
            for industry in industry_analysis['industry_distribution'][:5]:
                industry_html += f"""
                <tr>
                    <td>{industry.get('行业名称', '')}</td>
                    <td>{self._format_percent(industry.get('持仓占比', 0))}%</td>
                    <td>{self._format_number(industry.get('持仓市值', 0))}元</td>
                    <td>{industry.get('股票数量', 0)}只</td>
                </tr>
                """
            industry_html += "</table>"
        sections.append({'title': '二、行业分布分析', 'content': industry_html})
        
        # 3. 风险评估
        risk_html = "<h3>风险指标</h3>"
        risk_assessment = analysis_data.get('risk_assessment', {})
        if 'overall_risk' in risk_assessment:
            overall_risk = risk_assessment['overall_risk']
            risk_level = overall_risk.get('overall_risk_level', '')
            risk_class = 'success' if '低' in risk_level else 'warning' if '中' in risk_level else 'danger'
            
            risk_html += f"""
            <div class="highlight {risk_class}">
                <p><strong>风险等级:</strong> {risk_level}</p>
                <p><strong>风险分数:</strong> {self._format_number(overall_risk.get('overall_risk_score', 0), 1)}/100</p>
                <p><strong>风险容忍匹配:</strong> {overall_risk.get('risk_tolerance_match', '')}</p>
                <p><strong>建议监控频率:</strong> {overall_risk.get('risk_monitoring_frequency', '')}</p>
            </div>
            """
        
        # 风险警告
        if 'risk_warnings' in risk_assessment and risk_assessment['risk_warnings']:
            risk_html += "<h3>风险警告</h3><div class='warning'><ul>"
            for warning in risk_assessment['risk_warnings'][:3]:
                risk_html += f"<li>{warning}</li>"
            risk_html += "</ul></div>"
        
        sections.append({'title': '三、风险评估', 'content': risk_html})
        
        # 4. 投资建议
        recommendations_html = "<h3>投资建议</h3>"
        
        # 行业轮动建议
        rotation_analysis = analysis_data.get('rotation_analysis', {})
        if 'recommendations' in rotation_analysis and rotation_analysis['recommendations']:
            recommendations_html += "<h4>行业轮动建议</h4><ul>"
            for rec in rotation_analysis['recommendations'][:3]:
                recommendations_html += f"<li><strong>{rec.get('行业名称', '')}</strong>: {rec.get('建议方向', '')} {rec.get('建议幅度', 0)}%</li>"
            recommendations_html += "</ul>"
        
        # 风险控制建议
        if 'recommendations' in risk_assessment and risk_assessment['recommendations']:
            recommendations_html += "<h4>风险控制建议</h4><ul>"
            for rec in risk_assessment['recommendations'][:3]:
                recommendations_html += f"<li><strong>{rec.get('type', '')}</strong>: {rec.get('action', '')} - {rec.get('target', '')}</li>"
            recommendations_html += "</ul>"
        
        sections.append({'title': '四、投资建议', 'content': recommendations_html})
        
        return sections
    
    def _save_report(self, report_content: str, client_info: Dict, 
                    format_type: str) -> str:
        """
        保存报告到文件
        
        Args:
            report_content (str): 报告内容
            client_info (Dict): 客户信息
            format_type (str): 报告格式（md/html/pdf）
            
        Returns:
            str: 报告文件路径
        """
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        client_name = client_info.get('name', '未知客户').replace(' ', '_')
        
        if format_type == 'pdf':
            filename = f"{client_name}_持仓分析报告_{timestamp}.pdf"
        elif format_type == 'html':
            filename = f"{client_name}_持仓分析报告_{timestamp}.html"
        else:  # md
            filename = f"{client_name}_持仓分析报告_{timestamp}.md"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"报告保存到: {filepath}")
        return filepath
    
    def _format_number(self, value, decimals=0):
        """格式化数字"""
        if value is None:
            return "N/A"
        
        try:
            if abs(value) >= 1e8:  # 亿
                return f"{value/1e8:.{decimals}f}亿"
            elif abs(value) >= 1e4:  # 万
                return f"{value/1e4:.{decimals}f}万"
            else:
                return f"{value:,.{decimals}f}"
        except:
            return str(value)
    
    def _format_percent(self, value, decimals=1):
        """格式化百分比"""
        if value is None:
            return "N/A"
        
        try:
            return f"{value:.{decimals}f}"
        except:
            return str(value)
    
    def generate_comprehensive_report(self, portfolio_df: pd.DataFrame, 
                                    analysis_results: Dict, 
                                    client_info: Dict, 
                                    chart_files: Dict = None,
                                    output_formats: List[str] = None) -> Dict:
        """
        生成综合报告（支持多种格式）
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            analysis_results (Dict): 分析结果
            client_info (Dict): 客户信息
            chart_files (Dict, optional): 图表文件路径
            output_formats (List[str], optional): 输出格式列表，默认为['md', 'html']
            
        Returns:
            Dict: 生成的报告文件路径
        """
        if output_formats is None:
            output_formats = ['md', 'html']
        
        # 准备分析数据
        analysis_data = {
            'portfolio_data': portfolio_df,
            'portfolio_summary': analysis_results.get('portfolio_summary', {}),
            'industry_analysis': analysis_results.get('industry_analysis', {}),
            'risk_assessment': analysis_results.get('risk_assessment', {}),
            'rotation_analysis': analysis_results.get('rotation_analysis', {})
        }
        
        # 生成各种格式的报告
        report_files = {}
        
        for fmt in output_formats:
            if fmt == 'md':
                report_content = self.generate_markdown_report(analysis_data, client_info, chart_files)
                report_files['markdown'] = os.path.join(
                    self.output_dir, 
                    f"{client_info.get('name', '客户').replace(' ', '_')}_持仓分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                )
            
            elif fmt == 'html':
                report_content = self.generate_html_report(analysis_data, client_info, chart_files)
                report_files['html'] = os.path.join(
                    self.output_dir,
                    f"{client_info.get('name', '客户').replace(' ', '_')}_持仓分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                )
            
            elif fmt == 'pdf':
                pdf_path = self.generate_pdf_report(analysis_data, client_info, chart_files)
                if pdf_path:
                    report_files['pdf'] = pdf_path
        
        logger.info(f"生成综合报告完成，格式: {list(report_files.keys())}")
        return report_files


# 示例使用
if __name__ == "__main__":
    # 示例：报告生成测试
    generator = ReportGenerator()
    
    # 示例数据
    sample_portfolio = pd.DataFrame([
        {'股票代码': '000001', '股票名称': '平安银行', '持仓数量': 1000, '成本价': 15.20, '最新价': 16.50, 
         '持仓市值': 16500, '盈亏比例': 8.6, '行业分类': '银行'},
        {'股票代码': '600036', '股票名称': '招商银行', '持仓数量': 800, '成本价': 32.50, '最新价': 35.20, 
         '持仓市值': 28160, '盈亏比例': 8.3, '行业分类': '银行'},
        {'股票代码': '000858', '股票名称': '五粮液', '持仓数量': 500, '成本价': 180.30, '最新价': 195.00, 
         '持仓市值': 97500, '盈亏比例': 8.1, '行业分类': '食品饮料'},
    ])
    
    # 示例分析结果
    sample_analysis = {
        'portfolio_summary': {
            'total_market_value': 142160,
            'total_stocks': 3,
            'unique_industries': 2,
            'avg_position_size': 47387,
            'avg_pnl_ratio': 8.3,
            'profit_stocks': 3,
            'loss_stocks': 0,
            'break_even_point': -8.3
        },
        'industry_analysis': {
            'industry_distribution': [
                {'行业名称': '食品饮料', '持仓占比': 68.6, '持仓市值': 97500, '股票数量': 1, '平均持仓市值': 97500},
                {'行业名称': '银行', '持仓占比': 31.4, '持仓市值': 44660, '股票数量': 2, '平均持仓市值': 22330}
            ],
            'top_holdings': [
                {'股票代码': '000858', '股票名称': '五粮液', '行业分类': '食品饮料', '持仓占比': 68.6, '盈亏比例': 8.1},
                {'股票代码': '600036', '股票名称': '招商银行', '行业分类': '银行', '持仓占比': 19.8, '盈亏比例': 8.3},
                {'股票代码': '000001', '股票名称': '平安银行', '行业分类': '银行', '持仓占比': 11.6, '盈亏比例': 8.6}
            ],
            'concentration_analysis': {
                'hhi_index': 5230,
                'top_10_concentration': 100,
                'max_stock_exposure': 68.6,
                'concentration_risk_level': '高风险'
            }
        },
        'risk_assessment': {
            'overall_risk': {
                'overall_risk_level': '高风险',
                'overall_risk_score': 78.5,
                'risk_tolerance_match': '匹配进取型投资者',
                'risk_monitoring_frequency': '每日监控'
            },
            'stress_tests': {
                'summary': {
                    'worst_case_scenario': '市场崩盘',
                    'worst_case_loss': -25.3,
                    'overall_resilience': '低韧性'
                }
            },
            'value_at_risk': {
                'var_estimates_percentage': {
                    'var_95_1d': -3.2,
                    'var_99_1d': -5.8,
                    'conditional_var_95': -4.5
                }
            },
            'risk_warnings': [
                '持仓集中度过高，存在集中度风险',
                '食品饮料行业配置比例偏高'
            ],
            'recommendations': [
                {'type': '集中度风险', 'action': '降低最大持仓暴露', 'target': '将最大个股暴露从68.6%降低到10%以下', 'priority': '高'},
                {'type': '行业风险', 'action': '分散行业配置', 'target': '将最大行业暴露从68.6%降低到30%以下', 'priority': '高'}
            ]
        },
        'rotation_analysis': {
            'rotation_trends': [
                {'行业名称': '食品饮料', '当前权重': 68.6, '历史权重': {'1个月前': 65.2, '3个月前': 62.8, '6个月前': 58.4}, '短期趋势': '增配'},
                {'行业名称': '银行', '当前权重': 31.4, '历史权重': {'1个月前': 34.8, '3个月前': 37.2, '6个月前': 41.6}, '短期趋势': '减配'}
            ],
            'recommendations': [
                {'行业名称': '食品饮料', '建议方向': '减配', '建议幅度': 5.0, '理由': '当前权重已较高，建议适度减配', 'priority': 1},
                {'行业名称': '计算机', '建议方向': '增配', '建议幅度': 3.0, '理由': '行业趋势向上且动量强势', 'priority': 2}
            ]
        }
    }
    
    # 示例客户信息
    sample_client = {
        'name': '张三先生',
        'analyst': '富富（AI投顾助手）',
        'phone': '138-xxxx-xxxx',
        'email': 'zhangsan@example.com'
    }
    
    # 示例图表文件
    sample_charts = {
        'industry_pie_chart': '../outputs/charts/张三先生_industry_distribution_20260416_153045.png',
        'risk_radar_chart': '../outputs/charts/张三先生_risk_radar_20260416_153045.png'
    }
    
    # 生成Markdown报告
    print("生成Markdown报告...")
    md_report = generator.generate_markdown_report(sample_analysis, sample_client, sample_charts)
    
    if md_report:
        print("Markdown报告生成成功")
        # 显示报告前500字符
        print("\n报告预览（前500字符）:")
        print(md_report[:500] + "...")
    
    # 生成HTML报告
    print("\n生成HTML报告...")
    html_report = generator.generate_html_report(sample_analysis, sample_client, sample_charts)
    
    if html_report:
        print("HTML报告生成成功")
    
    # 生成综合报告
    print("\n生成综合报告...")
    report_files = generator.generate_comprehensive_report(
        sample_portfolio, sample_analysis, sample_client, sample_charts, ['md', 'html']
    )
    
    print(f"生成的报告文件: {report_files}")