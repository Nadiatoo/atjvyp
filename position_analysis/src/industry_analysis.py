#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行业分析模块
分析层：持仓结构分析、行业轮动分析、板块配置分析
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IndustryAnalyzer:
    """行业分析器"""
    
    def __init__(self, industry_mapping_file="../data/sw_industry.csv"):
        """
        初始化行业分析器
        
        Args:
            industry_mapping_file (str): 行业分类映射文件路径
        """
        self.industry_mapping = {}
        self.industry_data = {}
        self.history_data = {}  # 历史行业配置数据
        
        # 加载行业分类数据
        self._load_industry_mapping(industry_mapping_file)
    
    def _load_industry_mapping(self, file_path):
        """
        加载行业分类映射
        
        Args:
            file_path (str): 行业分类文件路径
        """
        try:
            if os.path.exists(file_path):
                df = pd.read_csv(file_path, encoding='utf-8')
                # 这里应该有一个股票代码到行业的映射表
                # 示例中我们使用简化的硬编码映射
                logger.info(f"加载行业分类数据: {file_path}")
            else:
                logger.warning(f"行业分类文件不存在: {file_path}")
                # 使用示例映射
                self._create_sample_mapping()
                
        except Exception as e:
            logger.error(f"加载行业分类数据失败: {str(e)}")
            self._create_sample_mapping()
    
    def _create_sample_mapping(self):
        """创建示例行业映射"""
        # 申万一级行业示例映射
        sample_mapping = {
            # 银行
            '000001': '银行', '600036': '银行', '601398': '银行', '601288': '银行',
            '601328': '银行', '601939': '银行', '601988': '银行', '601818': '银行',
            
            # 非银金融
            '601318': '非银金融', '601628': '非银金融', '601601': '非银金融',
            '600030': '非银金融', '600837': '非银金融', '000776': '非银金融',
            
            # 食品饮料
            '000858': '食品饮料', '600519': '食品饮料', '000568': '食品饮料',
            '600887': '食品饮料', '603288': '食品饮料', '000596': '食品饮料',
            
            # 电子
            '002415': '电子', '000725': '电子', '002475': '电子', '000100': '电子',
            '002241': '电子', '002456': '电子', '300433': '电子', '300782': '电子',
            
            # 医药生物
            '600276': '医药生物', '000538': '医药生物', '600196': '医药生物',
            '600085': '医药生物', '002294': '医药生物', '300760': '医药生物',
            
            # 家用电器
            '000333': '家用电器', '000651': '家用电器', '002032': '家用电器',
            '002050': '家用电器', '002242': '家用电器', '002035': '家用电器',
            
            # 电气设备
            '300750': '电气设备', '002812': '电气设备', '300274': '电气设备',
            '002129': '电气设备', '600875': '电气设备', '601012': '电气设备',
            
            # 计算机
            '000977': '计算机', '002230': '计算机', '300033': '计算机',
            '002405': '计算机', '600570': '计算机', '300017': '计算机',
            
            # 房地产
            '000002': '房地产', '600048': '房地产', '601155': '房地产',
            '000656': '房地产', '002146': '房地产', '600383': '房地产',
            
            # 汽车
            '600104': '汽车', '000625': '汽车', '002594': '汽车',
            '601238': '汽车', '000550': '汽车', '600660': '汽车',
        }
        
        self.industry_mapping = sample_mapping
        logger.info("使用示例行业映射，共包含 %d 只股票" % len(sample_mapping))
    
    def analyze_portfolio_structure(self, portfolio_df: pd.DataFrame) -> Dict:
        """
        分析持仓结构
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据，应包含股票代码、持仓市值
            
        Returns:
            Dict: 持仓结构分析结果
        """
        # 类型检查：确保portfolio_df是DataFrame
        if isinstance(portfolio_df, pd.Series):
            portfolio_df = pd.DataFrame([portfolio_df])
            logger.warning("输入为Series，已转换为DataFrame")
        elif not isinstance(portfolio_df, pd.DataFrame):
            logger.error(f"输入类型错误: {type(portfolio_df)}，应为DataFrame")
            return {}
        
        if portfolio_df is None or len(portfolio_df) == 0:
            logger.warning("持仓数据为空")
            return {}
        
        logger.info(f"开始分析持仓结构，共 {len(portfolio_df)} 只股票")
        
        # 确保portfolio_df是DataFrame
        if isinstance(portfolio_df, pd.Series):
            portfolio_df = portfolio_df.to_frame().T
        
        # 确保有持仓市值列
        if '持仓市值' not in portfolio_df.columns:
            logger.error("持仓数据缺少'持仓市值'列")
            return {}
        
        # 获取行业信息
        portfolio_df['行业分类'] = portfolio_df['股票代码'].apply(
            lambda x: self.industry_mapping.get(x, '其他')
        )
        
        # 计算行业分布
        industry_distribution = self._calculate_industry_distribution(portfolio_df)
        
        # 计算集中度指标
        concentration_metrics = self._calculate_concentration_metrics(portfolio_df, industry_distribution)
        
        # 计算行业偏离度（相对于市场基准）
        industry_deviation = self._calculate_industry_deviation(industry_distribution)
        
        # 构建分析结果
        analysis_result = {
            'portfolio_summary': {
                'total_stocks': len(portfolio_df),
                'total_market_value': float(portfolio_df['持仓市值'].sum()),
                'avg_position_size': float(portfolio_df['持仓市值'].mean()),
                'median_position_size': float(portfolio_df['持仓市值'].median()),
                'max_position': float(portfolio_df['持仓市值'].max()),
                'min_position': float(portfolio_df['持仓市值'].min()),
            },
            'industry_distribution': industry_distribution,
            'concentration_analysis': concentration_metrics,
            'industry_deviation': industry_deviation,
            'top_holdings': self._get_top_holdings(portfolio_df, top_n=10),
            'industry_exposure': self._calculate_industry_exposure(portfolio_df),
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        logger.info("持仓结构分析完成")
        return analysis_result
    
    def _calculate_industry_distribution(self, portfolio_df: pd.DataFrame) -> List[Dict]:
        """
        计算行业分布
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            
        Returns:
            List[Dict]: 行业分布列表
        """
        # 按行业分组计算
        industry_groups = portfolio_df.groupby('行业分类')
        
        distribution = []
        total_value = portfolio_df['持仓市值'].sum()
        
        for industry, group in industry_groups:
            industry_value = group['持仓市值'].sum()
            industry_proportion = industry_value / total_value * 100 if total_value > 0 else 0
            
            # 计算行业内个股分布
            stocks_in_industry = []
            for _, row in group.iterrows():
                stock_proportion = row['持仓市值'] / industry_value * 100 if industry_value > 0 else 0
                stocks_in_industry.append({
                    '股票代码': row['股票代码'],
                    '股票名称': row.get('股票名称', ''),
                    '持仓市值': float(row['持仓市值']),
                    '行业占比': float(stock_proportion),
                    '盈亏比例': float(row.get('盈亏比例', 0)) if '盈亏比例' in row.index else 0
                })
            
            # 按持仓市值排序
            stocks_in_industry.sort(key=lambda x: x['持仓市值'], reverse=True)
            
            distribution.append({
                '行业名称': industry,
                '持仓市值': float(industry_value),
                '持仓占比': float(industry_proportion),
                '股票数量': len(group),
                '平均持仓市值': float(group['持仓市值'].mean()),
                '最大持仓股票': group.loc[group['持仓市值'].idxmax(), '股票名称'] if '股票名称' in group.columns else '',
                '最大持仓市值': float(group['持仓市值'].max()),
                '股票明细': stocks_in_industry[:5]  # 只保留前5只
            })
        
        # 按持仓占比排序
        distribution.sort(key=lambda x: x['持仓占比'], reverse=True)
        
        return distribution
    
    def _calculate_concentration_metrics(self, portfolio_df: pd.DataFrame, 
                                        industry_distribution: List[Dict]) -> Dict:
        """
        计算集中度指标
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            industry_distribution (List[Dict]): 行业分布
            
        Returns:
            Dict: 集中度指标
        """
        # 计算赫芬达尔-赫希曼指数 (HHI)
        total_value = portfolio_df['持仓市值'].sum()
        if total_value > 0:
            market_shares = portfolio_df['持仓市值'] / total_value
            hhi = (market_shares ** 2).sum() * 10000  # HHI通常乘以10000
        else:
            hhi = 0
        
        # 行业集中度
        industry_hhi = 0
        if industry_distribution:
            industry_shares = [d['持仓占比'] / 100 for d in industry_distribution]
            industry_hhi = sum([s ** 2 for s in industry_shares]) * 10000
        
        # 前十大持仓集中度
        top_10_stocks = portfolio_df.nlargest(10, '持仓市值')
        top_10_concentration = top_10_stocks['持仓市值'].sum() / total_value * 100 if total_value > 0 else 0
        
        # 前三大行业集中度
        top_3_industries = sorted(industry_distribution, key=lambda x: x['持仓占比'], reverse=True)[:3]
        top_3_industry_concentration = sum([d['持仓占比'] for d in top_3_industries])
        
        # 最大单一行业暴露
        max_industry_exposure = max([d['持仓占比'] for d in industry_distribution]) if industry_distribution else 0
        
        # 最大单一股票暴露
        max_stock_exposure = portfolio_df['持仓市值'].max() / total_value * 100 if total_value > 0 else 0
        
        return {
            'hhi_index': float(hhi),
            'industry_hhi_index': float(industry_hhi),
            'top_10_concentration': float(top_10_concentration),
            'top_3_industry_concentration': float(top_3_industry_concentration),
            'max_industry_exposure': float(max_industry_exposure),
            'max_stock_exposure': float(max_stock_exposure),
            'concentration_risk_level': self._assess_concentration_risk(hhi, max_industry_exposure)
        }
    
    def _assess_concentration_risk(self, hhi: float, max_industry_exposure: float) -> str:
        """
        评估集中度风险等级
        
        Args:
            hhi (float): HHI指数
            max_industry_exposure (float): 最大行业暴露
            
        Returns:
            str: 风险等级
        """
        if hhi > 2500 or max_industry_exposure > 40:
            return "高风险"
        elif hhi > 1500 or max_industry_exposure > 30:
            return "中高风险"
        elif hhi > 1000 or max_industry_exposure > 20:
            return "中等风险"
        elif hhi > 500 or max_industry_exposure > 10:
            return "中低风险"
        else:
            return "低风险"
    
    def _calculate_industry_deviation(self, industry_distribution: List[Dict]) -> List[Dict]:
        """
        计算行业偏离度（相对于市场基准）
        
        Args:
            industry_distribution (List[Dict]): 实际行业分布
            
        Returns:
            List[Dict]: 行业偏离度分析
        """
        # 这里使用沪深300的行业权重作为基准（示例数据）
        # 实际应用中应从市场数据获取
        benchmark_weights = {
            '银行': 12.5,
            '非银金融': 10.2,
            '食品饮料': 8.7,
            '电子': 7.9,
            '医药生物': 7.3,
            '家用电器': 5.8,
            '电气设备': 5.2,
            '计算机': 4.9,
            '房地产': 4.5,
            '汽车': 4.1,
            '其他': 28.9  # 剩余行业
        }
        
        deviation_analysis = []
        
        for industry_data in industry_distribution:
            industry_name = industry_data['行业名称']
            actual_weight = industry_data['持仓占比']
            benchmark_weight = benchmark_weights.get(industry_name, 0)
            
            if industry_name not in benchmark_weights:
                benchmark_weight = benchmark_weights.get('其他', 0)
            
            deviation = actual_weight - benchmark_weight
            deviation_pct = (deviation / benchmark_weight * 100) if benchmark_weight > 0 else 0
            
            deviation_analysis.append({
                '行业名称': industry_name,
                '实际权重': float(actual_weight),
                '基准权重': float(benchmark_weight),
                '绝对偏离': float(deviation),
                '相对偏离': float(deviation_pct),
                '偏离方向': '超配' if deviation > 0 else '低配',
                '偏离程度': self._assess_deviation_level(abs(deviation))
            })
        
        # 按绝对偏离排序
        deviation_analysis.sort(key=lambda x: abs(x['绝对偏离']), reverse=True)
        
        return deviation_analysis
    
    def _assess_deviation_level(self, deviation: float) -> str:
        """评估偏离程度"""
        if deviation > 10:
            return "显著偏离"
        elif deviation > 5:
            return "较大偏离"
        elif deviation > 2:
            return "适度偏离"
        else:
            return "正常范围"
    
    def _get_top_holdings(self, portfolio_df: pd.DataFrame, top_n: int = 10) -> List[Dict]:
        """
        获取前N大持仓
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            top_n (int): 前N大持仓
            
        Returns:
            List[Dict]: 前N大持仓列表
        """
        top_stocks = portfolio_df.nlargest(top_n, '持仓市值')
        
        top_holdings = []
        for _, row in top_stocks.iterrows():
            holding = {
                '股票代码': row['股票代码'],
                '股票名称': row.get('股票名称', ''),
                '行业分类': self.industry_mapping.get(row['股票代码'], '其他'),
                '持仓数量': int(row['持仓数量']) if '持仓数量' in row.index else 0,
                '成本价': float(row.get('成本价', 0)),
                '最新价': float(row.get('最新价', 0)) if '最新价' in row.index else 0,
                '持仓市值': float(row['持仓市值']),
                '盈亏比例': float(row.get('盈亏比例', 0)) if '盈亏比例' in row.index else 0,
                '持仓占比': float(row['持仓市值'] / portfolio_df['持仓市值'].sum() * 100) if portfolio_df['持仓市值'].sum() > 0 else 0
            }
            top_holdings.append(holding)
        
        return top_holdings
    
    def _calculate_industry_exposure(self, portfolio_df: pd.DataFrame) -> Dict:
        """
        计算行业暴露度
        
        Args:
            portfolio_df (pandas.DataFrame): 持仓数据
            
        Returns:
            Dict: 行业暴露度分析
        """
        # 确保有行业分类
        # 确保portfolio_df是DataFrame
        if isinstance(portfolio_df, pd.Series):
            portfolio_df = portfolio_df.to_frame().T
        
        if '行业分类' not in portfolio_df.columns:
            portfolio_df['行业分类'] = portfolio_df['股票代码'].apply(
                lambda x: self.industry_mapping.get(x, '其他')
            )
        
        industry_exposure = {}
        total_value = portfolio_df['持仓市值'].sum()
        
        if total_value > 0:
            for industry in portfolio_df['行业分类'].unique():
                industry_value = portfolio_df[portfolio_df['行业分类'] == industry]['持仓市值'].sum()
                exposure_pct = industry_value / total_value * 100
                
                # 计算行业内个股相关性（简化版）
                industry_stocks = portfolio_df[portfolio_df['行业分类'] == industry]
                if len(industry_stocks) > 1:
                    # 这里可以计算实际的相关性，简化处理
                    correlation_risk = "中等" if len(industry_stocks) > 3 else "较高"
                else:
                    correlation_risk = "不适用"
                
                industry_exposure[industry] = {
                    '暴露比例': float(exposure_pct),
                    '股票数量': int(len(industry_stocks)),
                    '平均仓位': float(industry_stocks['持仓市值'].mean()),
                    '集中度': float(industry_stocks['持仓市值'].std() / industry_stocks['持仓市值'].mean()) if len(industry_stocks) > 1 else 0,
                    '相关性风险': correlation_risk
                }
        
        return industry_exposure
    
    def analyze_industry_rotation(self, current_portfolio: Dict, 
                                  historical_data: Optional[List] = None) -> Dict:
        """
        分析行业轮动
        
        Args:
            current_portfolio (Dict): 当前持仓分析结果
            historical_data (List, optional): 历史行业配置数据
            
        Returns:
            Dict: 行业轮动分析结果
        """
        logger.info("开始行业轮动分析")
        
        if historical_data is None:
            historical_data = self._get_sample_historical_data()
        
        rotation_analysis = {
            'current_industries': [],
            'rotation_trends': [],
            'momentum_analysis': [],
            'recommendations': []
        }
        
        # 分析当前行业配置
        if 'industry_distribution' in current_portfolio:
            current_industries = current_portfolio['industry_distribution']
            rotation_analysis['current_industries'] = current_industries
            
            # 分析行业轮动趋势
            if historical_data:
                rotation_trends = self._analyze_rotation_trends(current_industries, historical_data)
                rotation_analysis['rotation_trends'] = rotation_trends
            
            # 分析行业动量
            momentum_analysis = self._analyze_industry_momentum(current_industries)
            rotation_analysis['momentum_analysis'] = momentum_analysis
            
            # 生成轮动建议
            recommendations = self._generate_rotation_recommendations(
                current_industries, rotation_analysis.get('rotation_trends', []), momentum_analysis
            )
            rotation_analysis['recommendations'] = recommendations
        
        logger.info("行业轮动分析完成")
        return rotation_analysis
    
    def _analyze_rotation_trends(self, current_industries: List[Dict], 
                                 historical_data: List[Dict]) -> List[Dict]:
        """
        分析行业轮动趋势
        
        Args:
            current_industries (List[Dict]): 当前行业分布
            historical_data (List[Dict]): 历史行业配置数据
            
        Returns:
            List[Dict]: 轮动趋势分析
        """
        trends = []
        
        # 这里简化处理，实际应该比较历史数据
        # 示例：假设我们有一些历史配置数据
        
        # 创建行业变化趋势
        for industry in current_industries[:10]:  # 分析前10大行业
            industry_name = industry['行业名称']
            current_weight = industry['持仓占比']
            
            # 模拟历史数据（实际应从数据库获取）
            historical_weights = {
                '1个月前': current_weight * (1 + np.random.uniform(-0.2, 0.2)),
                '3个月前': current_weight * (1 + np.random.uniform(-0.3, 0.3)),
                '6个月前': current_weight * (1 + np.random.uniform(-0.4, 0.4))
            }
            
            # 计算变化趋势
            trend_1m = current_weight - historical_weights['1个月前']
            trend_3m = current_weight - historical_weights['3个月前']
            trend_6m = current_weight - historical_weights['6个月前']
            
            # 判断趋势方向
            if trend_1m > 1:
                short_term_trend = "增配"
            elif trend_1m < -1:
                short_term_trend = "减配"
            else:
                short_term_trend = "稳定"
            
            trends.append({
                '行业名称': industry_name,
                '当前权重': float(current_weight),
                '历史权重': historical_weights,
                '短期趋势': short_term_trend,
                '趋势强度': self._assess_trend_strength(trend_1m, trend_3m, trend_6m),
                '趋势持续性': self._assess_trend_consistency(trend_1m, trend_3m, trend_6m)
            })
        
        return trends
    
    def _analyze_industry_momentum(self, current_industries: List[Dict]) -> List[Dict]:
        """
        分析行业动量
        
        Args:
            current_industries (List[Dict]): 当前行业分布
            
        Returns:
            List[Dict]: 行业动量分析
        """
        momentum_analysis = []
        
        # 模拟行业动量数据（实际应从市场数据获取）
        for industry in current_industries[:10]:
            industry_name = industry['行业名称']
            
            # 模拟动量指标
            momentum_indicators = {
                '近期收益': np.random.uniform(-10, 15),  # 近1月收益率%
                '相对强度': np.random.uniform(0, 100),
                '动量得分': np.random.uniform(0, 100),
                '资金流向': np.random.uniform(-5, 5),  # 亿元
                '市场关注度': np.random.uniform(0, 100)
            }
            
            # 评估动量状态
            momentum_status = "强势" if momentum_indicators['近期收益'] > 5 else \
                             "弱势" if momentum_indicators['近期收益'] < -5 else "中性"
            
            momentum_analysis.append({
                '行业名称': industry_name,
                '动量指标': momentum_indicators,
                '动量状态': momentum_status,
                '投资吸引力': self._assess_investment_attractiveness(momentum_indicators),
                '建议关注度': "高" if momentum_indicators['相对强度'] > 70 else \
                           "低" if momentum_indicators['相对强度'] < 30 else "中"
            })
        
        # 按动量得分排序
        momentum_analysis.sort(key=lambda x: x['动量指标']['动量得分'], reverse=True)
        
        return momentum_analysis
    
    def _generate_rotation_recommendations(self, current_industries: List[Dict],
                                           rotation_trends: List[Dict],
                                           momentum_analysis: List[Dict]) -> List[Dict]:
        """
        生成行业轮动建议
        
        Args:
            current_industries (List[Dict]): 当前行业分布
            rotation_trends (List[Dict]): 轮动趋势分析
            momentum_analysis (List[Dict]): 行业动量分析
            
        Returns:
            List[Dict]: 轮动建议
        """
        recommendations = []
        
        # 结合当前配置、趋势和动量生成建议
        for i, industry in enumerate(current_industries[:8]):  # 分析前8大行业
            industry_name = industry['行业名称']
            current_weight = industry['持仓占比']
            
            # 找到对应的趋势和动量数据
            trend_data = next((t for t in rotation_trends if t['行业名称'] == industry_name), None)
            momentum_data = next((m for m in momentum_analysis if m['行业名称'] == industry_name), None)
            
            if trend_data and momentum_data:
                # 综合分析生成建议
                analysis = self._comprehensive_analysis(industry, trend_data, momentum_data)
                
                if analysis['recommendation'] != "维持":
                    recommendations.append({
                        '行业名称': industry_name,
                        '当前权重': float(current_weight),
                        '建议方向': analysis['recommendation'],
                        '建议幅度': analysis['suggested_change'],
                        '理由': analysis['rationale'],
                        '优先级': analysis['priority']
                    })
        
        # 按优先级排序
        recommendations.sort(key=lambda x: x['优先级'])
        
        return recommendations
    
    def _comprehensive_analysis(self, industry_data: Dict, trend_data: Dict, 
                               momentum_data: Dict) -> Dict:
        """综合行业分析"""
        industry_name = industry_data['行业名称']
        current_weight = industry_data['持仓占比']
        
        # 基于趋势和动量生成建议
        trend_direction = trend_data.get('短期趋势', '稳定')
        momentum_status = momentum_data.get('动量状态', '中性')
        
        # 决策逻辑
        if trend_direction == "增配" and momentum_status == "强势":
            if current_weight > 15:  # 权重已较高
                recommendation = "维持"
                suggested_change = 0
                rationale = f"{industry_name}趋势和动量良好，但当前权重已较高，建议维持"
                priority = 3
            else:
                recommendation = "增配"
                suggested_change = min(5, 15 - current_weight)  # 建议增配幅度
                rationale = f"{industry_name}趋势向上且动量强势，建议适度增配"
                priority = 1
                
        elif trend_direction == "减配" and momentum_status == "弱势":
            if current_weight < 5:  # 权重已较低
                recommendation = "维持"
                suggested_change = 0
                rationale = f"{industry_name}趋势向下且动量弱势，但当前权重已较低"
                priority = 3
            else:
                recommendation = "减配"
                suggested_change = min(3, current_weight - 2)  # 建议减配幅度
                rationale = f"{industry_name}趋势向下且动量弱势，建议适度减配"
                priority = 2
                
        else:
            recommendation = "维持"
            suggested_change = 0
            rationale = f"{industry_name}趋势和动量中性，建议维持当前配置"
            priority = 3
        
        return {
            'recommendation': recommendation,
            'suggested_change': suggested_change,
            'rationale': rationale,
            'priority': priority
        }
    
    def _get_sample_historical_data(self):
        """获取示例历史数据"""
        # 实际应从数据库获取
        return []
    
    def _assess_trend_strength(self, trend_1m, trend_3m, trend_6m):
        """评估趋势强度"""
        avg_trend = (abs(trend_1m) + abs(trend_3m) + abs(trend_6m)) / 3
        if avg_trend > 3:
            return "强"
        elif avg_trend > 1.5:
            return "中"
        else:
            return "弱"
    
    def _assess_trend_consistency(self, trend_1m, trend_3m, trend_6m):
        """评估趋势一致性"""
        signs = [np.sign(trend_1m), np.sign(trend_3m), np.sign(trend_6m)]
        if len(set(signs)) == 1:
            return "高度一致"
        elif signs.count(signs[0]) >= 2:
            return "基本一致"
        else:
            return "不一致"
    
    def _assess_investment_attractiveness(self, momentum_indicators):
        """评估投资吸引力"""
        score = (momentum_indicators['近期收益'] * 0.4 + 
                momentum_indicators['相对强度'] * 0.3 +
                momentum_indicators['市场关注度'] * 0.3)
        
        if score > 70:
            return "高"
        elif score > 40:
            return "中"
        else:
            return "低"


# 示例使用
if __name__ == "__main__":
    # 示例：行业分析
    analyzer = IndustryAnalyzer()
    
    # 示例持仓数据
    sample_portfolio = [
        {'股票代码': '000001', '股票名称': '平安银行', '持仓数量': 1000, '成本价': 15.20, '最新价': 16.50},
        {'股票代码': '600036', '股票名称': '招商银行', '持仓数量': 800, '成本价': 32.50, '最新价': 35.20},
        {'股票代码': '000858', '股票名称': '五粮液', '持仓数量': 500, '成本价': 180.30, '最新价': 195.00},
        {'股票代码': '002415', '股票名称': '海康威视', '持仓数量': 300, '成本价': 35.80, '最新价': 38.50},
        {'股票代码': '600519', '股票名称': '贵州茅台', '持仓数量': 200, '成本价': 1800.00, '最新价': 1850.00},
        {'股票代码': '000333', '股票名称': '美的集团', '持仓数量': 600, '成本价': 58.90, '最新价': 62.30},
        {'股票代码': '300750', '股票名称': '宁德时代', '持仓数量': 400, '成本价': 210.50, '最新价': 225.00},
        {'股票代码': '600887', '股票名称': '伊利股份', '持仓数量': 700, '成本价': 28.70, '最新价': 30.20},
        {'股票代码': '601318', '股票名称': '中国平安', '持仓数量': 900, '成本价': 45.60, '最新价': 48.30},
        {'股票代码': '000725', '股票名称': '京东方A', '持仓数量': 1000, '成本价': 4.20, '最新价': 4.50},
    ]
    
    portfolio_df = pd.DataFrame(sample_portfolio)
    
    # 计算持仓市值
    portfolio_df['持仓市值'] = portfolio_df['持仓数量'] * portfolio_df['最新价']
    portfolio_df['盈亏比例'] = (portfolio_df['最新价'] - portfolio_df['成本价']) / portfolio_df['成本价'] * 100
    
    # 分析持仓结构
    structure_analysis = analyzer.analyze_portfolio_structure(portfolio_df)
    
    if structure_analysis:
        print("持仓结构分析结果:")
        print(f"总市值: {structure_analysis['portfolio_summary']['total_market_value']:,.2f}元")
        print(f"股票数量: {structure_analysis['portfolio_summary']['total_stocks']}只")
        print(f"HHI指数: {structure_analysis['concentration_analysis']['hhi_index']:.2f}")
        
        print("\n行业分布（前5大）:")
        for i, industry in enumerate(structure_analysis['industry_distribution'][:5]):
            print(f"{i+1}. {industry['行业名称']}: {industry['持仓占比']:.1f}% ({industry['持仓市值']:,.0f}元)")
        
        print("\n前5大持仓:")
        for i, holding in enumerate(structure_analysis['top_holdings'][:5]):
            print(f"{i+1}. {holding['股票名称']}({holding['股票代码']}): {holding['持仓占比']:.1f}%")
        
        # 行业轮动分析
        rotation_analysis = analyzer.analyze_industry_rotation(structure_analysis)
        
        if rotation_analysis.get('recommendations'):
            print("\n行业轮动建议:")
            for rec in rotation_analysis['recommendations']:
                print(f"- {rec['行业名称']}: {rec['建议方向']} {rec['建议幅度']:.1f}% ({rec['理由']})")