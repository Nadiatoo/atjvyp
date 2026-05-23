#!/usr/bin/env python3
"""
直接测试行业分析模块
"""

import sys
import os
import pandas as pd

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_industry_analysis_directly():
    """直接测试行业分析"""
    print("🔍 直接测试行业分析模块...")
    
    try:
        from industry_analysis import IndustryAnalyzer
        
        # 创建分析器
        analyzer = IndustryAnalyzer()
        print("✅ 行业分析器创建成功")
        
        # 创建测试数据
        print("\n创建测试数据...")
        test_data = {
            '股票代码': ['000001', '600036', '000858'],
            '股票名称': ['平安银行', '招商银行', '五粮液'],
            '持仓数量': [1000, 800, 500],
            '成本价': [15.2, 32.5, 180.3],
            '持仓市值': [15200.0, 26000.0, 90150.0],
            '行业分类': ['银行', '银行', '食品饮料']
        }
        
        df = pd.DataFrame(test_data)
        print(f"测试DataFrame形状: {df.shape}")
        print(f"测试DataFrame列名: {list(df.columns)}")
        print(f"测试数据:")
        print(df)
        
        # 测试分析
        print("\n执行行业分析...")
        result = analyzer.analyze_portfolio_structure(df)
        print(f"分析结果类型: {type(result)}")
        
        if isinstance(result, dict):
            print(f"分析结果字典键: {list(result.keys())}")
            if result:
                for industry, data in result.items():
                    print(f"  {industry}: 市值={data.get('market_value', 0):.2f}, 比例={data.get('percentage', 0):.1f}%")
        else:
            print(f"分析结果: {result}")
            
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 检查错误位置
        tb = traceback.extract_tb(sys.exc_info()[2])
        for frame in tb[-3:]:  # 显示最后3个堆栈帧
            print(f"  文件: {frame.filename}, 行: {frame.lineno}, 函数: {frame.name}")
            print(f"  代码: {frame.line}")
        
        return False

def test_with_real_data():
    """使用真实数据测试"""
    print("\n🔍 使用真实数据测试...")
    
    try:
        # 加载真实数据
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'sample_portfolio.csv')
        df = pd.read_csv(data_path)
        print(f"原始数据形状: {df.shape}")
        
        # 添加持仓市值列（模拟）
        if '持仓数量' in df.columns and '成本价' in df.columns:
            df['持仓市值'] = df['持仓数量'] * df['成本价']
            print(f"添加持仓市值后形状: {df.shape}")
            print(f"列名: {list(df.columns)}")
            
            # 标准化股票代码
            df['股票代码'] = df['股票代码'].astype(str).str.zfill(6)
            print(f"标准化后股票代码示例: {df['股票代码'].iloc[:3].tolist()}")
            
            from industry_analysis import IndustryAnalyzer
            analyzer = IndustryAnalyzer()
            
            print("\n执行真实数据分析...")
            result = analyzer.analyze_portfolio_structure(df)
            
            if isinstance(result, dict) and result:
                print(f"✅ 分析成功，共 {len(result)} 个行业")
                total_value = sum(data.get('market_value', 0) for data in result.values())
                print(f"总市值: {total_value:.2f}")
                
                # 显示前5个行业
                print("\n前5个行业分布:")
                sorted_industries = sorted(result.items(), key=lambda x: x[1].get('market_value', 0), reverse=True)
                for i, (industry, data) in enumerate(sorted_industries[:5]):
                    percentage = data.get('percentage', 0)
                    print(f"  {i+1}. {industry}: {data.get('market_value', 0):.2f} ({percentage:.1f}%)")
                
                return True
            else:
                print(f"❌ 分析失败，结果: {result}")
                return False
        else:
            print("❌ 数据缺少必要列")
            return False
            
    except Exception as e:
        print(f"❌ 真实数据测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 70)
    print("行业分析模块 - 直接测试")
    print("=" * 70)
    
    # 测试1: 使用模拟数据
    test1_success = test_industry_analysis_directly()
    
    # 测试2: 使用真实数据
    test2_success = test_with_real_data()
    
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    
    if test1_success and test2_success:
        print("🎉 所有测试通过！行业分析模块工作正常。")
        print("\n问题可能在于:")
        print("1. main.py中传递的数据格式问题")
        print("2. 数据预处理步骤的问题")
        print("3. 其他模块的兼容性问题")
    elif test1_success and not test2_success:
        print("⚠️ 模拟数据测试通过，但真实数据测试失败")
        print("可能原因: 真实数据格式问题或行业映射问题")
    elif not test1_success and test2_success:
        print("⚠️ 真实数据测试通过，但模拟数据测试失败")
        print("可能原因: 测试数据格式问题")
    else:
        print("❌ 所有测试失败")
        print("需要检查行业分析模块的实现")
    
    print(f"\nPython路径: {sys.executable}")
    print(f"工作目录: {os.getcwd()}")

if __name__ == "__main__":
    main()