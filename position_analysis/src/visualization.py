#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化模块
应用层：图表生成、可视化展示
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from typing import Dict, List, Optional, Tuple
import os
import logging
from datetime import datetime
import json

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PortfolioVisualizer:
    """投资组合可视化器"""
    
    def __init__(self, output_dir="../outputs/charts", style="seaborn"):
        """
        初始化可视化器
        
        Args:
            output_dir (str): 图表输出目录
            style (str): 图表样式
        """
        self.output_dir = output_dir
        self.style = style
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置样式
        if style == "seaborn":
            plt.style.use('seaborn-v0_8-whitegrid')
            sns.set_palette("husl")
        elif style == "matplotlib":
            plt.style.use('default')
        elif style == "dark":
            plt.style.use('dark_background')
        
        # 颜色配置
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#18A999',
            'warning': '#F18F01',
            'danger': '#C73E1D',
            'neutral': '#6C757D',
            'light': '#F8F9FA',
            'dark': '#343A40'
        }
        
        # 行业颜色映射
        self.industry_colors = {
            '银行': '#1F77B4',
            '非银金融': '#FF7F0E',
            '食品饮料': '#2CA02C',
            '电子': '#D62728',
            '医药生物': '#9467BD',
            '家用电器': '#8C564B',
            '电气设备': '#E377C2',
            '计算机': '#7F7F7F',
            '房地产': '#BCBD22',
            '汽车': '#17BECF',
            '其他': '#9B9B9B'
        }
    
    def generate_all_charts(self, portfolio_data: pd.DataFrame, 
                           analysis_results: Dict, client_name: str = "") -> Dict:
        """
        生成所有图表
        
        Args:
            portfolio_data (pandas.DataFrame): 持仓数据
            analysis_results (Dict): 分析结果
            client_name (str): 客户名称
            
        Returns:
            Dict: 生成的图表文件路径
        """
        logger.info(f"开始为{client_name if client_name else '客户'}生成图表")
        
        chart_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        client_prefix = f"{client_name}_" if client_name else ""
        
        try:
            # 1. 行业分布饼图
            if 'industry_distribution' in analysis_results:
                pie_chart_path = self._generate_industry_pie_chart(
                    analysis_results['industry_distribution'],
                    f"{client_prefix}industry_distribution_{timestamp}.png"
                )
                chart_files['industry_pie_chart'] = pie_chart_path
            
            # 2. 行业分布柱状图
            if 'industry_distribution' in analysis_results:
                bar_chart_path = self._generate_industry_bar_chart(
                    analysis_results['industry_distribution'],
                    f"{client_prefix}industry_bar_chart_{timestamp}.png"
                )
                chart_files['industry_bar_chart'] = bar_chart_path
            
            # 3. 持仓结构图（前十大持仓）
            if 'top_holdings' in analysis_results:
                holdings_chart_path = self._generate_top_holdings_chart(
                    analysis_results['top_holdings'],
                    f"{client_prefix}top_holdings_{timestamp}.png"
                )
                chart_files['top_holdings_chart'] = holdings_chart_path
            
            # 4. 行业轮动趋势图（如果有历史数据）
            if 'rotation_trends' in analysis_results and analysis_results['rotation_trends']:
                rotation_chart_path = self._generate_rotation_trend_chart(
                    analysis_results['rotation_trends'],
                    f"{client_prefix}rotation_trend_{timestamp}.png"
                )
                chart_files['rotation_trend_chart'] = rotation_chart_path
            
            # 5. 风险指标雷达图
            if 'risk_metrics' in analysis_results:
                radar_chart_path = self._generate_risk_radar_chart(
                    analysis_results['risk_metrics'],
                    f"{client_prefix}risk_radar_{timestamp}.png"
                )
                chart_files['risk_radar_chart'] = radar_chart_path
            
            # 6. 压力测试结果图
            if 'stress_tests' in analysis_results:
                stress_test_chart_path = self._generate_stress_test_chart(
                    analysis_results['stress_tests'],
                    f"{client_prefix}stress_test_{timestamp}.png"
                )
                chart_files['stress_test_chart'] = stress_test_chart_path
            
            # 7. 相关性热力图（如果有相关性数据）
            if portfolio_data is not None and len(portfolio_data) > 1:
                correlation_chart_path = self._generate_correlation_heatmap(
                    portfolio_data,
                    f"{client_prefix}correlation_heatmap_{timestamp}.png"
                )
                chart_files['correlation_heatmap'] = correlation_chart_path
            
            # 8. 盈亏分布图
            if '盈亏比例' in portfolio_data.columns:
                pnl_chart_path = self._generate_pnl_distribution_chart(
                    portfolio_data,
                    f"{client_prefix}pnl_distribution_{timestamp}.png"
                )
                chart_files['pnl_distribution_chart'] = pnl_chart_path
            
            # 9. 组合摘要仪表板
            dashboard_path = self._generate_portfolio_dashboard(
                portfolio_data, analysis_results,
                f"{client_prefix}dashboard_{timestamp}.png"
            )
            chart_files['portfolio_dashboard'] = dashboard_path
            
            logger.info(f"成功生成 {len(chart_files)} 张图表")
            return chart_files
            
        except Exception as e:
            logger.error(f"生成图表失败: {str(e)}")
            return {}
    
    def _generate_industry_pie_chart(self, industry_distribution: List[Dict], 
                                    filename: str) -> str:
        """
        生成行业分布饼图
        
        Args:
            industry_distribution (List[Dict]): 行业分布数据
            filename (str): 输出文件名
            
        Returns:
            str: 图表文件路径
        """
        if not industry_distribution:
            logger.warning("行业分布数据为空，无法生成饼图")
            return ""
        
        # 提取数据
        industries = []
        proportions = []
        colors = []
        
        for item in industry_distribution:
            industry = item['行业名称']
            proportion = item['持仓占比']
            
            industries.append(industry)
            proportions.append(proportion)
            colors.append(self.industry_colors.get(industry, self.colors['neutral']))
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 绘制饼图
        wedges, texts, autotexts = ax.pie(
            proportions,
            labels=industries,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.85,
            textprops={'fontsize': 10}
        )
        
        # 美化百分比文本
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # 添加标题
        ax.set_title('持仓行业分布', fontsize=16, fontweight='bold', pad=20)
        
        # 添加图例
        ax.legend(wedges, industries, title="行业", loc="center left", 
                 bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)
        
        # 使饼图为圆形
        ax.axis('equal')
        
        # 添加总市值信息（如果有）
        if industry_distribution:
            total_value = sum([item['持仓市值'] for item in industry_distribution])
            plt.figtext(0.5, 0.01, f"总市值: {total_value:,.0f}元", 
                       ha='center', fontsize=11, style='italic')
        
        # 保存图表
        output_path = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"生成行业分布饼图: {output_path}")
        return output_path
    
    def _generate_industry_bar_chart(self, industry_distribution: List[Dict], 
                                    filename: str) -> str:
        """
        生成行业分布柱状图
        
        Args:
            industry_distribution (List[Dict]): 行业分布数据
            filename (str): 输出文件名
            
        Returns:
            str: 图表文件路径
        """
        if not industry_distribution:
            logger.warning("行业分布数据为空，无法生成柱状图")
            return ""
        
        # 提取数据（只显示前10个行业）
        top_industries = industry_distribution[:10]
        industries = [item['行业名称'] for item in top_industries]
        proportions = [item['持仓占比'] for item in top_industries]
        values = [item['持仓市值'] for item in top_industries]
        colors = [self.industry_colors.get(ind, self.colors['primary']) for ind in industries]
        
        # 创建图表
        fig, ax1 = plt.subplots(figsize=(12, 8))
        
        # 创建双轴
        ax2 = ax1.twinx()
        
        # 绘制柱状图（比例）
        bars = ax1.bar(industries, proportions, color=colors, alpha=0.7, label='持仓比例 (%)')
        ax1.set_ylabel('持仓比例 (%)', fontsize=12)
        ax1.set_ylim(0, max(proportions) * 1.2)
        
        # 绘制折线图（市值）
        line = ax2.plot(industries, values, color=self.colors['danger'], 
                       marker='o', linewidth=2, markersize=8, label='持仓市值 (元)')
        ax2.set_ylabel('持仓市值 (元)', fontsize=12)
        
        # 设置x轴标签旋转
        ax1.set_xticklabels(industries, rotation=45, ha='right')
        
        # 添加标题
        ax1.set_title('行业分布分析 (前十大行业)', fontsize=16, fontweight='bold', pad=20)
        
        # 在柱子上添加数值标签
        for bar, proportion in zip(bars, proportions):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{proportion:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # 在折线上添加市值标签
        for i, (industry, value) in enumerate(zip(industries, values)):
            ax2.text(i, value * 1.02, f'{value/10000:.0f}万', 
                    ha='center', va='bottom', fontsize=9, color=self.colors['danger'])
        
        # 合并图例
        lines_labels = [ax1.get_legend_handles_labels(), ax2.get_legend_handles_labels()]
        lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
        ax1.legend(lines, labels, loc='upper left', fontsize=10)
        
        # 添加网格
        ax1.grid(True, axis='y', alpha=0.3)
        
        # 保存图表
        output_path = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"生成行业分布柱状图: {output_path}")
        return output_path
    
    def _generate_top_holdings_chart(self, top_holdings: List[Dict], 
                                    filename: str) -> str:
        """
        生成前十大持仓图表
        
        Args:
            top_holdings (List[Dict]): 前十大持仓数据
            filename (str): 输出文件名
            
        Returns:
            str: 图表文件路径
        """
        if not top_holdings:
            logger.warning("前十大持仓数据为空")
            return ""
        
        # 提取数据
        holdings = top_holdings[:10]  # 确保只有10个
        stock_names = [f"{h['股票名称']}\n({h['股票代码']})" for h in holdings]
        proportions = [h['持仓占比'] for h in holdings]
        pnl_ratios = [h.get('盈亏比例', 0) for h in holdings]
        industries = [h.get('行业分类', '其他') for h in holdings]
        
        # 根据行业分配颜色
        colors = [self.industry_colors.get(ind, self.colors['neutral']) for ind in industries]
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                       gridspec_kw={'height_ratios': [3, 1]})
        
        # 上方：持仓比例柱状图
        bars = ax1.bar(stock_names, proportions, color=colors, alpha=0.7)
        ax1.set_ylabel('持仓比例 (%)', fontsize=12)
        ax1.set_title('前十大持仓分析', fontsize=16, fontweight='bold', pad=20)
        ax1.grid(True, axis='y', alpha=0.3)
        
        # 在柱子上添加比例标签
        for bar, proportion in zip(bars, proportions):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                    f'{proportion:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # 下方：盈亏比例热图
        # 创建颜色映射
        cmap = plt.cm.RdYlGn
        norm = plt.Normalize(min(pnl_ratios) - 5, max(pnl_ratios) + 5)
        
        # 创建热图单元格
        cell_colors = [cmap(norm(value)) for value in pnl_ratios]
        
        # 绘制热图
        for i, (name, color, value) in enumerate(zip(stock_names, cell_colors, pnl_ratios)):
            ax2.add_patch(plt.Rectangle((i, 0), 1, 1, color=color, alpha=0.7))
            ax2.text(i + 0.5, 0.5, f'{value:.1f}%', ha='center', va='center', 
                    fontsize=10, fontweight='bold', 
                    color='white' if abs(value) > 10 else 'black')
        
        ax2.set_xlim(0, len(stock_names))
        ax2.set_ylim(0, 1)
        ax2.set_xticks([i + 0.5 for i in range(len(stock_names))])
        ax2.set_xticklabels(stock_names, rotation=45, ha='right')
        ax2.set_yticks([])
        ax2.set_title('盈亏比例 (%)', fontsize=12, pad=10)
        
        # 添加盈亏比例图例
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax2, orientation='horizontal', pad=0.1)
        cbar.set_label('盈亏比例 (%)', fontsize=10)
        
        # 添加行业图例（简化）
        unique_industries = list(set(industries))
        industry_legend_elements = []
        for industry in unique_industries:
            industry_legend_elements.append(
                plt.Rectangle((0, 0), 1, 1, color=self.industry_colors.get(industry, self.colors['neutral']), 
                            label=industry)
            )
        
        if industry_legend_elements:
            ax1.legend(handles=industry_legend_elements, title='行业', 
                      loc='upper right', fontsize=9, title_fontsize=10)
        
        # 保存图表
        output_path = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"生成前十大持仓图表: {output_path}")
        return output_path
    
    def _generate_rotation_trend_chart(self, rotation_trends: List[Dict], 
                                      filename: str) -> str:
        """
        生成行业轮动趋势图
        
        Args:
            rotation_trends (List[Dict]): 行业轮动趋势数据
            filename (str): 输出文件名
            
        Returns:
            str: 图表文件路径
        """
        if not rotation_trends:
            logger.warning("行业轮动趋势数据为空")
            return ""
        
        # 提取数据（前8个行业）
        trends = rotation_trends[:8]
        industries = [t['行业名称'] for t in trends]
        
        # 提取历史权重数据
        time_periods = ['当前权重', '1个月前', '3个月前', '6个月前']
        weights_data = {}
        
        for industry in industries:
            trend_data = next((t for t in trends if t['行业名称'] == industry), None)
            if trend_data:
                weights_data[industry] = [
                    trend_data['当前权重'],
                    trend_data['历史权重']['1个月前'],
                    trend_data['历史权重']['3个月前'],
                    trend_data['历史权重']['6个月前']
                ]
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # 设置x轴位置
        x = np.arange(len(time_periods))
        width = 0.8 / len(industries)
        
        # 绘制分组柱状图
        for i, industry in enumerate(industries):
            weights = weights_data.get(industry, [0, 0, 0, 0])
            offset = (i - len(industries)/2 + 0.5) * width
            bars = ax.bar(x + offset, weights, width, 
                         label=industry, 
                         color=self.industry_colors.get(industry, self.colors['neutral']),
                         alpha=0.7)
            
            # 在柱子上添加数值标签
            for j, (bar, weight) in enumerate(zip(bars, weights)):
                if weight > 1:  # 只显示大于1%的标签
                    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.2,
                           f'{weight:.1f}%', ha='center', va='bottom', fontsize=8)
        
        # 设置图表属性
        ax.set_xlabel('时间周期', fontsize=12)
        ax.set_ylabel('持仓权重 (%)', fontsize=12)
        ax.set_title('行业轮动趋势分析', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(time_periods)
        ax.legend(title='行业', fontsize=9, title_fontsize=10)
        ax.grid(True, axis='y', alpha=0.3)
        
        # 添加趋势方向箭头
        for i, industry in enumerate(industries):
            trend_data = next((t for t in trends if t['行业名称'] == industry), None)
            if trend_data and trend_data['短期趋势'] != '稳定':
                # 计算变化方向
                current_weight = weights_data[industry][0]
                prev_weight = weights_data[industry][1]
                change = current_weight - prev_weight
                
                if abs(change) > 0.5:
                    # 添加箭头注释
                    arrow_color = self.colors['success'] if change > 0 else self.colors['danger']
                    arrow_symbol = '↑' if change > 0 else '↓'
                    ax.text(3.5, current_weight + i * 0.5, 
                           f'{industry}{arrow_symbol}{abs(change):.1f}%',
                           fontsize=9, color=arrow_color, va='center')
        
        # 保存图表
        output_path = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"生成行业轮动趋势图: {output_path}")
        return output_path
    
    def _generate_risk_radar_chart(self, risk_metrics: Dict, filename: str) -> str:
        """
        生成风险指标雷达图
        
        Args:
            risk_metrics (Dict): 风险指标数据
            filename (str): 输出文件名
            
        Returns:
            str: 图表文件路径
        """
        # 提取风险维度数据
        risk_categories = ['集中度风险', '波动性风险', '行业风险', '下行风险']
        
        # 获取风险分数
        risk_scores = []
        for category in risk_categories:
            if category in risk_metrics:
                score = risk_metrics[category].get(f'{category.lower().replace("风险", "_risk")}_score', 50)
                risk_scores.append(score)
            else:
                risk_scores.append(50)
        
        # 确保数据完整性
        if len(risk_scores) != len(risk_categories):
            logger.warning("风险指标数据不完整")
            return ""
        
        # 创建雷达图
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # 计算角度
        angles = np.linspace(0, 2 * np.pi, len(risk_categories), endpoint=False).tolist()
        angles += angles[:1]  # 闭合图形
        risk_scores += risk_scores[:1]
        
        # 绘制雷达图
        ax.plot(angles, risk_scores, 'o-', linewidth=2, color=self.colors['primary'])
        ax.fill(angles, risk_scores, alpha=0.25, color=self.colors['primary'])
        
        # 设置刻度标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(risk_categories, fontsize=12)
        
        # 设置径向刻度
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=10)
        ax.set_rlabel_position(0)
        
        # 添加风险等级区域
        # 低风险区域 (0-30)
        ax.fill_between(angles, 0, 30, alpha=0.1, color='green')
        # 中风险区域 (30-70)
        ax.fill_between(angles, 30, 70, alpha=0.1, color='orange')
        # 高风险区域 (70-100)
        ax.fill_between(angles, 70, 100, alpha=0.1, color='red')
        
        # 添加标题
        ax.set_title('投资组合风险雷达图', fontsize=16, fontweight='bold', pad=20)
        
        # 添加图例
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='green', alpha=0.3, label='低风险 (0-30)'),
            Patch(facecolor='orange', alpha=0.3, label='中风险 (30-70)'),
            Patch(facecolor='red', alpha=0.3, label='高风险 (70-100)'),
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        # 在数据点上添加数值标签
        for i, (angle, score) in enumerate(zip(angles[:-1], risk_scores[:-1])):
            ax.text(angle, score + 3, f'{score:.0f}', 
                   ha='center', va='center', fontsize=10, fontweight='bold')
        
        # 保存图表
        output_path = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"生成风险指标雷达图: {output_path}")
        return output_path
    
    def _generate_stress_test_chart(self, stress_tests: Dict, filename: str) -> str:
        """
        生成压力测试结果图
        
        Args:
            stress_tests (Dict): 压力测试数据
            filename (str): 输出文件名
            
        Returns:
            str: 图表文件路径
        """
        if 'summary' not in stress_tests:
            logger.warning("压力测试数据不完整")
            return ""
        
        # 提取压力测试场景数据
        scenarios = []
        losses = []
        colors = []
        
        for key, data in stress_tests.items():
            if key != 'summary' and isinstance(data, dict):
                scenarios.append(data.get('scenario_name', key))
                losses.append(abs(data.get('loss_percentage', 0)))
                
                # 根据损失程度分配颜色
                loss_pct = data.get('loss_percentage', 0)
                if loss_pct > -10:
                    colors.append(self.colors['success'])
                elif loss_pct > -20:
                    colors.append(self.colors['warning'])
                else:
                    colors.append(self.colors['danger'])
        
        if not scenarios:
            logger.warning("无有效的压力测试场景数据")
            return ""
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # 左侧：压力测试损失柱状图
        bars = ax1.barh(scenarios, losses, color=colors, alpha=0.7)
        ax1.set_xlabel('损失比例 (%)', fontsize=12)
        ax1.set_title('压力测试损失分析', fontsize=14, fontweight='bold', pad=15)
        ax1.grid(True, axis='x', alpha=0.3)
        
        # 在柱子上添加数值标签
        for bar, loss in zip(bars, losses):
            ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{loss:.1f}%', ha='left', va='center', fontsize=10)
        
        # 右侧：幸存率饼图
        survival_rates = [100 - loss for loss in losses]
        explode = [0.05] * len(scenarios)  # 轻微突出
        
        wedges, texts, autotexts = ax2.pie(
            survival_rates,
            labels=scenarios,
            colors=colors,
            explode=explode,
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.85,
            textprops={'fontsize': 10}
        )
        
        # 美化百分比文本
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax2.set_title('压力测试幸存率', fontsize=14, fontweight='bold', pad=15)
        
        # 添加整体韧性信息
        summary = stress_tests.get('summary', {})
        resilience = summary.get('overall_resilience', '未知')
        worst_case = summary.get('worst_case_loss', 0)
        
        fig.suptitle(f'压力测试结果 - 整体韧性: {resilience} (最坏情况损失: {worst_case:.1f}%)', 
                    fontsize=16, fontweight='bold')
        
        # 保存图表
        output_path = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"生成压力测试结果图: {output_path}")
        return output_path
    
    def _generate_correlation_heatmap(self, portfolio_df: pd.DataFrame, 
                                     filename: str) -> str:
        """
        生成相关性热力图
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            filename (str): 输出文件名
            
        Returns:
            str: 图表文件路径
        """
        # 简化实现：生成示例相关性矩阵
        # 实际应用中应从历史收益率计算
        
        if len(portfolio_df) < 2:
            logger.warning("持仓股票数量不足，无法生成相关性热力图")
            return ""
        
        # 创建示例相关性矩阵
        n_stocks = min(10, len(portfolio_df))  # 最多显示10只股票
        stock_codes = portfolio_df['股票代码'].head(n_stocks).tolist()
        stock_names = portfolio_df['股票名称'].head(n_stocks).tolist()
        
        # 生成随机相关性矩阵（对称且对角线为1）
        np.random.seed(42)  # 固定随机种子以获得可重复结果
        corr_matrix = np.random.randn(n_stocks, n_stocks)
        corr_matrix = np.corrcoef(corr_matrix)
        np.fill_diagonal(corr_matrix, 1.0)
        
        # 确保相关性在合理范围内
        corr_matrix = np.clip(corr_matrix, -1, 1)
        
        # 创建热力图
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 使用seaborn热力图
        sns.heatmap(
            corr_matrix,
            annot=True,
            fmt='.2f',
            cmap='RdBu_r',
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={'shrink': 0.8},
            ax=ax
        )
        
        # 设置刻度标签
        tick_labels = [f"{name}\n({code})" for name, code in zip(stock_names, stock_codes)]
        ax.set_xticklabels(tick_labels, rotation=45, ha='right', fontsize=10)
        ax.set_yticklabels(tick_labels, rotation=0, fontsize=10)
        
        # 添加标题
        ax.set_title('持仓股票相关性热力图', fontsize=16, fontweight='bold', pad=20)
        
        # 添加说明
        plt.figtext(0.5, 0.01, '注：颜色越红表示正相关性越强，颜色越蓝表示负相关性越强', 
                   ha='center', fontsize=10, style='italic')
        
        # 保存图表
        output_path = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"生成相关性热力图: {output_path}")
        return output_path
    
    def _generate_pnl_distribution_chart(self, portfolio_df: pd.DataFrame, 
                                        filename: str) -> str:
        """
        生成盈亏分布图
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            filename (str): 输出文件名
            
        Returns:
            str: 图表文件路径
        """
        if '盈亏比例' not in portfolio_df.columns:
            logger.warning("持仓数据缺少盈亏比例信息")
            return ""
        
        # 提取盈亏数据
        pnl_ratios = portfolio_df['盈亏比例'].dropna()
        
        if len(pnl_ratios) == 0:
            logger.warning("无有效的盈亏数据")
            return ""
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # 左侧：盈亏分布直方图
        ax1.hist(pnl_ratios, bins=20, color=self.colors['primary'], alpha=0.7, edgecolor='black')
        ax1.set_xlabel('盈亏比例 (%)', fontsize=12)
        ax1.set_ylabel('股票数量', fontsize=12)
        ax1.set_title('盈亏分布直方图', fontsize=14, fontweight='bold', pad=15)
        ax1.grid(True, alpha=0.3)
        
        # 添加统计信息
        mean_pnl = pnl_ratios.mean()
        median_pnl = pnl_ratios.median()
        std_pnl = pnl_ratios.std()
        
        ax1.axvline(mean_pnl, color='red', linestyle='--', linewidth=2, label=f'均值: {mean_pnl:.1f}%')
        ax1.axvline(median_pnl, color='green', linestyle='--', linewidth=2, label=f'中位数: {median_pnl:.1f}%')
        ax1.legend(fontsize=10)
        
        # 右侧：盈亏箱线图（按行业分组）
        if '行业分类' in portfolio_df.columns:
            # 按行业分组
            portfolio_df['行业分类'] = portfolio_df['行业分类'].fillna('其他')
            
            # 只显示有足够数据的行业
            industry_counts = portfolio_df['行业分类'].value_counts()
            top_industries = industry_counts[industry_counts >= 2].index.tolist()[:8]  # 最多8个行业
            
            if top_industries:
                # 准备数据
                industry_pnl_data = []
                industry_labels = []
                
                for industry in top_industries:
                    industry_data = portfolio_df[portfolio_df['行业分类'] == industry]['盈亏比例'].dropna()
                    if len(industry_data) > 0:
                        industry_pnl_data.append(industry_data)
                        industry_labels.append(industry)
                
                # 创建箱线图
                box = ax2.boxplot(industry_pnl_data, labels=industry_labels, patch_artist=True)
                
                # 设置箱线图颜色
                for patch, industry in zip(box['boxes'], industry_labels):
                    patch.set_facecolor(self.industry_colors.get(industry, self.colors['neutral']))
                    patch.set_alpha(0.7)
                
                ax2.set_xlabel('行业', fontsize=12)
                ax2.set_ylabel('盈亏比例 (%)', fontsize=12)
                ax2.set_title('按行业分组的盈亏分布', fontsize=14, fontweight='bold', pad=15)
                ax2.grid(True, axis='y', alpha=0.3)
                ax2.tick_params(axis='x', rotation=45)
                
                # 添加整体统计信息
                total_profit = portfolio_df[portfolio_df['盈亏比例'] > 0]['盈亏比例'].count()
                total_loss = portfolio_df[portfolio_df['盈亏比例'] < 0]['盈亏比例'].count()
                profit_ratio = total_profit / len(portfolio_df) * 100
                
                fig.suptitle(f'盈亏分布分析 - 盈利股票: {total_profit}只({profit_ratio:.1f}%)，亏损股票: {total_loss}只', 
                            fontsize=16, fontweight='bold')
        
        # 保存图表
        output_path = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"生成盈亏分布图: {output_path}")
        return output_path
    
    def _generate_portfolio_dashboard(self, portfolio_df: pd.DataFrame, 
                                     analysis_results: Dict, filename: str) -> str:
        """
        生成组合摘要仪表板
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            analysis_results (Dict): 分析结果
            filename (str): 输出文件名
            
        Returns:
            str: 图表文件路径
        """
        # 创建仪表板
        fig = plt.figure(figsize=(20, 12))
        
        # 定义网格布局
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # 1. 组合摘要指标（左上）
        ax1 = fig.add_subplot(gs[0, 0])
        self._add_portfolio_summary(ax1, portfolio_df, analysis_results)
        
        # 2. 风险摘要（右上）
        ax2 = fig.add_subplot(gs[0, 1])
        self._add_risk_summary(ax2, analysis_results)
        
        # 3. 行业分布饼图（中左）
        ax3 = fig.add_subplot(gs[1, 0])
        if 'industry_distribution' in analysis_results:
            self._add_industry_pie_mini(ax3, analysis_results['industry_distribution'])
        
        # 4. 风险雷达图（中中）
        ax4 = fig.add_subplot(gs[1, 1], projection='polar')
        if 'risk_metrics' in analysis_results:
            self._add_risk_radar_mini(ax4, analysis_results['risk_metrics'])
        
        # 5. 前五大持仓（中右）
        ax5 = fig.add_subplot(gs[1, 2])
        if 'top_holdings' in analysis_results:
            self._add_top_holdings_mini(ax5, analysis_results['top_holdings'][:5])
        
        # 6. 压力测试摘要（中下左）
        ax6 = fig.add_subplot(gs[2, 0])
        if 'stress_tests' in analysis_results:
            self._add_stress_test_mini(ax6, analysis_results['stress_tests'])
        
        # 7. 轮动建议（中下中）
        ax7 = fig.add_subplot(gs[2, 1])
        if 'recommendations' in analysis_results.get('rotation_analysis', {}):
            self._add_rotation_recommendations(ax7, analysis_results.get('rotation_analysis', {}))
        
        # 8. 风险警告（中下右）
        ax8 = fig.add_subplot(gs[2, 2])
        if 'risk_warnings' in analysis_results.get('risk_assessment', {}):
            self._add_risk_warnings(ax8, analysis_results.get('risk_assessment', {}))
        
        # 9. 标题区域（顶部）
        title_ax = fig.add_subplot(gs[0, 2:])
        title_ax.axis('off')
        
        # 添加主标题
        total_value = portfolio_df['持仓市值'].sum() if '持仓市值' in portfolio_df.columns else 0
        title_text = f"投资组合分析仪表板\n总市值: {total_value:,.0f}元"
        title_ax.text(0.5, 0.5, title_text, ha='center', va='center', 
                     fontsize=18, fontweight='bold')
        
        # 添加副标题（日期）
        date_text = f"分析日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        title_ax.text(0.5, 0.2, date_text, ha='center', va='center', 
                     fontsize=12, style='italic')
        
        # 保存图表
        output_path = os.path.join(self.output_dir, filename)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"生成组合摘要仪表板: {output_path}")
        return output_path
    
    def _add_portfolio_summary(self, ax, portfolio_df, analysis_results):
        """添加组合摘要"""
        ax.axis('off')
        
        # 提取关键指标
        total_stocks = len(portfolio_df)
        total_value = portfolio_df['持仓市值'].sum() if '持仓市值' in portfolio_df.columns else 0
        avg_position = total_value / total_stocks if total_stocks > 0 else 0
        
        # 如果有盈亏数据
        if '盈亏比例' in portfolio_df.columns:
            profit_stocks = (portfolio_df['盈亏比例'] > 0).sum()
            profit_ratio = profit_stocks / total_stocks * 100 if total_stocks > 0 else 0
            total_pnl = portfolio_df['盈亏比例'].mean() if '盈亏比例' in portfolio_df.columns else 0
        else:
            profit_ratio = 0
            total_pnl = 0
        
        # 行业数量
        if '行业分类' in portfolio_df.columns:
            industry_count = portfolio_df['行业分类'].nunique()
        else:
            industry_count = 0
        
        # 创建摘要文本
        summary_text = (
            f"📊 组合摘要\n\n"
            f"股票数量: {total_stocks}只\n"
            f"行业数量: {industry_count}个\n"
            f"总市值: {total_value:,.0f}元\n"
            f"平均持仓: {avg_position:,.0f}元\n"
            f"盈利比例: {profit_ratio:.1f}%\n"
            f"平均盈亏: {total_pnl:.1f}%"
        )
        
        ax.text(0.5, 0.5, summary_text, ha='center', va='center', 
               fontsize=11, transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
        ax.set_title('组合摘要', fontsize=12, fontweight='bold')
    
    def _add_risk_summary(self, ax, analysis_results):
        """添加风险摘要"""
        ax.axis('off')
        
        # 提取风险指标
        risk_assessment = analysis_results.get('risk_assessment', {})
        overall_risk = risk_assessment.get('overall_risk', {})
        
        risk_level = overall_risk.get('overall_risk_level', '未知')
        risk_score = overall_risk.get('overall_risk_score', 50)
        
        # 风险特征
        risk_features = overall_risk.get('risk_features', {})
        primary_risk = risk_features.get('primary_risk_source', '未知')
        
        # 创建风险摘要文本
        risk_text = (
            f"⚠️ 风险摘要\n\n"
            f"风险等级: {risk_level}\n"
            f"风险分数: {risk_score:.1f}/100\n"
            f"主要风险: {primary_risk}\n"
            f"风险容忍: {overall_risk.get('risk_tolerance_match', '未知')}\n"
            f"监控频率: {overall_risk.get('risk_monitoring_frequency', '未知')}"
        )
        
        # 根据风险等级设置颜色
        if '高' in risk_level:
            box_color = 'lightcoral'
        elif '中' in risk_level:
            box_color = 'lightyellow'
        else:
            box_color = 'lightgreen'
        
        ax.text(0.5, 0.5, risk_text, ha='center', va='center', 
               fontsize=11, transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor=box_color, alpha=0.5))
        ax.set_title('风险摘要', fontsize=12, fontweight='bold')
    
    def _add_industry_pie_mini(self, ax, industry_distribution):
        """添加迷你行业饼图"""
        if not industry_distribution:
            ax.axis('off')
            ax.text(0.5, 0.5, '无行业数据', ha='center', va='center')
            return
        
        # 只显示前5大行业
        top_industries = industry_distribution[:5]
        industries = [item['行业名称'] for item in top_industries]
        proportions = [item['持仓占比'] for item in top_industries]
        colors = [self.industry_colors.get(ind, self.colors['neutral']) for ind in industries]
        
        # 绘制迷你饼图
        ax.pie(proportions, labels=industries, colors=colors, autopct='%1.0f%%',
              startangle=90, textprops={'fontsize': 8})
        ax.set_title('行业分布 (前5大)', fontsize=10, fontweight='bold')
        ax.axis('equal')
    
    def _add_risk_radar_mini(self, ax, risk_metrics):
        """添加迷你风险雷达图"""
        # 简化雷达图
        risk_categories = ['集中度', '波动性', '行业', '下行']
        
        # 获取风险分数
        risk_scores = []
        for category in ['集中度风险', '波动性风险', '行业风险', '下行风险']:
            if category in risk_metrics:
                score_key = category.lower().replace('风险', '_risk') + '_score'
                score = risk_metrics[category].get(score_key, 50)
                risk_scores.append(score)
            else:
                risk_scores.append(50)
        
        # 闭合数据
        angles = np.linspace(0, 2 * np.pi, len(risk_categories), endpoint=False).tolist()
        angles += angles[:1]
        risk_scores += risk_scores[:1]
        
        # 绘制雷达图
        ax.plot(angles, risk_scores, 'o-', linewidth=1, color=self.colors['primary'])
        ax.fill(angles, risk_scores, alpha=0.25, color=self.colors['primary'])
        
        # 设置刻度
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(risk_categories, fontsize=8)
        ax.set_ylim(0, 100)
        ax.set_yticks([25, 50, 75, 100])
        ax.set_yticklabels(['25', '50', '75', '100'], fontsize=7)
        ax.set_title('风险雷达图', fontsize=10, fontweight='bold')
    
    def _add_top_holdings_mini(self, ax, top_holdings):
        """添加前五大持仓"""
        if not top_holdings:
            ax.axis('off')
            ax.text(0.5, 0.5, '无持仓数据', ha='center', va='center')
            return
        
        # 创建水平条形图
        stock_names = [f"{h['股票名称'][:4]}" for h in top_holdings]  # 简化名称
        proportions = [h['持仓占比'] for h in top_holdings]
        
        # 绘制条形图
        y_pos = np.arange(len(stock_names))
        bars = ax.barh(y_pos, proportions, color=self.colors['primary'], alpha=0.7)
        
        # 设置属性
        ax.set_yticks(y_pos)
        ax.set_yticklabels(stock_names, fontsize=9)
        ax.set_xlabel('持仓比例 (%)', fontsize=9)
        ax.set_title('前五大持仓', fontsize=10, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)
        
        # 添加数值标签
        for bar, proportion in zip(bars, proportions):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                   f'{proportion:.1f}%', ha='left', va='center', fontsize=8)
    
    def _add_stress_test_mini(self, ax, stress_tests):
        """添加压力测试摘要"""
        ax.axis('off')
        
        if 'summary' not in stress_tests:
            ax.text(0.5, 0.5, '无压力测试数据', ha='center', va='center')
            return
        
        summary = stress_tests['summary']
        worst_case = summary.get('worst_case_loss', 0)
        resilience = summary.get('overall_resilience', '未知')
        
        # 创建摘要文本
        stress_text = (
            f"🔄 压力测试\n\n"
            f"最坏损失: {worst_case:.1f}%\n"
            f"平均损失: {summary.get('avg_stress_loss', 0):.1f}%\n"
            f"整体韧性: {resilience}\n"
            f"测试场景: {summary.get('worst_case_scenario', '未知')}"
        )
        
        # 根据韧性设置颜色
        if '高' in resilience:
            box_color = 'lightgreen'
        elif '中' in resilience:
            box_color = 'lightyellow'
        else:
            box_color = 'lightcoral'
        
        ax.text(0.5, 0.5, stress_text, ha='center', va='center', 
               fontsize=10, transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor=box_color, alpha=0.5))
        ax.set_title('压力测试', fontsize=10, fontweight='bold')
    
    def _add_rotation_recommendations(self, ax, rotation_analysis):
        """添加轮动建议"""
        ax.axis('off')
        
        recommendations = rotation_analysis.get('recommendations', [])
        
        if not recommendations:
            ax.text(0.5, 0.5, '无轮动建议', ha='center', va='center')
            return
        
        # 创建建议文本
        rec_text = "🔄 轮动建议\n\n"
        for i, rec in enumerate(recommendations[:3]):  # 最多显示3条
            rec_text += f"{i+1}. {rec['行业名称']}: {rec['建议方向']}\n"
        
        ax.text(0.5, 0.5, rec_text, ha='center', va='center', 
               fontsize=10, transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
        ax.set_title('行业轮动建议', fontsize=10, fontweight='bold')
    
    def _add_risk_warnings(self, ax, risk_assessment):
        """添加风险警告"""
        ax.axis('off')
        
        warnings = risk_assessment.get('risk_warnings', [])
        
        if not warnings:
            ax.text(0.5, 0.5, '无风险警告', ha='center', va='center')
            return
        
        # 创建警告文本
        warning_text = "⚠️ 风险警告\n\n"
        for i, warning in enumerate(warnings[:3]):  # 最多显示3条
            warning_text += f"• {warning}\n"
        
        ax.text(0.5, 0.5, warning_text, ha='center', va='center', 
               fontsize=9, transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.3))
        ax.set_title('风险警告', fontsize=10, fontweight='bold')


