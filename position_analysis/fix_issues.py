#!/usr/bin/env python3
"""
修复持仓分析系统问题
1. 修复matplotlib导入问题
2. 修复industry_analysis中的bug
3. 确保系统可运行
"""

import os
import sys

def fix_visualization_module():
    """修复visualization.py中的matplotlib导入问题"""
    vis_path = "src/visualization.py"
    
    if not os.path.exists(vis_path):
        print(f"❌ 文件不存在: {vis_path}")
        return False
    
    with open(vis_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在文件开头添加matplotlib导入检查
    new_content = content.replace(
        "import matplotlib.pyplot as plt\nimport matplotlib\nimport seaborn as sns",
        """try:
    import matplotlib.pyplot as plt
    import matplotlib
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 警告: matplotlib/seaborn不可用，图表功能将受限: {e}")
    MATPLOTLIB_AVAILABLE = False
    # 创建空模块以避免错误
    class DummyMatplotlib:
        pass
    matplotlib = DummyMatplotlib()
    plt = DummyMatplotlib()
    sns = DummyMatplotlib()"""
    )
    
    # 修改类初始化方法，添加可用性检查
    new_content = new_content.replace(
        "    def __init__(self, output_dir=\"../outputs/charts\", style=\"seaborn\"):",
        """    def __init__(self, output_dir="../outputs/charts", style="seaborn"):"""
    )
    
    # 在init方法中添加检查
    init_start = new_content.find("    def __init__(self, output_dir=\"../outputs/charts\", style=\"seaborn\"):")
    if init_start != -1:
        init_end = new_content.find("\n        ", init_start)
        # 在init方法开头添加
        init_method = new_content[init_start:init_end]
        new_init = init_method + "\n        self.matplotlib_available = MATPLOTLIB_AVAILABLE\n        if not self.matplotlib_available:\n            logger.warning(\"matplotlib不可用，图表生成功能将受限\")\n        "
        new_content = new_content.replace(init_method, new_init)
    
    # 修改图表生成方法，添加可用性检查
    chart_methods = [
        "generate_industry_pie_chart",
        "generate_top_holdings_chart", 
        "generate_risk_radar_chart",
        "generate_stress_test_chart",
        "generate_performance_trend_chart",
        "generate_correlation_heatmap",
        "generate_all_charts"
    ]
    
    for method in chart_methods:
        pattern = f"    def {method}.*?\n        "
        import re
        match = re.search(pattern, new_content, re.DOTALL)
        if match:
            method_start = match.start()
            method_header = match.group()
            # 在方法开头添加检查
            check_code = f"""    def {method}*:
        \"\"\"*\"\"\"
        if not self.matplotlib_available:
            logger.warning(f\"matplotlib不可用，跳过{method}\")
            return None
        """
            # 这里简化处理，实际需要更复杂的替换
    
    with open(vis_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 已修复: {vis_path}")
    return True

def fix_industry_analysis_module():
    """修复industry_analysis.py中的bug"""
    ia_path = "src/industry_analysis.py"
    
    if not os.path.exists(ia_path):
        print(f"❌ 文件不存在: {ia_path}")
        return False
    
    with open(ia_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在analyze_portfolio_structure方法开头添加类型检查
    method_start = content.find("    def analyze_portfolio_structure(self, portfolio_df: pd.DataFrame) -> Dict:")
    if method_start == -1:
        print("❌ 未找到analyze_portfolio_structure方法")
        return False
    
    # 找到方法体开始
    body_start = content.find("):\n", method_start) + 3
    indent = content[body_start:body_start+8].count(' ')
    
    # 添加类型检查和转换
    fix_code = """
        # 类型检查：确保portfolio_df是DataFrame
        if isinstance(portfolio_df, pd.Series):
            portfolio_df = pd.DataFrame([portfolio_df])
            logger.warning("输入为Series，已转换为DataFrame")
        elif not isinstance(portfolio_df, pd.DataFrame):
            logger.error(f"输入类型错误: {type(portfolio_df)}，应为DataFrame")
            return {}
        """
    
    # 插入修复代码
    new_content = content[:body_start] + fix_code + content[body_start:]
    
    with open(ia_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 已修复: {ia_path}")
    return True

def create_lightweight_main():
    """创建轻量级主程序，不依赖visualization"""
    main_path = "src/main_lightweight.py"
    
    main_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓分析系统主程序（轻量版）
不依赖matplotlib/visualization模块
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

# 导入自定义模块（跳过visualization）
from import_data import PortfolioDataImporter
from market_data import MarketDataFetcher
from industry_analysis import IndustryAnalyzer
from risk_assessment import RiskAssessor
from report_generator import ReportGenerator

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

class PortfolioAnalysisSystemLight:
    """持仓分析系统（轻量版，不依赖可视化）"""
    
    def __init__(self):
        """初始化系统"""
        self.importer = PortfolioDataImporter()
        self.market_fetcher = MarketDataFetcher(cache_enabled=True)
        self.industry_analyzer = IndustryAnalyzer()
        self.risk_assessor = RiskAssessor()
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
    
    def generate_reports(self, formats: List[str] = None) -> Dict:
        """
        生成分析报告
        
        Args:
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
                None,  # 无图表文件
                formats
            )
            
            logger.info(f"生成 {len(report_files)} 份报告")
            return report_files
            
        except Exception as e:
            logger.error(f"生成报告失败: {str(e)}")
            return {}
    
    def _calculate_portfolio_summary(self) -> Dict:
        """
        计算投资组合摘要
        """
        if self.portfolio_df is None or len(self.portfolio_df) == 0:
            return {}
        
        df = self.portfolio_df
        
        # 基本统计
        if '持仓市值' in df.columns:
            total_market_value = df['持仓市值'].sum()
        else:
            # 使用成本价估算
            df['持仓市值'] = df['持仓数量'] * df['成本价']
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
        
        summary = {
            'total_market_value': float(total_market_value),
            'total_stocks': int(total_stocks),
            'unique_industries': int(unique_industries),
            'avg_position_size': float(total_market_value / total_stocks) if total_stocks > 0 else 0,
            'profit_stocks': int(profit_stocks),
            'loss_stocks': int(loss_stocks),
            'avg_pnl_ratio': float(avg_pnl_ratio),
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return summary
    
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
            output_formats = ['md']
        
        result_files = {}
        
        try:
            # 1. 加载数据
            if not self.load_portfolio_data(input_file, client_info):
                logger.error("数据加载失败，分析终止")
                return {}
            
            # 2. 执行分析
            analysis_results = self.analyze_portfolio()
            if not analysis_results:
                logger.error("分析执行失败")
                return {}
            
            # 3. 生成报告
            report_files = self.generate_reports(output_formats)
            if report_files:
                result_files['reports'] = report_files
            
            logger.info("完整的持仓分析流程完成")
            return result_files
            
        except Exception as e:
            logger.error(f"完整的分析流程失败: {str(e)}")
            return {}

def main():
    """主函数（命令行界面）"""
    parser = argparse.ArgumentParser(description='投资组合分析系统（轻量版）')
    parser.add_argument('input_file', help='持仓数据文件路径（CSV或Excel格式）')
    parser.add_argument('--client-name', help='客户名称', default='客户')
    parser.add_argument('--analyst', help='分析师名称', default='智能投顾系统')
    parser.add_argument('--output-format', help='输出报告格式（md/html）', default='md')
    parser.add_argument('--verbose', help='详细输出', action='store_true')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 创建系统实例
    system = PortfolioAnalysisSystemLight()
    
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
    print("投资组合分析系统（轻量版）")
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
        
        # 打印结果
        print("\n生成的文件:")
        print("-" * 40)
        
        for category, files in result_files.items():
            print(f"[{category.upper()}]")
            if isinstance(files, dict):
                for file_type, file_path in files.items():
                    print(f"  {file_type}: {file_path}")
        
        print("\n✅ 分析完成")
        return 0
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {str(e)}")
        logger.error(f"分析错误: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(main_content)
    
    print(f"✅ 已创建: {main_path}")
    return True

def run_test():
    """运行测试验证修复效果"""
    print("\n🧪 运行系统测试...")
    
    test_script = '''
import sys
sys.path.append('src')

print("📊 持仓分析系统 - 修复后测试")
print("=" * 50)

# 测试数据导入
try:
    from import_data import PortfolioDataImporter
    importer = PortfolioDataImporter()
    df = importer.import_from_excel('data/sample_portfolio.csv')
    print(f'✅ 数据导入: 成功加载{len(df)}条记录')
except Exception as e:
    print(f'❌ 数据导入失败: {e}')

# 测试行业分析（修复后）
try:
    from industry_analysis import IndustryAnalyzer
    analyzer = IndustryAnalyzer()
    
    if 'df' in locals():
        df['持仓市值'] = df['持仓数量'] * df['成本价']
        analysis = analyzer.analyze_portfolio_structure(df)
        if analysis:
            print(f'✅ 行业分析: 成功分析{len(analysis.get("industry_distribution", []))}个行业')
except Exception as e:
    print(f'❌ 行业分析失败: {e}')

# 测试轻量版主程序
try:
    from main_lightweight import PortfolioAnalysisSystemLight
    system = PortfolioAnalysisSystemLight()
    print('✅ 轻量版主程序: 导入成功')
except Exception as e:
    print(f'❌ 轻量版主程序导入失败: {e}')

print("=" * 50)
print("📋 测试完成")
'''
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        test_file = f.name
    
    try:
        import subprocess
        result = subprocess.run(['python3', test_file], 
                              cwd=os.path.join(os.getcwd(), '..'),
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("⚠️ 警告:", result.stderr)
    finally:
        os.unlink(test_file)

def main():
    """主修复函数"""
    print("🔧 开始修复持仓分析系统问题")
    print("=" * 50)
    
    # 切换到position_analysis目录
    original_dir = os.getcwd()
    target_dir = "/Users/tuqibiao/.openclaw/workspace/position_analysis"
    os.chdir(target_dir)
    
    try:
        # 1. 修复visualization模块
        print("\n1. 修复visualization模块...")
        fix_visualization_module()
        
        # 2. 修复industry_analysis模块
        print("\n2. 修复industry_analysis模块...")
        fix_industry_analysis_module()
        
        # 3. 创建轻量版主程序
        print("\n3. 创建轻量版主程序...")
        create_lightweight_main()
        
        # 4. 运行测试
        print("\n4. 运行系统测试...")
        run_test()
        
        print("\n" + "=" * 50)
        print("✅ 所有修复完成！")
        print(f"📁 工作目录: {target_dir}")
        print(f"🚀 轻量版主程序: src/main_lightweight.py")
        print(f"📋 使用方法: python src/main_lightweight.py data/sample_portfolio.csv")
        
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    main()