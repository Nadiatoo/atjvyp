#!/usr/bin/env python3
"""
基础功能测试
测试系统核心功能是否可用
"""

import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    modules_to_test = [
        ("import_data", "数据导入模块"),
        ("market_data", "行情数据模块"),
        ("industry_analysis", "行业分析模块"),
        ("risk_assessment", "风险评估模块"),
        ("report_generator", "报告生成模块"),
    ]
    
    all_passed = True
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {description}导入成功")
        except ImportError as e:
            print(f"❌ {description}导入失败: {e}")
            all_passed = False
    
    return all_passed

def test_data_loading():
    """测试数据加载"""
    print("\n📊 测试数据加载...")
    
    try:
        from import_data import PortfolioDataImporter
        
        # 创建导入器实例
        importer = PortfolioDataImporter()
        
        # 加载示例数据
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'sample_portfolio.csv')
        if os.path.exists(data_path):
            print(f"✅ 找到示例数据: {data_path}")
            
            # 尝试读取数据
            try:
                import pandas as pd
                df = pd.read_csv(data_path)
                print(f"✅ 数据读取成功，共 {len(df)} 条记录")
                print(f"   列名: {list(df.columns)}")
                return True
            except Exception as e:
                print(f"❌ 数据读取失败: {e}")
                return False
        else:
            print(f"❌ 示例数据文件不存在: {data_path}")
            return False
            
    except Exception as e:
        print(f"❌ 数据加载测试失败: {e}")
        return False

def test_main_module():
    """测试主模块"""
    print("\n🚀 测试主模块...")
    
    try:
        from main import PortfolioAnalysisSystem
        
        # 创建系统实例
        system = PortfolioAnalysisSystem()
        print("✅ 系统实例创建成功")
        
        # 检查系统属性
        print(f"   分析日期: {system.analysis_date if hasattr(system, 'analysis_date') else '未设置'}")
        print(f"   客户名称: {system.client_name if hasattr(system, 'client_name') else '未设置'}")
        print(f"   分析师: {system.analyst_name if hasattr(system, 'analyst_name') else '未设置'}")
        
        return True
    except Exception as e:
        print(f"❌ 主模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """测试依赖包"""
    print("\n📦 测试依赖包...")
    
    deps_to_test = [
        ("pandas", "数据处理"),
        ("numpy", "数值计算"),
        ("openpyxl", "Excel处理"),
        ("jinja2", "模板引擎"),
        ("markdown", "Markdown处理"),
        ("requests", "网络请求"),
    ]
    
    all_passed = True
    for dep_name, description in deps_to_test:
        try:
            __import__(dep_name)
            print(f"✅ {description} ({dep_name}) 可用")
        except ImportError:
            print(f"❌ {description} ({dep_name}) 缺失")
            all_passed = False
    
    return all_passed

def main():
    print("=" * 60)
    print("持仓分析系统 - 基础功能测试")
    print("=" * 60)
    
    # 测试依赖包
    deps_ok = test_dependencies()
    
    # 测试模块导入
    imports_ok = test_imports()
    
    # 测试数据加载
    data_ok = test_data_loading()
    
    # 测试主模块
    main_ok = test_main_module()
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    results = {
        "依赖包测试": deps_ok,
        "模块导入测试": imports_ok,
        "数据加载测试": data_ok,
        "主模块测试": main_ok,
    }
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有基础测试通过！系统可以运行。")
        print("\n下一步:")
        print("1. 运行完整分析: python src/main.py data/sample_portfolio.csv")
        print("2. 生成报告: python src/main.py data/sample_portfolio.csv --client-name '测试客户'")
    else:
        print("⚠️ 部分测试失败，需要修复问题。")
        print("\n建议:")
        print("1. 安装缺失的依赖包: pip install pandas numpy openpyxl jinja2 markdown requests")
        print("2. 检查模块导入错误")
        print("3. 确保数据文件存在")
    
    print(f"\nPython路径: {sys.executable}")
    print(f"当前目录: {os.getcwd()}")

if __name__ == "__main__":
    main()