# 示例使用
if __name__ == "__main__":
    # 示例：可视化测试
    visualizer = PortfolioVisualizer(output_dir="../outputs/charts")
    
    # 示例数据
    sample_portfolio = pd.DataFrame([
        {'股票代码': '000001', '股票名称': '平安银行', '持仓数量': 1000, '成本价': 15.20, '最新价': 16.50, '持仓市值': 16500, '盈亏比例': 8.6},
        {'股票代码': '600036', '股票名称': '招商银行', '持仓数量': 800, '成本价': 32.50, '最新价': 35.20, '持仓市值': 28160, '盈亏比例': 8.3},
        {'股票代码': '000858', '股票名称': '五粮液', '持仓数量': 500, '成本价': 180.30, '最新价': 195.00, '持仓市值': 97500, '盈亏比例': 8.1},
        {'股票代码': '002415', '股票名称': '海康威视', '持仓数量': 300, '成本价': 35.80, '最新价': 38.50, '持仓市值': 11550, '盈亏比例': 7.5},
        {'股票代码': '600519', '股票名称': '贵州茅台', '持仓数量': 200, '成本价': 1800.00, '最新价': 1850.00, '持仓市值': 370000, '盈亏比例': 2.8},
        {'股票代码': '000333', '股票名称': '美的集团', '持仓数量': 600, '成本价': 58.90, '最新价': 62.30, '持仓市值': 37380, '盈亏比例': 5.8},
        {'股票代码': '300750', '股票名称': '宁德时代', '持仓数量': 400, '成本价': 210.50, '最新价': 225.00, '持仓市值': 90000, '盈亏比例': 6.9},
    ])
    
    # 添加行业分类
    sample_portfolio['行业分类'] = ['银行', '银行', '食品饮料', '电子', '食品饮料', '家用电器', '电气设备']
    
    # 示例分析结果
    sample_analysis = {
        'industry_distribution': [
            {'行业名称': '食品饮料', '持仓占比': 45.0, '持仓市值': 467500},
            {'行业名称': '银行', '持仓占比': 35.0, '持仓市值': 44660},
            {'行业名称': '家用电器', '持仓占比': 10.0, '持仓市值': 37380},
            {'行业名称': '电气设备', '持仓占比': 6.0, '持仓市值': 90000},
            {'行业名称': '电子', '持仓占比': 4.0, '持仓市值': 11550},
        ],
        'top_holdings': [
            {'股票代码': '600519', '股票名称': '贵州茅台', '行业分类': '食品饮料', '持仓占比': 40.0},
            {'股票代码': '000858', '股票名称': '五粮液', '行业分类': '食品饮料', '持仓占比': 12.0},
            {'股票代码': '300750', '股票名称': '宁德时代', '行业分类': '电气设备', '持仓占比': 10.0},
            {'股票代码': '000333', '股票名称': '美的集团', '行业分类': '家用电器', '持仓占比': 8.0},
            {'股票代码': '600036', '股票名称': '招商银行', '行业分类': '银行', '持仓占比': 7.0},
        ],
        'risk_metrics': {
            '集中度风险': {'concentration_risk_score': 65},
            '波动性风险': {'volatility_risk_score': 55},
            '行业风险': {'industry_risk_score': 70},
            '下行风险': {'downside_risk_score': 60},
        },
        'stress_tests': {
            'summary': {
                'worst_case_scenario': '市场崩盘',
                'worst_case_loss': -18.5,
                'avg_stress_loss': -12.3,
                'overall_resilience': '中等韧性'
            }
        },
        'rotation_analysis': {
            'recommendations': [
                {'行业名称': '食品饮料', '建议方向': '减配'},
                {'行业名称': '计算机', '建议方向': '增配'},
                {'行业名称': '医药生物', '建议方向': '关注'},
            ]
        },
        'risk_assessment': {
            'risk_warnings': [
                '持仓集中度过高，存在集中度风险',
                '食品饮料行业配置比例偏高'
            ]
        }
    }
    
    # 生成图表
    chart_files = visualizer.generate_all_charts(sample_portfolio, sample_analysis, "测试客户")
    
    if chart_files:
        print("生成的图表文件:")
        for chart_type, file_path in chart_files.items():
            print(f"- {chart_type}: {file_path}")
    else:
        print("未能生成图表")