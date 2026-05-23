#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险评估模块
分析层：风险评估、压力测试、风险预警
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json
import math

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RiskAssessor:
    """风险评估器"""
    
    def __init__(self):
        """初始化风险评估器"""
        self.risk_levels = {
            'low': '低风险',
            'medium_low': '中低风险',
            'medium': '中等风险',
            'medium_high': '中高风险',
            'high': '高风险'
        }
        
        # 风险阈值配置
        self.risk_thresholds = {
            'max_industry_exposure': 30,  # 最大行业暴露阈值（%）
            'max_stock_exposure': 10,     # 最大个股暴露阈值（%）
            'hhi_threshold': 1500,        # HHI指数阈值
            'var_95': -5,                 # 95%置信度VaR阈值（%）
            'max_drawdown': -20,          # 最大回撤阈值（%）
            'liquidity_ratio': 0.1,       # 流动性比例阈值
        }
    
    def assess_portfolio_risk(self, portfolio_df: pd.DataFrame, 
                             industry_analysis: Dict) -> Dict:
        """
        评估投资组合风险
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            industry_analysis (Dict): 行业分析结果
            
        Returns:
            Dict: 风险评估结果
        """
        logger.info("开始风险评估")
        
        if portfolio_df is None or len(portfolio_df) == 0:
            logger.warning("持仓数据为空")
            return {}
        
        # 确保有必要的列
        required_columns = ['股票代码', '持仓市值']
        missing_cols = [col for col in required_columns if col not in portfolio_df.columns]
        if missing_cols:
            logger.error(f"持仓数据缺少必要的列: {missing_cols}")
            return {}
        
        # 计算各种风险指标
        risk_metrics = self._calculate_risk_metrics(portfolio_df, industry_analysis)
        
        # 执行压力测试
        stress_test_results = self._perform_stress_tests(portfolio_df, industry_analysis)
        
        # 风险价值计算
        var_analysis = self._calculate_value_at_risk(portfolio_df)
        
        # 流动性风险评估
        liquidity_risk = self._assess_liquidity_risk(portfolio_df)
        
        # 相关性风险分析
        correlation_risk = self._analyze_correlation_risk(portfolio_df, industry_analysis)
        
        # 构建综合风险评估
        overall_risk = self._assess_overall_risk(
            risk_metrics, stress_test_results, var_analysis, 
            liquidity_risk, correlation_risk
        )
        
        risk_assessment = {
            'risk_metrics': risk_metrics,
            'stress_tests': stress_test_results,
            'value_at_risk': var_analysis,
            'liquidity_risk': liquidity_risk,
            'correlation_risk': correlation_risk,
            'overall_risk': overall_risk,
            'risk_warnings': self._generate_risk_warnings(risk_metrics, overall_risk),
            'recommendations': self._generate_risk_recommendations(risk_metrics, overall_risk),
            'assessment_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        logger.info("风险评估完成")
        return risk_assessment
    
    def _calculate_risk_metrics(self, portfolio_df: pd.DataFrame, 
                               industry_analysis: Dict) -> Dict:
        """
        计算风险指标
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            industry_analysis (Dict): 行业分析结果
            
        Returns:
            Dict: 风险指标
        """
        total_value = portfolio_df['持仓市值'].sum()
        
        # 集中度风险指标
        concentration_metrics = self._calculate_concentration_risk(portfolio_df, total_value)
        
        # 波动性风险指标
        volatility_metrics = self._calculate_volatility_risk(portfolio_df)
        
        # 行业风险指标
        industry_risk_metrics = self._calculate_industry_risk(industry_analysis)
        
        # 下行风险指标
        downside_metrics = self._calculate_downside_risk(portfolio_df)
        
        # 组合风险指标
        portfolio_risk_metrics = {
            'total_risk_score': self._calculate_total_risk_score(
                concentration_metrics, volatility_metrics, 
                industry_risk_metrics, downside_metrics
            ),
            'risk_contribution': self._calculate_risk_contribution(portfolio_df),
            'risk_adjusted_return': self._calculate_risk_adjusted_return(portfolio_df),
            'risk_budget_utilization': self._calculate_risk_budget_utilization(
                concentration_metrics, volatility_metrics
            )
        }
        
        risk_metrics = {
            'concentration_risk': concentration_metrics,
            'volatility_risk': volatility_metrics,
            'industry_risk': industry_risk_metrics,
            'downside_risk': downside_metrics,
            'portfolio_risk': portfolio_risk_metrics
        }
        
        return risk_metrics
    
    def _calculate_concentration_risk(self, portfolio_df: pd.DataFrame, 
                                     total_value: float) -> Dict:
        """
        计算集中度风险
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            total_value (float): 总市值
            
        Returns:
            Dict: 集中度风险指标
        """
        if total_value <= 0:
            return {}
        
        # 赫芬达尔-赫希曼指数 (HHI)
        market_shares = portfolio_df['持仓市值'] / total_value
        hhi = (market_shares ** 2).sum() * 10000
        
        # 前十大持仓集中度
        top_10 = portfolio_df.nlargest(10, '持仓市值')
        top_10_concentration = top_10['持仓市值'].sum() / total_value * 100
        
        # 前五大持仓集中度
        top_5 = portfolio_df.nlargest(5, '持仓市值')
        top_5_concentration = top_5['持仓市值'].sum() / total_value * 100
        
        # 最大单一持仓暴露
        max_stock_exposure = portfolio_df['持仓市值'].max() / total_value * 100
        
        # 有效持仓数量（基于HHI）
        effective_n = 1 / (hhi / 10000) if hhi > 0 else 0
        
        # 集中度风险评分
        concentration_risk_score = self._score_concentration_risk(
            hhi, max_stock_exposure, top_5_concentration
        )
        
        return {
            'hhi_index': float(hhi),
            'top_5_concentration': float(top_5_concentration),
            'top_10_concentration': float(top_10_concentration),
            'max_stock_exposure': float(max_stock_exposure),
            'effective_number_of_stocks': float(effective_n),
            'concentration_risk_score': concentration_risk_score,
            'concentration_risk_level': self._get_risk_level(concentration_risk_score)
        }
    
    def _calculate_volatility_risk(self, portfolio_df: pd.DataFrame) -> Dict:
        """
        计算波动性风险
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            
        Returns:
            Dict: 波动性风险指标
        """
        # 这里使用简化的波动性估计
        # 实际应用中应该使用历史收益率数据
        
        # 模拟波动性数据（实际应从市场数据获取）
        volatility_estimates = {
            'portfolio_volatility': np.random.uniform(15, 30),  # 年化波动率%
            'avg_stock_volatility': np.random.uniform(20, 40),
            'max_stock_volatility': np.random.uniform(30, 60),
            'volatility_clustering': np.random.uniform(0, 1),  # 波动率聚集性
            'volatility_persistence': np.random.uniform(0.5, 0.9),  # 波动率持续性
        }
        
        # 波动性风险评分
        volatility_risk_score = self._score_volatility_risk(volatility_estimates)
        
        return {
            'volatility_estimates': volatility_estimates,
            'volatility_risk_score': volatility_risk_score,
            'volatility_risk_level': self._get_risk_level(volatility_risk_score)
        }
    
    def _calculate_industry_risk(self, industry_analysis: Dict) -> Dict:
        """
        计算行业风险
        
        Args:
            industry_analysis (Dict): 行业分析结果
            
        Returns:
            Dict: 行业风险指标
        """
        if not industry_analysis or 'industry_distribution' not in industry_analysis:
            return {}
        
        industry_distribution = industry_analysis['industry_distribution']
        
        # 最大行业暴露
        max_industry_exposure = max([d['持仓占比'] for d in industry_distribution]) if industry_distribution else 0
        
        # 前三大行业集中度
        top_3_industries = sorted(industry_distribution, key=lambda x: x['持仓占比'], reverse=True)[:3]
        top_3_concentration = sum([d['持仓占比'] for d in top_3_industries])
        
        # 行业多样性指数
        industry_shares = [d['持仓占比'] / 100 for d in industry_distribution]
        industry_diversity = 1 - sum([s ** 2 for s in industry_shares])  # 赫芬达尔指数的补集
        
        # 行业相关性风险（简化估计）
        industry_correlation_risk = self._estimate_industry_correlation_risk(industry_distribution)
        
        # 行业风险评分
        industry_risk_score = self._score_industry_risk(
            max_industry_exposure, top_3_concentration, industry_diversity
        )
        
        return {
            'max_industry_exposure': float(max_industry_exposure),
            'top_3_industry_concentration': float(top_3_concentration),
            'industry_diversity_index': float(industry_diversity),
            'industry_correlation_risk': industry_correlation_risk,
            'industry_risk_score': industry_risk_score,
            'industry_risk_level': self._get_risk_level(industry_risk_score)
        }
    
    def _calculate_downside_risk(self, portfolio_df: pd.DataFrame) -> Dict:
        """
        计算下行风险
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            
        Returns:
            Dict: 下行风险指标
        """
        # 模拟下行风险指标
        downside_metrics = {
            'expected_shortfall_95': np.random.uniform(-8, -2),  # 预期损失95%
            'worst_month_return': np.random.uniform(-15, -5),    # 最差月度回报
            'downside_deviation': np.random.uniform(5, 15),      # 下行标准差
            'pain_index': np.random.uniform(0.2, 0.8),           # 痛苦指数
            'ulcer_index': np.random.uniform(5, 20),             # 溃疡指数
        }
        
        # 最大回撤估计（基于模拟）
        drawdown_analysis = {
            'max_drawdown': np.random.uniform(-25, -10),
            'avg_drawdown': np.random.uniform(-15, -5),
            'drawdown_duration': np.random.uniform(30, 180),  # 天数
            'recovery_time': np.random.uniform(60, 360),      # 恢复时间（天）
        }
        
        # 下行风险评分
        downside_risk_score = self._score_downside_risk(downside_metrics, drawdown_analysis)
        
        return {
            'downside_metrics': downside_metrics,
            'drawdown_analysis': drawdown_analysis,
            'downside_risk_score': downside_risk_score,
            'downside_risk_level': self._get_risk_level(downside_risk_score)
        }
    
    def _perform_stress_tests(self, portfolio_df: pd.DataFrame, 
                             industry_analysis: Dict) -> Dict:
        """
        执行压力测试
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            industry_analysis (Dict): 行业分析结果
            
        Returns:
            Dict: 压力测试结果
        """
        logger.info("执行压力测试")
        
        total_value = portfolio_df['持仓市值'].sum()
        
        # 定义压力测试场景
        stress_scenarios = {
            'market_crash': {
                'name': '市场崩盘',
                'description': '全市场下跌20%，高波动性股票下跌30%',
                'overall_shock': -20,  # 整体冲击%
                'high_beta_multiplier': 1.5  # 高贝塔股票乘数
            },
            'industry_specific': {
                'name': '行业特定冲击',
                'description': '最大暴露行业下跌30%，相关行业下跌15%',
                'primary_shock': -30,
                'secondary_shock': -15
            },
            'liquidity_crisis': {
                'name': '流动性危机',
                'description': '小盘股和低流动性股票下跌40%，大盘股下跌15%',
                'small_cap_shock': -40,
                'large_cap_shock': -15
            },
            'interest_rate_shock': {
                'name': '利率冲击',
                'description': '利率敏感行业下跌25%（金融、房地产等）',
                'rate_sensitive_shock': -25
            }
        }
        
        stress_test_results = {}
        
        for scenario_name, scenario in stress_scenarios.items():
            # 计算压力测试下的损失
            loss_estimate = self._estimate_stress_loss(
                portfolio_df, industry_analysis, scenario
            )
            
            # 计算风险指标
            loss_pct = loss_estimate / total_value * 100 if total_value > 0 else 0
            
            stress_test_results[scenario_name] = {
                'scenario_name': scenario['name'],
                'scenario_description': scenario['description'],
                'estimated_loss': float(loss_estimate),
                'loss_percentage': float(loss_pct),
                'survival_rate': max(0, 100 - abs(loss_pct)),  # 幸存率
                'capital_adequacy': self._assess_capital_adequacy(loss_pct),
                'recovery_strategy': self._suggest_recovery_strategy(scenario_name, loss_pct)
            }
        
        # 最坏情况分析
        worst_case_loss = min([result['loss_percentage'] for result in stress_test_results.values()])
        worst_case_scenario = min(stress_test_results.items(), 
                                 key=lambda x: x[1]['loss_percentage'])[0]
        
        stress_test_results['summary'] = {
            'worst_case_scenario': worst_case_scenario,
            'worst_case_loss': float(worst_case_loss),
            'avg_stress_loss': float(np.mean([r['loss_percentage'] for r in stress_test_results.values()])),
            'stress_test_score': self._score_stress_test_results(stress_test_results),
            'overall_resilience': self._assess_overall_resilience(stress_test_results)
        }
        
        return stress_test_results
    
    def _estimate_stress_loss(self, portfolio_df: pd.DataFrame, 
                             industry_analysis: Dict, scenario: Dict) -> float:
        """
        估计压力测试损失
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            industry_analysis (Dict): 行业分析结果
            scenario (Dict): 压力测试场景
            
        Returns:
            float: 估计损失金额
        """
        total_loss = 0
        
        # 简化估计：根据场景类型应用不同的冲击
        scenario_type = list(scenario.keys())[0] if isinstance(scenario, dict) else ''
        
        if scenario_type == 'market_crash':
            # 市场崩盘场景：所有股票下跌，高波动性股票下跌更多
            for _, row in portfolio_df.iterrows():
                base_shock = scenario['overall_shock']
                # 简化的波动性判断（实际应根据历史波动性）
                stock_volatility = np.random.uniform(0.8, 1.5)  # 波动性乘数
                stock_shock = base_shock * stock_volatility
                stock_loss = row['持仓市值'] * abs(stock_shock) / 100
                total_loss += stock_loss
                
        elif scenario_type == 'industry_specific':
            # 行业特定冲击
            if industry_analysis and 'industry_distribution' in industry_analysis:
                industry_dist = industry_analysis['industry_distribution']
                if industry_dist:
                    # 找出最大暴露行业
                    max_industry = max(industry_dist, key=lambda x: x['持仓占比'])
                    max_industry_name = max_industry['行业名称']
                    
                    for _, row in portfolio_df.iterrows():
                        # 获取股票行业（简化处理）
                        stock_industry = self._get_stock_industry(row['股票代码'])
                        
                        if stock_industry == max_industry_name:
                            shock = scenario['primary_shock']
                        elif self._are_industries_related(stock_industry, max_industry_name):
                            shock = scenario['secondary_shock']
                        else:
                            shock = -5  # 轻微影响
                        
                        stock_loss = row['持仓市值'] * abs(shock) / 100
                        total_loss += stock_loss
        
        elif scenario_type == 'liquidity_crisis':
            # 流动性危机：小盘股和低流动性股票受影响更大
            for _, row in portfolio_df.iterrows():
                # 简化的流动性判断（实际应根据市值和换手率）
                stock_market_cap = row.get('总市值', 0)
                if stock_market_cap < 50e8:  # 小于500亿
                    shock = scenario['small_cap_shock']
                else:
                    shock = scenario['large_cap_shock']
                
                stock_loss = row['持仓市值'] * abs(shock) / 100
                total_loss += stock_loss
                
        else:
            # 默认：统一冲击
            base_shock = -20
            for _, row in portfolio_df.iterrows():
                stock_loss = row['持仓市值'] * abs(base_shock) / 100
                total_loss += stock_loss
        
        return total_loss
    
    def _calculate_value_at_risk(self, portfolio_df: pd.DataFrame) -> Dict:
        """
        计算风险价值（VaR）
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            
        Returns:
            Dict: VaR分析结果
        """
        # 简化VaR计算（实际应使用历史模拟法或蒙特卡洛模拟）
        total_value = portfolio_df['持仓市值'].sum()
        
        # 模拟VaR估计
        var_estimates = {
            'var_95_1d': np.random.uniform(-3, -1),      # 95%置信度，1天VaR
            'var_99_1d': np.random.uniform(-5, -2),      # 99%置信度，1天VaR
            'var_95_10d': np.random.uniform(-8, -4),     # 95%置信度，10天VaR
            'var_99_10d': np.random.uniform(-12, -6),    # 99%置信度，10天VaR
            'conditional_var_95': np.random.uniform(-5, -2.5),  # 条件VaR
        }
        
        # 转换为金额
        var_amounts = {}
        for key, var_pct in var_estimates.items():
            var_amounts[key.replace('var', 'var_amount')] = total_value * abs(var_pct) / 100
        
        # VaR回测评分（简化）
        var_backtest_score = np.random.uniform(0, 100)
        
        return {
            'var_estimates_percentage': var_estimates,
            'var_estimates_amount': var_amounts,
            'var_backtest_score': float(var_backtest_score),
            'var_model_adequacy': self._assess_var_model_adequacy(var_backtest_score),
            'var_breach_probability': self._estimate_var_breach_probability(var_estimates)
        }
    
    def _assess_liquidity_risk(self, portfolio_df: pd.DataFrame) -> Dict:
        """
        评估流动性风险
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            
        Returns:
            Dict: 流动性风险评估
        """
        # 简化流动性风险评估
        liquidity_metrics = {
            'portfolio_liquidity_score': np.random.uniform(0, 100),
            'avg_daily_turnover': np.random.uniform(0.5, 3),  # 平均日换手率%
            'illiquid_assets_ratio': np.random.uniform(0, 0.3),  # 非流动性资产比例
            'liquidation_horizon': np.random.uniform(5, 30),  # 清算时间（天）
            'market_impact_cost': np.random.uniform(0.5, 2.5),  # 市场冲击成本%
        }
        
        # 流动性压力测试
        liquidity_stress = {
            'crisis_liquidity': liquidity_metrics['portfolio_liquidity_score'] * 0.3,  # 危机时期流动性
            'fire_sale_discount': np.random.uniform(15, 40),  # 紧急抛售折价%
            'funding_liquidity_risk': np.random.uniform(0, 1),  # 融资流动性风险
        }
        
        # 流动性风险评分
        liquidity_risk_score = self._score_liquidity_risk(liquidity_metrics, liquidity_stress)
        
        return {
            'liquidity_metrics': liquidity_metrics,
            'liquidity_stress': liquidity_stress,
            'liquidity_risk_score': liquidity_risk_score,
            'liquidity_risk_level': self._get_risk_level(liquidity_risk_score),
            'liquidity_warnings': self._generate_liquidity_warnings(liquidity_metrics)
        }
    
    def _analyze_correlation_risk(self, portfolio_df: pd.DataFrame, 
                                 industry_analysis: Dict) -> Dict:
        """
        分析相关性风险
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            industry_analysis (Dict): 行业分析结果
            
        Returns:
            Dict: 相关性风险分析
        """
        # 简化相关性分析
        correlation_metrics = {
            'avg_correlation': np.random.uniform(0.3, 0.7),
            'max_pairwise_correlation': np.random.uniform(0.6, 0.9),
            'correlation_clustering': np.random.uniform(0, 1),
            'diversification_benefit': np.random.uniform(10, 40),  # 分散化收益%
            'tail_correlation': np.random.uniform(0.4, 0.8),  # 尾部相关性
        }
        
        # 系统性风险暴露
        systemic_risk = {
            'market_beta': np.random.uniform(0.8, 1.2),
            'size_factor_exposure': np.random.uniform(-0.5, 0.5),
            'value_factor_exposure': np.random.uniform(-0.3, 0.3),
            'momentum_factor_exposure': np.random.uniform(-0.2, 0.2),
        }
        
        # 相关性风险评分
        correlation_risk_score = self._score_correlation_risk(correlation_metrics, systemic_risk)
        
        return {
            'correlation_metrics': correlation_metrics,
            'systemic_risk': systemic_risk,
            'correlation_risk_score': correlation_risk_score,
            'correlation_risk_level': self._get_risk_level(correlation_risk_score),
            'diversification_effectiveness': self._assess_diversification_effectiveness(correlation_metrics)
        }
    
    def _assess_overall_risk(self, risk_metrics: Dict, stress_test_results: Dict,
                            var_analysis: Dict, liquidity_risk: Dict, 
                            correlation_risk: Dict) -> Dict:
        """
        综合风险评估
        
        Args:
            risk_metrics (Dict): 风险指标
            stress_test_results (Dict): 压力测试结果
            var_analysis (Dict): VaR分析结果
            liquidity_risk (Dict): 流动性风险评估
            correlation_risk (Dict): 相关性风险分析
            
        Returns:
            Dict: 综合风险评估
        """
        # 收集各个维度的风险评分
        risk_scores = {
            'concentration_risk': risk_metrics.get('concentration_risk', {}).get('concentration_risk_score', 50),
            'volatility_risk': risk_metrics.get('volatility_risk', {}).get('volatility_risk_score', 50),
            'industry_risk': risk_metrics.get('industry_risk', {}).get('industry_risk_score', 50),
            'downside_risk': risk_metrics.get('downside_risk', {}).get('downside_risk_score', 50),
            'stress_test': stress_test_results.get('summary', {}).get('stress_test_score', 50),
            'var_risk': var_analysis.get('var_backtest_score', 50),
            'liquidity_risk': liquidity_risk.get('liquidity_risk_score', 50),
            'correlation_risk': correlation_risk.get('correlation_risk_score', 50),
        }
        
        # 计算加权总分
        weights = {
            'concentration_risk': 0.15,
            'volatility_risk': 0.15,
            'industry_risk': 0.15,
            'downside_risk': 0.15,
            'stress_test': 0.10,
            'var_risk': 0.10,
            'liquidity_risk': 0.10,
            'correlation_risk': 0.10,
        }
        
        overall_score = sum(risk_scores[key] * weights[key] for key in weights.keys())
        
        # 风险等级
        risk_level = self._get_risk_level(overall_score)
        
        # 风险特征分析
        risk_features = self._analyze_risk_features(risk_scores)
        
        return {
            'overall_risk_score': float(overall_score),
            'overall_risk_level': risk_level,
            'component_scores': risk_scores,
            'risk_features': risk_features,
            'risk_tolerance_match': self._assess_risk_tolerance_match(overall_score),
            'risk_monitoring_frequency': self._recommend_monitoring_frequency(overall_score)
        }
    
    # 辅助方法（评分、评估、建议等）
    def _score_concentration_risk(self, hhi, max_stock_exposure, top_5_concentration):
        """集中度风险评分（分数越高风险越高）"""
        score = 0
        if hhi > 2500:
            score += 90
        elif hhi > 1500:
            score += 70
        elif hhi > 1000:
            score += 50
        elif hhi > 500:
            score += 30
        else:
            score += 10
        
        if max_stock_exposure > 20:
            score += 80
        elif max_stock_exposure > 10:
            score += 60
        elif max_stock_exposure > 5:
            score += 40
        else:
            score += 20
        
        if top_5_concentration > 80:
            score += 70
        elif top_5_concentration > 60:
            score += 50
        elif top_5_concentration > 40:
            score += 30
        else:
            score += 10
        
        return min(100, score / 3)  # 平均分
    
    def _score_volatility_risk(self, volatility_estimates):
        """波动性风险评分"""
        portfolio_vol = volatility_estimates['portfolio_volatility']
        if portfolio_vol > 40:
            return 90
        elif portfolio_vol > 30:
            return 70
        elif portfolio_vol > 20:
            return 50
        elif portfolio_vol > 10:
            return 30
        else:
            return 10
    
    def _score_industry_risk(self, max_industry_exposure, top_3_concentration, industry_diversity):
        """行业风险评分"""
        score = 0
        if max_industry_exposure > 40:
            score += 90
        elif max_industry_exposure > 30:
            score += 70
        elif max_industry_exposure > 20:
            score += 50
        elif max_industry_exposure > 10:
            score += 30
        else:
            score += 10
        
        if top_3_concentration > 80:
            score += 80
        elif top_3_concentration > 60:
            score += 60
        elif top_3_concentration > 40:
            score += 40
        else:
            score += 20
        
        if industry_diversity < 0.3:
            score += 70
        elif industry_diversity < 0.5:
            score += 50
        elif industry_diversity < 0.7:
            score += 30
        else:
            score += 10
        
        return min(100, score / 3)
    
    def _score_downside_risk(self, downside_metrics, drawdown_analysis):
        """下行风险评分"""
        score = 0
        if downside_metrics['expected_shortfall_95'] < -10:
            score += 90
        elif downside_metrics['expected_shortfall_95'] < -7:
            score += 70
        elif downside_metrics['expected_shortfall_95'] < -4:
            score += 50
        elif downside_metrics['expected_shortfall_95'] < -2:
            score += 30
        else:
            score += 10
        
        if drawdown_analysis['max_drawdown'] < -30:
            score += 80
        elif drawdown_analysis['max_drawdown'] < -20:
            score += 60
        elif drawdown_analysis['max_drawdown'] < -10:
            score += 40
        else:
            score += 20
        
        return min(100, score / 2)
    
    def _score_stress_test_results(self, stress_test_results):
        """压力测试评分"""
        worst_case_loss = stress_test_results['summary']['worst_case_loss']
        if worst_case_loss < -30:
            return 90
        elif worst_case_loss < -20:
            return 70
        elif worst_case_loss < -10:
            return 50
        elif worst_case_loss < -5:
            return 30
        else:
            return 10
    
    def _score_liquidity_risk(self, liquidity_metrics, liquidity_stress):
        """流动性风险评分"""
        score = liquidity_metrics['portfolio_liquidity_score']
        # 反转分数：流动性分数越高，风险越低
        return 100 - score
    
    def _score_correlation_risk(self, correlation_metrics, systemic_risk):
        """相关性风险评分"""
        score = 0
        if correlation_metrics['avg_correlation'] > 0.7:
            score += 80
        elif correlation_metrics['avg_correlation'] > 0.5:
            score += 60
        elif correlation_metrics['avg_correlation'] > 0.3:
            score += 40
        else:
            score += 20
        
        if abs(systemic_risk['market_beta'] - 1) > 0.3:
            score += 20
        
        return min(100, score)
    
    def _calculate_total_risk_score(self, concentration_risk, volatility_risk, 
                                   industry_risk, downside_risk):
        """计算总风险分数"""
        scores = [
            concentration_risk.get('concentration_risk_score', 50),
            volatility_risk.get('volatility_risk_score', 50),
            industry_risk.get('industry_risk_score', 50),
            downside_risk.get('downside_risk_score', 50)
        ]
        return sum(scores) / len(scores)
    
    def _calculate_risk_contribution(self, portfolio_df):
        """计算风险贡献"""
        # 简化实现
        return {"method": "需要历史收益率数据"}
    
    def _calculate_risk_adjusted_return(self, portfolio_df):
        """计算风险调整后收益"""
        # 简化实现
        return {"sharpe_ratio": 0.5, "sortino_ratio": 0.7}
    
    def _calculate_risk_budget_utilization(self, concentration_risk, volatility_risk):
        """计算风险预算使用率"""
        return {"utilization": 75, "budget_remaining": 25}
    
    def _estimate_industry_correlation_risk(self, industry_distribution):
        """估计行业相关性风险"""
        return {"level": "中等", "description": "行业间相关性适中"}
    
    def _get_stock_industry(self, stock_code):
        """获取股票行业（简化）"""
        # 实际应从行业映射获取
        return "银行" if stock_code in ['000001', '600036'] else "其他"
    
    def _are_industries_related(self, industry1, industry2):
        """判断行业是否相关"""
        related_groups = [
            ['银行', '非银金融'],
            ['食品饮料', '家用电器'],
            ['电子', '计算机', '通信'],
            ['医药生物', '化工']
        ]
        for group in related_groups:
            if industry1 in group and industry2 in group:
                return True
        return False
    
    def _assess_capital_adequacy(self, loss_pct):
        """评估资本充足性"""
        if loss_pct > -10:
            return "充足"
        elif loss_pct > -20:
            return "适度"
        elif loss_pct > -30:
            return "紧张"
        else:
            return "不足"
    
    def _suggest_recovery_strategy(self, scenario_name, loss_pct):
        """建议恢复策略"""
        if loss_pct > -10:
            return "正常运作，无需特别措施"
        elif loss_pct > -20:
            return "适度降低风险敞口，增加流动性"
        elif loss_pct > -30:
            return "显著减仓，增加对冲"
        else:
            return "紧急措施：大幅减仓，增加现金比例"
    
    def _assess_var_model_adequacy(self, backtest_score):
        """评估VaR模型充分性"""
        if backtest_score > 90:
            return "优秀"
        elif backtest_score > 70:
            return "良好"
        elif backtest_score > 50:
            return "一般"
        else:
            return "需要改进"
    
    def _estimate_var_breach_probability(self, var_estimates):
        """估计VaR突破概率"""
        return {"probability": 5.2, "confidence": "中等"}
    
    def _generate_liquidity_warnings(self, liquidity_metrics):
        """生成流动性警告"""
        warnings = []
        if liquidity_metrics['illiquid_assets_ratio'] > 0.2:
            warnings.append("非流动性资产比例较高")
        if liquidity_metrics['liquidation_horizon'] > 20:
            warnings.append("清算时间较长")
        if liquidity_metrics['market_impact_cost'] > 2:
            warnings.append("市场冲击成本较高")
        return warnings
    
    def _assess_diversification_effectiveness(self, correlation_metrics):
        """评估分散化效果"""
        if correlation_metrics['diversification_benefit'] > 30:
            return "优秀"
        elif correlation_metrics['diversification_benefit'] > 20:
            return "良好"
        elif correlation_metrics['diversification_benefit'] > 10:
            return "一般"
        else:
            return "有限"
    
    def _analyze_risk_features(self, risk_scores):
        """分析风险特征"""
        max_risk = max(risk_scores.items(), key=lambda x: x[1])
        min_risk = min(risk_scores.items(), key=lambda x: x[1])
        
        features = {
            'primary_risk_source': max_risk[0],
            'primary_risk_level': self._get_risk_level(max_risk[1]),
            'relative_strength': min_risk[0],
            'risk_balance': "均衡" if max(risk_scores.values()) - min(risk_scores.values()) < 30 else "不均衡",
            'risk_concentration': "分散" if len([s for s in risk_scores.values() if s > 70]) < 2 else "集中"
        }
        return features
    
    def _assess_risk_tolerance_match(self, overall_score):
        """评估风险容忍度匹配"""
        if overall_score < 30:
            return "匹配保守型投资者"
        elif overall_score < 50:
            return "匹配稳健型投资者"
        elif overall_score < 70:
            return "匹配平衡型投资者"
        elif overall_score < 85:
            return "匹配成长型投资者"
        else:
            return "匹配进取型投资者"
    
    def _recommend_monitoring_frequency(self, overall_score):
        """建议监控频率"""
        if overall_score > 70:
            return "每日监控"
        elif overall_score > 50:
            return "每周监控"
        elif overall_score > 30:
            return "每月监控"
        else:
            return "每季度监控"
    
    def _get_risk_level(self, score):
        """获取风险等级"""
        if score < 30:
            return self.risk_levels['low']
        elif score < 50:
            return self.risk_levels['medium_low']
        elif score < 70:
            return self.risk_levels['medium']
        elif score < 85:
            return self.risk_levels['medium_high']
        else:
            return self.risk_levels['high']
    
    def _generate_risk_warnings(self, risk_metrics, overall_risk):
        """生成风险警告"""
        warnings = []
        
        # 检查各项风险指标
        if risk_metrics.get('concentration_risk', {}).get('concentration_risk_level', '') == '高风险':
            warnings.append("⚠️ 持仓集中度过高，存在集中度风险")
        
        if risk_metrics.get('industry_risk', {}).get('industry_risk_level', '') == '高风险':
            warnings.append("⚠️ 行业集中度过高，存在行业风险")
        
        if risk_metrics.get('downside_risk', {}).get('downside_risk_level', '') == '高风险':
            warnings.append("⚠️ 下行风险较高，可能存在较大回撤")
        
        if overall_risk.get('overall_risk_level', '') in ['中高风险', '高风险']:
            warnings.append("⚠️ 整体风险等级较高，建议调整仓位")
        
        return warnings
    
    def _generate_risk_recommendations(self, risk_metrics, overall_risk):
        """生成风险建议"""
        recommendations = []
        
        # 根据风险指标生成建议
        concentration_data = risk_metrics.get('concentration_risk', {})
        if concentration_data.get('max_stock_exposure', 0) > 10:
            recommendations.append({
                'type': '集中度风险',
                'action': '降低最大持仓暴露',
                'target': f"将最大个股暴露从{concentration_data['max_stock_exposure']:.1f}%降低到10%以下",
                'priority': '高'
            })
        
        industry_data = risk_metrics.get('industry_risk', {})
        if industry_data.get('max_industry_exposure', 0) > 30:
            recommendations.append({
                'type': '行业风险',
                'action': '分散行业配置',
                'target': f"将最大行业暴露从{industry_data['max_industry_exposure']:.1f}%降低到30%以下",
                'priority': '高'
            })
        
        if overall_risk.get('overall_risk_level', '') in ['中高风险', '高风险']:
            recommendations.append({
                'type': '整体风险',
                'action': '降低整体风险敞口',
                'target': '将仓位降低10-20%，增加现金比例',
                'priority': '高'
            })
        
        # 添加一般性建议
        recommendations.append({
            'type': '风险管理',
            'action': '建立止损机制',
            'target': '设置个股和组合级别的止损线',
            'priority': '中'
        })
        
        recommendations.append({
            'type': '监控',
            'action': '加强风险监控',
            'target': overall_risk.get('risk_monitoring_frequency', '每周监控'),
            'priority': '中'
        })
        
        return recommendations
    
    def _assess_overall_resilience(self, stress_test_results):
        """评估整体韧性"""
        avg_loss = stress_test_results['summary']['avg_stress_loss']
        if avg_loss > -10:
            return "高韧性"
        elif avg_loss > -20:
            return "中等韧性"
        elif avg_loss > -30:
            return "低韧性"
        else:
            return "脆弱"


# 示例使用
if __name__ == "__main__":
    # 示例：风险评估
    assessor = RiskAssessor()
    
    # 示例持仓数据
    sample_portfolio = pd.DataFrame([
        {'股票代码': '000001', '股票名称': '平安银行', '持仓数量': 1000, '成本价': 15.20, '最新价': 16.50, '持仓市值': 16500},
        {'股票代码': '600036', '股票名称': '招商银行', '持仓数量': 800, '成本价': 32.50, '最新价': 35.20, '持仓市值': 28160},
        {'股票代码': '000858', '股票名称': '五粮液', '持仓数量': 500, '成本价': 180.30, '最新价': 195.00, '持仓市值': 97500},
        {'股票代码': '002415', '股票名称': '海康威视', '持仓数量': 300, '成本价': 35.80, '最新价': 38.50, '持仓市值': 11550},
        {'股票代码': '600519', '股票名称': '贵州茅台', '持仓数量': 200, '成本价': 1800.00, '最新价': 1850.00, '持仓市值': 370000},
    ])
    
    # 示例行业分析
    sample_industry_analysis = {
        'industry_distribution': [
            {'行业名称': '食品饮料', '持仓占比': 45.0},
            {'行业名称': '银行', '持仓占比': 35.0},
            {'行业名称': '电子', '持仓占比': 20.0},
        ]
    }
    
    # 执行风险评估
    risk_assessment = assessor.assess_portfolio_risk(sample_portfolio, sample_industry_analysis)
    
    if risk_assessment:
        print("风险评估结果:")
        print(f"整体风险等级: {risk_assessment['overall_risk']['overall_risk_level']}")
        print(f"整体风险分数: {risk_assessment['overall_risk']['overall_risk_score']:.1f}")
        
        print("\n风险警告:")
        for warning in risk_assessment['risk_warnings']:
            print(f"- {warning}")
        
        print("\n风险建议:")
        for rec in risk_assessment['recommendations'][:3]:
            print(f"- [{rec['priority']}] {rec['action']}: {rec['target']}")
        
        print("\n压力测试最坏情况:")
        stress_summary = risk_assessment['stress_tests']['summary']
        print(f"场景: {stress_summary['worst_case_scenario']}")
        print(f"损失: {stress_summary['worst_case_loss']:.1f}%")
        print(f"整体韧性: {stress_summary['overall_resilience']}")