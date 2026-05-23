#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓分析系统主程序
集成所有模块，提供命令行界面
"""

import argparse
import sys
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

# 添加模块路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入自定义模块
from import_data import PortfolioDataImporter
from market_data import MarketDataFetcher
from industry_analysis import IndustryAnalyzer
from risk_assessment import RiskAssessor
from report_generator import ReportGenerator

# 可选导入visualization（可能因matplotlib问题失败）
try:
    from visualization import PortfolioVisualizer
    VISUALIZATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 警告: visualization模块导入失败，图表功能将受限: {e}")
    VISUALIZATION_AVAILABLE = False
    # 创建空类作为占位符
    class PortfolioVisualizer:
        def __init__(self, *args, **kwargs):
            self.output_dir = kwargs.get('output_dir', '../outputs/charts')
            print(f"⚠️ visualization不可用，使用占位符")
        def generate_all_charts(self, *args, **kwargs):
            return {}
        def generate_industry_pie_chart(self, *args, **kwargs):
            return None

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../outputs/analysis.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PortfolioAnalysisSystem:
    """持仓分析系统（主控制器）"""
    
    def __init__(self):
        """初始化系统"""
        self.importer = PortfolioDataImporter()
        self.market_fetcher = MarketDataFetcher(cache_enabled=True)
        self.industry_analyzer = IndustryAnalyzer()
        self.risk_assessor = RiskAssessor()
        # 根据可用性初始化visualizer
        if VISUALIZATION_AVAILABLE:
            self.visualizer = PortfolioVisualizer(output_dir="../outputs/charts")
            self.visualization_enabled = True
        else:
            self.visualizer = None
            self.visualization_enabled = False
            logger.warning("visualization不可用，图表生成功能将受限")
        self.report_generator = ReportGenerator(output_dir="../outputs/reports")
        
        self.portfolio_df = None
        self.analysis_results = {}
        self.client_info = {}
        
    def load_portfolio_data(self, file_path: str, client_info: Dict = None) -> bool:
        """
        加载持仓数据
        
        Args:
            file_path (str): 数据文件路径
            client_info (Dict, optional): 客户信息
            
        Returns:
            bool: 是否成功加载
        """
        logger.info(f"加载持仓数据: {file_path}")
        
        try:
            # 导入数据
            self.portfolio_df = self.importer.import_from_excel(file_path)
            
            # 设置客户信息
            if client_info:
                self.client_info = client_info
            else:
                # 使用默认客户信息
                self.client_info = {
                    'name': os.path.basename(file_path).replace('.csv', '').replace('.xlsx', ''),
                    'analyst': '智能投顾系统',
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
            
            # 打印数据摘要
            validation_report = self.importer.get_validation_report()
            logger.info(f"数据加载成功: {validation_report['total_records']}条记录")
            
            if validation_report['has_errors']:
                logger.warning(f"数据验证发现{validation_report['error_count']}个问题")
                for error in validation_report['validation_errors'][:5]:  # 只显示前5个错误
                    logger.warning(f"  - {error}")
            
            return True
            
        except Exception as e:
            logger.error(f"加载持仓数据失败: {str(e)}")
            return False
    
    def update_market_data(self) -> bool:
        """
        更新市场数据
        
        Returns:
            bool: 是否成功更新
        """
        if self.portfolio_df is None or len(self.portfolio_df) == 0:
            logger.error("没有持仓数据，无法更新市场数据")
            return False
        
        logger.info("更新市场数据...")
        
        try:
            # 获取实时行情并计算持仓价值
            valued_portfolio = self.market_fetcher.calculate_portfolio_values(self.portfolio_df)
            
            if valued_portfolio is not None and not valued_portfolio.empty:
                self.portfolio_df = valued_portfolio
                logger.info(f"市场数据更新成功，共{len(self.portfolio_df)}只股票")
                return True
            else:
                logger.warning("市场数据更新失败，使用成本价计算")
                return False
                
        except Exception as e:
            logger.error(f"更新市场数据失败: {str(e)}")
            return False
    
    def analyze_portfolio(self) -> Dict:
        """
        执行完整的持仓分析
        
        Returns:
            Dict: 分析结果
        """
        if self.portfolio_df is None or len(self.portfolio_df) == 0:
            logger.error("没有持仓数据，无法进行分析")
            return {}
        
        logger.info("开始执行持仓分析...")
        
        try:
            # 1. 计算组合摘要
            portfolio_summary = self._calculate_portfolio_summary()
            
            # 2. 行业分析
            industry_analysis = self.industry_analyzer.analyze_portfolio_structure(self.portfolio_df)
            
            # 3. 行业轮动分析
            rotation_analysis = self.industry_analyzer.analyze_industry_rotation(industry_analysis)
            
            # 4. 风险评估
            risk_assessment = self.risk_assessor.assess_portfolio_risk(self.portfolio_df, industry_analysis)
            
            # 5. 整合分析结果
            self.analysis_results = {
                'portfolio_summary': portfolio_summary,
                'industry_analysis': industry_analysis,
                'rotation_analysis': rotation_analysis,
                'risk_assessment': risk_assessment,
                'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'client_info': self.client_info
            }
            
            logger.info("持仓分析完成")
            return self.analysis_results
            
        except Exception as e:
            logger.error(f"持仓分析失败: {str(e)}")
            return {}
    
    def generate_visualizations(self) -> Dict:
        """
        生成可视化图表
        
        Returns:
            Dict: 生成的图表文件路径
        """
        if not self.analysis_results:
            logger.warning("没有分析结果，请先执行分析")
            return {}
        
        logger.info("生成可视化图表...")
        
        try:
            client_name = self.client_info.get('name', '客户')
            chart_files = self.visualizer.generate_all_charts(
                self.portfolio_df, 
                self.analysis_results, 
                client_name
            )
            
            logger.info(f"生成 {len(chart_files)} 张图表")
            return chart_files
            
        except Exception as e:
            logger.error(f"生成可视化图表失败: {str(e)}")
            return {}
    
    def generate_reports(self, chart_files: Dict = None, 
                        formats: List[str] = None) -> Dict:
        """
        生成分析报告
        
        Args:
            chart_files (Dict, optional): 图表文件路径
            formats (List[str], optional): 报告格式列表
            
        Returns:
            Dict: 生成的报告文件路径
        """
        if not self.analysis_results:
            logger.warning("没有分析结果，请先执行分析")
            return {}
        
        if formats is None:
            formats = ['md', 'html']
        
        logger.info(f"生成分析报告，格式: {formats}")
        
        try:
            # 生成报告
            report_files = self.report_generator.generate_comprehensive_report(
                self.portfolio_df,
                self.analysis_results,
                self.client_info,
                chart_files,
                formats
            )
            
            logger.info(f"生成 {len(report_files)} 份报告")
            return report_files
            
        except Exception as e:
            logger.error(f"生成报告失败: {str(e)}")
            return {}
    
    def export_results(self, output_dir: str = "../outputs") -> Dict:
        """
        导出分析结果
        
        Args:
            output_dir (str): 输出目录
            
        Returns:
            Dict: 导出的文件路径
        """
        if not self.analysis_results:
            logger.warning("没有分析结果，请先执行分析")
            return {}
        
        logger.info("导出分析结果...")
        
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            client_name = self.client_info.get('name', '客户').replace(' ', '_')
            base_filename = f"{client_name}_分析结果_{timestamp}"
            
            exported_files = {}
            
            # 1. 导出持仓数据
            if self.portfolio_df is not None:
                portfolio_file = os.path.join(output_dir, f"{base_filename}_持仓数据.csv")
                self.portfolio_df.to_csv(portfolio_file, index=False, encoding='utf-8-sig')
                exported_files['portfolio_data'] = portfolio_file
                logger.info(f"导出持仓数据: {portfolio_file}")
            
            # 2. 导出分析结果（JSON）
            analysis_file = os.path.join(output_dir, f"{base_filename}_分析结果.json")
            with open(analysis_file, 'w', encoding='utf-8') as f:
                import json
                
                # 转换DataFrame为可序列化格式
                analysis_data = self.analysis_results.copy()
                if 'portfolio_data' in analysis_data:
                    del analysis_data['portfolio_data']
                
                json.dump(analysis_data, f, ensure_ascii=False, indent=2, default=str)
            
            exported_files['analysis_results'] = analysis_file
            logger.info(f"导出分析结果: {analysis_file}")
            
            # 3. 导出摘要报告（文本）
            summary_file = os.path.join(output_dir, f"{base_filename}_分析摘要.txt")
            self._export_summary_report(summary_file)
            exported_files['summary_report'] = summary_file
            logger.info(f"导出分析摘要: {summary_file}")
            
            return exported_files
            
        except Exception as e:
            logger.error(f"导出结果失败: {str(e)}")
            return {}
    
    def _calculate_portfolio_summary(self) -> Dict:
        """
        计算投资组合摘要
        
        Returns:
            Dict: 组合摘要
        """
        if self.portfolio_df is None or len(self.portfolio_df) == 0:
            return {}
        
        df = self.portfolio_df
        
        # 基本统计
        total_market_value = df['持仓市值'].sum()
        total_stocks = len(df)
        
        # 行业数量
        if '行业分类' in df.columns:
            unique_industries = df['行业分类'].nunique()
        else:
            unique_industries = 0
        
        # 盈亏统计
        if '盈亏比例' in df.columns:
            profit_stocks = (df['盈亏比例'] > 0).sum()
            loss_stocks = (df['盈亏比例'] < 0).sum()
            avg_pnl_ratio = df['盈亏比例'].mean()
        else:
            profit_stocks = 0
            loss_stocks = 0
            avg_pnl_ratio = 0
        
        # 仓位统计
        if '持仓占比' not in df.columns and total_market_value > 0:
            df['持仓占比'] = df['持仓市值'] / total_market_value * 100
        
        # 集中度指标
        if '持仓占比' in df.columns:
            top_5_concentration = df.nlargest(5, '持仓占比')['持仓占比'].sum()
            max_stock_exposure = df['持仓占比'].max()
        else:
            top_5_concentration = 0
            max_stock_exposure = 0
        
        summary = {
            'total_market_value': float(total_market_value),
            'total_stocks': int(total_stocks),
            'unique_industries': int(unique_industries),
            'avg_position_size': float(total_market_value / total_stocks) if total_stocks > 0 else 0,
            'median_position_size': float(df['持仓市值'].median()) if '持仓市值' in df.columns else 0,
            'profit_stocks': int(profit_stocks),
            'loss_stocks': int(loss_stocks),
            'avg_pnl_ratio': float(avg_pnl_ratio),
            'top_5_concentration': float(top_5_concentration),
            'max_stock_exposure': float(max_stock_exposure),
            'break_even_point': float(-avg_pnl_ratio) if avg_pnl_ratio > 0 else 0,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return summary
    
    def _export_summary_report(self, output_file: str):
        """
        导出摘要报告
        
        Args:
            output_file (str): 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("投资组合分析摘要\n")
            f.write("=" * 60 + "\n\n")
            
            # 客户信息
            f.write(f"客户名称: {self.client_info.get('name', '未知客户')}\n")
            f.write(f"分析日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 组合摘要
            if 'portfolio_summary' in self.analysis_results:
                summary = self.analysis_results['portfolio_summary']
                f.write("[组合概览]\n")
                f.write(f"  总市值: {summary.get('total_market_value', 0):,.0f}元\n")
                f.write(f"  股票数量: {summary.get('total_stocks', 0)}只\n")
                f.write(f"  行业数量: {summary.get('unique_industries', 0)}个\n")
                f.write(f"  平均盈亏: {summary.get('avg_pnl_ratio', 0):.1f}%\n")
                f.write(f"  盈利股票: {summary.get('profit_stocks', 0)}只\n")
                f.write(f"  亏损股票: {summary.get('loss_stocks', 0)}只\n\n")
            
            # 行业分布
            if 'industry_analysis' in self.analysis_results:
                industry_data = self.analysis_results['industry_analysis']
                if 'industry_distribution' in industry_data:
                    f.write("[行业分布 - 前5大]\n")
                    for i, industry in enumerate(industry_data['industry_distribution'][:5]):
                        f.write(f"  {i+1}. {industry.get('行业名称', '')}: {industry.get('持仓占比', 0):.1f}%\n")
                    f.write("\n")
            
            # 风险评估
            if 'risk_assessment' in self.analysis_results:
                risk_data = self.analysis_results['risk_assessment']
                if 'overall_risk' in risk_data:
                    overall_risk = risk_data['overall_risk']
                    f.write("[风险评估]\n")
                    f.write(f"  风险等级: {overall_risk.get('overall_risk_level', '')}\n")
                    f.write(f"  风险分数: {overall_risk.get('overall_risk_score', 0):.1f}/100\n")
                    f.write(f"  建议监控频率: {overall_risk.get('risk_monitoring_frequency', '')}\n\n")
                
                # 风险警告
                if 'risk_warnings' in risk_data and risk_data['risk_warnings']:
                    f.write("[风险警告]\n")
                    for warning in risk_data['risk_warnings'][:3]:
                        f.write(f"  ⚠️ {warning}\n")
                    f.write("\n")
            
            # 投资建议
            f.write("[关键建议]\n")
            
            # 行业轮动建议
            if 'rotation_analysis' in self.analysis_results:
                rotation_data = self.analysis_results['rotation_analysis']
                if 'recommendations' in rotation_data and rotation_data['recommendations']:
                    f.write("  行业轮动建议:\n")
                    for rec in rotation_data['recommendations'][:2]:
                        f.write(f"    • {rec.get('行业名称', '')}: {rec.get('建议方向', '')}\n")
            
            # 风险控制建议
            if 'risk_assessment' in self.analysis_results:
                risk_data = self.analysis_results['risk_assessment']
                if 'recommendations' in risk_data and risk_data['recommendations']:
                    f.write("  风险控制建议:\n")
                    for rec in risk_data['recommendations'][:2]:
                        f.write(f"    • {rec.get('action', '')}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("报告结束\n")
            f.write("=" * 60 + "\n")
    
    def run_full_analysis(self, input_file: str, client_info: Dict = None, 
                         output_formats: List[str] = None) -> Dict:
        """
        运行完整的分析流程
        
        Args:
            input_file (str): 输入文件路径
            client_info (Dict, optional): 客户信息
            output_formats (List[str], optional): 输出格式列表
            
        Returns:
            Dict: 所有生成的文件路径
        """
        logger.info("开始完整的持仓分析流程")
        
        if output_formats is None:
            output_formats = ['md', 'html']
        
        result_files = {}
        
        try:
            # 1. 加载数据
            if not self.load_portfolio_data(input_file, client_info):
                logger.error("数据加载失败，分析终止")
                return {}
            
            # 2. 更新市场数据
            self.update_market_data()
            
            # 3. 执行分析
            analysis_results = self.analyze_portfolio()
            if not analysis_results:
                logger.error("分析执行失败")
                return {}
            
            # 4. 生成可视化图表
            chart_files = self.generate_visualizations()
            if chart_files:
                result_files['charts'] = chart_files
            
            # 5. 生成报告
            report_files = self.generate_reports(chart_files, output_formats)
            if report_files:
                result_files['reports'] = report_files
            
            # 6. 导出结果
            export_files = self.export_results()
            if export_files:
                result_files['exports'] = export_files
            
            logger.info("完整的持仓分析流程完成")
            return result_files
            
        except Exception as e:
            logger.error(f"完整的分析流程失败: {str(e)}")
            return {}
    
    def print_analysis_summary(self):
        """打印分析摘要"""
        if not self.analysis_results:
            print("没有分析结果")
            return
        
        print("=" * 70)
        print("投资组合分析摘要")
        print("=" * 70)
        
        # 客户信息
        print(f"客户: {self.client_info.get('name', '未知客户')}")
        print(f"分析时间: {self.analysis_results.get('analysis_time', '未知')}")
        print()
        
        # 组合摘要
        if 'portfolio_summary' in self.analysis_results:
            summary = self.analysis_results['portfolio_summary']
            print("[组合概览]")
            print(f"  总市值: {summary.get('total_market_value', 0):,.0f}元")
            print(f"  股票数量: {summary.get('total_stocks', 0)}只")
            print(f"  行业数量: {summary.get('unique_industries', 0)}个")
            print(f"  平均盈亏: {summary.get('avg_pnl_ratio', 0):.1f}%")
            print()
        
        # 行业分布
        if 'industry_analysis' in self.analysis_results:
            industry_data = self.analysis_results['industry_analysis']
            if 'industry_distribution' in industry_data:
                print("[行业分布 - 前3大]")
                for i, industry in enumerate(industry_data['industry_distribution'][:3]):
                    print(f"  {i+1}. {industry.get('行业名称', '')}: {industry.get('持仓占比', 0):.1f}%")
                print()
        
        # 风险评估
        if 'risk_assessment' in self.analysis_results:
            risk_data = self.analysis_results['risk_assessment']
            if 'overall_risk' in risk_data:
                overall_risk = risk_data['overall_risk']
                print("[风险评估]")
                print(f"  风险等级: {overall_risk.get('overall_risk_level', '')}")
                print(f"  风险分数: {overall_risk.get('overall_risk_score', 0):.1f}/100")
                
                # 风险警告
                if 'risk_warnings' in risk_data and risk_data['risk_warnings']:
                    print(f"  风险警告: {len(risk_data['risk_warnings'])}条")
                print()
        
        # 关键建议
        print("[关键建议]")
        
        # 行业轮动建议
        if 'rotation_analysis' in self.analysis_results:
            rotation_data = self.analysis_results['rotation_analysis']
            if 'recommendations' in rotation_data and rotation_data['recommendations']:
                print("  行业轮动:")
                for rec in rotation_data['recommendations'][:2]:
                    print(f"    • {rec.get('行业名称', '')}: {rec.get('建议方向', '')}")
        
        # 风险控制建议
        if 'risk_assessment' in self.analysis_results:
            risk_data = self.analysis_results['risk_assessment']
            if 'recommendations' in risk_data and risk_data['recommendations']:
                print("  风险控制:")
                for rec in risk_data['recommendations'][:2]:
                    print(f"    • {rec.get('action', '')}")
        
        print()
        print("=" * 70)


def main():
    """主函数（命令行界面）"""
    parser = argparse.ArgumentParser(description='投资组合分析系统')
    parser.add_argument('input_file', help='持仓数据文件路径（CSV或Excel格式）')
    parser.add_argument('--client-name', help='客户名称', default='客户')
    parser.add_argument('--analyst', help='分析师名称', default='智能投顾系统')
    parser.add_argument('--output-format', help='输出报告格式（md/html/pdf/all）', default='md')
    parser.add_argument('--update-market', help='更新市场数据', action='store_true')
    parser.add_argument('--export-all', help='导出所有结果', action='store_true')
    parser.add_argument('--verbose', help='详细输出', action='store_true')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 创建系统实例
    system = PortfolioAnalysisSystem()
    
    # 准备客户信息
    client_info = {
        'name': args.client_name,
        'analyst': args.analyst,
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # 确定输出格式
    if args.output_format == 'all':
        output_formats = ['md', 'html']
    else:
        output_formats = [args.output_format]
    
    print("=" * 70)
    print("投资组合分析系统")
    print("=" * 70)
    print(f"客户: {args.client_name}")
    print(f"数据文件: {args.input_file}")
    print(f"输出格式: {', '.join(output_formats)}")
    print("=" * 70)
    print()
    
    try:
        # 运行完整分析
        result_files = system.run_full_analysis(
            input_file=args.input_file,
            client_info=client_info,
            output_formats=output_formats
        )
        
        if not result_files:
            print("❌ 分析失败")
            return 1
        
        # 打印结果摘要
        system.print_analysis_summary()
        
        # 打印生成的文件
        print("\n生成的文件:")
        print("-" * 40)
        
        for category, files in result_files.items():
            print(f"[{category.upper()}]")
            if isinstance(files, dict):
                for file_type, file_path in files.items():
                    print(f"  {file_type}: {file_path}")
            else:
                print(f"  {files}")
        
        print("\n✅ 分析完成")
        return 0
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {str(e)}")
        logger.error(f"分析错误: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    # 测试模式：使用示例数据
    if len(sys.argv) == 1:
        print("测试模式：使用示例数据")
        
        # 创建系统实例
        system = PortfolioAnalysisSystem()
        
        # 使用示例数据
        sample_file = "../data/sample_portfolio.csv"
        if os.path.exists(sample_file):
            print(f"使用示例文件: {sample_file}")
            
            # 运行分析
            result_files = system.run_full_analysis(
                input_file=sample_file,
                client_info={'name': '测试客户', 'analyst': '系统测试'},
                output_formats=['md']
            )
            
            # 打印摘要
            system.print_analysis_summary()
            
            if result_files:
                print("\n生成的文件:")
                for category, files in result_files.items():
                    print(f"[{category.upper()}]")
                    if isinstance(files, dict):
                        for file_type, file_path in files.items():
                            print(f"  {file_type}: {file_path}")
        else:
            print(f"示例文件不存在: {sample_file}")
            print("请先创建示例数据文件")
    else:
        # 命令行模式
        sys.exit(main())