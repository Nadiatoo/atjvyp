#!/usr/bin/env python3
"""
调试持仓分析系统
"""

import sys
import os
import pandas as pd

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def debug_portfolio_data():
    """调试持仓数据"""
    print("🔍 调试持仓数据...")
    
    try:
        from import_data import PortfolioDataImporter
        
        # 创建导入器
        importer = PortfolioDataImporter()
        
        # 加载数据
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'sample_portfolio.csv')
        print(f"数据文件: {data_path}")
        
        # 直接使用pandas读取
        df = pd.read_csv(data_path)
        print(f"原始数据形状: {df.shape}")
        print(f"原始数据类型: {type(df)}")
        print(f"原始数据列名: {list(df.columns)}")
        print(f"前3行数据:")
        print(df.head(3))
        
        # 使用导入器加载
        print("\n使用导入器加载数据...")
        portfolio_data = importer.import_excel_file(data_path)
        print(f"导入器返回类型: {type(portfolio_data)}")
        
        if isinstance(portfolio_data, pd.DataFrame):
            print(f"导入器返回DataFrame形状: {portfolio_data.shape}")
            print(f"导入器返回DataFrame列名: {list(portfolio_data.columns)}")
            print(f"前3行数据:")
            print(portfolio_data.head(3))
        elif isinstance(portfolio_data, bool):
            print(f"导入器返回布尔值: {portfolio_data}")
        else:
            print(f"导入器返回其他类型: {portfolio_data}")
            
        return portfolio_data
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def debug_industry_analysis(portfolio_data):
    """调试行业分析"""
    print("\n🔍 调试行业分析...")
    
    try:
        from industry_analysis import IndustryAnalyzer
        
        # 创建分析器
        analyzer = IndustryAnalyzer()
        
        print(f"传递给分析器的数据类型: {type(portfolio_data)}")
        
        if isinstance(portfolio_data, pd.DataFrame):
            print(f"DataFrame形状: {portfolio_data.shape}")
            print(f"DataFrame列名: {list(portfolio_data.columns)}")
            
            # 检查是否有持仓市值列
            if '持仓市值' in portfolio_data.columns:
                print("✅ DataFrame包含'持仓市值'列")
            else:
                print("❌ DataFrame缺少'持仓市值'列")
                # 尝试添加模拟的持仓市值列
                if '持仓数量' in portfolio_data.columns and '成本价' in portfolio_data.columns:
                    print("尝试添加模拟持仓市值...")
                    portfolio_data['持仓市值'] = portfolio_data['持仓数量'] * portfolio_data['成本价']
                    print(f"添加后列名: {list(portfolio_data.columns)}")
        
        # 执行分析
        print("\n执行行业分析...")
        result = analyzer.analyze_portfolio_structure(portfolio_data)
        print(f"分析结果类型: {type(result)}")
        
        if isinstance(result, dict):
            print(f"分析结果字典键: {list(result.keys())}")
            if result:
                first_key = list(result.keys())[0]
                print(f"第一个行业数据: {first_key} = {result[first_key]}")
        else:
            print(f"分析结果: {result}")
            
        return result
        
    except Exception as e:
        print(f"❌ 行业分析调试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def debug_main_module():
    """调试主模块"""
    print("\n🔍 调试主模块...")
    
    try:
        from main import PortfolioAnalysisSystem
        
        # 创建系统实例
        system = PortfolioAnalysisSystem()
        print("✅ 系统实例创建成功")
        
        # 检查属性
        print(f"系统属性:")
        for attr in ['portfolio_df', 'industry_analyzer', 'risk_assessor']:
            if hasattr(system, attr):
                value = getattr(system, attr)
                print(f"  {attr}: {type(value)}")
                if attr == 'portfolio_df' and value is not None:
                    print(f"   形状: {value.shape if hasattr(value, 'shape') else 'N/A'}")
            else:
                print(f"  {attr}: 未设置")
        
        # 尝试加载数据
        print("\n尝试加载数据...")
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'sample_portfolio.csv')
        success = system.load_portfolio_data(data_path, client_info={"name": "测试客户"})
        print(f"加载数据结果: {success}")
        
        if success and hasattr(system, 'portfolio_df') and system.portfolio_df is not None:
            print(f"portfolio_df类型: {type(system.portfolio_df)}")
            if isinstance(system.portfolio_df, pd.DataFrame):
                print(f"portfolio_df形状: {system.portfolio_df.shape}")
                print(f"portfolio_df列名: {list(system.portfolio_df.columns)}")
            elif isinstance(system.portfolio_df, pd.Series):
                print(f"portfolio_df是Series，转换为DataFrame测试...")
                df = system.portfolio_df.to_frame().T
                print(f"转换后形状: {df.shape}")
                print(f"转换后列名: {list(df.columns)}")
        
        return system
        
    except Exception as e:
        print(f"❌ 主模块调试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("=" * 70)
    print("持仓分析系统 - 深度调试")
    print("=" * 70)
    
    # 调试1: 数据加载
    portfolio_data = debug_portfolio_data()
    
    if portfolio_data is not None:
        # 调试2: 行业分析
        analysis_result = debug_industry_analysis(portfolio_data)
    
    # 调试3: 主模块
    system = debug_main_module()
    
    print("\n" + "=" * 70)
    print("调试完成")
    print("=" * 70)
    
    print("\n建议:")
    if portfolio_data is None:
        print("1. 检查数据文件格式和路径")
    elif isinstance(portfolio_data, bool) and not portfolio_data:
        print("1. 数据加载失败，检查导入器逻辑")
    else:
        print("1. 数据加载正常")
    
    print("2. 检查industry_analysis.py中的类型转换逻辑")
    print("3. 确保main.py正确设置portfolio_df属性")
    
    print(f"\nPython路径: {sys.executable}")
    print(f"pandas版本: {pd.__version__}")

if __name__ == "__main__":
    main()